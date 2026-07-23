from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from sqlalchemy import exists, select

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.graph.checkpointer import open_checkpointer
from app.graph.conversation import build_graph
from app.llm.factory import get_llm_client, get_orchestration_llm_client
from app.runtime.contracts import RuntimeEventEmitter
from app.runtime.event_bus import RuntimeEventBus
from app.runtime.events import EventType, RuntimeEvent
from app.runtime.instrumentation import emit_safely
from app.runtime.subscribers import AgentStepsSubscriber, LoggingSubscriber
from app.schemas.conversation import (
    ConversationListResponse,
    ConversationMessage,
    ConversationMessagesResponse,
    ConversationSummary,
)
from app.schemas.graph_state import GraphState, Message
from app.schemas.run_context import RunContext
from app.services.conversation.exceptions import ConversationNotFoundError
from app.services.task.service import TaskService

logger = logging.getLogger("app.services.conversation")


class ConversationService:
    """Boundary between HTTP and the graph. `messages` is the system of record; the
    checkpointer holds derived working state (spec §5)."""

    def __init__(
        self,
        *,
        task_service: TaskService | None = None,
        event_bus: RuntimeEventEmitter | None = None,
    ) -> None:
        self._task_service = task_service or TaskService()
        # Composition root: the bus is wired with concrete subscribers here, never
        # inside the bus or Business agents (ADR-0030 C2/R8).
        self._event_bus: RuntimeEventEmitter = event_bus or RuntimeEventBus(
            [AgentStepsSubscriber(), LoggingSubscriber()]
        )

    async def _emit(self, event_type: EventType, rc: RunContext | None, **metadata) -> None:
        if rc is None:
            return
        await emit_safely(
            self._event_bus,
            RuntimeEvent(
                event_type=event_type,
                run_id=rc.agent_run_id,
                correlation_id=rc.trace_id,
                metadata=metadata,
            ),
        )

    async def _get_or_create_conversation(
        self,
        session,
        conversation_id: str | None,
        *,
        title: str | None = None,
    ) -> models.Conversation:
        if conversation_id:
            conv = await session.get(models.Conversation, conversation_id)
            if conv:
                return conv
        conv = models.Conversation(
            id=conversation_id or str(uuid.uuid4()),
            title=title or "New Conversation",
        )
        session.add(conv)
        await session.flush()
        return conv

    async def _record_project_scope(
        self,
        session,
        conversation_id: str,
        project_id: str,
    ) -> None:
        """Associate a conversation with a project without altering the conversations table."""
        scoped = (
            await session.execute(
                select(models.AgentRun.id)
                .where(
                    models.AgentRun.conversation_id == conversation_id,
                    models.AgentRun.input["project_id"].as_string() == project_id,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if scoped is not None:
            return
        now = datetime.now(timezone.utc)
        session.add(
            models.AgentRun(
                conversation_id=conversation_id,
                graph="conversation",
                trigger="scope",
                status="done",
                started_at=now,
                finished_at=now,
                input={"project_id": project_id},
            )
        )
        await session.flush()

    def _summary(self, conv: models.Conversation, project_id: str) -> ConversationSummary:
        return ConversationSummary(
            id=conv.id,
            project_id=project_id,
            title=conv.title,
            created_at=conv.created_at,
        )

    async def list_conversations(self, project_id: str) -> ConversationListResponse:
        async with AsyncSessionLocal() as session:
            rows = (
                await session.execute(
                    select(models.Conversation)
                    .where(
                        exists().where(
                            models.AgentRun.conversation_id == models.Conversation.id,
                            models.AgentRun.input["project_id"].as_string() == project_id,
                        )
                    )
                    .order_by(models.Conversation.created_at.desc())
                )
            ).scalars().all()
            return ConversationListResponse(
                items=[self._summary(conv, project_id) for conv in rows]
            )

    async def create_conversation(
        self,
        project_id: str,
        *,
        title: str | None = None,
    ) -> ConversationSummary:
        async with AsyncSessionLocal() as session:
            conv = await self._get_or_create_conversation(session, None, title=title)
            await self._record_project_scope(session, conv.id, project_id)
            await session.commit()
            return self._summary(conv, project_id)

    async def list_messages(self, conversation_id: str) -> ConversationMessagesResponse:
        async with AsyncSessionLocal() as session:
            conv = await session.get(models.Conversation, conversation_id)
            if conv is None:
                raise ConversationNotFoundError(conversation_id)
            rows = (
                await session.execute(
                    select(models.Message)
                    .where(models.Message.conversation_id == conversation_id)
                    .order_by(models.Message.created_at)
                )
            ).scalars().all()
            return ConversationMessagesResponse(
                items=[
                    ConversationMessage(
                        id=row.id,
                        role=row.role,
                        content=row.content,
                        created_at=row.created_at,
                    )
                    for row in rows
                ]
            )

    async def _load_messages(self, session, conversation_id: str) -> list[Message]:
        rows = (await session.execute(
            select(models.Message).where(models.Message.conversation_id == conversation_id)
            .order_by(models.Message.created_at)
        )).scalars().all()
        return [Message(role=r.role, content=r.content) for r in rows]

    async def stream_turn(
        self,
        *,
        conversation_id: str | None,
        user_text: str,
        project_id: str | None = None,
    ) -> AsyncIterator[dict]:
        """Yield SSE-ready dicts: {"event": "token"|"done"|"error", "data": {...}}.
        Persists the user message before streaming and the assistant message on completion.
        The AgentRun is finalized on every exit path (success, error, client disconnect)
        so a run never stays stuck in `running`."""
        # Generate the run id up front so the RunContext (ADR-0014 trace propagation)
        # can be recorded on agent_runs.input within the same transaction.
        run_id = str(uuid.uuid4())
        conv_id: str | None = None
        rc: RunContext | None = None
        usage: dict = {}
        finalized = False

        # --- Setup (guarded): persist the user message + open the AgentRun, load history.
        try:
            async with AsyncSessionLocal() as session:
                conv = await self._get_or_create_conversation(session, conversation_id)
                conv_id = conv.id
                if project_id:
                    await self._record_project_scope(session, conv_id, project_id)
                session.add(models.Message(conversation_id=conv_id, role="user", content=user_text))
                rc = RunContext(
                    conversation_id=conv_id,
                    agent_run_id=run_id,
                    trace_id=str(uuid.uuid4()),
                    request_id=str(uuid.uuid4()),
                )
                run_input: dict = {"trace_id": rc.trace_id, "request_id": rc.request_id}
                if project_id:
                    run_input["project_id"] = project_id
                run = models.AgentRun(
                    id=run_id,
                    conversation_id=conv_id,
                    graph="orchestrated_conversation",
                    trigger="chat",
                    status="running",
                    started_at=datetime.now(timezone.utc),
                    input=run_input,
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
        task_id: str | None = None
        await self._emit(EventType.RUN_STARTED, rc, conversation_id=conv_id, trace_id=rc.trace_id)
        try:
            try:
                async with open_checkpointer() as saver:
                    graph = build_graph(
                        get_llm_client(),
                        orchestration_llm=get_orchestration_llm_client(),
                        checkpointer=saver,
                        task_service=self._task_service,
                        emitter=self._event_bus,
                        run_context=rc,
                    )
                    # RunContext travels via LangGraph config, never GraphState (ADR-0014).
                    cfg = {
                        "configurable": {
                            "thread_id": conv_id,
                            "run_context": rc.model_dump(),
                            "project_id": project_id,
                        }
                    }
                    async for chunk in graph.astream(state, cfg, stream_mode="custom"):
                        if chunk.get("type") == "token":
                            parts.append(chunk["text"])
                            yield {"event": "token", "data": {"text": chunk["text"]}}
                        elif chunk.get("type") == "replace":
                            parts = [chunk.get("text", "")]
                            yield {
                                "event": "replace",
                                "data": {"text": chunk.get("text", "")},
                            }
                        elif chunk.get("type") == "sources":
                            yield {"event": "sources", "data": {"sources": chunk.get("sources", [])}}
                        elif chunk.get("type") == "usage":
                            usage = chunk.get("usage", {})
                    snap = await graph.aget_state(cfg)
                    task = snap.values.get("task") if snap.values else None
                    if task is not None:
                        task_id = task.id
                message_id = await self._persist_assistant(conv_id, "".join(parts))
                await self._finalize(run_id, conv_id, status="done", usage=usage, task_id=task_id)
                finalized = True
                await self._emit(EventType.RUN_COMPLETED, rc, status="done", task_id=task_id)
                yield {"event": "done", "data": {"conversation_id": conv_id,
                                                 "message_id": message_id, "usage": usage}}
            except NotImplementedError:
                await self._safe_finalize(run_id, conv_id, status="error", usage=usage,
                                          error="llm_not_configured")
                finalized = True
                await self._emit(EventType.RUN_COMPLETED, rc, status="error", error="llm_not_configured")
                yield {"event": "error", "data": {"code": "llm_not_configured",
                                                  "message": "LLM runtime not configured"}}
            except Exception as e:  # mid-stream / persistence failure
                logger.exception("chat stream failed for conversation %s", conv_id)
                await self._safe_finalize(run_id, conv_id, status="error", usage=usage, error=str(e))
                finalized = True
                await self._emit(EventType.RUN_COMPLETED, rc, status="error")
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
                    await asyncio.shield(self._emit(EventType.RUN_COMPLETED, rc, status="cancelled"))
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

    async def _finalize(
        self,
        run_id: str,
        conversation_id: str,
        *,
        status: str,
        usage: dict,
        error: str | None = None,
        task_id: str | None = None,
    ) -> None:
        async with AsyncSessionLocal() as session:
            run = await session.get(models.AgentRun, run_id)
            if run:
                run.status = status
                run.error = error
                run.finished_at = datetime.now(timezone.utc)
                run.output = {"usage": usage} if usage else {}   # token accounting on agent_runs (spec §5)
                await session.commit()
        if status == "done" and task_id is not None:
            try:
                await self._task_service.mark_done(task_id)
            except Exception:
                logger.exception("failed to mark task %s done after turn finalize", task_id)
