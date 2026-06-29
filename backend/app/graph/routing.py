"""LangGraph dispatch helpers for M5 conditional routing (M5.2A).

Maps ``GraphState.route`` (set by router node) to conditional edge keys.
Route vocabulary and normalization live in ``orchestration/`` (M5.1); this
module is graph dispatch only — no ``build_graph()`` wiring here.
"""

from __future__ import annotations

from app.graph.orchestration.constants import DEFAULT_ROUTE, WIRED_ROUTES, WRITER_ROUTE
from app.schemas.graph_state import GraphState

# LangGraph conditional edge keys (ADR-0027; M6 adds `writer`) — identical to
# wired route strings.
M5_ROUTE_EDGE_KEYS: frozenset[str] = WIRED_ROUTES


def resolve_route(state: GraphState) -> str:
    """Return a wired route key for graph dispatch.

    The router node owns semantic normalization (M5.1). This function only
    validates ``state.route`` and falls back to ``conversation`` when missing
    or not in the wired vocabulary (defensive default for graph wiring).
    """
    route = state.route
    if route is None:
        return DEFAULT_ROUTE
    key = str(route).strip().lower()
    if key in WIRED_ROUTES:
        return key
    return DEFAULT_ROUTE


def route_after_router(state: GraphState) -> str:
    """Conditional edge selector after ``memory_context_node`` (ADR-0027 §1; M6 §1).

    Dispatches the resolved route. Both ``grounded_chat`` and ``writer`` flow
    through the retriever first; ``conversation`` skips it.
    """
    return resolve_route(state)


def route_after_retriever(state: GraphState) -> str:
    """Conditional edge selector after ``retriever_node`` (M6, ADR-0031 §1).

    The grounded path continues to ``conversation_node`` (M5, unchanged); the
    writer path continues to ``writer_node``.
    """
    return WRITER_ROUTE if resolve_route(state) == WRITER_ROUTE else DEFAULT_ROUTE
