from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from sqlalchemy import select

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.graph.checkpointer import open_checkpointer
from app.graph.conversation import build_graph
from app.llm.factory import get_llm_client
from app.schemas.graph_state import GraphState, Message
from app.schemas.run_context import RunContext

logger = logging.getLogger("app.services.conversation")


class ConversationService:
    """Boundary between HTTP and the graph. `messages` is the system of record; the
    checkpointer holds derived working state (spec §5)."""

    async def _get_or_create_conversation(self, session, conversation_id: str | None) -> models.Conversation:
        if conversation_id:
            conv = await session.get(models.Conversation, conversation_id)
            if conv:
                return conv
        conv = models.Conversation(id=conversation_id or str(uuid.uuid4()), title="New Conversation")
        session.add(conv)
        await session.flush()
        return conv

    async def _load_messages(self, session, conversation_id: str) -> list[Message]:
        rows = (await session.execute(
            select(models.Message).where(models.Message.conversation_id == conversation_id)
            .order_by(models.Message.created_at)
        )).scalars().all()
        return [Message(role=r.role, content=r.content) for r in rows]

    async def stream_turn(self, *, conversation_id: str | None, user_text: str) -> AsyncIterator[dict]:
        """Yield SSE-ready dicts: {"event": "token"|"done"|"error", "data": {...}}.
        Persists the user message before streaming and the assistant message on completion."""
        # Generate the run id up front so the RunContext (ADR-0014 trace propagation)
        # can be recorded on agent_runs.input within the same transaction.
        run_id = str(uuid.uuid4())
        async with AsyncSessionLocal() as session:
            conv = await self._get_or_create_conversation(session, conversation_id)
            conv_id = conv.id
            session.add(models.Message(conversation_id=conv_id, role="user", content=user_text))
            rc = RunContext(
                conversation_id=conv_id,
                agent_run_id=run_id,
                trace_id=str(uuid.uuid4()),
                request_id=str(uuid.uuid4()),
            )
            run = models.AgentRun(
                id=run_id,
                conversation_id=conv_id,
                graph="conversation",
                trigger="chat",
                status="running",
                started_at=datetime.now(timezone.utc),
                input={"trace_id": rc.trace_id, "request_id": rc.request_id},
            )
            session.add(run)
            await session.commit()
            history = await self._load_messages(session, conv_id)

        state = GraphState(messages=history)
        parts: list[str] = []
        usage: dict = {}
        try:
            async with open_checkpointer() as saver:
                graph = build_graph(get_llm_client(), checkpointer=saver)
                cfg = {"configurable": {"thread_id": conv_id}}
                async for chunk in graph.astream(state, cfg, stream_mode="custom"):
                    if chunk.get("type") == "token":
                        parts.append(chunk["text"])
                        yield {"event": "token", "data": {"text": chunk["text"]}}
                    elif chunk.get("type") == "usage":
                        usage = chunk.get("usage", {})
        except NotImplementedError:
            yield {"event": "error", "data": {"code": "llm_not_configured",
                                              "message": "Vertex runtime unavailable"}}
            await self._finalize(run_id, conv_id, status="error", usage=usage, error="llm_not_configured")
            return
        except Exception as e:  # mid-stream failure
            logger.exception("chat stream failed for conversation %s", conv_id)
            yield {"event": "error", "data": {"code": "stream_error",
                                              "message": "An error occurred while streaming the response"}}
            await self._finalize(run_id, conv_id, status="error", usage=usage, error=str(e))
            return

        message_id = await self._persist_assistant(conv_id, "".join(parts))
        await self._finalize(run_id, conv_id, status="done", usage=usage)
        yield {"event": "done", "data": {"conversation_id": conv_id,
                                         "message_id": message_id, "usage": usage}}

    async def _persist_assistant(self, conversation_id: str, content: str) -> str:
        async with AsyncSessionLocal() as session:
            msg = models.Message(conversation_id=conversation_id, role="assistant", content=content)
            session.add(msg)
            await session.commit()
            return msg.id

    async def _finalize(self, run_id: str, conversation_id: str, *, status: str,
                        usage: dict, error: str | None = None) -> None:
        async with AsyncSessionLocal() as session:
            run = await session.get(models.AgentRun, run_id)
            if run:
                run.status = status
                run.error = error
                run.finished_at = datetime.now(timezone.utc)
                run.output = {"usage": usage} if usage else {}   # token accounting on agent_runs (spec §5)
                await session.commit()
