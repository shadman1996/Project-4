"""
Project 4 — SECURED Chainlit Multi-Agent Dashboard.

Run: `chainlit run app_secured.py`

This is the "AFTER" version with the Human-in-the-Loop (HITL)
security gate that blocks dangerous tool calls and requires
user approval via Approve/Deny buttons.
"""

from __future__ import annotations

import json
import logging
import time

import chainlit as cl

from src.config import AGENT_COLORS, AGENT_ICONS
from src.agents.coordinator import CoordinatorOrchestrator
from src.agents.data import DataAgent
from src.security.interceptor import SecurityInterceptor, RiskLevel
from src.schemas import (
    CoordinatorPlan,
    SearchResult,
    VerificationResult,
    RankedResults,
    SynthesisReport,
    DataResult,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("app_secured")

# Global state per session
_orchestrators: dict[str, CoordinatorOrchestrator] = {}
_interceptors: dict[str, SecurityInterceptor] = {}


def _get_orchestrator() -> CoordinatorOrchestrator:
    session_id = cl.context.session.id
    if session_id not in _orchestrators:
        _orchestrators[session_id] = CoordinatorOrchestrator()
    return _orchestrators[session_id]


def _get_interceptor() -> SecurityInterceptor:
    session_id = cl.context.session.id
    if session_id not in _interceptors:
        _interceptors[session_id] = SecurityInterceptor()
    return _interceptors[session_id]


def _agent_label(name: str) -> str:
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

    return str(result)


async def hitl_approve(operation: str, target: str, risk_level: RiskLevel, reason: str) -> bool:
    """
    Present a Human-in-the-Loop approval dialog in Chainlit.

    Returns True if user approves, False if denied.
    """
    risk_emoji = {
        RiskLevel.HIGH: "🟠",
        RiskLevel.CRITICAL: "🔴",
    }.get(risk_level, "⚠️")

    alert_content = (
        f"{risk_emoji} **SECURITY ALERT — {risk_level.value} RISK**\n\n"
        f"**Operation:** `{operation}`\n"
        f"**Target:** `{target}`\n"
        f"**Reason blocked:** {reason}\n\n"
        f"An agent is attempting a potentially dangerous operation. "
        f"Do you want to allow it?"
    )

    res = await cl.AskActionMessage(
        content=alert_content,
        actions=[
            cl.Action(name="approve", payload={"value": "approve"}, label="✅ Approve"),
            cl.Action(name="deny", payload={"value": "deny"}, label="❌ Deny"),
        ],
    ).send()

    if res and res.get("payload", {}).get("value") == "approve":
        await cl.Message(content="✅ **Approved** — proceeding with operation.").send()
        return True
    else:
        await cl.Message(content="🛑 **Denied** — operation blocked by user.").send()
        return False


# Monkey-patch the Data Agent to go through the interceptor
_original_data_run = DataAgent.run


async def _secured_data_run(self, task: str, context: str = "") -> DataResult:
    """Secured version of DataAgent.run that checks the interceptor first."""
    interceptor = _get_interceptor()
    task_lower = task.lower()

    # Check for env access
    if any(kw in task_lower for kw in ["env", "environment", "variable"]):
        check = interceptor.check_env_access()
        if not check.allowed:
            approved = await hitl_approve(check.operation, check.target, check.risk_level, check.reason)
            if not approved:
                return DataResult(
                    operation="env_read",
                    success=False,
                    error=f"🛑 BLOCKED by security policy: {check.reason}",
                )

    # Check for file reads
    if any(kw in task_lower for kw in ["read", "cat", "show", "display", "contents"]):
        path = DataAgent._extract_path(task)
        check = interceptor.check_file_read(path)
        if not check.allowed:
            approved = await hitl_approve(check.operation, check.target, check.risk_level, check.reason)
            if not approved:
                return DataResult(
                    operation="file_read",
                    success=False,
                    file_path=path,
                    error=f"🛑 BLOCKED by security policy: {check.reason}",
                )

    # If all checks pass, run the original
    result = await _original_data_run(self, task, context)

    # Post-execution: scan output for leaks
    if isinstance(result, DataResult) and result.content:
        leak_check = interceptor.check_output(result.content)
        if not leak_check.allowed:
            await cl.Message(
                content=(
                    f"🔴 **OUTPUT LEAK DETECTED**\n\n"
                    f"The agent's output contained sensitive data.\n"
                    f"**Reason:** {leak_check.reason}\n\n"
                    f"The output has been redacted."
                )
            ).send()
            result.content = "[REDACTED — sensitive data detected]"

    return result


@cl.on_chat_start
async def on_chat_start():
    """Initialize the secured session."""
    # Apply the security monkey-patch
    DataAgent.run = _secured_data_run

    interceptor = _get_interceptor()

    await cl.Message(
        content=(
            "🔬 **SECURED Multi-Agent Security Research System**\n\n"
            "🛡️ **Security Interceptor: ACTIVE**\n"
            "All file operations and terminal commands are monitored.\n"
            "High-risk operations require your explicit **Approve / Deny**.\n\n"
            "Try asking a research question, or test the security with a prompt injection!"
        ),
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle user messages — run the secured multi-agent pipeline."""
    orchestrator = _get_orchestrator()
    interceptor = _get_interceptor()
    user_query = message.content
    start_time = time.time()

    active_steps: dict[str, cl.Step] = {}

    async def step_callback(agent_name: str, status: str, result):
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

                # Post-execution output scan
                output_check = interceptor.check_output(formatted)
                if not output_check.allowed:
                    formatted = (
                        f"🔴 **OUTPUT REDACTED** — {output_check.reason}\n\n"
                        f"The agent's output contained potentially sensitive information "
                        f"and has been blocked by the security interceptor."
                    )

                await step.stream_token(f"\n{formatted}")
                step.output = formatted
                await step.update()

    # Rate-limit toast — visible to the user instead of silent spinning
    async def rate_limit_callback(wait_secs: int, attempt: int):
        await cl.Message(
            content=(
                f"⏳ **Gemini API quota reached** (attempt {attempt}/4)\n"
                f"Auto-retrying in **{wait_secs} seconds** — please wait, the pipeline will continue automatically."
            )
        ).send()

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

    # Security summary
    summary = interceptor.get_log_summary()
    security_footer = ""
    if summary["blocked"] > 0:
        security_footer = (
            f"\n\n---\n"
            f"🛡️ **Security Report:** {summary['blocked']} operation(s) blocked | "
            f"{summary['total_checks']} total checks | "
            f"Risk breakdown: {json.dumps(summary['by_risk'])}"
        )

    if isinstance(result, SynthesisReport):
        final_content = _format_result(result)
        final_content += f"\n\n---\n*⏱ Completed in {elapsed:.1f}s using 7 agents*"
        final_content += security_footer
        await cl.Message(content=final_content).send()
    else:
        msg = str(result) + security_footer
        await cl.Message(content=msg).send()
