"""Project registry (PX6-EWO-007)."""

from __future__ import annotations

from datetime import datetime, timezone
import re
import uuid

from pydantic import BaseModel, Field


class ProjectEntry(BaseModel):
    id: str
    display_name: str
    created_at: str
    kind: str = "owned"


class ProjectListResponse(BaseModel):
    items: list[ProjectEntry]


class ProjectCreateRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower().strip())
    slug = slug.strip("-") or "project"
    return slug[:48]


_DEFAULT: list[ProjectEntry] = [
    ProjectEntry(
        id="thesis-agent",
        display_name="Demo (esempio)",
        created_at="2026-07-01T00:00:00Z",
        kind="demo",
    ),
    ProjectEntry(
        id="demo-thesis",
        display_name="Progetto dimostrativo",
        created_at="2026-07-07T00:00:00Z",
        kind="demo",
    ),
]

_registry: list[ProjectEntry] = list(_DEFAULT)


class ProjectRegistryService:
    def list_projects(self) -> ProjectListResponse:
        return ProjectListResponse(items=list(_registry))

    def create_project(self, body: ProjectCreateRequest) -> ProjectEntry:
        base = _slugify(body.display_name)
        project_id = base
        existing = {p.id for p in _registry}
        if project_id in existing:
            project_id = f"{base}-{uuid.uuid4().hex[:6]}"
        entry = ProjectEntry(
            id=project_id,
            display_name=body.display_name.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        _registry.append(entry)
        return entry
