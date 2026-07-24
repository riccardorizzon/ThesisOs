"""Deterministic citation format validation (PX6-EWO-002).

Product-layer W-06 mitigation — does not re-prove OR-6 oracle.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_PARENTHETICAL_AUTHOR_DATE_RE = re.compile(
    r"\((?P<authors>[A-ZÀ-ÖØ-Þ][^,()]{0,120}),\s*"
    r"(?P<year>(?:19|20)\d{2}|[ns]\.?\s*d\.?)\)"
)
_NARRATIVE_AUTHOR_DATE_RE = re.compile(
    r"(?P<authors>[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÿ'’\-]+"
    r"(?:\s+(?:&|e|and)\s+[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÿ'’\-]+)*)"
    r"\s*\(\s*(?P<year>(?:19|20)\d{2}|[ns]\.?\s*d\.?)\s*\)"
)
_NUMERIC_CITE_RE = re.compile(r"\[\d+\]")
_LINKED_MARKER_RE = re.compile(r"\[@\w+\d*\]")
_AUTHOR_CONNECTORS = {"e", "and", "et", "al"}

_ISSUE_MESSAGES = {
    "invalid_numeric": "Citazione numerica — preferire (Autore, Anno)",
    "needs_review": "Formato citazione da verificare",
    "unlinked_author_date": "Citazione non collegata alla bibliografia del progetto",
}


@dataclass(frozen=True)
class CitationIssue:
    start: int
    end: int
    code: str
    message: str
    suggestion: str | None = None
    matched: str = ""


def _surname_from_author(author: str) -> str:
    parts = author.strip().split()
    return parts[-1].strip("_,.") if parts else "Autore"


def suggest_author_date(sources: list[dict] | None, index: int | None = None) -> str | None:
    """Suggest author-date from source metadata (PX6-EWO-003)."""
    if not sources:
        return "(Autore, Anno)"
    if index is not None and 1 <= index <= len(sources):
        src = sources[index - 1]
    else:
        src = sources[0]
    author = src.get("author") or src.get("subtitle") or ""
    year = src.get("year") or src.get("meta", "")
    year_match = re.search(r"\b(19|20)\d{2}\b", str(year))
    yr = year_match.group(0) if year_match else "n.d."
    surname = _surname_from_author(str(author))
    return f"({surname}, {yr})"


def _normalized_tokens(value: str) -> set[str]:
    ascii_value = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    tokens = re.findall(r"[a-z0-9]+", ascii_value.casefold())
    return {
        token
        for token in tokens
        if token not in _AUTHOR_CONNECTORS and len(token) > 1
    }


def _normalized_year(value: str | int | None) -> str:
    match = re.search(r"\b(19|20)\d{2}\b", str(value or ""))
    return match.group(0) if match else "n.d."


def _is_linked_author_date(
    authors: str,
    year: str,
    sources: list[dict],
) -> bool:
    cited_tokens = _normalized_tokens(authors)
    cited_year = _normalized_year(year)
    if not cited_tokens:
        return False
    for source in sources:
        source_author = str(
            source.get("author") or source.get("subtitle") or ""
        )
        if _normalized_year(source.get("year")) != cited_year:
            continue
        if cited_tokens.issubset(_normalized_tokens(source_author)):
            return True
    return False


def _author_date_matches(text: str):
    matches = [
        *_PARENTHETICAL_AUTHOR_DATE_RE.finditer(text),
        *_NARRATIVE_AUTHOR_DATE_RE.finditer(text),
    ]
    return sorted(matches, key=lambda match: match.start())


def validate_citations(text: str, sources: list[dict] | None = None) -> list[CitationIssue]:
    """Scan text for citation format issues."""
    if not text.strip():
        return []

    issues: list[CitationIssue] = []
    seen_spans: set[tuple[int, int]] = set()

    for match in _NUMERIC_CITE_RE.finditer(text):
        span = (match.start(), match.end())
        if span in seen_spans:
            continue
        seen_spans.add(span)
        idx = int(match.group(0).strip("[]"))
        issues.append(
            CitationIssue(
                start=match.start(),
                end=match.end(),
                code="invalid_numeric",
                message=_ISSUE_MESSAGES["invalid_numeric"],
                suggestion=suggest_author_date(sources, idx),
                matched=match.group(0),
            )
        )

    for match in _LINKED_MARKER_RE.finditer(text):
        span = (match.start(), match.end())
        if span in seen_spans:
            continue
        seen_spans.add(span)
        # Linked markers from PX-2 cite flow are valid — no issue

    if sources is not None:
        for match in _author_date_matches(text):
            span = (match.start(), match.end())
            if span in seen_spans:
                continue
            seen_spans.add(span)
            if _is_linked_author_date(
                match.group("authors"),
                match.group("year"),
                sources,
            ):
                continue
            issues.append(
                CitationIssue(
                    start=match.start(),
                    end=match.end(),
                    code="unlinked_author_date",
                    message=_ISSUE_MESSAGES["unlinked_author_date"],
                    suggestion="Aggiungi o collega questa fonte alla bibliografia",
                    matched=match.group(0),
                )
            )

    return issues


def has_blocking_citation_issues(text: str, sources: list[dict] | None = None) -> bool:
    """True when Applica should be blocked (PX6-EWO-004)."""
    return any(
        issue.code in {"invalid_numeric", "unlinked_author_date"}
        for issue in validate_citations(text, sources)
    )


def count_invalid_numeric(text: str) -> int:
    return sum(1 for i in validate_citations(text) if i.code == "invalid_numeric")
