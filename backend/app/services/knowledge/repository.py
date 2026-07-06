"""Concept persistence — sole DB write port for PX-4 domain (ADR-0037)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import Concept, ConceptSourceLink
from app.schemas.knowledge import (
    ConceptCreate,
    ConceptDetailEnvelope,
    ConceptUpdate,
    KnowledgeObjectEnvelope,
    LinkedCounts,
)
from app.services.knowledge.catalog import _concept_knowledge_state, build_concept_envelope


class ConceptNotFoundError(LookupError):
    pass


class ConceptSlugExistsError(ValueError):
    pass


def _row_to_envelope(concept: Concept, source_count: int) -> KnowledgeObjectEnvelope:
    state = concept.knowledge_state
    if state != "deprecated":
        state = _concept_knowledge_state(source_count)
    return KnowledgeObjectEnvelope(
        id=concept.slug,
        slug=concept.slug,
        type="concept",
        title=concept.title,
        subtitle=concept.subtitle,
        summary=concept.summary,
        confidence=concept.confidence,  # type: ignore[arg-type]
        knowledge_state=state,  # type: ignore[arg-type]
        linked_counts=LinkedCounts(sources=source_count),
        created_by=concept.created_by,  # type: ignore[arg-type]
        proposal_state=concept.proposal_state,  # type: ignore[arg-type]
        is_core=concept.is_core,
    )


async def _source_count(session: AsyncSession, concept_id: str) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(ConceptSourceLink)
        .where(ConceptSourceLink.concept_id == concept_id)
    )
    return int(result.scalar_one())


async def _sync_source_links(
    session: AsyncSession,
    concept: Concept,
    source_slugs: list[str],
) -> None:
    await session.execute(
        delete(ConceptSourceLink).where(ConceptSourceLink.concept_id == concept.id)
    )
    for slug in source_slugs:
        session.add(ConceptSourceLink(concept_id=concept.id, source_slug=slug))
    count = len(source_slugs)
    if concept.knowledge_state != "deprecated":
        concept.knowledge_state = _concept_knowledge_state(count)


class ConceptRepository:
    async def list_concepts(
        self,
        session: AsyncSession,
        project_id: str,
        *,
        include_deprecated: bool = False,
    ) -> list[KnowledgeObjectEnvelope]:
        result = await session.execute(
            select(Concept).where(Concept.project_id == project_id).order_by(Concept.title)
        )
        concepts = result.scalars().all()
        envelopes: list[KnowledgeObjectEnvelope] = []
        for concept in concepts:
            count = await _source_count(session, concept.id)
            envelope = _row_to_envelope(concept, count)
            if not include_deprecated and envelope.knowledge_state == "deprecated":
                continue
            envelopes.append(envelope)
        return envelopes

    async def get_by_slug(
        self,
        session: AsyncSession,
        project_id: str,
        slug: str,
    ) -> KnowledgeObjectEnvelope:
        concept = await self._fetch(session, project_id, slug)
        count = await _source_count(session, concept.id)
        return _row_to_envelope(concept, count)

    async def get_detail(
        self,
        session: AsyncSession,
        project_id: str,
        slug: str,
    ) -> ConceptDetailEnvelope:
        concept = await self._fetch(session, project_id, slug)
        count = await _source_count(session, concept.id)
        base = _row_to_envelope(concept, count)
        return ConceptDetailEnvelope(
            **base.model_dump(),
            definition=concept.definition or concept.summary,
        )

    async def create(
        self,
        session: AsyncSession,
        project_id: str,
        data: ConceptCreate,
    ) -> KnowledgeObjectEnvelope:
        existing = await session.execute(
            select(Concept.id).where(
                Concept.project_id == project_id,
                Concept.slug == data.slug,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ConceptSlugExistsError(data.slug)

        state = _concept_knowledge_state(len(data.source_slugs))
        concept = Concept(
            project_id=project_id,
            slug=data.slug,
            title=data.title,
            subtitle=data.subtitle,
            summary=data.summary,
            definition=data.definition or data.summary,
            confidence=data.confidence,
            knowledge_state=state,
            is_core=data.is_core,
            created_by=data.created_by,
        )
        session.add(concept)
        await session.flush()
        if data.source_slugs:
            await _sync_source_links(session, concept, data.source_slugs)
        count = len(data.source_slugs)
        return _row_to_envelope(concept, count)

    async def update(
        self,
        session: AsyncSession,
        project_id: str,
        slug: str,
        data: ConceptUpdate,
    ) -> KnowledgeObjectEnvelope:
        concept = await self._fetch(session, project_id, slug)
        if data.title is not None:
            concept.title = data.title
        if data.subtitle is not None:
            concept.subtitle = data.subtitle
        if data.summary is not None:
            concept.summary = data.summary
        if data.definition is not None:
            concept.definition = data.definition
        if data.confidence is not None:
            concept.confidence = data.confidence
        if data.knowledge_state is not None:
            concept.knowledge_state = data.knowledge_state
        if data.is_core is not None:
            concept.is_core = data.is_core
        if data.proposal_state is not None:
            concept.proposal_state = data.proposal_state
        if data.source_slugs is not None:
            await _sync_source_links(session, concept, data.source_slugs)
        concept.updated_at = datetime.now(timezone.utc)
        count = await _source_count(session, concept.id)
        return _row_to_envelope(concept, count)

    async def delete(
        self,
        session: AsyncSession,
        project_id: str,
        slug: str,
    ) -> None:
        concept = await self._fetch(session, project_id, slug)
        await session.delete(concept)

    async def get_related_concepts_for_source(
        self,
        session: AsyncSession,
        project_id: str,
        source_slug: str,
    ) -> list[dict[str, str]]:
        if await self.count_for_project(session, project_id) == 0:
            return []
        result = await session.execute(
            select(Concept)
            .join(ConceptSourceLink, ConceptSourceLink.concept_id == Concept.id)
            .where(
                Concept.project_id == project_id,
                ConceptSourceLink.source_slug == source_slug,
            )
            .order_by(Concept.title)
        )
        return [
            {"id": c.slug, "slug": c.slug, "title": c.title}
            for c in result.scalars().all()
        ]

    async def get_source_slugs_for_concepts(
        self,
        session: AsyncSession,
        project_id: str,
        *,
        limit: int = 20,
    ) -> list[str]:
        if await self.count_for_project(session, project_id) == 0:
            return []
        result = await session.execute(
            select(ConceptSourceLink.source_slug)
            .join(Concept, Concept.id == ConceptSourceLink.concept_id)
            .where(Concept.project_id == project_id)
            .distinct()
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_for_project(self, session: AsyncSession, project_id: str) -> int:
        result = await session.execute(
            select(func.count()).select_from(Concept).where(Concept.project_id == project_id)
        )
        return int(result.scalar_one())

    async def _fetch(self, session: AsyncSession, project_id: str, slug: str) -> Concept:
        result = await session.execute(
            select(Concept).where(Concept.project_id == project_id, Concept.slug == slug)
        )
        concept = result.scalar_one_or_none()
        if concept is None:
            raise ConceptNotFoundError(slug)
        return concept


def catalog_concept_envelope(entry: dict[str, object]) -> KnowledgeObjectEnvelope:
    """Bridge for catalog fallback when DB has no rows."""
    return build_concept_envelope(entry)
