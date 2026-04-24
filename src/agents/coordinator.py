"""
Project 4 — Coordinator Agent.

The Coordinator is the "brain" of the pipeline. It receives the user's query,
creates a research plan, dispatches tasks to specialist agents, and aggregates
the final result.
"""

from __future__ import annotations

import json
import logging

from src.agents.base import BaseAgent
from src.schemas import (
    CoordinatorPlan,
    SearchResult,
    VerificationResult,
    RankedResults,
    SynthesisReport,
)

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    name = "Coordinator"
    output_schema = CoordinatorPlan
    system_prompt = """You are the Coordinator Agent for a Graduate-Level Academic Research Pipeline.

Your job is to:
1. Understand the user's research query
2. Break it down into tasks for specialist agents
3. Create an ordered execution plan

Available specialist agents:
- Search-A: Web and academic research (broad literature, papers, articles)
- Search-B: Technical and CVE-focused search (vulnerabilities, exploits, technical docs)
- Verification: Cross-references findings and checks accuracy
- Ranking: Ranks verified findings by relevance, credibility, and recency
- Synthesis: Produces a coherent final report from ranked findings
- Data: File I/O operations (reading configs, saving reports)

Create a plan with specific tasks for each agent. Always include at least one Search agent,
the Verification agent, the Ranking agent, and the Synthesis agent for research queries."""


class CoordinatorOrchestrator:
    """
    Orchestrates the full multi-agent pipeline.

    This is the class that Chainlit calls. It manages the lifecycle:
    Coordinator → Search(es) → Verification → Ranking → Synthesis
    """

    def __init__(self):
        self.coordinator = CoordinatorAgent()
        # Import here to avoid circular imports
        from src.agents.search import SearchAgentA, SearchAgentB
        from src.agents.verification import VerificationAgent
        from src.agents.ranking import RankingAgent
        from src.agents.synthesis import SynthesisAgent
        from src.agents.data import DataAgent

        self.agents = {
            "Search-A": SearchAgentA(),
            "Search-B": SearchAgentB(),
            "Verification": VerificationAgent(),
            "Ranking": RankingAgent(),
            "Synthesis": SynthesisAgent(),
            "Data": DataAgent(),
        }
        self.execution_log: list[dict] = []

    async def run_pipeline(self, user_query: str, step_callback=None, rate_limit_callback=None):
        """
        Run the full research pipeline.

        Args:
            user_query: The user's research question.
            step_callback: Optional async callback(agent_name, status, result)
                          for Chainlit to render live updates.
            rate_limit_callback: Optional async callback(wait_secs, attempt)
                          shown in Chainlit when Gemini quota is hit.

        Returns:
            Final SynthesisReport or error string.
        """
        rl = rate_limit_callback  # shorthand

        # Step 1: Coordinator creates a plan
        if step_callback:
            await step_callback("Coordinator", "planning", None)

        plan: CoordinatorPlan = await self.coordinator.run(user_query, on_rate_limit=rl)
        self.execution_log.append({"phase": "planning", "plan": plan.model_dump()})

        if step_callback:
            await step_callback("Coordinator", "plan_ready", plan)

        # Step 2: Execute search tasks
        search_results: list[SearchResult] = []
        for task in plan.tasks:
            if task.target_agent.startswith("Search"):
                agent_key = task.target_agent
                if agent_key not in self.agents:
                    agent_key = "Search-A"  # fallback

                if step_callback:
                    await step_callback(agent_key, "running", task.task_description)

                result = await self.agents[agent_key].run(task.task_description, on_rate_limit=rl)
                if isinstance(result, SearchResult):
                    search_results.append(result)

                if step_callback:
                    await step_callback(agent_key, "done", result)

        if not search_results:
            return "No search results were generated. Please try a different query."

        # Step 3: Verification
        search_context = json.dumps(
            [r.model_dump() for r in search_results], indent=2, default=str
        )

        if step_callback:
            await step_callback("Verification", "running", None)

        verification: VerificationResult = await self.agents["Verification"].run(
            f"Verify these search findings for accuracy and credibility:\n{search_context}",
            context=f"Original query: {user_query}",
            on_rate_limit=rl,
        )

        if step_callback:
            await step_callback("Verification", "done", verification)

        # Step 4: Ranking
        verified_context = verification.model_dump_json(indent=2)

        if step_callback:
            await step_callback("Ranking", "running", None)

        ranked: RankedResults = await self.agents["Ranking"].run(
            f"Rank these verified findings by relevance, credibility, and recency:\n{verified_context}",
            context=f"Original query: {user_query}",
            on_rate_limit=rl,
        )

        if step_callback:
            await step_callback("Ranking", "done", ranked)

        # Step 5: Synthesis
        ranked_context = ranked.model_dump_json(indent=2)

        if step_callback:
            await step_callback("Synthesis", "running", None)

        report: SynthesisReport = await self.agents["Synthesis"].run(
            f"Synthesize a comprehensive research report from these ranked findings:\n{ranked_context}",
            context=f"Original query: {user_query}",
            on_rate_limit=rl,
        )

        if step_callback:
            await step_callback("Synthesis", "done", report)

        self.execution_log.append({"phase": "complete", "report_title": report.title})

        return report

    def get_all_call_logs(self) -> list[dict]:
        """Collect call logs from all agents for the appendix."""
        logs = self.coordinator.call_log.copy()
        for agent in self.agents.values():
            logs.extend(agent.call_log)
        return logs
