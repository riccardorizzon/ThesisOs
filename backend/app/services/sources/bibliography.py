"""Bibliography export (PX6-EWO-005)."""

from __future__ import annotations

import re

from app.graph.corpus_query import CORPUS_PICKER_SOURCES


def _surname(author: str) -> str:
    parts = author.strip().split()
    return re.sub(r"[^a-zA-Z]", "", parts[-1]) if parts else "Unknown"


def _bibtex_key(author: str, year: str, source_id: str) -> str:
    return f"{_surname(author)}{year}_{source_id.replace('-', '')}"


def _escape_bibtex(value: str) -> str:
    return value.replace("{", "\\{").replace("}", "\\}")


def export_bibliography_bibtex(project_id: str) -> str:
    """Export approved sources as BibTeX (academic order by author)."""
    approved = [
        s
        for s in CORPUS_PICKER_SOURCES
        if s.get("status") == "approvata"
    ]
    approved.sort(key=lambda s: (s.get("author", ""), s.get("year", "")))

    lines = [f"% Bibliography export — project: {project_id}", ""]
    for src in approved:
        author = src.get("author", "Unknown")
        year = src.get("year", "n.d.")
        title = src.get("title", "Untitled")
        key = _bibtex_key(author, year, src["id"])
        lines.extend(
            [
                f"@book{{{key},",
                f"  author = {{{_escape_bibtex(author)}}},",
                f"  title = {{{_escape_bibtex(title)}}},",
                f"  year = {{{year}}},",
                "}",
                "",
            ]
        )
    return "\n".join(lines)
