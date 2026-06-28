"""Unit tests for M5 routing infrastructure (M5.2A)."""

from __future__ import annotations

import inspect

from app.graph import routing
from app.graph.conversation import build_graph
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE, WIRED_ROUTES
from app.graph.routing import M5_ROUTE_EDGE_KEYS, resolve_route, route_after_router
from app.schemas.graph_state import GraphState, Message, Plan


def test_m5_route_edge_keys_match_wired_vocabulary():
    assert M5_ROUTE_EDGE_KEYS is WIRED_ROUTES
    assert M5_ROUTE_EDGE_KEYS == frozenset({DEFAULT_ROUTE, GROUNDED_ROUTE})


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
    state = GraphState(messages=[], route="writer")
    assert resolve_route(state) == DEFAULT_ROUTE


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


def test_build_graph_unchanged_linear_m4_topology():
    source = inspect.getsource(build_graph)
    assert "supervisor" not in source
    assert "route_after_router" not in source
    assert "add_conditional_edges" not in source
    assert 'add_edge(START, "memory_context_node")' in source


def test_routing_reexports_no_duplicate_constants():
    from app.graph.orchestration import constants as orch_constants

    assert routing.M5_ROUTE_EDGE_KEYS is orch_constants.WIRED_ROUTES
