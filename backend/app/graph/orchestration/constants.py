"""M5 route vocabulary (spec §6.2). Wired routes only — normalization lives in router node."""

from __future__ import annotations

DEFAULT_ROUTE = "conversation"
GROUNDED_ROUTE = "grounded_chat"

WIRED_ROUTES: frozenset[str] = frozenset({DEFAULT_ROUTE, GROUNDED_ROUTE})

RESERVED_ROUTES: frozenset[str] = frozenset({"writer", "critic", "citation", "document"})

# Heuristic keywords for reserved-route normalization (spec §6.2).
RETRIEVAL_KEYWORDS: frozenset[str] = frozenset(
    {
        "document",
        "documents",
        "corpus",
        "source",
        "sources",
        "uploaded",
        "upload",
        "retrieve",
        "retrieval",
        "search",
        "cite",
        "citation",
        "chapter",
        "paper",
        "pdf",
        "according to",
        "what does",
        "what do",
        "from my",
        "in my library",
    }
)
