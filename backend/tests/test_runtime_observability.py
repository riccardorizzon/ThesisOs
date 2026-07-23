"""Runtime observability integration (M5.4C) — events emitted at lifecycle boundaries
and agent_steps persisted, with Business node bodies untouched."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.db import models
from app.runtime.event_bus import RuntimeEventBus
from app.runtime.events import EventType, RuntimeEvent
from app.runtime.subscribers import AgentStepsSubscriber
from app.services.conversation.service import ConversationService
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


class SpySubscriber:
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    async def on_event(self, event: RuntimeEvent) -> None:
        self.events.append(event)


class AlwaysFailingSubscriber:
    async def on_event(self, event: RuntimeEvent) -> None:
        raise RuntimeError("subscriber down")


async def _run_turn(svc: ConversationService) -> list[dict]:
    return [e async for e in svc.stream_turn(conversation_id=None, user_text="hello")]


@pytest.mark.asyncio
async def test_turn_emits_canonical_event_sequence(db_session, langgraph_ready, orchestration_llm):
    spy = SpySubscriber()
    svc = ConversationService(event_bus=RuntimeEventBus([spy]))

    events = await _run_turn(svc)
    assert any(e["event"] == "done" for e in events)

    types = [e.event_type for e in spy.events]
    assert types[0] == EventType.RUN_STARTED
    assert types[-1] == EventType.RUN_COMPLETED
    assert EventType.ROUTE_SELECTED in types
    assert EventType.TASK_PERSISTED in types

    completed_agents = {
        e.metadata.get("agent") for e in spy.events if e.event_type == EventType.NODE_COMPLETED
    }
    assert {"supervisor", "planner", "router", "memory_context", "conversation"} <= completed_agents

    run_completed = next(e for e in spy.events if e.event_type == EventType.RUN_COMPLETED)
    assert run_completed.metadata.get("status") == "done"
    # All events share the same run correlation (RunContext flowed via config, not state).
    assert len({e.run_id for e in spy.events}) == 1


@pytest.mark.asyncio
async def test_turn_persists_agent_steps(db_session, langgraph_ready, orchestration_llm):
    svc = ConversationService(event_bus=RuntimeEventBus([AgentStepsSubscriber()]))

    await _run_turn(svc)

    db_session.expire_all()
    rows = list((await db_session.execute(select(models.AgentStep))).scalars().all())
    agents = {r.agent for r in rows}
    assert {"supervisor", "planner", "router", "memory_context", "conversation"} <= agents
    assert all(r.status == "done" for r in rows)
    assert all(r.agent_run_id for r in rows)


@pytest.mark.asyncio
async def test_failing_subscriber_does_not_break_turn(db_session, langgraph_ready, orchestration_llm):
    svc = ConversationService(event_bus=RuntimeEventBus([AlwaysFailingSubscriber()]))

    events = await _run_turn(svc)

    assert any(e["event"] == "done" for e in events)
    assert not any(e["event"] == "error" for e in events)
