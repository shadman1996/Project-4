"""
Project 4 — Gemini LLM wrapper.

Thin async interface to Google Gemini for all 7 agents.
"""

from __future__ import annotations

import json
import logging
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from src.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

# Initialize the Gemini client once
_client = genai.Client(api_key=GEMINI_API_KEY)

T = TypeVar("T", bound=BaseModel)


async def call_gemini(
    system_prompt: str,
    user_message: str,
    schema: Type[T] | None = None,
    temperature: float = 0.3,
) -> T | str:
    """
    Call Gemini and return either a Pydantic model (if schema given)
    or raw text.

    Args:
        system_prompt: The system instruction for the agent role.
        user_message: The user/task message.
        schema: Optional Pydantic model class for structured output.
        temperature: Sampling temperature (lower = more deterministic).

    Returns:
        Parsed Pydantic model instance, or raw string.
    """
    logger.info("Gemini call: model=%s, schema=%s", GEMINI_MODEL, schema.__name__ if schema else "None")

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
    )

    # If we want structured output, ask Gemini to return JSON
    if schema:
        json_schema = schema.model_json_schema()
        config.system_instruction = (
            system_prompt
            + "\n\n--- OUTPUT FORMAT ---\n"
            + f"You MUST respond with ONLY a valid JSON object matching this schema:\n"
            + f"```json\n{json.dumps(json_schema, indent=2)}\n```\n"
            + "Do NOT include any text before or after the JSON. No markdown fences."
        )

    import asyncio as _asyncio

    async def _generate_with_retry(msg: str):
        last_error = None
        for attempt in range(4):
            try:
                return await _client.aio.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=msg,
                    config=config,
                )
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = 60
                    logger.warning("Gemini 429 Quota Exceeded (attempt %d/4), retrying in %ds...", attempt + 1, wait)
                    await _asyncio.sleep(wait)
                elif "503" in err_str or "UNAVAILABLE" in err_str:
                    wait = 2 ** attempt + 2
                    logger.warning("Gemini 503 Unavailable (attempt %d/4), retrying in %ds...", attempt + 1, wait)
                    await _asyncio.sleep(wait)
                else:
                    raise
        raise last_error

    response = await _generate_with_retry(user_message)
    raw_text = response.text.strip()

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
            logger.warning("Failed to parse structured output: %s\nRaw: %s", e, raw_text[:200])
            retry_msg = (
                f"Your previous response was not valid JSON. "
                f"Please respond with ONLY this JSON schema: {json.dumps(json_schema)}\n\n"
                f"Original task: {user_message}"
            )
            retry_response = await _generate_with_retry(retry_msg)
            retry_text = retry_response.text.strip()
            if retry_text.startswith("```"):
                lines = retry_text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                retry_text = "\n".join(lines)
            data = json.loads(retry_text)
            return schema.model_validate(data)

    return raw_text
