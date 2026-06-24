import json
import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.llm.base import NotConfiguredLLM
from app.llm.factory import get_llm_client
from app.services.conversation import ConversationService
from app.services.conversation.locks import conversation_locks

router = APIRouter()
_service = ConversationService()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=32000)
    conversation_id: str | None = None


@router.post("/chat")
async def chat(req: ChatRequest):
    # Fail fast (before opening the SSE stream) when the LLM runtime is not
    # configured — the contract's documented 503 (ADR-0013 / spec §8).
    if isinstance(get_llm_client(), NotConfiguredLLM):
        return JSONResponse(status_code=503,
                            content={"code": "llm_not_configured",
                                     "message": "LLM runtime not configured"})

    # Lock the conversation for the whole turn. New conversations get a server
    # id up front so the single-active-run guard also covers them (spec §8/§11).
    conversation_id = req.conversation_id or str(uuid.uuid4())
    if not conversation_locks.try_acquire(conversation_id):
        return JSONResponse(status_code=409,
                            content={"code": "conversation_busy",
                                     "message": "A response is already streaming"})

    async def event_gen():
        try:
            async for ev in _service.stream_turn(conversation_id=conversation_id, user_text=req.message):
                yield {"event": ev["event"], "data": json.dumps(ev["data"])}
        finally:
            conversation_locks.release(conversation_id)

    # ping=15 sends an SSE comment heartbeat every 15s to keep the connection alive (spec §7)
    return EventSourceResponse(event_gen(), ping=15)
