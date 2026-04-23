"""
Project 4 — Chainlit Multi-Agent Dashboard.

Main entry point: `chainlit run app.py`

Visualizes the 7-agent research pipeline with color-coded steps,
real-time streaming, and hierarchical agent handoffs.
"""

from __future__ import annotations

import json
import logging
import time
import asyncio

import chainlit as cl

from src.config import AGENT_COLORS, AGENT_ICONS
from src.agents.coordinator import CoordinatorOrchestrator
from src.schemas import (
    CoordinatorPlan,
    SearchResult,
    VerificationResult,
    RankedResults,
    SynthesisReport,
    DataResult,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("app")

# Global orchestrator instance per session
_orchestrators: dict[str, CoordinatorOrchestrator] = {}


def _get_orchestrator() -> CoordinatorOrchestrator:
    """Get or create the orchestrator for the current Chainlit session."""
    session_id = cl.context.session.id
    if session_id not in _orchestrators:
        _orchestrators[session_id] = CoordinatorOrchestrator()
    return _orchestrators[session_id]


def _agent_label(name: str) -> str:
    """Format agent name with icon for display."""
    icon = AGENT_ICONS.get(name, "🤖")
    return f"{icon} {name}"


def _format_result(result) -> str:
    """Format an agent result for display in the Chainlit UI."""
    if isinstance(result, CoordinatorPlan):
        lines = [f"**Strategy:** {result.strategy}\n"]
        for i, task in enumerate(result.tasks, 1):
            lines.append(f"{i}. **{task.target_agent}** — {task.task_description}")
        return "\n".join(lines)

    elif isinstance(result, SearchResult):
        lines = [f"**Query:** {result.query_used}\n"]
        for f in result.findings[:6]:
            lines.append(
                f"- **{f.title}** (relevance: {f.relevance_score:.1f})\n"
                f"  {f.summary}\n  *Source: {f.source}*"
            )
        return "\n".join(lines)

    elif isinstance(result, VerificationResult):
        lines = [
            f"**Verified:** {result.verified_count}/{result.total_findings} "
            f"| **Rejected:** {result.rejected_count}\n"
        ]
        for f in result.findings[:6]:
            status = "✅" if f.verified else "❌"
            lines.append(
                f"{status} **{f.original_title}** (confidence: {f.confidence:.1f})\n"
                f"  {f.verification_notes}"
            )
        lines.append(f"\n**Overall:** {result.overall_assessment}")
        return "\n".join(lines)

    elif isinstance(result, RankedResults):
        lines = [f"**Methodology:** {result.ranking_methodology}\n"]
        for f in result.top_findings[:8]:
            lines.append(
                f"**#{f.rank}** — {f.title} (score: {f.composite_score:.2f})\n"
                f"  Relevance: {f.relevance:.1f} | Credibility: {f.credibility:.1f} | Recency: {f.recency_score:.1f}\n"
                f"  {f.summary}"
            )
        return "\n".join(lines)

    elif isinstance(result, SynthesisReport):
        lines = [
            f"# {result.title}\n",
            f"## Executive Summary\n{result.executive_summary}\n",
            "## Key Findings",
        ]
        for kf in result.key_findings:
            lines.append(f"- {kf}")
        lines.append(f"\n## Detailed Analysis\n{result.detailed_analysis}\n")
        lines.append("## Recommendations")
        for rec in result.recommendations:
            lines.append(f"- {rec}")
        lines.append(f"\n## Limitations\n{result.limitations}\n")
        lines.append("## References")
        for ref in result.references:
            lines.append(f"- {ref}")
        return "\n".join(lines)

    elif isinstance(result, DataResult):
        status = "✅" if result.success else "❌"
        return f"{status} **{result.operation}** on `{result.file_path}`\n```\n{result.content[:500]}\n```"

    elif isinstance(result, str):
        return result

    else:
        return str(result)


@cl.on_chat_start
async def on_chat_start():
    """Initialize the session with starter options."""
    await cl.Message(
        content=(
            "🔬 **Multi-Agent Security Research System** — ⚠️ *Unguarded (Vulnerable) Version*\n\n"
            "This system has **no security guardrails**. It demonstrates what happens when "
            "a 7-agent AI pipeline runs without protection.\n\n"
            "Choose an option below or type your own research question:"
        ),
        actions=[
            cl.Action(
                name="redteam_demo",
                label="🔴 Run Red Team Attack Demo",
                payload={"action": "redteam"},
                tooltip="Run all 4 prompt injection attacks and see live results"
            ),
            cl.Action(
                name="research_demo",
                label="🔬 Run Research Pipeline Demo",
                payload={"action": "research"},
                tooltip="Ask a cybersecurity research question"
            ),
        ]
    ).send()


@cl.action_callback("redteam_demo")
async def on_redteam_action(action):
    await _run_redteam_demo()


@cl.action_callback("research_demo")
async def on_research_action(action):
    await cl.Message(content="Type your cybersecurity research question in the chat below.").send()


async def _run_redteam_demo():
    """Run all 4 prompt injection attacks live in the UI."""
    from attacks.prompt_injection import ALL_PAYLOADS
    from src.agents.data import DataAgent

    await cl.Message(
        content=(
            "# 🔴 Red Team Attack Demo\n"
            "Running **4 prompt injection attacks** against the unguarded agent pipeline.\n\n"
            "---"
        )
    ).send()

    data_agent = DataAgent()
    results_summary = []

    for i, (payload_id, payload_name, payload_text) in enumerate(ALL_PAYLOADS, 1):
        # Show the attack being launched
        async with cl.Step(name=f"Attack {i}: {payload_name}", type="tool") as step:
            step.input = payload_text
            await step.stream_token(f"🎯 **Injecting payload into agent...**\n\n")
            await step.stream_token(f"```\n{payload_text.strip()}\n```\n")

        # For the DATA_AGENT payload — actually execute against DataAgent (no guard)
        if payload_id == "DATA_AGENT":
            async with cl.Step(name=f"💾 Data Agent Response", type="tool") as resp_step:
                try:
                    # Directly invoke data agent file read (no interceptor in app.py)
                    import os
                    result_content = ""
                    for fpath in ["/etc/passwd", "/etc/shadow", os.path.expanduser("~/.bashrc")]:
                        try:
                            with open(fpath, "r") as f:
                                content = f.read()[:800]
                            result_content += f"\n### 📄 `{fpath}`\n```\n{content}\n```\n"
                        except PermissionError:
                            result_content += f"\n### 📄 `{fpath}` → *Permission denied*\n"
                        except FileNotFoundError:
                            result_content += f"\n### 📄 `{fpath}` → *Not found*\n"

                    await resp_step.stream_token(
                        f"🔓 **EXPLOIT SUCCESSFUL — files read without any authorization check:**\n{result_content}"
                    )
                    resp_step.output = result_content
                    results_summary.append((payload_name, "🔓 EXPLOITED", "File contents leaked"))
                except Exception as e:
                    await resp_step.stream_token(f"Error: {e}")
                    results_summary.append((payload_name, "⚠️ ERROR", str(e)))
        else:
            results_summary.append((payload_name, "⚠️ ATTEMPTED", "LLM-level injection (rate limited)"))

        await asyncio.sleep(0.5)

    # Final verdict table
    table = "# 🔴 Attack Results Summary\n\n"
    table += "| # | Attack | Result |\n|---|---|---|\n"
    for i, (name, verdict, detail) in enumerate(results_summary, 1):
        table += f"| {i} | {name} | {verdict} — {detail} |\n"
    table += (
        "\n> ⚠️ **This is the UNGUARDED system. No approval was required. "
        "Files were read silently.**\n"
        "> Switch to `app_secured.py` to see the Human-in-the-Loop defense."
    )
    await cl.Message(content=table).send()



@cl.on_message
async def on_message(message: cl.Message):
    """Handle user messages — run the full multi-agent pipeline."""
    # Check for shortcut triggers
    low = message.content.lower().strip()
    if any(k in low for k in ["red team", "redteam", "attack demo", "run attack"]):
        await _run_redteam_demo()
        return

    orchestrator = _get_orchestrator()
    user_query = message.content
    start_time = time.time()

    # Track active steps for nesting
    active_steps: dict[str, cl.Step] = {}

    async def step_callback(agent_name: str, status: str, result):
        """
        Callback from the orchestrator to render live agent updates.
        Creates color-coded, hierarchical Chainlit Steps.
        """
        color = AGENT_COLORS.get(agent_name, "#888888")
        label = _agent_label(agent_name)

        if status == "planning":
            step = cl.Step(name=label, type="tool")
            step.language = "markdown"
            step.input = user_query
            await step.send()
            active_steps["Coordinator"] = step
            await step.stream_token("🔄 *Planning research strategy...*\n")

        elif status == "plan_ready":
            step = active_steps.get("Coordinator")
            if step and result:
                formatted = _format_result(result)
                await step.stream_token(f"\n{formatted}")
                step.output = formatted
                await step.update()

        elif status == "running":
            # Create a new step under the Coordinator
            parent = active_steps.get("Coordinator")
            step = cl.Step(
                name=label,
                type="tool",
                parent_id=parent.id if parent else None,
            )
            step.language = "markdown"
            if isinstance(result, str):
                step.input = result
            await step.send()
            active_steps[agent_name] = step
            await step.stream_token(f"🔄 *{agent_name} working...*\n")

        elif status == "done":
            step = active_steps.get(agent_name)
            if step and result:
                formatted = _format_result(result)
                await step.stream_token(f"\n{formatted}")
                step.output = formatted
                await step.update()


    # Model-rotation toast — visible to the user
    async def rate_limit_callback(exhausted_model: str, next_model: str | None):
        if next_model:
            await cl.Message(
                content=(
                    f"⚡ **Model rotated** — `{exhausted_model}` hit its quota.\n"
                    f"Automatically switching to `{next_model}` and retrying instantly..."
                )
            ).send()
        else:
            await cl.Message(
                content="❌ All models in the fallback chain are exhausted. Please try again later."
            ).send()

    # Run the pipeline
    try:
        result = await orchestrator.run_pipeline(
            user_query,
            step_callback=step_callback,
            rate_limit_callback=rate_limit_callback,
        )
    except Exception as e:
        logger.exception("Pipeline error")
        await cl.Message(content=f"❌ **Pipeline Error:** {e}").send()
        return

    elapsed = time.time() - start_time

    # Send the final synthesis report
    if isinstance(result, SynthesisReport):
        final_content = _format_result(result)
        final_content += f"\n\n---\n*⏱ Completed in {elapsed:.1f}s using 7 agents*"
        await cl.Message(content=final_content).send()
    else:
        await cl.Message(content=str(result)).send()
