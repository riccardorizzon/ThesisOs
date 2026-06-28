"""Tests for shared M5 orchestration helpers."""

from __future__ import annotations

import pytest

from app.graph.orchestration.coerce import coerce_m5_route
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE
from app.graph.orchestration.llm import extract_json_object
from app.graph.orchestration.messages import (
    build_orchestration_user_block,
    last_user_message,
)
from app.schemas.graph_state import GraphState, Message, Plan, TaskRef


def test_last_user_message_skips_system_prefix():
    msgs = [
        Message(role="system", content="memory"),
        Message(role="user", content="  hello  "),
    ]
    assert last_user_message(msgs) == "hello"


def test_last_user_message_none_when_empty():
    assert last_user_message([Message(role="assistant", content="hi")]) is None


def test_extract_json_object_plain():
    assert extract_json_object('{"route": "conversation"}') == {"route": "conversation"}


def test_extract_json_object_markdown_fence():
    raw = 'Here is JSON:\n```json\n{"plan_steps": ["a"]}\n```'
    assert extract_json_object(raw) == {"plan_steps": ["a"]}


def test_extract_json_object_invalid():
    assert extract_json_object("not json") is None
    assert extract_json_object("") is None


def test_build_orchestration_user_block_includes_plan_and_task():
    state = GraphState(
        messages=[Message(role="user", content="Question?")],
        plan=Plan(steps=["step one"]),
        task=TaskRef(id="t-1", title="Research"),
    )
    block = build_orchestration_user_block(state, include_plan=True, include_task=True)
    assert "step one" in block
    assert "Research" in block
    assert "Question?" in block


@pytest.mark.parametrize(
    ("raw", "query", "expected_route"),
    [
        ("conversation", "hello", DEFAULT_ROUTE),
        ("grounded_chat", "hello", GROUNDED_ROUTE),
        ("writer", "search my documents", GROUNDED_ROUTE),
        ("writer", "hello there", DEFAULT_ROUTE),
        ("unknown_route", "hello", DEFAULT_ROUTE),
    ],
)
def test_coerce_m5_route(raw, query, expected_route):
    assert coerce_m5_route(raw, user_message=query) == expected_route
