"""Supervisor node unit tests (M5.1)."""

from __future__ import annotations

import json

import pytest

from app.graph.supervisor import make_supervisor_node
from app.schemas.graph_state import GraphState, Message, Plan, TaskRef


class FakeLLM:
    def __init__(self, response: str):
        self._response = response
        self.last_messages: list[dict] | None = None

    async def generate(self, messages, *, model=None, params=None) -> str:
        self.last_messages = messages
        return self._response

    async def astream(self, *a, **k):
        raise NotImplementedError

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError


def _state(**kwargs) -> GraphState:
    defaults = {"messages": [Message(role="user", content="Explain habitus")]}
    defaults.update(kwargs)
    return GraphState(**defaults)


async def test_supervisor_happy_path():
    payload = json.dumps(
        {
            "plan_steps": ["Clarify concept", "Draft answer"],
            "route_hint": "conversation",
            "no_objective": False,
        }
    )
    node = make_supervisor_node(FakeLLM(payload))
    out = await node(_state())

    assert out["plan"].steps == ["Clarify concept", "Draft answer"]
    assert out["route"] == "conversation"
    assert not any(e.message == "no_objective" for e in out["errors"])


async def test_supervisor_grounded_route_hint():
    payload = json.dumps(
        {
            "plan_steps": ["Search corpus", "Answer with citations"],
            "route_hint": "grounded_chat",
            "no_objective": False,
        }
    )
    node = make_supervisor_node(FakeLLM(payload))
    out = await node(_state(messages=[Message(role="user", content="What do my PDFs say?")]))

    assert out["route"] == "grounded_chat"


async def test_supervisor_no_objective_from_llm():
    payload = json.dumps({"plan_steps": [], "route_hint": "conversation", "no_objective": True})
    node = make_supervisor_node(FakeLLM(payload))
    out = await node(_state())

    assert out["plan"].steps == []
    assert out["route"] == "conversation"
    assert any(e.agent == "supervisor" and e.message == "no_objective" for e in out["errors"])


async def test_supervisor_no_user_message_skips_llm():
    llm = FakeLLM("{}")
    node = make_supervisor_node(llm)
    out = await node(_state(messages=[Message(role="assistant", content="only assistant")]))

    assert llm.last_messages is None
    assert out["route"] == "conversation"
    assert any(e.message == "no_objective" for e in out["errors"])


async def test_supervisor_parse_failure_fallback():
    node = make_supervisor_node(FakeLLM("```not valid json"))
    out = await node(_state())

    assert out["plan"].steps == []
    assert out["route"] == "conversation"
    assert any(e.message == "no_objective" for e in out["errors"])


async def test_supervisor_empty_plan_steps_is_no_objective():
    payload = json.dumps({"plan_steps": [], "route_hint": "conversation", "no_objective": False})
    node = make_supervisor_node(FakeLLM(payload))
    out = await node(_state())

    assert any(e.message == "no_objective" for e in out["errors"])


async def test_supervisor_reads_task_in_prompt():
    llm = FakeLLM(
        json.dumps(
            {
                "plan_steps": ["Continue task"],
                "route_hint": "conversation",
                "no_objective": False,
            }
        )
    )
    node = make_supervisor_node(llm)
    await node(_state(task=TaskRef(id="abc", title="Thesis outline")))

    assert llm.last_messages is not None
    user_content = llm.last_messages[1]["content"]
    assert "Thesis outline" in user_content


async def test_supervisor_output_keys_only_contract_fields():
    payload = json.dumps(
        {"plan_steps": ["One"], "route_hint": "conversation", "no_objective": False}
    )
    node = make_supervisor_node(FakeLLM(payload))
    out = await node(_state())

    assert set(out.keys()) <= {"plan", "route", "errors"}
