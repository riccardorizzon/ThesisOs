"""LLM JSON request + parse helpers for orchestration nodes."""

from __future__ import annotations

import json
import re

from app.llm.base import LLMClient

_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


async def request_json(llm: LLMClient, *, system: str, user: str) -> str:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return await llm.generate(messages)


def extract_json_object(text: str) -> dict | None:
    """Parse a JSON object from raw LLM text (tolerates markdown fences)."""
    stripped = text.strip()
    if not stripped:
        return None

    fence = _JSON_FENCE.search(stripped)
    if fence is not None:
        stripped = fence.group(1).strip()

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            parsed = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None

    return parsed if isinstance(parsed, dict) else None
