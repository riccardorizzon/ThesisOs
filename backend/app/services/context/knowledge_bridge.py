"""Bridge Context Engine ↔ persisted Knowledge domain (PX4-EWO-009)."""

from __future__ import annotations

from app.db.session_async import AsyncSessionLocal
from app.graph.corpus_query import CORPUS_PICKER_SOURCES
from app.schemas.context import ConceptRef, DefinitionRef, KnowledgeNode, SourceRef
from app.services.knowledge.catalog import CONCEPT_CATALOG
from app.services.knowledge.dev_catalog import dev_catalog_enabled
from app.services.knowledge.repository import ConceptRepository

_MAX_CONCEPTS = 12
_MAX_DEFINITIONS = 6
_MAX_SOURCES = 10

_CORPUS_TITLE_BY_ID = {raw["id"]: raw["title"] for raw in CORPUS_PICKER_SOURCES}


def _catalog_knowledge_node() -> KnowledgeNode:
    concepts: list[ConceptRef] = []
    definitions: list[DefinitionRef] = []
    source_ids: set[str] = set()

    for entry in CONCEPT_CATALOG:
        slug = str(entry["id"])
        title = str(entry["title"])
        concepts.append(ConceptRef(id=slug, title=title, slug=slug))
        summary = str(entry.get("summary") or "")
        if entry.get("is_core") and summary:
            definitions.append(DefinitionRef(term=title, definition=summary))
        for sid in entry.get("related_source_ids", ()):
            source_ids.add(str(sid))

    sources = [
        SourceRef(id=sid, title=_CORPUS_TITLE_BY_ID.get(sid, sid), kind="source")
        for sid in sorted(source_ids)[:_MAX_SOURCES]
    ]
    return KnowledgeNode(
        concepts=concepts[:_MAX_CONCEPTS],
        definitions=definitions[:_MAX_DEFINITIONS],
        sources=sources,
    )


def _empty_knowledge_node() -> KnowledgeNode:
    return KnowledgeNode(concepts=[], definitions=[], sources=[])


async def assemble_knowledge_node(project_id: str) -> KnowledgeNode:
    """Load knowledge refs for ContextPacket — DB first, dev catalog when enabled."""
    try:
        async with AsyncSessionLocal() as session:
            repo = ConceptRepository()
            if await repo.count_for_project(session, project_id) == 0:
                if dev_catalog_enabled():
                    return _catalog_knowledge_node()
                return _empty_knowledge_node()

            envelopes = await repo.list_concepts(session, project_id)
            core_first = sorted(
                envelopes,
                key=lambda e: (0 if e.is_core else 1, e.title),
            )
            concepts = [
                ConceptRef(id=e.slug, title=e.title, slug=e.slug)
                for e in core_first[:_MAX_CONCEPTS]
            ]

            definitions: list[DefinitionRef] = []
            for env in core_first:
                if not env.is_core and env.knowledge_state not in ("validated", "linked"):
                    continue
                detail = await repo.get_detail(session, project_id, env.slug)
                text = detail.definition or detail.summary
                if text:
                    definitions.append(DefinitionRef(term=detail.title, definition=text))
                if len(definitions) >= _MAX_DEFINITIONS:
                    break

            source_slugs = await repo.get_source_slugs_for_concepts(
                session, project_id, limit=_MAX_SOURCES
            )
            sources = [
                SourceRef(
                    id=slug,
                    title=_CORPUS_TITLE_BY_ID.get(slug, slug),
                    kind="source",
                )
                for slug in source_slugs
            ]

            return KnowledgeNode(
                concepts=concepts,
                definitions=definitions,
                sources=sources,
            )
    except Exception:
        if dev_catalog_enabled():
            return _catalog_knowledge_node()
        return _empty_knowledge_node()
