"""Route coercion for the router node (spec §6.2; M6 writer, ADR-0031 §4).

Not routing.py graph edges — this maps an LLM route token to a wired route.
"""

from __future__ import annotations

from app.graph.orchestration.constants import (
    DEFAULT_ROUTE,
    DIRECT_ROUTES,
    GROUNDED_ROUTE,
    RETRIEVAL_KEYWORDS,
    WRITER_PHRASES,
    WRITER_ROUTE,
    WRITER_STRUCTURE_TOKENS,
)


def has_retrieval_intent(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in RETRIEVAL_KEYWORDS)


def _has_writer_intent(raw_route: str, user_message: str) -> bool:
    """A genuine thesis-drafting request (ADR-0031 §4).

    Triggers on an explicit drafting phrase, or when the LLM itself chose the
    writer route AND the message references a thesis structure (chapter/section).
    """
    lower = user_message.lower()
    if any(phrase in lower for phrase in WRITER_PHRASES):
        return True
    if raw_route == WRITER_ROUTE and any(tok in lower for tok in WRITER_STRUCTURE_TOKENS):
        return True
    return False


def coerce_m5_route(raw: str, *, user_message: str) -> str:
    """Map an LLM route token to a wired route.

    Direct routes (conversation/grounded_chat) pass through. The writer route
    activates only on thesis-drafting intent (M6). Otherwise reserved/unknown
    routes normalize silently: retrieval keywords → grounded, else conversation
    (spec §6.2). Callers emit ``no_route`` only for missing/empty/parse failure.
    """
    route = str(raw).strip().lower()
    if _has_writer_intent(route, user_message):
        return WRITER_ROUTE
    if route == GROUNDED_ROUTE:
        return GROUNDED_ROUTE
    if has_retrieval_intent(user_message):
        return GROUNDED_ROUTE
    if route in DIRECT_ROUTES:
        return route
    return DEFAULT_ROUTE
