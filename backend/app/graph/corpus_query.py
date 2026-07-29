"""Shared corpus-query detection for retrieval boost and grounding instructions."""

from __future__ import annotations

import re

_CORPUS_QUERY_RE = re.compile(
    r"corpus|esclus|fondamentale|supporto|autori",
    re.IGNORECASE,
)

EXCLUSION_BOOST_QUERY = (
    "CORPUS-02 CORPUS-03 Mythologies Bourriaud escluso corpus attivo ESCLUSO"
)

CORPUS_LIST_BOOST_QUERY = (
    "Bibliography-Master v1.0 AUTORI FONDAMENTALI SUPPORTO PERIFERICO "
    "A.1 A.2 A.3 Eco Flügel Löbach Csikszentmihalyi Sennett Warburg CORPUS-01"
)

CORPUS_RETRIEVAL_LIMIT = 12

# When the user names an author/work, boost the primary document over
# secondary mentions in Outline / Core-Theory-Map (demo RAG quality).
# Tuple: (query pattern, English-leaning boost query, title substring to keep).
_AUTHOR_DOC_BOOSTS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(
            r"\bsennett\b|craftsman|craftsmanship|artigian",
            re.IGNORECASE,
        ),
        "The Craftsman workmanship material consciousness hand practice",
        "Sennett_The-Craftsman",
    ),
    (
        re.compile(r"\bbenjamin\b|\baura\b|riproducibilit", re.IGNORECASE),
        "aura mechanical reproduction work of art Benjamin",
        "Benjamin_Opera-Arte-Riproducibilita",
    ),
    (
        re.compile(r"\bbarthes\b|mytholog", re.IGNORECASE),
        "Mythologies Barthes myth",
        "Barthes Mythologies",
    ),
    (
        re.compile(r"\balbers\b|interaction of color", re.IGNORECASE),
        "Interaction of Color Albers relational color",
        "Albers Interaction-of-Color",
    ),
    (
        re.compile(r"\bhollander\b|sex and suits", re.IGNORECASE),
        "Sex and Suits Hollander fashion",
        "Hollander Sex-and-Suits",
    ),
    (
        re.compile(r"csikszentmihalyi|\bflow\b", re.IGNORECASE),
        "Flow Csikszentmihalyi optimal experience",
        "Csikszentmihalyi Flow",
    ),
)


def author_document_boosts(query: str) -> list[tuple[str, str]]:
    """Return (boost_query, title_substring) pairs for named authors in the user query."""
    return [
        (boost_query, title_sub)
        for pattern, boost_query, title_sub in _AUTHOR_DOC_BOOSTS
        if pattern.search(query)
    ]


def author_document_boost_queries(query: str) -> list[str]:
    """Extra retrieval queries that prefer the named author's primary document."""
    return [boost_query for boost_query, _title in author_document_boosts(query)]


# Legacy read-only catalog for corpus-query boost and graph picker (PX2-EWO-004).
# Sources API list/get reads DB only (M7 P-SOURCES-DB); do not use here for happy path.
CORPUS_PICKER_SOURCES: tuple[dict[str, str], ...] = (
    {
        "id": "benjamin-opera-arte",
        "title": "L'opera d'arte nell'epoca della riproducibilità tecnica",
        "author": "Walter Benjamin",
        "year": "1936",
        "status": "approvata",
    },
    {
        "id": "barthes-mythologies",
        "title": "Mythologies",
        "author": "Roland Barthes",
        "year": "1957",
        "status": "esclusa",
    },
    {
        "id": "albers-interaction-color",
        "title": "Interaction of Color",
        "author": "Josef Albers",
        "year": "1963",
        "status": "candidata",
    },
    {
        "id": "csikszentmihalyi-flow",
        "title": "Flow",
        "author": "Mihaly Csikszentmihalyi",
        "year": "1990",
        "status": "candidata",
    },
    {
        "id": "hollander-sex-suits",
        "title": "Sex and Suits",
        "author": "Anne Hollander",
        "year": "1994",
        "status": "approvata",
    },
)

EXCLUDED_SOURCE_IDS: frozenset[str] = frozenset(
    entry["id"] for entry in CORPUS_PICKER_SOURCES if entry["status"] == "esclusa"
)


def is_corpus_list_query(query: str) -> bool:
    return bool(_CORPUS_QUERY_RE.search(query))


def list_corpus_for_picker(
    query: str = "",
    *,
    include_excluded: bool = False,
) -> list[dict[str, str]]:
    """Return read-only corpus entries for source picker (IR-4: excluded omitted by default)."""
    q = query.strip().lower()
    entries = list(CORPUS_PICKER_SOURCES)
    if not include_excluded:
        entries = [e for e in entries if e["status"] != "esclusa"]
    if not q:
        return entries
    return [
        e
        for e in entries
        if q in e["title"].lower()
        or q in e["author"].lower()
        or q in e.get("year", "")
    ]


def is_excluded_source_id(source_id: str) -> bool:
    return source_id in EXCLUDED_SOURCE_IDS
