"""PX6-EWO-002 citation validation tests."""

import pytest

from app.services.citation.validation import (
    has_blocking_citation_issues,
    suggest_author_date,
    validate_citations,
)

SOURCES = [
    {"author": "Josef Albers", "year": "1963"},
    {"author": "Walter Benjamin", "year": "1936"},
    {"author": "Barney Glaser e Anselm Strauss", "year": "1967"},
]


def test_flags_numeric_cite():
    issues = validate_citations("Teoria cromatica [2] secondo Albers.", SOURCES)
    assert len(issues) == 1
    assert issues[0].code == "invalid_numeric"
    assert issues[0].matched == "[2]"


def test_author_date_not_flagged():
    issues = validate_citations("Secondo Albers (Albers, 1963) il colore …", SOURCES)
    assert issues == []


def test_suggests_author_date_from_index():
    suggestion = suggest_author_date(SOURCES, 2)
    assert suggestion == "(Benjamin, 1936)"


def test_blocking_when_numeric_present():
    assert has_blocking_citation_issues("Riferimento [1] nel testo.", SOURCES)


def test_not_blocking_when_clean():
    assert not has_blocking_citation_issues("Secondo (Albers, 1963).", SOURCES)


@pytest.mark.parametrize(
    "text",
    [
        "L’aura cambia (Benjamin, 1936).",
        "Benjamin (1936) descrive l’aura.",
        "Il metodo è iterativo (Glaser & Strauss, 1967).",
        "Il metodo è iterativo (Glaser e Strauss, 1967).",
    ],
)
def test_linked_author_date_citations_are_not_flagged(text):
    assert validate_citations(text, SOURCES) == []


def test_unlinked_author_date_is_blocking():
    text = "Una tesi inesistente (FantomaAutore, 2050)."

    issues = validate_citations(text, SOURCES)

    assert len(issues) == 1
    assert issues[0].code == "unlinked_author_date"
    assert issues[0].matched == "(FantomaAutore, 2050)"
    assert has_blocking_citation_issues(text, SOURCES)


def test_explicit_empty_source_list_marks_author_date_unlinked():
    issues = validate_citations("(Benjamin, 1936)", [])
    assert [issue.code for issue in issues] == ["unlinked_author_date"]


def test_omitted_sources_keeps_local_format_only_mode():
    assert validate_citations("(FantomaAutore, 2050)", None) == []
