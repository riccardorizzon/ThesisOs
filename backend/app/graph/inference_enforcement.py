"""Shared LLM streaming helpers for inference enforcement (EWO-7C)."""

from __future__ import annotations

from collections.abc import Callable

from app.llm.base import LLMClient

Emit = Callable[[dict], None]
MINIMAL_REASONING_PARAMS = {"reasoning_effort": "minimal"}


async def generate_with_citation_enforcement(
    llm: LLMClient,
    wire: list[dict],
    *,
    academic: bool,
    emit: Emit | None = None,
) -> tuple[str, dict, bool]:
    """Generate text; one deterministic retry if academic numeric cites without author-date.

    Returns (final_text, usage, retried).
    Non-academic chunks stream immediately. Academic output remains buffered until
    citation validation accepts either the first pass or its deterministic retry.
    """
    if not academic:
        parts: list[str] = []
        usage: dict = {}
        async for chunk in llm.astream(wire, params=MINIMAL_REASONING_PARAMS):
            if chunk.text:
                parts.append(chunk.text)
                if emit is not None:
                    emit({"type": "token", "text": chunk.text})
            if chunk.metadata.get("usage"):
                usage = chunk.metadata["usage"]
        return "".join(parts), usage, False

    from app.graph.academic_production import (
        CITATION_ENFORCEMENT_RETRY_MESSAGE,
        needs_citation_enforcement_retry,
    )

    parts: list[str] = []
    usage: dict = {}
    async for chunk in llm.astream(wire):
        if chunk.text:
            parts.append(chunk.text)
        if chunk.metadata.get("usage"):
            usage = chunk.metadata["usage"]
    text = "".join(parts)

    if not needs_citation_enforcement_retry(text):
        if emit is not None:
            for token in parts:
                emit({"type": "token", "text": token})
        return text, usage, False

    retry_wire = [
        *wire,
        {"role": "assistant", "content": text},
        {"role": "user", "content": CITATION_ENFORCEMENT_RETRY_MESSAGE},
    ]
    parts = []
    usage = {}
    async for chunk in llm.astream(retry_wire):
        if chunk.text:
            parts.append(chunk.text)
            if emit is not None:
                emit({"type": "token", "text": chunk.text})
        if chunk.metadata.get("usage"):
            usage = chunk.metadata["usage"]
    return "".join(parts), usage, True
