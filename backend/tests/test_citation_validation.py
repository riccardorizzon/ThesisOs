"""PX6-EWO-002 citation validation tests."""

from app.services.citation.validation import (
    has_blocking_citation_issues,
    suggest_author_date,
    validate_citations,
)

SOURCES = [
    {"author": "Josef Albers", "year": "1963"},
    {"author": "Walter Benjamin", "year": "1936"},
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
