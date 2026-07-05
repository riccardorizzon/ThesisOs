"""Knowledge Object read service (PX3-EWO-001)."""

from __future__ import annotations

from app.schemas.knowledge import (
    ConceptDefinitionEnvelope,
    ConceptDetailEnvelope,
    ConceptHeaderEnvelope,
    KnowledgeObjectEnvelope,
    KnowledgeObjectListResponse,
)
from app.services.knowledge.catalog import get_knowledge_object, list_knowledge_objects


class KnowledgeObjectNotFoundError(LookupError):
    pass


class KnowledgeService:
    def list_objects(
        self,
        *,
        object_type: str | None = None,
        include_deprecated: bool = False,
    ) -> KnowledgeObjectListResponse:
        typed = object_type if object_type in ("concept", "source") else None
        objects = list_knowledge_objects(
            object_type=typed,  # type: ignore[arg-type]
            include_deprecated=include_deprecated,
        )
        return KnowledgeObjectListResponse(objects=objects, total=len(objects))

    def get_object(self, slug: str) -> KnowledgeObjectEnvelope:
        obj = get_knowledge_object(slug)
        if obj is None:
            raise KnowledgeObjectNotFoundError(slug)
        return obj

    def get_concept_detail(self, slug: str) -> ConceptDetailEnvelope:
        obj = get_knowledge_object(slug)
        if obj is None or obj.type != "concept":
            raise KnowledgeObjectNotFoundError(slug)
        return ConceptDetailEnvelope(
            **obj.model_dump(),
            definition=obj.summary,
        )

    def get_concept_header(self, slug: str) -> ConceptHeaderEnvelope:
        obj = get_knowledge_object(slug)
        if obj is None or obj.type != "concept":
            raise KnowledgeObjectNotFoundError(slug)
        return ConceptHeaderEnvelope(
            id=obj.id,
            slug=obj.slug,
            title=obj.title,
            subtitle=obj.subtitle,
            confidence=obj.confidence,
            knowledge_state=obj.knowledge_state,
            is_core=obj.is_core,
        )

    def get_concept_definition(self, slug: str) -> ConceptDefinitionEnvelope:
        obj = get_knowledge_object(slug)
        if obj is None or obj.type != "concept":
            raise KnowledgeObjectNotFoundError(slug)
        return ConceptDefinitionEnvelope(
            slug=obj.slug,
            definition=obj.summary,
            source_count=obj.linked_counts.sources,
        )
