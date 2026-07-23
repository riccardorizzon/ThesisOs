"""Source persistence — DB read/write port for M7 sources API."""

from __future__ import annotations

import json
from dataclasses import dataclass

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import Concept, ConceptSourceLink
from app.schemas.context import DEFAULT_PROJECT_ID
from app.schemas.knowledge import KnowledgeState, LinkedCounts

_STATUS_TO_STATE: dict[str, KnowledgeState] = {
    "candidata": "candidate",
    "approvata": "validated",
    "esclusa": "deprecated",
}


@dataclass(frozen=True)
class SourceRow:
    slug: str
    title: str
    subtitle: str | None
    summary: str | None
    year: int | None
    corpus_status: str
    confidence: str
    knowledge_state: str
    is_core: bool
    created_by: str
    source_type: str
    document_id: str | None


class SourceNotFoundError(LookupError):
    pass


class SourceNotDeletableError(PermissionError):
    pass


async def register_uploaded_document(
    session: AsyncSession,
    *,
    document_id: str,
    title: str,
    author: str | None,
    source_type: str,
    project_id: str = DEFAULT_PROJECT_ID,
) -> None:
    """Expose an uploaded document in the Sources corpus (slug = document id)."""
    existing = await session.execute(
        text(
            """
            SELECT 1 FROM sources
            WHERE project_id = :project_id AND slug = :slug
            """
        ),
        {"project_id": project_id, "slug": document_id},
    )
    if existing.one_or_none() is not None:
        return

    authors_json = json.dumps([{"literal": author}] if author else [])
    await session.execute(
        text(
            """
            INSERT INTO sources (
                project_id, slug, type, document_id, title, subtitle, summary,
                corpus_status, confidence, knowledge_state, is_core, created_by, authors
            ) VALUES (
                :project_id, :slug, 'upload', :document_id, :title, :subtitle, :summary,
                'candidata', 'non_valutata', 'candidate', false, 'importazione',
                CAST(:authors AS jsonb)
            )
            """
        ),
        {
            "project_id": project_id,
            "slug": document_id,
            "document_id": document_id,
            "title": title,
            "subtitle": author,
            "summary": f"Caricato · {source_type.upper()}",
            "authors": authors_json,
        },
    )


def _effective_knowledge_state(corpus_status: str, concept_count: int) -> KnowledgeState:
    base = _STATUS_TO_STATE.get(corpus_status, "candidate")
    if base == "deprecated":
        return "deprecated"
    if concept_count >= 2:
        return "linked"
    return base


async def _concept_count(session: AsyncSession, project_id: str, source_slug: str) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(ConceptSourceLink)
        .join(Concept, Concept.id == ConceptSourceLink.concept_id)
        .where(
            Concept.project_id == project_id,
            ConceptSourceLink.source_slug == source_slug,
        )
    )
    return int(result.scalar_one())


class SourceRepository:
    async def list_for_project(
        self,
        session: AsyncSession,
        project_id: str,
    ) -> list[SourceRow]:
        result = await session.execute(
            text(
                """
                SELECT slug, title, subtitle, summary, year, corpus_status,
                       confidence, knowledge_state, is_core, created_by,
                       type AS source_type, document_id::text AS document_id
                FROM sources
                WHERE project_id = :project_id
                ORDER BY title
                """
            ),
            {"project_id": project_id},
        )
        return [
            SourceRow(
                slug=row.slug,
                title=row.title,
                subtitle=row.subtitle,
                summary=row.summary,
                year=row.year,
                corpus_status=row.corpus_status,
                confidence=row.confidence,
                knowledge_state=row.knowledge_state,
                is_core=row.is_core,
                created_by=row.created_by,
                source_type=row.source_type,
                document_id=row.document_id,
            )
            for row in result
        ]

    async def get_by_slug(
        self,
        session: AsyncSession,
        project_id: str,
        slug: str,
    ) -> SourceRow:
        result = await session.execute(
            text(
                """
                SELECT slug, title, subtitle, summary, year, corpus_status,
                       confidence, knowledge_state, is_core, created_by,
                       type AS source_type, document_id::text AS document_id
                FROM sources
                WHERE project_id = :project_id AND slug = :slug
                """
            ),
            {"project_id": project_id, "slug": slug},
        )
        row = result.one_or_none()
        if row is None:
            raise SourceNotFoundError(slug)
        return SourceRow(
            slug=row.slug,
            title=row.title,
            subtitle=row.subtitle,
            summary=row.summary,
            year=row.year,
            corpus_status=row.corpus_status,
            confidence=row.confidence,
            knowledge_state=row.knowledge_state,
            is_core=row.is_core,
            created_by=row.created_by,
            source_type=row.source_type,
            document_id=row.document_id,
        )

    async def delete_upload_source(
        self,
        session: AsyncSession,
        project_id: str,
        slug: str,
    ) -> str:
        """Remove an uploaded source row; returns linked document_id."""
        result = await session.execute(
            text(
                """
                DELETE FROM sources
                WHERE project_id = :project_id
                  AND slug = :slug
                  AND type = 'upload'
                  AND document_id IS NOT NULL
                RETURNING document_id::text AS document_id
                """
            ),
            {"project_id": project_id, "slug": slug},
        )
        row = result.one_or_none()
        if row is None:
            existing = await session.execute(
                text(
                    """
                    SELECT 1 FROM sources
                    WHERE project_id = :project_id AND slug = :slug
                    """
                ),
                {"project_id": project_id, "slug": slug},
            )
            if existing.one_or_none() is None:
                raise SourceNotFoundError(slug)
            raise SourceNotDeletableError(slug)
        return row.document_id

    async def linked_counts(
        self,
        session: AsyncSession,
        project_id: str,
        source_slug: str,
    ) -> LinkedCounts:
        count = await _concept_count(session, project_id, source_slug)
        return LinkedCounts(concepts=count)

    async def effective_state(
        self,
        session: AsyncSession,
        project_id: str,
        row: SourceRow,
    ) -> KnowledgeState:
        count = await _concept_count(session, project_id, row.slug)
        return _effective_knowledge_state(row.corpus_status, count)
