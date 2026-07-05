"""POST /writing/actions — lateral Writing panel AI actions (PX2-EWO-003)."""

from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.graph.writer import LLMWriter, WriterGenerationError, run_writing_panel_action
from app.llm.base import NotConfiguredLLM
from app.llm.factory import get_llm_client

router = APIRouter(prefix="/writing", tags=["writing"])

VALID_ACTIONS = frozenset({"rewrite", "verify", "find-sources", "expand"})


class WritingActionRequest(BaseModel):
    action: str = Field(min_length=1, max_length=64)
    chapter_id: str | None = None
    selection_text: str | None = None
    chapter_content: str = ""
    context_summary: str | None = None


@router.post("/actions")
async def writing_actions(req: WritingActionRequest):
    if req.action not in VALID_ACTIONS:
        return JSONResponse(
            status_code=400,
            content={"code": "invalid_action", "message": f"Unknown action: {req.action}"},
        )

    llm = get_llm_client()
    if isinstance(llm, NotConfiguredLLM):
        return JSONResponse(
            status_code=503,
            content={"code": "llm_not_configured", "message": "LLM runtime not configured"},
        )

    writer = LLMWriter(llm)

    async def event_gen():
        tokens: list[str] = []

        def emit(ev: dict) -> None:
            text = ev.get("text")
            if text:
                tokens.append(text)

        try:
            result = await run_writing_panel_action(
                writer,
                action=req.action,
                selection_text=req.selection_text,
                chapter_content=req.chapter_content,
                context_summary=req.context_summary,
                retrieved_context=[],
                emit=emit,
            )
        except WriterGenerationError as exc:
            yield {
                "event": "error",
                "data": json.dumps({"code": "generation_failed", "message": str(exc)}),
            }
            return

        draft = result.draft
        if not tokens and draft:
            chunk_size = max(1, len(draft) // 8)
            for i in range(0, len(draft), chunk_size):
                piece = draft[i : i + chunk_size]
                yield {"event": "token", "data": json.dumps({"text": piece})}
        else:
            for piece in tokens:
                yield {"event": "token", "data": json.dumps({"text": piece})}

        yield {"event": "done", "data": json.dumps({"draft": draft})}

    return EventSourceResponse(event_gen(), ping=15)
