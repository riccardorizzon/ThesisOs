"""Project registry — durable thesis-workspace SoR (PX6-EWO-007, ADR-0047).

DB-backed: created theses survive restarts (INV-MTW-3). The two seed rows
(`thesis-agent`, `demo-thesis`) are self-healed on access so fresh databases and
truncating test fixtures always converge to the same baseline.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_async import AsyncSessionLocal

THESIS_AGENT_ID = "thesis-agent"
DEMO_THESIS_ID = "demo-thesis"
THESIS_AGENT_TITLE = "Prima dei dieci minuti. Il processo creativo nel fashion design"

_SEQUENTIAL_ID = re.compile(r"^thesis-(\d+)$")


class ProjectEntry(BaseModel):
    id: str
    display_name: str
    created_at: str
    kind: str = "owned"


class ProjectListResponse(BaseModel):
    items: list[ProjectEntry]


class ProjectCreateRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)


class ProjectUpdateRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)


def _entry(row) -> ProjectEntry:
    return ProjectEntry(
        id=row.id,
        display_name=row.display_name,
        created_at=row.created_at.isoformat() if hasattr(row.created_at, "isoformat") else str(row.created_at),
        kind=row.kind,
    )


async def _ensure_defaults(session: AsyncSession) -> None:
    await session.execute(
        text(
            """
            INSERT INTO projects (id, display_name, kind) VALUES
              (:tid, :ttitle, 'owned'),
              (:did, 'Progetto dimostrativo', 'demo')
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {"tid": THESIS_AGENT_ID, "ttitle": THESIS_AGENT_TITLE, "did": DEMO_THESIS_ID},
    )


async def _next_sequential_id(session: AsyncSession) -> str:
    result = await session.execute(text("SELECT id FROM projects"))
    highest = 1  # thesis-agent is conceptually thesis-001
    for (project_id,) in result:
        match = _SEQUENTIAL_ID.match(project_id)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"thesis-{highest + 1:03d}"


class ProjectRegistryService:
    async def list_projects(self) -> ProjectListResponse:
        async with AsyncSessionLocal() as session:
            await _ensure_defaults(session)
            result = await session.execute(
                text(
                    """
                    SELECT id, display_name, kind, created_at FROM projects
                    WHERE status = 'active'
                    ORDER BY created_at, id
                    """
                )
            )
            items = [_entry(row) for row in result]
            await session.commit()
        return ProjectListResponse(items=items)

    async def get(self, project_id: str) -> ProjectEntry | None:
        async with AsyncSessionLocal() as session:
            await _ensure_defaults(session)
            result = await session.execute(
                text(
                    "SELECT id, display_name, kind, created_at FROM projects WHERE id = :pid"
                ),
                {"pid": project_id},
            )
            row = result.one_or_none()
            await session.commit()
        return _entry(row) if row is not None else None

    async def has(self, project_id: str) -> bool:
        return await self.get(project_id) is not None

    async def create_project(self, body: ProjectCreateRequest) -> ProjectEntry:
        async with AsyncSessionLocal() as session:
            await _ensure_defaults(session)
            project_id = await _next_sequential_id(session)
            await session.execute(
                text(
                    """
                    INSERT INTO projects (id, display_name, kind)
                    VALUES (:pid, :name, 'owned')
                    """
                ),
                {"pid": project_id, "name": body.display_name.strip()},
            )
            result = await session.execute(
                text(
                    "SELECT id, display_name, kind, created_at FROM projects WHERE id = :pid"
                ),
                {"pid": project_id},
            )
            row = result.one()
            await session.commit()
        return _entry(row)

    async def rename(self, project_id: str, body: ProjectUpdateRequest) -> ProjectEntry | None:
        async with AsyncSessionLocal() as session:
            await _ensure_defaults(session)
            result = await session.execute(
                text(
                    """
                    UPDATE projects
                    SET display_name = :name, updated_at = now()
                    WHERE id = :pid
                    RETURNING id, display_name, kind, created_at
                    """
                ),
                {"pid": project_id, "name": body.display_name.strip()},
            )
            row = result.one_or_none()
            await session.commit()
        return _entry(row) if row is not None else None
