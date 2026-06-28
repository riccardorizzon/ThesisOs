"""Fake LLM for M5 orchestration graph tests."""

from __future__ import annotations

import json

from app.graph.orchestration.constants import DEFAULT_ROUTE
from app.llm.base import TokenChunk


class OrchestrationLLM:
    """Returns contract JSON from generate(); streams tokens from astream()."""

    def __init__(
        self,
        *,
        route: str = DEFAULT_ROUTE,
        stream_parts: list[str] | None = None,
    ):
        self.route = route
        self.stream_parts = stream_parts if stream_parts is not None else ["ok"]
        self.last_stream_messages: list[dict] | None = None
        self.generate_calls = 0

    async def generate(self, messages, *, model=None, params=None) -> str:
        self.generate_calls += 1
        system = messages[0]["content"] if messages else ""
        if "Supervisor agent" in system:
            return json.dumps(
                {
                    "plan_steps": ["Respond to user"],
                    "route_hint": self.route,
                    "no_objective": False,
                }
            )
        if "Planner agent" in system:
            return json.dumps(
                {
                    "plan_steps": ["Respond to user"],
                    "task_title": "Chat turn",
                    "unplannable": False,
                }
            )
        if "Router agent" in system:
            return json.dumps({"route": self.route})
        return "{}"

    async def astream(self, messages, *, model=None, params=None):
        self.last_stream_messages = messages
        for part in self.stream_parts:
            yield TokenChunk(text=part)
        yield TokenChunk(
            text="",
            finish_reason="stop",
            metadata={"usage": {"total_tokens": max(len(self.stream_parts), 1)}},
        )

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError
