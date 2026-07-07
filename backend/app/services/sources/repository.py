"""Source persistence — DB read port for M7 sources API."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import Concept, ConceptSourceLink
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


class SourceNotFoundError(LookupError):
    pass


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
                       confidence, knowledge_state, is_core, created_by
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
                       confidence, knowledge_state, is_core, created_by
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
        )

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
