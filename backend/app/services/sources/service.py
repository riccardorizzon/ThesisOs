"""Sources list service (PX3-EWO-002)."""

from __future__ import annotations

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


class SourcesService:
    def list_sources(
        self,
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

            related = [
                RelatedConceptRef(**ref)
                for ref in get_related_concepts_for_source(raw["id"])
            ]
            items.append(
                SourceListItem(
                    **envelope.model_dump(),
                    related_concepts=related,
                    corpus_status=raw.get("status"),
                )
            )

        return SourceListResponse(sources=items, total=len(items))
