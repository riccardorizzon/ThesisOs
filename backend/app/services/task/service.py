"""TaskService — persist planner TaskRef rows and finalize task status (M5)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.schemas.graph_state import TaskRef

logger = logging.getLogger("app.services.task")


class TaskService:
    """Single write service for ``tasks`` rows triggered by orchestration."""

    async def upsert_from_task_ref(
        self,
        task_ref: TaskRef,
        *,
        owner_agent: str | None,
        plan_steps: list[str],
        project_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        if session is not None:
            await self._upsert(
                session,
                task_ref,
                owner_agent=owner_agent,
                plan_steps=plan_steps,
                project_id=project_id,
            )
            return
        async with AsyncSessionLocal() as s:
            try:
                await self._upsert(
                    s,
                    task_ref,
                    owner_agent=owner_agent,
                    plan_steps=plan_steps,
                    project_id=project_id,
                )
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    async def mark_done(
        self,
        task_id: str,
        *,
        session: AsyncSession | None = None,
    ) -> None:
        if session is not None:
            await self._mark_done(session, task_id)
            return
        async with AsyncSessionLocal() as s:
            try:
                await self._mark_done(s, task_id)
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    async def _upsert(
        self,
        session: AsyncSession,
        task_ref: TaskRef,
        *,
        owner_agent: str | None,
        plan_steps: list[str],
        project_id: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        payload = {"plan_steps": list(plan_steps)}
        scoped_project = project_id or "thesis-agent"
        stmt = (
            insert(models.Task)
            .values(
                id=task_ref.id,
                project_id=scoped_project,
                title=task_ref.title,
                status="in_progress",
                owner_agent=owner_agent,
                payload=payload,
                updated_at=now,
            )
            .on_conflict_do_update(
                index_elements=[models.Task.id],
                set_={
                    "title": task_ref.title,
                    "status": "in_progress",
                    "owner_agent": owner_agent,
                    "payload": payload,
                    "updated_at": now,
                },
            )
        )
        await session.execute(stmt)

    async def _mark_done(self, session: AsyncSession, task_id: str) -> None:
        row = await session.get(models.Task, task_id)
        if row is None:
            logger.warning("mark_done: task %s not found", task_id)
            return
        row.status = "done"
        row.updated_at = datetime.now(timezone.utc)
