"""Runtime subscriber + boundary tests (M5.4C)."""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import select

import app
from app.db import models
from app.runtime.events import EventType, RuntimeEvent
from app.runtime.subscribers import AgentStepsSubscriber, LoggingSubscriber
from app.schemas.graph_state import GraphState

BUSINESS_AGENT_MODULES = [
    "graph/supervisor.py",
    "graph/planner.py",
    "graph/router.py",
    "graph/memory_context.py",
    "graph/retriever.py",
]


async def _seed_run(db_session) -> str:
    run_id = str(uuid.uuid4())
    conv_id = str(uuid.uuid4())
    db_session.add(models.Conversation(id=conv_id, title="Test"))
    await db_session.flush()
    db_session.add(
        models.AgentRun(id=run_id, conversation_id=conv_id, graph="conversation", trigger="chat", status="running")
    )
    await db_session.commit()
    return run_id


async def _steps(db_session, run_id: str) -> list[models.AgentStep]:
    db_session.expire_all()
    return list(
        (await db_session.execute(select(models.AgentStep).where(models.AgentStep.agent_run_id == run_id)))
        .scalars()
        .all()
    )


@pytest.mark.asyncio
async def test_agent_steps_subscriber_persists_node_completed(db_session):
    run_id = await _seed_run(db_session)
    sub = AgentStepsSubscriber()

    await sub.on_event(
        RuntimeEvent(
            event_type=EventType.NODE_COMPLETED,
            run_id=run_id,
            metadata={"agent": "planner", "phase": "plan", "duration_ms": 12.5},
        )
    )

    rows = await _steps(db_session, run_id)
    assert len(rows) == 1
    assert rows[0].agent == "planner"
    assert rows[0].phase == "plan"
    assert rows[0].status == "done"
    assert rows[0].output == {"duration_ms": 12.5}


@pytest.mark.asyncio
async def test_agent_steps_subscriber_persists_node_failed(db_session):
    run_id = await _seed_run(db_session)
    sub = AgentStepsSubscriber()

    await sub.on_event(
        RuntimeEvent(
            event_type=EventType.NODE_FAILED,
            run_id=run_id,
            metadata={"agent": "retriever", "phase": "implement", "error": "boom"},
        )
    )

    rows = await _steps(db_session, run_id)
    assert len(rows) == 1
    assert rows[0].status == "error"
    assert rows[0].output.get("error") == "boom"


@pytest.mark.asyncio
async def test_agent_steps_subscriber_ignores_run_level_events(db_session):
    run_id = await _seed_run(db_session)
    sub = AgentStepsSubscriber()

    for et in (EventType.RUN_STARTED, EventType.NODE_STARTED, EventType.ROUTE_SELECTED,
               EventType.TASK_PERSISTED, EventType.RUN_COMPLETED):
        await sub.on_event(RuntimeEvent(event_type=et, run_id=run_id, metadata={"agent": "x"}))

    assert await _steps(db_session, run_id) == []


@pytest.mark.asyncio
async def test_agent_steps_subscriber_never_raises_on_bad_run_id(db_session):
    sub = AgentStepsSubscriber()
    # Unknown run_id violates the FK; the subscriber must swallow, not raise (R6).
    await sub.on_event(
        RuntimeEvent(event_type=EventType.NODE_COMPLETED, run_id="missing", metadata={"agent": "x"})
    )


@pytest.mark.asyncio
async def test_logging_subscriber_logs_event(caplog):
    sub = LoggingSubscriber()
    with caplog.at_level("INFO", logger="app.runtime.events"):
        await sub.on_event(RuntimeEvent(event_type=EventType.RUN_STARTED, run_id="r1"))
    assert any("RunStarted" in r.message for r in caplog.records)


def test_runcontext_is_not_a_graphstate_field():
    # ADR-0014 / C5: execution metadata never enters the domain state.
    assert "run_context" not in GraphState.model_fields
    assert "agent_run_id" not in GraphState.model_fields


def test_business_agents_do_not_import_runtime():
    """R8 / C3: Business agents must not know the event bus / runtime emission."""
    app_root = os.path.dirname(app.__file__)
    offenders = []
    for rel in BUSINESS_AGENT_MODULES:
        with open(os.path.join(app_root, rel), encoding="utf-8") as fh:
            if "app.runtime" in fh.read():
                offenders.append(rel)
    assert offenders == [], f"Business agents import app.runtime: {offenders}"
