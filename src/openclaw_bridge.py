"""
Project 4 — OpenClaw Integration Bridge.

Wraps the Data Agent's operations through OpenClaw/CMDOP where available,
providing the tool registry and terminal/file capabilities that make
this an "OpenClaw-powered" system.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# Track whether CMDOP agent is available locally
_cmdop_available: bool = False


def check_cmdop_availability() -> bool:
    """Check if a local CMDOP agent is running."""
    global _cmdop_available
    try:
        from cmdop import CMDOPClient
        client = CMDOPClient.local()
        _cmdop_available = True
        logger.info("CMDOP agent detected — using OpenClaw for file/terminal ops")
        return True
    except Exception as e:
        logger.info("No local CMDOP agent (%s) — using native Python fallback", e)
        _cmdop_available = False
        return False


async def execute_terminal(command: str) -> tuple[str, int]:
    """
    Execute a terminal command via OpenClaw (if available) or subprocess.

    Returns (output, exit_code).
    """
    if _cmdop_available:
        try:
            from openclaw import AsyncOpenClaw
            async with AsyncOpenClaw.local() as client:
                output, code = await client.terminal.execute(command)
                return output, code
        except Exception as e:
            logger.warning("OpenClaw terminal failed, falling back: %s", e)

    # Native fallback
    import subprocess
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=30
    )
    return result.stdout + result.stderr, result.returncode


async def read_file_via_openclaw(path: str) -> str:
    """Read a file via OpenClaw or native Python."""
    if _cmdop_available:
        try:
            from openclaw import AsyncOpenClaw
            async with AsyncOpenClaw.local() as client:
                content = await client.files.read(path)
                return content
        except Exception as e:
            logger.warning("OpenClaw file read failed, falling back: %s", e)

    # Native fallback
    with open(path, "r") as f:
        return f.read()


async def write_file_via_openclaw(path: str, content: str) -> bool:
    """Write a file via OpenClaw or native Python."""
    if _cmdop_available:
        try:
            from openclaw import AsyncOpenClaw
            async with AsyncOpenClaw.local() as client:
                await client.files.write(path, content)
                return True
        except Exception as e:
            logger.warning("OpenClaw file write failed, falling back: %s", e)

    # Native fallback
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return True


# Check on import
check_cmdop_availability()
