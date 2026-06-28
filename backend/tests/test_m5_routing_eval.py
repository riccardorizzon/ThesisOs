"""M5.5 routing eval harness — deterministic routing KPI over a labeled set.

Feeds the real router node a raw LLM route per case and asserts the final wired
dispatch key (`route_after_router`). Validates coerce + reserved-route
normalization + keyword fallback + no_route/parse-failure defaults.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.graph.router import make_router_node
from app.graph.routing import route_after_router
from app.schemas.graph_state import GraphState, Message

_FIXTURE = Path(__file__).parent / "fixtures" / "m5_routing_eval.json"


class RouteLLM:
    """Returns a fixed raw payload for the router node's generate() call."""

    def __init__(self, payload: str) -> None:
        self._payload = payload

    async def generate(self, messages, *, model=None, params=None) -> str:
        return self._payload

    async def astream(self, *a, **k):
        raise NotImplementedError

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError


def _payload_for(llm_route) -> str:
    if llm_route is None:
        return "{}"
    if llm_route == "__malformed__":
        return "not valid json at all"
    return json.dumps({"route": llm_route})


async def _final_route(case: dict) -> str:
    node = make_router_node(RouteLLM(_payload_for(case["llm_route"])))
    state = GraphState(messages=[Message(role="user", content=case["user_message"])])
    out = await node(state)
    return route_after_router(GraphState(messages=state.messages, route=out["route"]))


def _load() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_routing_eval_meets_threshold():
    data = _load()
    cases = data["cases"]
    results = [(c["name"], await _final_route(c), c["expected"]) for c in cases]

    failed = [(name, actual, expected) for name, actual, expected in results if actual != expected]
    accuracy = (len(results) - len(failed)) / len(results)

    assert len(cases) >= 8, "routing eval set too small to be meaningful"
    assert accuracy >= data["threshold"], (
        f"routing accuracy {accuracy:.3f} < threshold {data['threshold']}; failed={failed}"
    )


@pytest.mark.asyncio
async def test_routing_eval_cases_have_unique_names():
    names = [c["name"] for c in _load()["cases"]]
    assert len(names) == len(set(names))
