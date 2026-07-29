"""Sources list service (PX3-EWO-002; M7 P-SOURCES-DB — DB-backed)."""

from __future__ import annotations

import re
import uuid

from app.db.session_async import AsyncSessionLocal
from app.schemas.knowledge import (
    ConfidenceLevel,
    KnowledgeState,
    RelatedConceptRef,
    SourceListItem,
    SourceListResponse,
)
from app.services.knowledge.repository import ConceptRepository
from app.services.sources.repository import (
    SourceNotDeletableError,
    SourceNotFoundError,
    SourceRepository,
)

__all__ = [
    "SourceNotDeletableError",
    "SourceNotFoundError",
    "SourcesService",
    "dedupe_sources_by_document",
]

_STATE_RANK: dict[str, int] = {
    "linked": 40,
    "validated": 30,
    "candidate": 20,
    "deprecated": 0,
}
_CORPUS_RANK: dict[str, int] = {
    "approvata": 40,
    "candidata": 20,
    "esclusa": 0,
    "archiviata": 10,
}
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _is_uuid_slug(slug: str) -> bool:
    if not _UUID_RE.match(slug):
        return False
    try:
        uuid.UUID(slug)
        return True
    except ValueError:
        return False


def _source_rank(item: SourceListItem) -> tuple[int, int, int, str]:
    """Higher is better — prefer catalog/linked over upload/candidate duplicates."""
    return (
        _STATE_RANK.get(item.knowledge_state, 10),
        _CORPUS_RANK.get(item.corpus_status or "", 10),
        0 if _is_uuid_slug(item.slug) else 1,
        item.slug,
    )


def dedupe_sources_by_document(items: list[SourceListItem]) -> list[SourceListItem]:
    """Keep one row per ``document_id`` (null document_ids are never collapsed)."""
    best: dict[str, SourceListItem] = {}
    passthrough: list[SourceListItem] = []
    for item in items:
        doc_id = item.document_id
        if not doc_id:
            passthrough.append(item)
            continue
        prev = best.get(doc_id)
        if prev is None or _source_rank(item) > _source_rank(prev):
            best[doc_id] = item
    merged = passthrough + list(best.values())
    merged.sort(key=lambda s: (s.title or "").lower())
    return merged


class SourcesService:
    def __init__(self) -> None:
        self._sources = SourceRepository()
        self._concepts = ConceptRepository()

    async def _related_concepts(
        self,
        session,
        project_id: str,
        source_id: str,
    ) -> list[RelatedConceptRef]:
        refs = await self._concepts.get_related_concepts_for_source(
            session, project_id, source_id
        )
        return [RelatedConceptRef(**ref) for ref in refs]

    def _matches_query(self, row, query: str) -> bool:
        if not query:
            return True
        haystack = " ".join(
            filter(
                None,
                [
                    row.title,
                    row.subtitle,
                    row.summary,
                    str(row.year) if row.year is not None else None,
                ],
            )
        ).lower()
        return query in haystack

    async def _to_list_item(
        self,
        session,
        project_id: str,
        row,
    ) -> SourceListItem:
        state = await self._sources.effective_state(session, project_id, row)
        linked = await self._sources.linked_counts(session, project_id, row.slug)
        related = await self._related_concepts(session, project_id, row.slug)
        summary = row.summary
        if not summary and row.year is not None:
            summary = f"{row.year} · Fonte bibliografica"
        return SourceListItem(
            id=row.slug,
            slug=row.slug,
            type="source",
            title=row.title,
            subtitle=row.subtitle,
            summary=summary,
            confidence=row.confidence,  # type: ignore[arg-type]
            knowledge_state=state,
            linked_counts=linked,
            created_by=row.created_by,  # type: ignore[arg-type]
            is_core=row.is_core,
            related_concepts=related,
            corpus_status=row.corpus_status,
            document_id=row.document_id,
            deletable=row.source_type == "upload" and row.document_id is not None,
        )

    async def list_sources(
        self,
        project_id: str,
        *,
        query: str = "",
        knowledge_state: KnowledgeState | None = None,
        confidence: ConfidenceLevel | None = None,
        include_deprecated: bool = False,
    ) -> SourceListResponse:
        q = query.strip().lower()
        items: list[SourceListItem] = []

        async with AsyncSessionLocal() as session:
            rows = await self._sources.list_for_project(session, project_id)
            for row in rows:
                item = await self._to_list_item(session, project_id, row)
                if not include_deprecated and item.knowledge_state == "deprecated":
                    continue
                if knowledge_state is not None and item.knowledge_state != knowledge_state:
                    continue
                if confidence is not None and item.confidence != confidence:
                    continue
                if not self._matches_query(row, q):
                    continue
                items.append(item)

        items = dedupe_sources_by_document(items)
        return SourceListResponse(sources=items, total=len(items))

    async def approved_citation_refs(self, project_id: str) -> list[dict]:
        async with AsyncSessionLocal() as session:
            return await self._sources.approved_citation_refs(
                session,
                project_id,
            )

    async def get_source(
        self,
        project_id: str,
        slug: str,
    ) -> SourceListItem:
        async with AsyncSessionLocal() as session:
            try:
                row = await self._sources.get_by_slug(session, project_id, slug)
            except SourceNotFoundError:
                raise SourceNotFoundError(slug) from None
            return await self._to_list_item(session, project_id, row)

    async def add_to_bibliography(
        self,
        project_id: str,
        slug: str,
    ) -> SourceListItem:
        async with AsyncSessionLocal() as session:
            try:
                row = await self._sources.approve_for_bibliography(
                    session,
                    project_id,
                    slug,
                )
                item = await self._to_list_item(session, project_id, row)
                await session.commit()
                return item
            except Exception:
                await session.rollback()
                raise

    async def delete_source(self, project_id: str, slug: str) -> None:
        document_id: str | None = None
        async with AsyncSessionLocal() as session:
            document_id = await self._sources.delete_upload_source(
                session, project_id, slug
            )
            await session.commit()

        if document_id is None:
            return

        from app.services.document import DocumentNotFoundError, DocumentService

        try:
            await DocumentService().delete(document_id)
        except DocumentNotFoundError:
            pass
