"""Route coercion for the router node (spec §6.2). Not routing.py graph edges."""

from __future__ import annotations

from app.graph.orchestration.constants import (
    DEFAULT_ROUTE,
    GROUNDED_ROUTE,
    RETRIEVAL_KEYWORDS,
    WIRED_ROUTES,
)


def _has_retrieval_keywords(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in RETRIEVAL_KEYWORDS)


def coerce_m5_route(raw: str, *, user_message: str) -> str:
    """Map an LLM route token to a wired M5 route.

    Reserved or unknown routes are normalized silently (spec §6.2).
    Callers emit ``no_route`` only for missing/empty route or JSON parse failure.
    """
    route = str(raw).strip().lower()
    if route in WIRED_ROUTES:
        return route
    if _has_retrieval_keywords(user_message):
        return GROUNDED_ROUTE
    return DEFAULT_ROUTE
