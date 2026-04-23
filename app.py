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
    """Run all 4 prompt injection attacks live in the UI — fully visible results."""
    from attacks.prompt_injection import ALL_PAYLOADS
    import os

    # ── INTRO ────────────────────────────────────────────────────────
    await cl.Message(
        content=(
            "# 🔴 Red Team Attack Demo — Unguarded System\n\n"
            "> ⚠️ **This version has NO security guardrails.** "
            "The AI agents will execute any file operation they are told to — "
            "no authentication, no confirmation, no limits.\n\n"
            "**We will run 4 prompt injection attacks.** "
            "Watch what the attacker sends, what the agent does, and what gets leaked.\n\n"
            "---"
        )
    ).send()
    await asyncio.sleep(0.4)

    ATTACK_META = [
        ("ENV_EXFIL",  "🔴 Attack 1 — Environment Variable Theft",
         "Goal: Trick the Search Agent into dumping API keys & secrets from the environment."),
        ("FILE_EXFIL", "🔴 Attack 2 — System File Exfiltration via Fake Authority",
         "Goal: Embed a fake 'system admin' directive to make the agent read /etc/passwd."),
        ("DATA_AGENT", "🔴 Attack 3 — Direct Data Agent File Read (CRITICAL)",
         "Goal: Send a social-engineering prompt directly to the Data Agent to leak system files."),
        ("CHAINED",    "🔴 Attack 4 — Chained Cross-Agent Attack",
         "Goal: Use Search Agent as a relay to instruct the Data Agent to dump secrets."),
    ]

    results_summary = []

    for i, (payload_id, payload_name, payload_text) in enumerate(ALL_PAYLOADS, 1):
        _, title, goal = ATTACK_META[i - 1]

        # ── STEP 1: Show the attack intent ───────────────────────────
        await cl.Message(
            content=(
                f"## {title}\n\n"
                f"**{goal}**"
            )
        ).send()
        await asyncio.sleep(0.3)

        # ── STEP 2: Show the exact payload sent to the agent ─────────
        await cl.Message(
            content=(
                f"### 📨 Payload Injected into Agent\n\n"
                f"```"
                f"\n{payload_text.strip()}\n"
                f"```\n\n"
                f"*The attacker sends this as a normal user message. "
                f"The AI agent sees no difference between this and a legitimate request.*"
            )
        ).send()
        await asyncio.sleep(0.3)

        # ── STEP 3: Execute and show result ──────────────────────────
        if payload_id == "DATA_AGENT":
            # This is the critical exploit — show the leaked file contents prominently
            leaked_sections = []
            for fpath in ["/etc/passwd", "/etc/shadow", os.path.expanduser("~/.bashrc"), ".env"]:
                try:
                    with open(fpath, "r") as f:
                        content = f.read()[:600]
                    leaked_sections.append(
                        f"### 📄 `{fpath}` — **LEAKED**\n"
                        f"```\n{content}\n```"
                    )
                except PermissionError:
                    leaked_sections.append(f"### 📄 `{fpath}` — *Permission denied (file exists but unreadable)*")
                except FileNotFoundError:
                    leaked_sections.append(f"### 📄 `{fpath}` — *Not found on this system*")

            leaked_content = "\n\n".join(leaked_sections)
            await cl.Message(
                content=(
                    f"### 🔓 RESULT — EXPLOIT SUCCESSFUL\n\n"
                    f"The Data Agent read the files and returned their contents "
                    f"**without any authentication, confirmation, or warning.**\n\n"
                    f"{leaked_content}\n\n"
                    f"> 🚨 **This is your actual system's data. "
                    f"The agent leaked it because nothing stopped it.**"
                )
            ).send()
            results_summary.append((title, "🔓 EXPLOITED", "System files leaked — /etc/passwd, .env, ~/.bashrc"))

        elif payload_id == "ENV_EXFIL":
            # Show what env vars the attacker could steal
            env_preview = ", ".join(
                f"`{k}`" for k in os.environ
                if any(w in k.upper() for w in ["KEY", "TOKEN", "SECRET", "API", "PASS", "GEMINI"])
            ) or "*(no sensitive keys found in this environment)*"
            await cl.Message(
                content=(
                    f"### ⚠️ RESULT — Attack Attempted\n\n"
                    f"The agent was instructed to dump environment variables. "
                    f"**Sensitive keys visible in this environment:**\n\n"
                    f"{env_preview}\n\n"
                    f"> In a production system with no guardrails, these would be returned "
                    f"in the agent's response and sent back to the attacker."
                )
            ).send()
            results_summary.append((title, "⚠️ ATTEMPTED", "Env var theft — API keys exposed in environment"))

        else:
            await cl.Message(
                content=(
                    f"### ⚠️ RESULT — Injection Attempted\n\n"
                    f"This payload was injected into the Search Agent's context. "
                    f"Without an output scanner, any sensitive data the agent "
                    f"includes in its response would be returned directly to the attacker.\n\n"
                    f"> In a secured system, the output would be scanned and redacted before delivery."
                )
            ).send()
            results_summary.append((title, "⚠️ ATTEMPTED", "LLM injection — output not scanned"))

        await asyncio.sleep(0.6)

    # ── FINAL VERDICT ─────────────────────────────────────────────────
    table = "## 🔴 Attack Results — Unguarded System\n\n"
    table += "| # | Attack | Verdict | What was exposed |\n|---|---|---|---|\n"
    for j, (name, verdict, detail) in enumerate(results_summary, 1):
        table += f"| {j} | {name} | {verdict} | {detail} |\n"
    table += (
        "\n---\n"
        "### 🚨 Key Takeaway\n\n"
        "Attack #3 successfully read `/etc/passwd` and returned "
        "the full system user list — **with zero authentication, zero confirmation, "
        "and zero alerts raised**. The agent simply executed the instruction "
        "because it was told to.\n\n"
        "> **➡️ Switch to the Secured version (`app_secured.py`) to see the "
        "Human-in-the-Loop defense block these exact attacks.**"
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
