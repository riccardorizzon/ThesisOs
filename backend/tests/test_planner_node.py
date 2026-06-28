"""Planner node unit tests (M5.1)."""

from __future__ import annotations

import json
import uuid

import pytest

from app.graph.planner import make_planner_node
from app.schemas.graph_state import AgentError, GraphState, Message, Plan, TaskRef


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


def _state(**kwargs) -> GraphState:
    defaults = {
        "messages": [Message(role="user", content="Draft section 2")],
        "plan": Plan(steps=["Supervisor step"]),
    }
    defaults.update(kwargs)
    return GraphState(**defaults)


async def test_planner_happy_path():
    payload = json.dumps(
        {
            "plan_steps": ["Outline section", "Write draft"],
            "task_title": "Section 2 draft",
            "unplannable": False,
        }
    )
    node = make_planner_node(FakeLLM(payload))
    out = await node(_state())

    assert out["plan"].steps == ["Outline section", "Write draft"]
    assert out["task"] is not None
    assert out["task"].title == "Section 2 draft"
    uuid.UUID(out["task"].id)
    assert not any(e.message == "unplannable" for e in out["errors"])


async def test_planner_preserves_existing_task_id():
    payload = json.dumps(
        {
            "plan_steps": ["Refine"],
            "task_title": "Same task",
            "unplannable": False,
        }
    )
    node = make_planner_node(FakeLLM(payload))
    out = await node(_state(task=TaskRef(id="fixed-id-123", title="Old")))

    assert out["task"].id == "fixed-id-123"
    assert out["task"].title == "Same task"


async def test_planner_unplannable_from_llm():
    payload = json.dumps({"plan_steps": [], "task_title": "", "unplannable": True})
    node = make_planner_node(FakeLLM(payload))
    out = await node(_state())

    assert out["task"] is None
    assert any(e.agent == "planner" and e.message == "unplannable" for e in out["errors"])


async def test_planner_parse_failure():
    node = make_planner_node(FakeLLM("{ broken"))
    out = await node(_state())

    assert out["task"] is None
    assert any(e.message == "unplannable" for e in out["errors"])


async def test_planner_missing_task_title_unplannable():
    payload = json.dumps(
        {"plan_steps": ["Only steps"], "task_title": "  ", "unplannable": False}
    )
    node = make_planner_node(FakeLLM(payload))
    out = await node(_state())

    assert out["task"] is None
    assert any(e.message == "unplannable" for e in out["errors"])


async def test_planner_propagates_prior_errors():
    prior = [AgentError(agent="supervisor", message="no_objective")]
    payload = json.dumps(
        {"plan_steps": ["Step"], "task_title": "Work", "unplannable": False}
    )
    node = make_planner_node(FakeLLM(payload))
    out = await node(_state(errors=prior))

    assert out["errors"][0].agent == "supervisor"
    assert len(out["errors"]) == 1


async def test_planner_output_keys_only_contract_fields():
    payload = json.dumps(
        {"plan_steps": ["A"], "task_title": "T", "unplannable": False}
    )
    node = make_planner_node(FakeLLM(payload))
    out = await node(_state())

    assert set(out.keys()) <= {"plan", "task", "errors"}
