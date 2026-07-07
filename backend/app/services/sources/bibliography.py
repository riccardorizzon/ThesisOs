"""Bibliography export (M7 P-BIBTEX-DB — DB-backed)."""

from __future__ import annotations

import re

from app.db.session_async import AsyncSessionLocal
from app.services.sources.repository import SourceRepository, SourceRow


def _surname(author: str) -> str:
    parts = author.strip().split()
    return re.sub(r"[^a-zA-Z]", "", parts[-1]) if parts else "Unknown"


def _bibtex_key(author: str, year: str, source_id: str) -> str:
    return f"{_surname(author)}{year}_{source_id.replace('-', '')}"


def _escape_bibtex(value: str) -> str:
    return value.replace("{", "\\{").replace("}", "\\}")


def _author_from_row(row: SourceRow) -> str:
    return (row.subtitle or "Unknown").strip()


def _year_str(row: SourceRow) -> str:
    return str(row.year) if row.year is not None else "n.d."


def _render_bibtex(project_id: str, rows: list[SourceRow]) -> str:
    approved = [r for r in rows if r.corpus_status == "approvata"]
    approved.sort(key=lambda r: (_author_from_row(r), _year_str(r)))

    lines = [f"% Bibliography export — project: {project_id}", ""]
    for row in approved:
        author = _author_from_row(row)
        year = _year_str(row)
        title = row.title or "Untitled"
        key = _bibtex_key(author, year, row.slug)
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


async def export_bibliography_bibtex(project_id: str) -> str:
    """Export approved DB sources as BibTeX (academic order by author)."""
    async with AsyncSessionLocal() as session:
        repo = SourceRepository()
        rows = await repo.list_for_project(session, project_id)
    return _render_bibtex(project_id, rows)
