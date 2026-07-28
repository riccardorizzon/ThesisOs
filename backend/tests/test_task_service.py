"""TaskService unit tests (M5.3)."""

from __future__ import annotations

import json
import uuid

import pytest
from sqlalchemy import select

from app.db import models
from app.graph.planner import make_planner_node
from app.schemas.graph_state import GraphState, Message, Plan, TaskRef
from app.services.conversation.service import ConversationService
from app.services.task.service import TaskService


class FakeLLM:
    def __init__(self, response: str):
        self._response = response

    async def generate(self, messages, *, model=None, params=None) -> str:
        return self._response

    async def astream(self, *a, **k):
        raise NotImplementedError

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError


class SpyTaskService(TaskService):
    def __init__(self):
        self.upserts: list[tuple[TaskRef, str | None, list[str], str | None]] = []
        self.done_ids: list[str] = []

    async def upsert_from_task_ref(
        self,
        task_ref: TaskRef,
        *,
        owner_agent: str | None,
        plan_steps: list[str],
        project_id: str | None = None,
        session=None,
    ) -> None:
        self.upserts.append((task_ref, owner_agent, list(plan_steps), project_id))

    async def mark_done(self, task_id: str, *, session=None) -> None:
        self.done_ids.append(task_id)


@pytest.mark.asyncio
async def test_upsert_stores_project_id(db_session):
    svc = TaskService()
    task_ref = TaskRef(id=str(uuid.uuid4()), title="Scoped")

    await svc.upsert_from_task_ref(
        task_ref,
        owner_agent="planner",
        plan_steps=["a"],
        project_id="thesis-002",
        session=db_session,
    )
    await db_session.commit()

    row = await db_session.get(models.Task, task_ref.id)
    assert row is not None
    assert row.project_id == "thesis-002"


@pytest.mark.asyncio
async def test_upsert_inserts_task_row(db_session):
    svc = TaskService()
    task_ref = TaskRef(id=str(uuid.uuid4()), title="Draft section 2")

    await svc.upsert_from_task_ref(
        task_ref,
        owner_agent="planner",
        plan_steps=["Outline", "Write"],
        session=db_session,
    )
    await db_session.commit()

    row = await db_session.get(models.Task, task_ref.id)
    assert row is not None
    assert row.title == "Draft section 2"
    assert row.status == "in_progress"
    assert row.owner_agent == "planner"
    assert row.payload == {"plan_steps": ["Outline", "Write"]}


@pytest.mark.asyncio
async def test_upsert_updates_existing_task(db_session):
    svc = TaskService()
    task_id = str(uuid.uuid4())
    task_ref = TaskRef(id=task_id, title="First title")

    await svc.upsert_from_task_ref(
        task_ref,
        owner_agent="planner",
        plan_steps=["Step A"],
        session=db_session,
    )
    await db_session.commit()

    updated = TaskRef(id=task_id, title="Revised title")
    await svc.upsert_from_task_ref(
        updated,
        owner_agent="planner",
        plan_steps=["Step A", "Step B"],
        session=db_session,
    )
    await db_session.commit()

    rows = (
        await db_session.execute(select(models.Task).where(models.Task.id == task_id))
    ).scalars().all()
    assert len(rows) == 1
    assert rows[0].title == "Revised title"
    assert rows[0].payload == {"plan_steps": ["Step A", "Step B"]}


@pytest.mark.asyncio
async def test_mark_done_sets_status(db_session):
    svc = TaskService()
    task_ref = TaskRef(id=str(uuid.uuid4()), title="Finish me")

    await svc.upsert_from_task_ref(
        task_ref,
        owner_agent="planner",
        plan_steps=["Work"],
        session=db_session,
    )
    await db_session.commit()

    await svc.mark_done(task_ref.id, session=db_session)
    await db_session.commit()

    row = await db_session.get(models.Task, task_ref.id)
    assert row is not None
    assert row.status == "done"


