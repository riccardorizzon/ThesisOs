"""Deterministic citation format validation (PX6-EWO-002).

Product-layer W-06 mitigation — does not re-prove OR-6 oracle.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_AUTHOR_DATE_RE = re.compile(r"\([A-Za-zÀ-ÿ][\w\-']+,\s*\d{4}\)")
_AUTHOR_DATE_ALT_RE = re.compile(r"[A-Za-zÀ-ÿ][\w\-']+\s*\(\s*\d{4}\s*\)")
_NUMERIC_CITE_RE = re.compile(r"\[\d+\]")
_LINKED_MARKER_RE = re.compile(r"\[@\w+\d*\]")

_ISSUE_MESSAGES = {
    "invalid_numeric": "Citazione numerica — preferire (Autore, Anno)",
    "needs_review": "Formato citazione da verificare",
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

    return issues


def has_blocking_citation_issues(text: str, sources: list[dict] | None = None) -> bool:
    """True when Applica should be blocked (PX6-EWO-004)."""
    return any(i.code == "invalid_numeric" for i in validate_citations(text, sources))


def count_invalid_numeric(text: str) -> int:
    return sum(1 for i in validate_citations(text) if i.code == "invalid_numeric")
