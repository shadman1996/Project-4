"""
Project 4 — Base Agent class.

All 7 agents inherit from this and implement their specialized logic.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Type, TypeVar

from pydantic import BaseModel

from src.config import AGENT_COLORS, AGENT_ICONS
from src.llm import call_gemini

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC):
    """
    Abstract base for every agent in the 7-agent pipeline.

    Subclasses must define:
        - name: str
        - system_prompt: str
        - output_schema: Type[BaseModel]
    """

    name: str = "BaseAgent"
    system_prompt: str = "You are a helpful AI assistant."
    output_schema: Type[BaseModel] | None = None

    def __init__(self):
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.color = AGENT_COLORS.get(self.name, "#888888")
        self.icon = AGENT_ICONS.get(self.name, "🤖")
        self.call_log: list[dict] = []  # Track all calls for the appendix

    async def run(self, task: str, context: str = "") -> BaseModel | str:
        """
        Execute the agent on a task.

        Args:
            task: The task/query to process.
            context: Optional prior context from upstream agents.

        Returns:
            Structured output (Pydantic model) or raw text.
        """
        full_message = task
        if context:
            full_message = f"--- CONTEXT FROM PREVIOUS AGENTS ---\n{context}\n\n--- YOUR TASK ---\n{task}"

        self.logger.info("[%s %s] Starting task: %s", self.icon, self.name, task[:80])

        result = await call_gemini(
            system_prompt=self.system_prompt,
            user_message=full_message,
            schema=self.output_schema,
        )

        # Log for the AI-Assisted Learning Appendix
        self.call_log.append({
            "agent": self.name,
            "task": task,
            "context_length": len(context),
            "output_type": type(result).__name__,
        })

        self.logger.info("[%s %s] Completed task", self.icon, self.name)
        return result

    def get_description(self) -> str:
        """Return a human-readable description for the Chainlit UI."""
        return f"{self.icon} **{self.name}** — {self.system_prompt[:100]}..."
