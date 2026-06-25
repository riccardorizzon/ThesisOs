"""DocumentService — sole writer for documents/document_versions/chunks (ADR-0020).

Mirrors the MemoryService pattern (ADR-0015): every mutation goes through this
class; API handlers, jobs, and future agents call it and never touch the session
or storage directly. Orchestrates GCS/local storage + the parser boundary.

M3 scope only: no embeddings, retrieval, search, ranking, or graph integration.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.schemas.document import (
    VALID_SOURCE_TYPES,
    DocumentChunk,
    DocumentListFilters,
    DocumentRecord,
    DocumentUpdate,
    DocumentUploadMetadata,
    DocumentVersionRecord,
    infer_source_type,
)
from app.services.document.chunking import compute_chunk_hash, estimate_tokens
from app.services.document.exceptions import (
    DocumentNotFoundError,
    DocumentServiceError,
    DocumentWriteConflictError,
    UnsupportedFormatError,
)
from app.services.document.parsers import Parser, parse_document
from app.services.document.storage import StorageAdapter, build_storage_adapter, storage_key


class DocumentService:
    """Single write/read service for the document ingestion domain."""

    def __init__(self, storage: StorageAdapter | None = None):
        self._storage = storage or build_storage_adapter()

    # ------------------------------------------------------------------
    # Public API — optional injected session for tests; else self-contained
    # ------------------------------------------------------------------

    async def upload(
        self,
        *,
        filename: str,
        data: bytes,
        source_type: str | None = None,
        meta: DocumentUploadMetadata | None = None,
        session: AsyncSession | None = None,
    ) -> DocumentRecord:
        if session is not None:
            return await self._upload(session, filename, data, source_type, meta)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._upload(s, filename, data, source_type, meta)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def get(self, document_id: str, *, session: AsyncSession | None = None) -> DocumentRecord:
        if session is not None:
            return await self._get(session, document_id)
        async with AsyncSessionLocal() as s:
            return await self._get(s, document_id)

    async def list(
        self,
        filters: DocumentListFilters | None = None,
        *,
        session: AsyncSession | None = None,
    ) -> list[DocumentRecord]:
        filters = filters or DocumentListFilters()
        if session is not None:
            return await self._list(session, filters)
        async with AsyncSessionLocal() as s:
            return await self._list(s, filters)

    async def update(
        self,
        document_id: str,
        data: DocumentUpdate,
        *,
        session: AsyncSession | None = None,
    ) -> DocumentRecord:
        if session is not None:
            return await self._update(session, document_id, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._update(s, document_id, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def delete(self, document_id: str, *, session: AsyncSession | None = None) -> None:
        if session is not None:
            await self._delete(session, document_id)
            return
        async with AsyncSessionLocal() as s:
            try:
                await self._delete(s, document_id)
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    async def parse(
        self,
        document_id: str,
        *,
        primary: Parser | None = None,
        fallback: Parser | None = None,
        session: AsyncSession | None = None,
    ) -> DocumentRecord:
        if session is not None:
            return await self._parse(session, document_id, primary, fallback)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._parse(s, document_id, primary, fallback)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def reparse(
        self,
        document_id: str,
        *,
        primary: Parser | None = None,
        fallback: Parser | None = None,
        session: AsyncSession | None = None,
    ) -> DocumentRecord:
        """Public alias for parse after a user-triggered re-parse (spec §7.1)."""
        return await self.parse(
            document_id, primary=primary, fallback=fallback, session=session
        )

    async def list_chunks(
        self,
        document_id: str,
        *,
        session: AsyncSession | None = None,
    ) -> list[DocumentChunk]:
        if session is not None:
            return await self._list_chunks(session, document_id)
        async with AsyncSessionLocal() as s:
            return await self._list_chunks(s, document_id)

    async def list_versions(
        self,
        document_id: str,
        *,
        session: AsyncSession | None = None,
    ) -> list[DocumentVersionRecord]:
        if session is not None:
            return await self._list_versions(session, document_id)
        async with AsyncSessionLocal() as s:
            return await self._list_versions(s, document_id)

    # ------------------------------------------------------------------
    # Internal write path — the only place that mutates the domain tables
    # ------------------------------------------------------------------

    async def _upload(
        self,
        session: AsyncSession,
        filename: str,
        data: bytes,
        source_type: str | None,
        meta: DocumentUploadMetadata | None,
    ) -> DocumentRecord:
        resolved = (source_type or infer_source_type(filename) or "").lower()
        if resolved not in VALID_SOURCE_TYPES:
            raise UnsupportedFormatError(source_type or filename)
        meta = meta or DocumentUploadMetadata()
        now = datetime.now(timezone.utc)

        row = models.Document(
            title=meta.title or _title_from_filename(filename),
            author=meta.author,
            source_type=resolved,
            original_filename=filename,
            status="uploaded",
            language=meta.language,
            version=1,
            metadata_=meta.metadata,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        await session.flush()  # assign id

        row.gcs_uri = self._storage.put(storage_key(row.id, filename), data)
        await session.flush()
        await self._append_version_snapshot(session, row, change_reason="metadata")
        await session.flush()
        return self._to_record(row)

    async def _get(self, session: AsyncSession, document_id: str) -> DocumentRecord:
        row = await session.get(models.Document, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        return self._to_record(row)

    async def _list(
        self, session: AsyncSession, filters: DocumentListFilters
    ) -> list[DocumentRecord]:
        stmt = select(models.Document)
        if filters.source_type is not None:
            stmt = stmt.where(models.Document.source_type == filters.source_type)
        if filters.status is not None:
            stmt = stmt.where(models.Document.status == filters.status)
        if filters.q:
            # ILIKE on title/filename ONLY — never chunk content (ADR-0022, §13).
            pattern = f"%{filters.q}%"
            stmt = stmt.where(
                or_(
                    models.Document.title.ilike(pattern),
                    models.Document.original_filename.ilike(pattern),
                )
            )
        stmt = (
            stmt.order_by(models.Document.updated_at.desc())
            .limit(filters.limit)
            .offset(filters.offset)
        )
        rows = (await session.execute(stmt)).scalars().all()
        return [self._to_record(r) for r in rows]

    async def _update(
        self, session: AsyncSession, document_id: str, data: DocumentUpdate
    ) -> DocumentRecord:
        row = await session.get(models.Document, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        if row.version != data.expected_version:
            raise DocumentWriteConflictError(
                document_id,
                expected_version=data.expected_version,
                actual_version=row.version,
            )
        if data.title is not None:
            row.title = data.title
        if data.author is not None:
            row.author = data.author
        if data.language is not None:
            row.language = data.language
        if data.metadata is not None:
            row.metadata_ = data.metadata
        row.version += 1
        row.updated_at = datetime.now(timezone.utc)
        await session.flush()
        await self._append_version_snapshot(session, row, change_reason="metadata")
        await session.flush()
        return self._to_record(row)

    async def _delete(self, session: AsyncSession, document_id: str) -> None:
        row = await session.get(models.Document, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        await session.execute(delete(models.Chunk).where(models.Chunk.document_id == document_id))
        await session.execute(
            delete(models.DocumentVersion).where(
                models.DocumentVersion.document_id == document_id
            )
        )
        self._storage.delete(storage_key(document_id, row.original_filename))
        await session.delete(row)
        await session.flush()

    async def _parse(
        self,
        session: AsyncSession,
        document_id: str,
        primary: Parser | None,
        fallback: Parser | None,
    ) -> DocumentRecord:
        row = await session.get(models.Document, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)

        row.status = "processing"
        row.error_message = None
        await session.flush()

        try:
            data = self._storage.get(storage_key(row.id, row.original_filename))
            result = parse_document(row.source_type, data, primary=primary, fallback=fallback)
        except (DocumentServiceError, OSError) as exc:
            # Failed parse leaves ZERO chunks (spec §7.2, Critic Phase 2).
            await session.execute(
                delete(models.Chunk).where(models.Chunk.document_id == document_id)
            )
            row.status = "failed"
            row.error_message = str(exc)
            await session.flush()
            return self._to_record(row)

        await session.execute(delete(models.Chunk).where(models.Chunk.document_id == document_id))
        now = datetime.now(timezone.utc)
        chunk_rows: list[models.Chunk] = []
        index = 0
        for parsed in result.chunks:
            content = parsed.content
            if not content or not content.strip():
                continue  # never insert zero-length chunks (spec §5.1)
            chunk_rows.append(
                models.Chunk(
                    document_id=row.id,
                    chunk_index=index,
                    chunk_hash=compute_chunk_hash(row.id, index, content),
                    content=content,
                    token_count=estimate_tokens(content),
                    page_from=parsed.page_from,
                    page_to=parsed.page_to,
                    section_path=parsed.section_path,
                    metadata_=parsed.metadata or {},
                    created_at=now,
                )
            )
            index += 1

        if not chunk_rows:
            row.status = "failed"
            row.error_message = "parser produced no usable chunks"
            await session.flush()
            return self._to_record(row)

        session.add_all(chunk_rows)
        row.status = "parsed"
        row.version += 1
        row.parser = result.parser
        row.parsed_at = now
        row.chunk_count = len(chunk_rows)
        row.error_message = None
        if result.page_count is not None:
            row.page_count = result.page_count
        if result.author and not row.author:
            row.author = result.author
        if result.language and not row.language:
            row.language = result.language
        row.updated_at = now
        await session.flush()
        await self._append_version_snapshot(session, row, change_reason="parse")
        await session.flush()
        return self._to_record(row)

    async def _list_chunks(
        self, session: AsyncSession, document_id: str
    ) -> list[DocumentChunk]:
        await self._get(session, document_id)  # 404 if missing
        rows = (
            (
                await session.execute(
                    select(models.Chunk)
                    .where(models.Chunk.document_id == document_id)
                    .order_by(models.Chunk.chunk_index)
                )
            )
            .scalars()
            .all()
        )
        return [self._to_chunk(r) for r in rows]

    async def _list_versions(
        self, session: AsyncSession, document_id: str
    ) -> list[DocumentVersionRecord]:
        await self._get(session, document_id)  # 404 if missing
        rows = (
            (
                await session.execute(
                    select(models.DocumentVersion)
                    .where(models.DocumentVersion.document_id == document_id)
                    .order_by(models.DocumentVersion.version)
                )
            )
            .scalars()
            .all()
        )
        return [self._to_version_record(r) for r in rows]

    async def _append_version_snapshot(
        self, session: AsyncSession, row: models.Document, *, change_reason: str
    ) -> None:
        session.add(
            models.DocumentVersion(
                document_id=row.id,
                version=row.version,
                title=row.title,
                author=row.author,
                source_type=row.source_type,
                page_count=row.page_count,
                chunk_count=row.chunk_count,
                parser=row.parser,
                metadata_=dict(row.metadata_ or {}),
                change_reason=change_reason,
            )
        )

    # ------------------------------------------------------------------
    # Row → DTO mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_record(row: models.Document) -> DocumentRecord:
        return DocumentRecord(
            id=row.id,
            title=row.title,
            author=row.author,
            source_type=row.source_type,
            original_filename=row.original_filename,
            gcs_uri=row.gcs_uri,
            status=row.status,
            page_count=row.page_count,
            language=row.language,
            version=row.version,
            parser=row.parser,
            parsed_at=row.parsed_at,
            chunk_count=row.chunk_count,
            error_message=row.error_message,
            metadata=dict(row.metadata_ or {}),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_chunk(row: models.Chunk) -> DocumentChunk:
        return DocumentChunk(
            id=row.id,
            document_id=row.document_id,
            chunk_index=row.chunk_index,
            chunk_hash=row.chunk_hash,
            content=row.content,
            page_from=row.page_from,
            page_to=row.page_to,
            section_path=row.section_path,
            token_count=row.token_count,
            metadata=dict(row.metadata_ or {}),
            created_at=row.created_at,
        )

    @staticmethod
    def _to_version_record(row: models.DocumentVersion) -> DocumentVersionRecord:
        return DocumentVersionRecord(
            document_id=row.document_id,
            version=row.version,
            title=row.title,
            author=row.author,
            source_type=row.source_type,
            page_count=row.page_count,
            chunk_count=row.chunk_count,
            parser=row.parser,
            metadata=dict(row.metadata_ or {}),
            change_reason=row.change_reason,
            changed_at=row.changed_at,
        )


def _title_from_filename(filename: str | None) -> str:
    base = (filename or "Untitled").replace("\\", "/").split("/")[-1]
    if "." in base:
        base = base[: base.rfind(".")]
    return base or "Untitled"
