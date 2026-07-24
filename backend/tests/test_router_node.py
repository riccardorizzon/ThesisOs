"""Router node unit tests (M5.1)."""

from __future__ import annotations

import json

from app.graph.router import make_router_node
from app.schemas.graph_state import AgentError, GraphState, Message, Plan


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
        "messages": [Message(role="user", content="Hello")],
        "plan": Plan(steps=["Answer greeting"]),
    }
    defaults.update(kwargs)
    return GraphState(**defaults)


async def test_router_conversation():
    payload = json.dumps({"route": "conversation"})
    node = make_router_node(FakeLLM(payload))
    out = await node(_state())

    assert out["route"] == "conversation"
    assert not any(e.message == "no_route" for e in out["errors"])


async def test_router_grounded_chat():
    payload = json.dumps({"route": "grounded_chat"})
    node = make_router_node(FakeLLM(payload))
    out = await node(_state(messages=[Message(role="user", content="Search my library")]))

    assert out["route"] == "grounded_chat"


async def test_router_forces_explicit_italian_document_query_to_grounded_chat():
    node = make_router_node(FakeLLM("not-json"))
    out = await node(
        _state(
            messages=[
                Message(
                    role="user",
                    content="Cosa dice il mio documento sulla triangolazione?",
                )
            ]
        )
    )

    assert out["route"] == "grounded_chat"
    assert not any(error.message == "no_route" for error in out["errors"])


async def test_router_parse_failure_no_route():
    node = make_router_node(FakeLLM("not-json"))
    out = await node(_state())

    assert out["route"] == "conversation"
    assert any(e.agent == "router" and e.message == "no_route" for e in out["errors"])


async def test_router_missing_route_key():
    node = make_router_node(FakeLLM(json.dumps({"other": "x"})))
    out = await node(_state())

    assert out["route"] == "conversation"
    assert any(e.message == "no_route" for e in out["errors"])


async def test_router_reserved_route_silent_normalize_to_conversation():
    payload = json.dumps({"route": "writer"})
    node = make_router_node(FakeLLM(payload))
    out = await node(_state(messages=[Message(role="user", content="Say hi")]))

    assert out["route"] == "conversation"
    assert not any(e.agent == "router" for e in out["errors"])


async def test_router_reserved_route_silent_normalize_with_retrieval_keywords():
    payload = json.dumps({"route": "writer"})
    node = make_router_node(FakeLLM(payload))
    out = await node(
        _state(messages=[Message(role="user", content="Search my uploaded documents")])
    )

    assert out["route"] == "grounded_chat"
    assert not any(e.agent == "router" for e in out["errors"])


async def test_router_propagates_prior_errors():
    prior = [AgentError(agent="planner", message="unplannable")]
    payload = json.dumps({"route": "conversation"})
    node = make_router_node(FakeLLM(payload))
    out = await node(_state(errors=prior))

    assert out["errors"][0].agent == "planner"
    assert out["route"] == "conversation"


async def test_router_output_keys_only_contract_fields():
    payload = json.dumps({"route": "conversation"})
    node = make_router_node(FakeLLM(payload))
    out = await node(_state())

    assert set(out.keys()) <= {"route", "errors"}
