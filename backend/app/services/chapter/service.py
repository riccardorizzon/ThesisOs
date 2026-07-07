"""ChapterService — sole writer for chapters / chapter_versions (ADR-0032).

Mirrors the DocumentService pattern (ADR-0020): every mutation goes through this
class; API handlers, graph nodes, and agents call it and never touch the session
directly. Versioning is an append-only change stream (ADR-0033).

M6 scope: no outline tree ops (reorder/move), no ChapterCreated product event,
no retrieval/embeddings over chapters (all M8 / out of scope).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.schemas.chapter import (
    VALID_CHAPTER_STATUSES,
    ChapterContentUpdate,
    ChapterCreate,
    ChapterListFilters,
    ChapterMetadataUpdate,
    ChapterRecord,
    ChapterReorderRequest,
    ChapterVersionRecord,
)
from app.services.chapter.exceptions import (
    ChapterNotFoundError,
    ChapterWriteConflictError,
    InvalidChapterStatusError,
)


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
            return await self._list(s, filters)

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

    # ------------------------------------------------------------------
    # Internals (operate on an injected session)
    # ------------------------------------------------------------------

    async def _create(self, session: AsyncSession, data: ChapterCreate) -> ChapterRecord:
        status = data.status or "draft"
        if status not in VALID_CHAPTER_STATUSES:
            raise InvalidChapterStatusError(status)
        row = models.Chapter(
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
        stmt = select(models.Chapter)
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
        return [self._to_record(r) for r in rows]

    async def _update_content(
        self, session: AsyncSession, chapter_id: str, data: ChapterContentUpdate
    ) -> ChapterRecord:
        row = self._require_version(await session.get(models.Chapter, chapter_id), chapter_id, data.expected_version)
        row.content_md = data.content_md
        row.word_count = _word_count(data.content_md)
        row.version += 1
        row.updated_at = datetime.now(timezone.utc)
        await session.flush()
        self._append_change(session, row, change_kind="EDIT")
        await session.flush()
        return self._to_record(row)

    async def _update_metadata(
        self, session: AsyncSession, chapter_id: str, data: ChapterMetadataUpdate
    ) -> ChapterRecord:
        row = self._require_version(await session.get(models.Chapter, chapter_id), chapter_id, data.expected_version)
        status_change = False
        if data.status is not None:
            if data.status not in VALID_CHAPTER_STATUSES:
                raise InvalidChapterStatusError(data.status)
            status_change = data.status != row.status
            row.status = data.status
        if data.title is not None:
            row.title = data.title
        if data.summary is not None:
            row.summary = data.summary
        row.version += 1
        row.updated_at = datetime.now(timezone.utc)
        await session.flush()
        # A status transition is recorded as PROMOTE; other metadata edits as EDIT (ADR-0033 §3).
        self._append_change(session, row, change_kind="PROMOTE" if status_change else "EDIT")
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

    async def _reorder(
        self, session: AsyncSession, data: ChapterReorderRequest
    ) -> list[ChapterRecord]:
        rows = (await session.execute(select(models.Chapter))).scalars().all()
        by_id = {r.id: r for r in rows}
        missing = [cid for cid in data.ordered_ids if cid not in by_id]
        if missing:
            raise ChapterNotFoundError(missing[0])
        for index, chapter_id in enumerate(data.ordered_ids):
            row = by_id[chapter_id]
            row.order_index = index
            row.updated_at = datetime.now(timezone.utc)
        await session.flush()
        return await self._list(session, ChapterListFilters(limit=500))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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
