"""Unit tests for M5 routing infrastructure (M5.2A)."""

from __future__ import annotations

from app.graph import routing
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE, WIRED_ROUTES
from app.graph.routing import M5_ROUTE_EDGE_KEYS, resolve_route, route_after_router
from app.schemas.graph_state import GraphState, Message, Plan


def test_m5_route_edge_keys_match_wired_vocabulary():
    from app.graph.orchestration.constants import WRITER_ROUTE

    assert M5_ROUTE_EDGE_KEYS is WIRED_ROUTES
    # M6 (ADR-0031) activated the reserved `writer` route additively.
    assert M5_ROUTE_EDGE_KEYS == frozenset({DEFAULT_ROUTE, GROUNDED_ROUTE, WRITER_ROUTE})


def test_resolve_route_conversation():
    state = GraphState(messages=[], route="conversation")
    assert resolve_route(state) == DEFAULT_ROUTE


def test_resolve_route_grounded_chat():
    state = GraphState(messages=[], route="grounded_chat")
    assert resolve_route(state) == GROUNDED_ROUTE


def test_resolve_route_none_defaults_to_conversation():
    state = GraphState(messages=[Message(role="user", content="hi")])
    assert state.route is None
    assert resolve_route(state) == DEFAULT_ROUTE


def test_resolve_route_empty_string_defaults_to_conversation():
    state = GraphState(messages=[], route="")
    assert resolve_route(state) == DEFAULT_ROUTE


def test_resolve_route_unknown_defaults_to_conversation():
    # `writer` is wired in M6; use a still-reserved route for the unknown case.
    state = GraphState(messages=[], route="critic")
    assert resolve_route(state) == DEFAULT_ROUTE


def test_resolve_route_writer_is_wired():
    state = GraphState(messages=[], route="writer")
    assert resolve_route(state) == "writer"


def test_route_after_retriever_grounded_to_conversation():
    state = GraphState(messages=[], route=GROUNDED_ROUTE)
    assert routing.route_after_retriever(state) == DEFAULT_ROUTE


def test_route_after_retriever_writer_to_writer():
    state = GraphState(messages=[], route="writer")
    assert routing.route_after_retriever(state) == "writer"


def test_resolve_route_normalizes_case():
    state = GraphState(messages=[], route="Grounded_Chat")
    assert resolve_route(state) == GROUNDED_ROUTE


def test_route_after_router_delegates_to_resolve_route():
    state = GraphState(messages=[], route=GROUNDED_ROUTE)
    assert route_after_router(state) == GROUNDED_ROUTE


def test_route_after_router_with_full_state():
    state = GraphState(
        messages=[Message(role="user", content="Search corpus")],
        plan=Plan(steps=["retrieve", "answer"]),
        route=GROUNDED_ROUTE,
    )
    assert route_after_router(state) == GROUNDED_ROUTE


def test_routing_reexports_no_duplicate_constants():
    from app.graph.orchestration import constants as orch_constants

    assert routing.M5_ROUTE_EDGE_KEYS is orch_constants.WIRED_ROUTES