@pytest.mark.asyncio
async def test_planner_calls_persist_hook_on_happy_path():
    payload = json.dumps(
        {
            "plan_steps": ["Outline section", "Write draft"],
            "task_title": "Section 2 draft",
            "unplannable": False,
        }
    )
    upserts: list[tuple[TaskRef, list[str], str | None]] = []

    async def on_task_ref(task: TaskRef, plan_steps: list[str], project_id: str | None = None) -> None:
        upserts.append((task, list(plan_steps), project_id))

    node = make_planner_node(FakeLLM(payload), on_task_ref=on_task_ref)
    state = GraphState(
        messages=[Message(role="user", content="Draft section 2")],
        plan=Plan(steps=["Supervisor step"]),
    )
    out = await node(state, {})

    assert out["task"] is not None
    assert len(upserts) == 1
    task_ref, steps, project_id = upserts[0]
    assert task_ref.id == out["task"].id
    assert task_ref.title == "Section 2 draft"
    assert steps == ["Outline section", "Write draft"]
    assert project_id is None


@pytest.mark.asyncio
async def test_planner_skips_persist_hook_when_unplannable():
    payload = json.dumps({"plan_steps": [], "task_title": "", "unplannable": True})
    upserts: list[tuple[TaskRef, list[str], str | None]] = []

    async def on_task_ref(task: TaskRef, plan_steps: list[str], project_id: str | None = None) -> None:
        upserts.append((task, list(plan_steps), project_id))

    node = make_planner_node(FakeLLM(payload), on_task_ref=on_task_ref)
    state = GraphState(messages=[Message(role="user", content="???")])
    await node(state, {})

    assert upserts == []


@pytest.mark.asyncio
async def test_planner_continues_when_persist_hook_raises():
    async def failing_hook(task: TaskRef, plan_steps: list[str], project_id: str | None = None) -> None:
        raise RuntimeError("db down")

    payload = json.dumps(
        {"plan_steps": ["Step"], "task_title": "Work", "unplannable": False}
    )
    node = make_planner_node(FakeLLM(payload), on_task_ref=failing_hook)
    out = await node(
        GraphState(messages=[Message(role="user", content="Go")], plan=Plan(steps=[])),
        {},
    )

    assert out["task"] is not None
    assert out["task"].title == "Work"


@pytest.mark.asyncio
async def test_finalize_marks_task_done(db_session):
    svc = TaskService()
    task_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    conv_id = str(uuid.uuid4())

    db_session.add(models.Conversation(id=conv_id, title="Test"))
    await db_session.flush()
    db_session.add(
        models.AgentRun(
            id=run_id,
            conversation_id=conv_id,
            graph="conversation",
            trigger="chat",
            status="running",
        )
    )
    await svc.upsert_from_task_ref(
        TaskRef(id=task_id, title="Turn task"),
        owner_agent="planner",
        plan_steps=["Step"],
        session=db_session,
    )
    await db_session.commit()

    conv_svc = ConversationService(task_service=svc)
    await conv_svc._finalize(run_id, conv_id, status="done", usage={}, task_id=task_id)

    db_session.expire_all()
    row = await db_session.get(models.Task, task_id)
    assert row is not None
    assert row.status == "done"


@pytest.mark.asyncio
async def test_finalize_skips_mark_done_on_error(db_session):
    spy = SpyTaskService()
    run_id = str(uuid.uuid4())
    conv_id = str(uuid.uuid4())

    db_session.add(models.Conversation(id=conv_id, title="Test"))
    await db_session.flush()
    db_session.add(
        models.AgentRun(
            id=run_id,
            conversation_id=conv_id,
            graph="conversation",
            trigger="chat",
            status="running",
        )
    )
    await db_session.commit()

    conv_svc = ConversationService(task_service=spy)
    await conv_svc._finalize(run_id, conv_id, status="error", usage={}, task_id="some-task")

    assert spy.done_ids == []
