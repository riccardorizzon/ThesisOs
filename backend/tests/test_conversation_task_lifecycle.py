"""ConversationService task lifecycle behavior tests (M5.3 freeze gate)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from app.db import models
from app.graph.conversation import build_graph
from app.services.conversation.service import ConversationService
from app.services.task.service import TaskService
from tests.support.orchestration_llm import OrchestrationLLM


@pytest.fixture
async def langgraph_ready(db_session):
    from app.graph.checkpointer import ensure_langgraph_schema

    await ensure_langgraph_schema()


@pytest.fixture
def orchestration_llm(monkeypatch):
    llm = OrchestrationLLM(stream_parts=["hello"])
    monkeypatch.setattr("app.services.conversation.service.get_llm_client", lambda: llm)
    monkeypatch.setattr(
        "app.services.conversation.service.get_orchestration_llm_client",
        lambda: llm,
    )
    return llm


async def _collect_stream(svc: ConversationService, *, user_text: str = "hello") -> list[dict]:
    events: list[dict] = []
    async for event in svc.stream_turn(conversation_id=None, user_text=user_text):
        events.append(event)
    return events


async def _task_rows(db_session) -> list[models.Task]:
    db_session.expire_all()
    return list((await db_session.execute(select(models.Task))).scalars().all())


async def _latest_agent_run(db_session):
    db_session.expire_all()
    return (
        await db_session.execute(
            select(models.AgentRun).order_by(models.AgentRun.created_at.desc()).limit(1)
        )
    ).scalar_one()


@pytest.mark.asyncio
async def test_stream_turn_success_marks_task_done(db_session, langgraph_ready, orchestration_llm):
    svc = ConversationService()
    events = await _collect_stream(svc)

    assert any(e["event"] == "done" for e in events)
    assert not any(e["event"] == "error" for e in events)

    tasks = await _task_rows(db_session)
    assert len(tasks) == 1
    assert tasks[0].status == "done"
    assert tasks[0].title == "Chat turn"

    run = await _latest_agent_run(db_session)
    assert run.status == "done"


@pytest.mark.asyncio
async def test_stream_turn_exception_leaves_task_in_progress(
    db_session, langgraph_ready, orchestration_llm, monkeypatch
):
    def exploding_build(*args, **kwargs):
        graph = build_graph(*args, **kwargs)
        original_astream = graph.astream

        async def astream_with_failure(*a, **kw):
            async for chunk in original_astream(*a, **kw):
                yield chunk
                raise RuntimeError("simulated stream failure")

        graph.astream = astream_with_failure  # type: ignore[method-assign]
        return graph

    monkeypatch.setattr("app.services.conversation.service.build_graph", exploding_build)

    svc = ConversationService()
    events = await _collect_stream(svc)

    assert any(e["event"] == "error" for e in events)
    assert not any(e["event"] == "done" for e in events)

    tasks = await _task_rows(db_session)
    assert len(tasks) == 1
    assert tasks[0].status == "in_progress"

    run = await _latest_agent_run(db_session)
    assert run.status == "error"


@pytest.mark.asyncio
async def test_stream_turn_client_disconnect_leaves_task_not_done(
    db_session, langgraph_ready, orchestration_llm
):
    svc = ConversationService()
    gen = svc.stream_turn(conversation_id=None, user_text="hello")
    try:
        async for event in gen:
            if event["event"] == "token":
                break
    finally:
        await gen.aclose()

    tasks = await _task_rows(db_session)
    if tasks:
        assert tasks[0].status != "done"

    run = await _latest_agent_run(db_session)
    assert run.status == "cancelled"


@pytest.mark.asyncio
async def test_stream_turn_mark_done_failure_still_completes_turn(
    db_session, langgraph_ready, orchestration_llm
):
    class FailingMarkDoneService(TaskService):
        async def mark_done(self, task_id: str, *, session=None) -> None:
            raise RuntimeError("mark_done unavailable")

    svc = ConversationService(task_service=FailingMarkDoneService())
    events = await _collect_stream(svc)

    assert any(e["event"] == "done" for e in events)
    assert not any(e["event"] == "error" for e in events)

    tasks = await _task_rows(db_session)
    assert len(tasks) == 1
    assert tasks[0].status == "in_progress"

    run = await _latest_agent_run(db_session)
    assert run.status == "done"
