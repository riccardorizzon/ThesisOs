import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.services.conversation import ConversationService
from app.services.conversation.locks import conversation_locks

router = APIRouter()
_service = ConversationService()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@router.post("/chat")
async def chat(req: ChatRequest):
    if req.conversation_id and not conversation_locks.try_acquire(req.conversation_id):
        return JSONResponse(status_code=409,
                            content={"code": "conversation_busy",
                                     "message": "A response is already streaming"})
    locked_id = req.conversation_id

    async def event_gen():
        nonlocal locked_id
        try:
            async for ev in _service.stream_turn(conversation_id=req.conversation_id, user_text=req.message):
                # acquire lock lazily once the conversation id is known (new conversations)
                cid = ev["data"].get("conversation_id")
                if locked_id is None and cid:
                    conversation_locks.try_acquire(cid)
                    locked_id = cid
                yield {"event": ev["event"], "data": json.dumps(ev["data"])}
        finally:
            if locked_id:
                conversation_locks.release(locked_id)

    # ping= sends `event: ping` heartbeats every 15s (spec §7)
    return EventSourceResponse(event_gen(), ping=15)
