from __future__ import annotations

import asyncio
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
        Persists the user message before streaming and the assistant message on completion.
        The AgentRun is finalized on every exit path (success, error, client disconnect)
        so a run never stays stuck in `running`."""
        # Generate the run id up front so the RunContext (ADR-0014 trace propagation)
        # can be recorded on agent_runs.input within the same transaction.
        run_id = str(uuid.uuid4())
        conv_id: str | None = None
        usage: dict = {}
        finalized = False

        # --- Setup (guarded): persist the user message + open the AgentRun, load history.
        try:
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
        except Exception:
            logger.exception("chat setup failed for conversation %s", conversation_id)
            await self._safe_finalize(run_id, conv_id, status="error", usage={}, error="setup_failed")
            yield {"event": "error", "data": {"code": "setup_error",
                                              "message": "Could not start the conversation"}}
            return

        # --- Stream + persist (guarded so the AgentRun is always finalized).
        state = GraphState(messages=history)
        parts: list[str] = []
        try:
            try:
                async with open_checkpointer() as saver:
                    graph = build_graph(get_llm_client(), checkpointer=saver)
                    cfg = {"configurable": {"thread_id": conv_id}}
                    async for chunk in graph.astream(state, cfg, stream_mode="custom"):
                        if chunk.get("type") == "token":
                            parts.append(chunk["text"])
                            yield {"event": "token", "data": {"text": chunk["text"]}}
                        elif chunk.get("type") == "sources":
                            yield {"event": "sources", "data": {"sources": chunk.get("sources", [])}}
                        elif chunk.get("type") == "usage":
                            usage = chunk.get("usage", {})
                message_id = await self._persist_assistant(conv_id, "".join(parts))
                await self._finalize(run_id, conv_id, status="done", usage=usage)
                finalized = True
                yield {"event": "done", "data": {"conversation_id": conv_id,
                                                 "message_id": message_id, "usage": usage}}
            except NotImplementedError:
                await self._safe_finalize(run_id, conv_id, status="error", usage=usage,
                                          error="llm_not_configured")
                finalized = True
                yield {"event": "error", "data": {"code": "llm_not_configured",
                                                  "message": "LLM runtime not configured"}}
            except Exception as e:  # mid-stream / persistence failure
                logger.exception("chat stream failed for conversation %s", conv_id)
                await self._safe_finalize(run_id, conv_id, status="error", usage=usage, error=str(e))
                finalized = True
                yield {"event": "error", "data": {"code": "stream_error",
                                                  "message": "An error occurred while streaming the response"}}
        finally:
            # Client disconnect / cancellation (GeneratorExit, CancelledError) bypasses the
            # handlers above; finalize best-effort (shielded) so the run never stays "running".
            if conv_id is not None and not finalized:
                try:
                    await asyncio.shield(
                        self._finalize(run_id, conv_id, status="cancelled", usage=usage, error="interrupted")
                    )
                except Exception:
                    logger.exception("failed to finalize interrupted run %s", run_id)

    async def _safe_finalize(self, run_id: str, conv_id: str | None, *, status: str,
                             usage: dict, error: str | None = None) -> None:
        """Finalize best-effort so a finalize failure never masks the error event we still yield."""
        if conv_id is None:
            return
        try:
            await self._finalize(run_id, conv_id, status=status, usage=usage, error=error)
        except Exception:
            logger.exception("failed to finalize agent_run %s", run_id)

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
