"""ChapterService — sole writer for chapters / chapter_versions (ADR-0032).

Mirrors the DocumentService pattern (ADR-0020): every mutation goes through this
class; API handlers, graph nodes, and agents call it and never touch the session
directly. Versioning is an append-only change stream (ADR-0033).

M6 scope: no outline tree ops (reorder/move), no ChapterCreated product event,
no retrieval/embeddings over chapters (all M8 / out of scope).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.services.project_scope import resolve_project_id
from app.schemas.chapter import (
    VALID_CHAPTER_STATUSES,
    ChapterContentUpdate,
    ChapterCreate,
    ChapterListFilters,
    ChapterMetadataUpdate,
    ChapterRecord,
    ChapterReorderRequest,
    ChapterVersionRecord,
    CopyDemoStructureResponse,
)
from app.services.chapter.exceptions import (
    ChapterNotDeletableError,
    ChapterNotFoundError,
    ChapterWriteConflictError,
    InvalidDemoCopyTargetError,
    InvalidChapterStatusError,
)
from app.services.demo_seed import DEMO_CHAPTERS, DEMO_THESIS_ID, ensure_demo_seed


def _is_migration_seed(row: models.Chapter) -> bool:
    return (row.content_md or "").lstrip().startswith("<!-- migration_slug:")


def _chapter_is_deletable(row: models.Chapter) -> bool:
    """Demo rows and migration seeds cannot be deleted from the UI."""
    if resolve_project_id(getattr(row, "project_id", None)) == DEMO_THESIS_ID:
        return False
    if _is_migration_seed(row):
        return False
    return True


def _word_count(content_md: str | None) -> int:
    return len(content_md.split()) if content_md else 0


class ChapterService:
    """Single write/read service for the chapter (writing workspace) domain."""

    # ------------------------------------------------------------------
    # Public API — optional injected session for tests; else self-contained
    # ------------------------------------------------------------------

    async def create(
        self, data: ChapterCreate, *, session: AsyncSession | None = None
    ) -> ChapterRecord:
        if session is not None:
            return await self._create(session, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._create(s, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def get(self, chapter_id: str, *, session: AsyncSession | None = None) -> ChapterRecord:
        if session is not None:
            return await self._get(session, chapter_id)
        async with AsyncSessionLocal() as s:
            return await self._get(s, chapter_id)

    async def list(
        self, filters: ChapterListFilters | None = None, *, session: AsyncSession | None = None
    ) -> list[ChapterRecord]:
        filters = filters or ChapterListFilters()
        if session is not None:
            return await self._list(session, filters)
        async with AsyncSessionLocal() as s:
            records = await self._list(s, filters)
            await s.commit()
            return records

    async def update_content(
        self, chapter_id: str, data: ChapterContentUpdate, *, session: AsyncSession | None = None
    ) -> ChapterRecord:
        if session is not None:
            return await self._update_content(session, chapter_id, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._update_content(s, chapter_id, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def update_metadata(
        self, chapter_id: str, data: ChapterMetadataUpdate, *, session: AsyncSession | None = None
    ) -> ChapterRecord:
        if session is not None:
            return await self._update_metadata(session, chapter_id, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._update_metadata(s, chapter_id, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def list_versions(
        self, chapter_id: str, *, session: AsyncSession | None = None
    ) -> list[ChapterVersionRecord]:
        if session is not None:
            return await self._list_versions(session, chapter_id)
        async with AsyncSessionLocal() as s:
            return await self._list_versions(s, chapter_id)

    async def reorder(
        self, data: ChapterReorderRequest, *, session: AsyncSession | None = None
    ) -> list[ChapterRecord]:
        if session is not None:
            return await self._reorder(session, data)
        async with AsyncSessionLocal() as s:
            try:
                records = await self._reorder(s, data)
                await s.commit()
                return records
            except Exception:
                await s.rollback()
                raise

    async def copy_demo_structure(
        self, *, project_id: str | None = None, session: AsyncSession | None = None
    ) -> CopyDemoStructureResponse:
        if session is not None:
            return await self._copy_demo_structure(session, project_id=project_id)
        async with AsyncSessionLocal() as s:
            try:
                result = await self._copy_demo_structure(s, project_id=project_id)
                await s.commit()
                return result
            except Exception:
                await s.rollback()
                raise

    async def delete(self, chapter_id: str, *, session: AsyncSession | None = None) -> None:
        if session is not None:
            await self._delete(session, chapter_id)
            return
        async with AsyncSessionLocal() as s:
            try:
                await self._delete(s, chapter_id)
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    # ------------------------------------------------------------------
    # Internals (operate on an injected session)
    # ------------------------------------------------------------------

    async def _create(self, session: AsyncSession, data: ChapterCreate) -> ChapterRecord:
        status = data.status or "draft"
        if status not in VALID_CHAPTER_STATUSES:
            raise InvalidChapterStatusError(status)
        row = models.Chapter(
            project_id=resolve_project_id(data.project_id),
            parent_id=data.parent_id,
            order_index=data.order_index,
            title=data.title,
            status=status,
            content_md=data.content_md,
            summary=data.summary,
            word_count=_word_count(data.content_md),
            version=1,
        )
        session.add(row)
        await session.flush()
        self._append_change(session, row, change_kind="WRITE")
        await session.flush()
        return self._to_record(row)

    async def _get(self, session: AsyncSession, chapter_id: str) -> ChapterRecord:
        row = await session.get(models.Chapter, chapter_id)
        if row is None:
            raise ChapterNotFoundError(chapter_id)
        return self._to_record(row)

    async def _list(
        self, session: AsyncSession, filters: ChapterListFilters
    ) -> list[ChapterRecord]:
        project_id = resolve_project_id(filters.project_id)
        if project_id == DEMO_THESIS_ID:
            await ensure_demo_seed(session)
        stmt = select(models.Chapter).where(
            models.Chapter.project_id == project_id
        )
        if filters.parent_id is not None:
            stmt = stmt.where(models.Chapter.parent_id == filters.parent_id)
        if filters.q:
            # ILIKE on title ONLY — never content_md (ADR-0032 §5; not retrieval).
            stmt = stmt.where(models.Chapter.title.ilike(f"%{filters.q}%"))
        stmt = (
            stmt.order_by(models.Chapter.order_index, models.Chapter.created_at)
            .limit(filters.limit)
            .offset(filters.offset)
        )
        rows = (await session.execute(stmt)).scalars().all()
        scoped = self._apply_scope(rows, filters.scope)
        return [self._to_record(r) for r in scoped]

    async def _copy_demo_structure(
        self, session: AsyncSession, *, project_id: str | None = None
    ) -> CopyDemoStructureResponse:
        target_project = resolve_project_id(project_id)
        if target_project == DEMO_THESIS_ID:
            raise InvalidDemoCopyTargetError(target_project)

        await ensure_demo_seed(session)
        seed_ids = [seed.id for seed in DEMO_CHAPTERS]
        demo_rows = sorted(
            (
                (
                    await session.execute(
                        select(models.Chapter).where(
                            models.Chapter.project_id == DEMO_THESIS_ID,
                            models.Chapter.id.in_(seed_ids),
                        )
                    )
                )
                .scalars()
                .all()
            ),
            key=lambda r: (r.order_index, r.created_at),
        )
        owned_titles = {
            r.title.strip().casefold()
            for r in (
                (
                    await session.execute(
                        select(models.Chapter).where(
                            models.Chapter.project_id == target_project
                        )
                    )
                )
                .scalars()
                .all()
            )
        }
        created: list[ChapterRecord] = []
        skipped: list[str] = []
        for row in demo_rows:
            title_key = row.title.strip().casefold()
            if title_key in owned_titles:
                skipped.append(row.title)
                continue
            record = await self._create(
                session,
                ChapterCreate(
                    title=row.title,
                    project_id=target_project,
                    parent_id=None,
                    order_index=row.order_index,
                    status="draft",
                    content_md="",
                    summary=None,
                ),
            )
            created.append(record)
            owned_titles.add(title_key)
        return CopyDemoStructureResponse(created=created, skipped_titles=skipped)

    async def _update_content(
        self, session: AsyncSession, chapter_id: str, data: ChapterContentUpdate
    ) -> ChapterRecord:
        result = await session.execute(
            update(models.Chapter)
            .where(
                models.Chapter.id == chapter_id,
                models.Chapter.version == data.expected_version,
            )
            .values(
                content_md=data.content_md,
                word_count=_word_count(data.content_md),
                version=data.expected_version + 1,
                updated_at=datetime.now(timezone.utc),
            )
            .returning(models.Chapter)
        )
        row = result.scalar_one_or_none()
        if row is None:
            existing = await session.get(models.Chapter, chapter_id)
            if existing is None:
                raise ChapterNotFoundError(chapter_id)
            raise ChapterWriteConflictError(
                chapter_id,
                expected_version=data.expected_version,
                actual_version=existing.version,
            )
        self._append_change(session, row, change_kind="EDIT")
        await session.flush()
        return self._to_record(row)

    async def _update_metadata(
        self, session: AsyncSession, chapter_id: str, data: ChapterMetadataUpdate
    ) -> ChapterRecord:
        existing = await session.get(models.Chapter, chapter_id)
        if existing is None:
            raise ChapterNotFoundError(chapter_id)
        if existing.version != data.expected_version:
            raise ChapterWriteConflictError(
                chapter_id,
                expected_version=data.expected_version,
                actual_version=existing.version,
            )

        status_change = False
        values: dict = {
            "version": data.expected_version + 1,
            "updated_at": datetime.now(timezone.utc),
        }
        if data.status is not None:
            if data.status not in VALID_CHAPTER_STATUSES:
                raise InvalidChapterStatusError(data.status)
            status_change = data.status != existing.status
            values["status"] = data.status
        if data.title is not None:
            values["title"] = data.title
        if data.summary is not None:
            values["summary"] = data.summary

        result = await session.execute(
            update(models.Chapter)
            .where(
                models.Chapter.id == chapter_id,
                models.Chapter.version == data.expected_version,
            )
            .values(**values)
            .returning(models.Chapter)
        )
        row = result.scalar_one_or_none()
        if row is None:
            refreshed = await session.get(models.Chapter, chapter_id)
            assert refreshed is not None
            raise ChapterWriteConflictError(
                chapter_id,
                expected_version=data.expected_version,
                actual_version=refreshed.version,
            )
        self._append_change(
            session, row, change_kind="PROMOTE" if status_change else "EDIT"
        )
        await session.flush()
        return self._to_record(row)

    async def _list_versions(
        self, session: AsyncSession, chapter_id: str
    ) -> list[ChapterVersionRecord]:
        await self._get(session, chapter_id)  # 404 if missing
        rows = (
            (
                await session.execute(
                    select(models.ChapterVersion)
                    .where(models.ChapterVersion.chapter_id == chapter_id)
                    .order_by(models.ChapterVersion.version)
                )
            )
            .scalars()
            .all()
        )
        return [self._to_version_record(r) for r in rows]

    async def _delete(self, session: AsyncSession, chapter_id: str) -> None:
        row = await session.get(models.Chapter, chapter_id)
        if row is None:
            raise ChapterNotFoundError(chapter_id)
        if not _chapter_is_deletable(row):
            raise ChapterNotDeletableError(chapter_id)

        child = (
            await session.execute(
                select(models.Chapter.id)
                .where(models.Chapter.parent_id == chapter_id)
                .limit(1)
            )
        ).scalar_one_or_none()
        if child is not None:
            raise ChapterNotDeletableError(chapter_id)

        await session.execute(
            delete(models.Proposal).where(models.Proposal.chapter_id == chapter_id)
        )
        await session.execute(
            update(models.Citation)
            .where(models.Citation.chapter_id == chapter_id)
            .values(chapter_id=None)
        )
        await session.delete(row)
        await session.flush()

    async def _reorder(
        self, session: AsyncSession, data: ChapterReorderRequest
    ) -> list[ChapterRecord]:
        rows = (
            await session.execute(
                select(models.Chapter).where(models.Chapter.project_id == data.project_id)
            )
        ).scalars().all()
        by_id = {r.id: r for r in rows}
        missing = [cid for cid in data.ordered_ids if cid not in by_id]
        if missing:
            raise ChapterNotFoundError(missing[0])
        for index, chapter_id in enumerate(data.ordered_ids):
            row = by_id[chapter_id]
            row.order_index = index
            row.updated_at = datetime.now(timezone.utc)
        await session.flush()
        return await self._list(
            session, ChapterListFilters(project_id=data.project_id, limit=500)
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_scope(rows: list[models.Chapter], scope: str) -> list[models.Chapter]:
        # Rows are already isolated by project_id. Scope is retained for API
        # compatibility; provenance must never be inferred from user titles.
        return rows

    @staticmethod
    def _require_version(
        row: models.Chapter | None, chapter_id: str, expected_version: int
    ) -> models.Chapter:
        if row is None:
            raise ChapterNotFoundError(chapter_id)
        if row.version != expected_version:
            raise ChapterWriteConflictError(
                chapter_id, expected_version=expected_version, actual_version=row.version
            )
        return row

    @staticmethod
    def _append_change(session: AsyncSession, row: models.Chapter, *, change_kind: str) -> None:
        session.add(
            models.ChapterVersion(
                chapter_id=row.id,
                version=row.version,
                change_kind=change_kind,
                title=row.title,
                status=row.status,
                content_md=row.content_md,
                summary=row.summary,
                word_count=row.word_count,
            )
        )

    @staticmethod
    def _to_record(row: models.Chapter) -> ChapterRecord:
        return ChapterRecord(
            id=row.id,
            project_id=resolve_project_id(getattr(row, "project_id", None)),
            parent_id=row.parent_id,
            order_index=row.order_index,
            title=row.title,
            status=row.status,
            content_md=row.content_md,
            summary=row.summary,
            word_count=row.word_count,
            version=row.version,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deletable=_chapter_is_deletable(row),
        )

    @staticmethod
    def _to_version_record(row: models.ChapterVersion) -> ChapterVersionRecord:
        return ChapterVersionRecord(
            chapter_id=row.chapter_id,
            version=row.version,
            change_kind=row.change_kind,
            title=row.title,
            status=row.status,
            content_md=row.content_md,
            summary=row.summary,
            word_count=row.word_count,
            metadata=dict(row.metadata_ or {}),
            changed_at=row.changed_at,
        )
