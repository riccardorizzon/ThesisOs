"""Sources list service (PX3-EWO-002; PX4-EWO-008 Knowledge links)."""

from __future__ import annotations

from app.db.session_async import AsyncSessionLocal
from app.graph.corpus_query import CORPUS_PICKER_SOURCES
from app.schemas.knowledge import (
    ConfidenceLevel,
    KnowledgeState,
    RelatedConceptRef,
    SourceListItem,
    SourceListResponse,
)
from app.services.knowledge.catalog import (
    build_source_envelope,
    get_related_concepts_for_source,
)
from app.services.knowledge.repository import ConceptRepository


class SourceNotFoundError(LookupError):
    pass


class SourcesService:
    async def _related_concepts(
        self,
        project_id: str,
        source_id: str,
    ) -> list[RelatedConceptRef]:
        try:
            async with AsyncSessionLocal() as session:
                repo = ConceptRepository()
                if await repo.count_for_project(session, project_id) > 0:
                    refs = await repo.get_related_concepts_for_source(
                        session, project_id, source_id
                    )
                    if refs:
                        return [RelatedConceptRef(**ref) for ref in refs]
        except Exception:
            pass
        return [
            RelatedConceptRef(**ref)
            for ref in get_related_concepts_for_source(source_id)
        ]

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

        for raw in CORPUS_PICKER_SOURCES:
            envelope = build_source_envelope(raw)
            if not include_deprecated and envelope.knowledge_state == "deprecated":
                continue
            if knowledge_state is not None and envelope.knowledge_state != knowledge_state:
                continue
            if confidence is not None and envelope.confidence != confidence:
                continue

            if q:
                haystack = " ".join(
                    filter(
                        None,
                        [
                            envelope.title,
                            envelope.subtitle,
                            envelope.summary,
                            raw.get("author"),
                            raw.get("year"),
                        ],
                    )
                ).lower()
                if q not in haystack:
                    continue

            related = await self._related_concepts(project_id, raw["id"])
            items.append(
                SourceListItem(
                    **envelope.model_dump(),
                    related_concepts=related,
                    corpus_status=raw.get("status"),
                )
            )

        return SourceListResponse(sources=items, total=len(items))

    async def get_source(
        self,
        project_id: str,
        slug: str,
    ) -> SourceListItem:
        raw = next((entry for entry in CORPUS_PICKER_SOURCES if entry["id"] == slug), None)
        if raw is None:
            raise SourceNotFoundError(slug)
        envelope = build_source_envelope(raw)
        related = await self._related_concepts(project_id, slug)
        return SourceListItem(
            **envelope.model_dump(),
            related_concepts=related,
            corpus_status=raw.get("status"),
        )
