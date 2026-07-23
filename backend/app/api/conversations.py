"""Conversations API (M7) — list/create threads and fetch persisted messages."""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas.conversation import ConversationCreate
from app.services.conversation.exceptions import ConversationNotFoundError
from app.services.conversation.service import ConversationService

router = APIRouter()
_service = ConversationService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.get("/conversations")
async def list_conversations(project_id: str = Query(min_length=1)):
    return await _service.list_conversations(project_id)


@router.post("/conversations", status_code=201)
async def create_conversation(body: ConversationCreate):
    return await _service.create_conversation(body.project_id, title=body.title)


@router.get("/conversations/{conversation_id}/messages")
async def list_messages(conversation_id: str, project_id: str | None = None):
    try:
        return await _service.list_messages(conversation_id, project_id=project_id)
    except ConversationNotFoundError as exc:
        return _err(404, "conversation_not_found", str(exc))
