"""
Project 4 — Gemini LLM wrapper with automatic model fallback.

When any model hits its quota (429), the wrapper instantly rotates
to the next model in MODEL_FALLBACK_CHAIN — no waiting, no crashes.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from src.config import GEMINI_API_KEY, GEMINI_MODEL, MODEL_FALLBACK_CHAIN

logger = logging.getLogger(__name__)

# Initialize the Gemini client once
_client = genai.Client(api_key=GEMINI_API_KEY)

T = TypeVar("T", bound=BaseModel)

# --- Model rotation state (shared across all calls in a session) ---
# Start from whichever model is configured in .env
_current_model_index: int = 0

def _get_chain() -> list[str]:
    """
    Return MODEL_FALLBACK_CHAIN, starting from GEMINI_MODEL if it's in the list.
    """
    chain = MODEL_FALLBACK_CHAIN.copy()
    if GEMINI_MODEL in chain:
        idx = chain.index(GEMINI_MODEL)
        return chain[idx:]  # Start from configured model
    return [GEMINI_MODEL] + chain  # Prepend if not in list


def _get_active_model() -> str:
    return _get_chain()[min(_current_model_index, len(_get_chain()) - 1)]


async def _generate_with_model_fallback(
    msg: str,
    config: types.GenerateContentConfig,
    on_rate_limit=None,
) -> tuple[str, str]:
    """
    Try each model in the fallback chain until one succeeds.

    Returns (response_text, model_used).
    """
    global _current_model_index
    chain = _get_chain()

    for i in range(len(chain)):
        model_idx = (_current_model_index + i) % len(chain)
        model = chain[model_idx]

        try:
            response = await _client.aio.models.generate_content(
                model=model,
                contents=msg,
                config=config,
            )
            # Success — lock in this model for future calls
            if i > 0:
                logger.info("✅ Model rotation successful: now using %s", model)
                _current_model_index = model_idx
            return response.text.strip(), model

        except Exception as e:
            err_str = str(e)

            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                next_model = chain[(model_idx + 1) % len(chain)] if i + 1 < len(chain) else None
                logger.warning(
                    "⚡ %s quota exhausted — switching to %s",
                    model, next_model or "no more models"
                )
                if on_rate_limit:
                    try:
                        await on_rate_limit(model, next_model)
                    except Exception:
                        pass
                continue  # Instant switch — no waiting

            elif "503" in err_str or "UNAVAILABLE" in err_str:
                wait = 3
                logger.warning("⚠️ %s unavailable, retrying in %ds...", model, wait)
                await asyncio.sleep(wait)
                continue

            elif "404" in err_str or "NOT_FOUND" in err_str:
                logger.warning("❌ %s not found — skipping", model)
                continue

            elif "model output" in err_str.lower() or "empty" in err_str.lower() or "finish_reason" in err_str.lower():
                # Model returned an empty response — rotate to next
                next_model = chain[(model_idx + 1) % len(chain)] if i + 1 < len(chain) else None
                logger.warning("⚠️ %s returned empty output — switching to %s", model, next_model or "no more models")
                if on_rate_limit:
                    try:
                        await on_rate_limit(model, next_model)
                    except Exception:
                        pass
                continue

            else:
                raise

    raise RuntimeError(
        f"All models in the fallback chain are exhausted: {chain}. "
        "Please try again tomorrow or add a billing account."
    )


async def call_gemini(
    system_prompt: str,
    user_message: str,
    schema: Type[T] | None = None,
    temperature: float = 0.3,
    on_rate_limit=None,
) -> T | str:
    """
    Call Gemini with automatic model fallback.

    Args:
        system_prompt: The system instruction for the agent role.
        user_message: The user/task message.
        schema: Optional Pydantic model class for structured output.
        temperature: Sampling temperature (lower = more deterministic).
        on_rate_limit: Optional async callback(exhausted_model, next_model)
                       for showing a UI toast when model rotates.

    Returns:
        Parsed Pydantic model instance, or raw string.
    """
    active = _get_active_model()
    logger.info("LLM call: model=%s, schema=%s", active, schema.__name__ if schema else "None")

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
    )

    # Structured output: embed schema in system prompt
    json_schema = None
    if schema:
        json_schema = schema.model_json_schema()
        config.system_instruction = (
            system_prompt
            + "\n\n--- OUTPUT FORMAT ---\n"
            + "You MUST respond with ONLY a valid JSON object matching this schema:\n"
            + f"```json\n{json.dumps(json_schema, indent=2)}\n```\n"
            + "Do NOT include any text before or after the JSON. No markdown fences."
        )

    raw_text, model_used = await _generate_with_model_fallback(
        user_message, config, on_rate_limit=on_rate_limit
    )

    if schema:
        cleaned = raw_text
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
            return schema.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Failed to parse structured output from %s: %s\nRaw: %s", model_used, e, raw_text[:200])
            retry_msg = (
                f"Your previous response was not valid JSON. "
                f"Please respond with ONLY this JSON schema: {json.dumps(json_schema)}\n\n"
                f"Original task: {user_message}"
            )
            retry_text, _ = await _generate_with_model_fallback(
                retry_msg, config, on_rate_limit=on_rate_limit
            )
            if retry_text.startswith("```"):
                lines = retry_text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                retry_text = "\n".join(lines)
            data = json.loads(retry_text)
            return schema.model_validate(data)

    return raw_text
