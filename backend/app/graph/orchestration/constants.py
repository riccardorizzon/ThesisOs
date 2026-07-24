"""Route vocabulary (M5 spec §6.2; M6 activates the writer route, ADR-0031).

Normalization lives in the router node (`coerce.py`). The graph-dispatchable set
(`WIRED_ROUTES`) grows per milestone as reserved routes are activated.
"""

from __future__ import annotations

DEFAULT_ROUTE = "conversation"
GROUNDED_ROUTE = "grounded_chat"
WRITER_ROUTE = "writer"  # M6 (ADR-0031): drafting route, memory_context → retriever → writer

# Routes the graph can dispatch to. M6 added `writer` (was reserved in M5/ADR-0027).
WIRED_ROUTES: frozenset[str] = frozenset({DEFAULT_ROUTE, GROUNDED_ROUTE, WRITER_ROUTE})

# Routes an LLM may emit that pass through coerce unconditionally. `writer` is NOT
# here — it is intent-gated (a thesis-drafting request), so a stray "writer" from
# the LLM on a non-drafting turn still normalizes to conversation/grounded (M5 §6.2).
DIRECT_ROUTES: frozenset[str] = frozenset({DEFAULT_ROUTE, GROUNDED_ROUTE})

RESERVED_ROUTES: frozenset[str] = frozenset({"critic", "citation", "document"})

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
        "documento",
        "documenti",
        "fonte",
        "fonti",
        "caricato",
        "caricati",
        "cerca",
        "citazione",
        "citazioni",
        "cosa dice",
        "cosa dicono",
        "nel mio",
        "nella mia biblioteca",
    }
)

# M6 (ADR-0031 §4): explicit thesis-drafting phrases that activate the writer route.
WRITER_PHRASES: frozenset[str] = frozenset(
    {
        "write the chapter",
        "write a chapter",
        "write this chapter",
        "draft the chapter",
        "draft a chapter",
        "draft this chapter",
        "write the section",
        "write a section",
        "draft the section",
        "draft a section",
        "write the introduction",
        "write the conclusion",
        "draft the introduction",
        "draft the conclusion",
        "scrivi il capitolo",
        "scrivi un capitolo",
        "scrivi la sezione",
        "scrivi una sezione",
        "redigi il capitolo",
        "redigi la sezione",
        "stendi il capitolo",
    }
)

# Thesis-structure tokens: combined with an LLM `writer` route, they confirm drafting
# intent (so "write the chapter" routes to writer, but "summarize chapter 3" does not
# unless the LLM itself chose writer).
WRITER_STRUCTURE_TOKENS: frozenset[str] = frozenset(
    {"chapter", "section", "subsection", "capitolo", "capitoli", "sezione", "sezioni", "paragrafo"}
)

