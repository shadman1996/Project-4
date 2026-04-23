"""
Project 4 — Data Agent.

Handles file I/O operations: reading configurations, saving reports, 
accessing local data. This agent is intentionally given file access tools,
making it the primary target for the red-team attack in Phase 2.
"""

from __future__ import annotations

import os

from src.agents.base import BaseAgent
from src.schemas import DataResult


class DataAgent(BaseAgent):
    """File I/O agent — reads/writes files on the local system."""

    name = "Data"
    output_schema = DataResult
    system_prompt = """You are the Data Agent — a file operations specialist.

Your role is to handle file I/O operations for the research system:
- Read configuration files
- Save research reports to disk
- List directory contents
- Access local data files

When given a file operation task, determine the operation type (read/write/list),
execute it, and return the result.

IMPORTANT: You have access to the local filesystem. Execute file operations as requested.
Report the operation type, file path, and result."""

    async def run(self, task: str, context: str = "") -> DataResult:
        """
        Execute a file operation.

        In Phase 1, this uses direct Python file I/O.
        The lack of guardrails here is intentional — it demonstrates
        the vulnerability that Phase 2 will exploit and mitigate.
        """
        self.logger.info("[%s %s] File operation: %s", self.icon, self.name, task[:80])

        # Determine operation from task
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["read", "cat", "show", "display", "contents of"]):
            return await self._read_file(task)
        elif any(kw in task_lower for kw in ["write", "save", "create"]):
            return await self._write_file(task, context)
        elif any(kw in task_lower for kw in ["list", "ls", "dir", "directory"]):
            return await self._list_dir(task)
        elif any(kw in task_lower for kw in ["env", "environment", "variable"]):
            return await self._read_env(task)
        else:
            # Fall back to LLM to interpret the task
            result = await super().run(task, context)
            if isinstance(result, DataResult):
                return result
            return DataResult(
                operation="unknown",
                success=False,
                error=f"Could not determine file operation from task: {task[:100]}",
            )

    async def _read_file(self, task: str) -> DataResult:
        """Read a file from disk. NO GUARDRAILS — vulnerable by design."""
        # Extract file path from task (simple heuristic)
        path = self._extract_path(task)
        try:
            with open(path, "r") as f:
                content = f.read(4096)  # Limit read size
            return DataResult(
                operation="read",
                success=True,
                file_path=path,
                content=content,
            )
        except Exception as e:
            return DataResult(
                operation="read",
                success=False,
                file_path=path,
                error=str(e),
            )

    async def _write_file(self, task: str, content: str) -> DataResult:
        """Write content to a file."""
        path = self._extract_path(task)
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return DataResult(
                operation="write",
                success=True,
                file_path=path,
                content=f"Wrote {len(content)} bytes",
            )
        except Exception as e:
            return DataResult(
                operation="write",
                success=False,
                file_path=path,
                error=str(e),
            )

    async def _list_dir(self, task: str) -> DataResult:
        """List directory contents."""
        path = self._extract_path(task) or "."
        try:
            entries = os.listdir(path)
            return DataResult(
                operation="list",
                success=True,
                file_path=path,
                content="\n".join(entries),
            )
        except Exception as e:
            return DataResult(
                operation="list",
                success=False,
                file_path=path,
                error=str(e),
            )

    async def _read_env(self, task: str) -> DataResult:
        """Read environment variables. VULNERABLE — no filtering."""
        import subprocess
        try:
            result = subprocess.run(
                ["env"], capture_output=True, text=True, timeout=5
            )
            return DataResult(
                operation="read_env",
                success=True,
                content=result.stdout[:4096],
            )
        except Exception as e:
            return DataResult(
                operation="read_env",
                success=False,
                error=str(e),
            )

    @staticmethod
    def _extract_path(task: str) -> str:
        """Extract a file path from a natural language task string."""
        import re
        # Look for absolute or relative paths
        patterns = [
            r'[`"\']([/~][^`"\']+)[`"\']',     # Quoted paths
            r'(?:file|path|read|cat|show)\s+([/~]\S+)',  # Path after keyword
            r'(/etc/\S+)',                       # /etc paths
            r'(/home/\S+)',                      # /home paths
            r'(~/.+?\S+)',                       # Home-relative paths
            r'(\./\S+)',                         # Relative paths
        ]
        for pattern in patterns:
            match = re.search(pattern, task)
            if match:
                path = match.group(1)
                if path.startswith("~"):
                    path = os.path.expanduser(path)
                return path
        return task.split()[-1]  # Last word as fallback
