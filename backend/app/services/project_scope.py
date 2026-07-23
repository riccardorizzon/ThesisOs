"""Project scope resolution (ADR-0047 §4).

Single place where "which thesis?" is answered: explicit value wins, otherwise
the Default Thesis. Registry validation stays where it already lives
(`services/context/project.py`); this resolver is pure and dependency-free so
every layer can use it.
"""

from __future__ import annotations

from app.schemas.context import DEFAULT_PROJECT_ID


def resolve_project_id(explicit: str | None = None) -> str:
    """INV-MTW-1: absent/blank project ⇒ Default Thesis (thesis-agent)."""
    value = (explicit or "").strip()
    return value or DEFAULT_PROJECT_ID
