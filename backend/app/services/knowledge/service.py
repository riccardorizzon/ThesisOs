"""Knowledge Object service — read catalog + PX-4 persisted concepts."""

from __future__ import annotations

import logging

from app.db.session_async import AsyncSessionLocal
from app.schemas.knowledge import (
    ConceptCreate,
    ConceptDefinitionEnvelope,
    ConceptDetailEnvelope,
    ConceptHeaderEnvelope,
    ConceptUpdate,
    KnowledgeObjectEnvelope,
    KnowledgeObjectListResponse,
)
from app.services.knowledge.catalog import get_knowledge_object, list_knowledge_objects
from app.services.knowledge.repository import (
    ConceptNotFoundError,
    ConceptRepository,
)


logger = logging.getLogger("app.services.knowledge")


class KnowledgeObjectNotFoundError(LookupError):
    pass


class KnowledgeService:
    def __init__(self) -> None:
        self._concepts = ConceptRepository()

    def list_objects(
        self,
        *,
        project_id: str = "thesis-agent",
        object_type: str | None = None,
        include_deprecated: bool = False,
    ) -> KnowledgeObjectListResponse:
        typed = object_type if object_type in ("concept", "source") else None
        objects = list_knowledge_objects(
            object_type=typed,  # type: ignore[arg-type]
            include_deprecated=include_deprecated,
        )
        return KnowledgeObjectListResponse(objects=objects, total=len(objects))

    async def list_objects_async(
        self,
        *,
        project_id: str,
        object_type: str | None = None,
        include_deprecated: bool = False,
    ) -> KnowledgeObjectListResponse:
        typed = object_type if object_type in ("concept", "source") else None
        items: list[KnowledgeObjectEnvelope] = []

        if typed in (None, "concept"):
            items.extend(await self._load_db_concepts(project_id, include_deprecated))

        if typed in (None, "source"):
            for raw in list_knowledge_objects(object_type="source", include_deprecated=include_deprecated):
                items.append(raw)

        return KnowledgeObjectListResponse(objects=items, total=len(items))

    def get_object(self, slug: str) -> KnowledgeObjectEnvelope:
        obj = get_knowledge_object(slug)
        if obj is None:
            raise KnowledgeObjectNotFoundError(slug)
        return obj

    async def get_object_async(self, project_id: str, slug: str) -> KnowledgeObjectEnvelope:
        try:
            async with AsyncSessionLocal() as session:
                count = await self._concepts.count_for_project(session, project_id)
                if count > 0:
                    return await self._concepts.get_by_slug(session, project_id, slug)
        except ConceptNotFoundError:
            pass  # not in DB — expected, fall back to the static catalog
        except Exception:
            logger.exception(
                "DB concept lookup failed for %s/%s — falling back to catalog",
                project_id,
                slug,
            )
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

    async def get_concept_detail_async(self, project_id: str, slug: str) -> ConceptDetailEnvelope:
        try:
            async with AsyncSessionLocal() as session:
                if await self._concepts.count_for_project(session, project_id) > 0:
                    return await self._concepts.get_detail(session, project_id, slug)
        except ConceptNotFoundError:
            raise KnowledgeObjectNotFoundError(slug) from None
        except Exception:
            logger.exception(
                "DB concept detail failed for %s/%s — falling back to catalog",
                project_id,
                slug,
            )
        return self.get_concept_detail(slug)

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

    async def get_concept_header_async(self, project_id: str, slug: str) -> ConceptHeaderEnvelope:
        obj = await self.get_object_async(project_id, slug)
        if obj.type != "concept":
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

    async def get_concept_definition_async(self, project_id: str, slug: str) -> ConceptDefinitionEnvelope:
        obj = await self.get_object_async(project_id, slug)
        if obj.type != "concept":
            raise KnowledgeObjectNotFoundError(slug)
        detail = await self.get_concept_detail_async(project_id, slug)
        return ConceptDefinitionEnvelope(
            slug=obj.slug,
            definition=detail.definition,
            source_count=obj.linked_counts.sources,
        )

    async def create_concept(
        self,
        project_id: str,
        data: ConceptCreate,
        *,
        session=None,
    ) -> KnowledgeObjectEnvelope:
        if session is not None:
            return await self._concepts.create(session, project_id, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._concepts.create(s, project_id, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def update_concept(
        self,
        project_id: str,
        slug: str,
        data: ConceptUpdate,
        *,
        session=None,
    ) -> KnowledgeObjectEnvelope:
        if session is not None:
            return await self._concepts.update(session, project_id, slug, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._concepts.update(s, project_id, slug, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def delete_concept(self, project_id: str, slug: str, *, session=None) -> None:
        if session is not None:
            await self._concepts.delete(session, project_id, slug)
            return
        async with AsyncSessionLocal() as s:
            try:
                await self._concepts.delete(s, project_id, slug)
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    async def _load_db_concepts(
        self,
        project_id: str,
        include_deprecated: bool,
    ) -> list[KnowledgeObjectEnvelope]:
        try:
            async with AsyncSessionLocal() as session:
                return await self._concepts.list_concepts(
                    session, project_id, include_deprecated=include_deprecated
                )
        except Exception:
            return []
