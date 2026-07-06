"""Knowledge Graph builder (PX3-EWO-009; PX4-EWO-005 DB-backed)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import select

from app.db.session_async import AsyncSessionLocal
from app.models.knowledge import Concept, ConceptRelation, ConceptSourceLink
from app.schemas.knowledge_graph import (
    DEFAULT_VISIBLE_NODES,
    HARD_NODE_LIMIT,
    SOFT_NODE_LIMIT,
    GraphRelationType,
    KnowledgeGraphEdge,
    KnowledgeGraphLimits,
    KnowledgeGraphNode,
    KnowledgeGraphResponse,
)
from app.services.knowledge.catalog import CONCEPT_CATALOG, build_concept_envelope
from app.services.knowledge.repository import ConceptRepository


def _catalog_entries() -> list[dict[str, Any]]:
    return list(CONCEPT_CATALOG)


def _concept_source_map(entries: list[dict[str, Any]]) -> dict[str, tuple[str, ...]]:
    return {
        str(entry["id"]): tuple(str(x) for x in entry.get("related_source_ids", ()))
        for entry in entries
    }


def _edges_from_source_map(source_map: dict[str, tuple[str, ...]]) -> list[KnowledgeGraphEdge]:
    source_to_concepts: dict[str, list[str]] = defaultdict(list)
    for concept_id, sources in source_map.items():
        for source_id in sources:
            source_to_concepts[source_id].append(concept_id)
    seen: set[tuple[str, str]] = set()
    edges: list[KnowledgeGraphEdge] = []
    for concept_ids in source_to_concepts.values():
        if len(concept_ids) < 2:
            continue
        sorted_ids = sorted(concept_ids)
        for i, left in enumerate(sorted_ids):
            for right in sorted_ids[i + 1 :]:
                key = (left, right)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(KnowledgeGraphEdge(source=left, target=right, relation="related"))
    return edges


def _merge_edges(*groups: list[KnowledgeGraphEdge]) -> list[KnowledgeGraphEdge]:
    seen: set[tuple[str, str, str]] = set()
    merged: list[KnowledgeGraphEdge] = []
    for group in groups:
        for edge in group:
            key = (edge.source, edge.target, edge.relation)
            if key in seen:
                continue
            seen.add(key)
            merged.append(edge)
    return merged


async def _load_db_graph(project_id: str) -> tuple[list[dict[str, Any]], list[KnowledgeGraphEdge]] | None:
    try:
        async with AsyncSessionLocal() as session:
            repo = ConceptRepository()
            if await repo.count_for_project(session, project_id) == 0:
                return None
            concepts_result = await session.execute(
                select(Concept).where(Concept.project_id == project_id)
            )
            concepts = list(concepts_result.scalars().all())
            slug_by_id = {c.id: c.slug for c in concepts}

            source_map: dict[str, tuple[str, ...]] = {}
            for concept in concepts:
                link_result = await session.execute(
                    select(ConceptSourceLink.source_slug).where(
                        ConceptSourceLink.concept_id == concept.id
                    )
                )
                source_map[concept.slug] = tuple(link_result.scalars().all())

            rel_result = await session.execute(
                select(ConceptRelation).where(
                    ConceptRelation.from_concept_id.in_([c.id for c in concepts])
                )
            )
            typed: GraphRelationType
            db_edges: list[KnowledgeGraphEdge] = []
            for relation in rel_result.scalars().all():
                rel = relation.relation_type
                typed = rel if rel in ("related", "supports", "extends", "contradicts") else "related"  # type: ignore[assignment]
                db_edges.append(
                    KnowledgeGraphEdge(
                        source=slug_by_id[relation.from_concept_id],
                        target=slug_by_id[relation.to_concept_id],
                        relation=typed,
                    )
                )

            entries = [
                {
                    "id": c.slug,
                    "title": c.title,
                    "is_core": c.is_core,
                    "related_source_ids": source_map.get(c.slug, ()),
                }
                for c in concepts
            ]
            return entries, _merge_edges(_edges_from_source_map(source_map), db_edges)
    except Exception:
        return None


def _neighbors(slug: str, edges: list[KnowledgeGraphEdge]) -> set[str]:
    found: set[str] = {slug}
    for edge in edges:
        if edge.source == slug:
            found.add(edge.target)
        elif edge.target == slug:
            found.add(edge.source)
    return found


def _select_nodes(
    *,
    entries: list[dict[str, Any]],
    edges: list[KnowledgeGraphEdge],
    focus_slug: str | None,
    depth: int,
    max_nodes: int,
) -> set[str]:
    all_slugs = {str(entry["id"]) for entry in entries}

    if focus_slug is None or focus_slug not in all_slugs:
        core = {str(entry["id"]) for entry in entries if entry.get("is_core")}
        selected = set(core) if core else set(all_slugs)
    else:
        selected = {focus_slug}
        frontier = {focus_slug}
        for _ in range(max(0, depth)):
            next_frontier: set[str] = set()
            for slug in frontier:
                next_frontier |= _neighbors(slug, edges)
            selected |= next_frontier
            frontier = next_frontier - selected

    if len(selected) > max_nodes:
        ordered = sorted(
            selected,
            key=lambda slug: (
                0 if slug == focus_slug else 1,
                0 if any(str(e["id"]) == slug and e.get("is_core") for e in entries) else 1,
                slug,
            ),
        )
        selected = set(ordered[:max_nodes])
    return selected


def _build_graph_response(
    *,
    entries: list[dict[str, Any]],
    all_edges: list[KnowledgeGraphEdge],
    focus_slug: str | None,
    depth: int,
    max_nodes: int,
    force_list: bool,
) -> KnowledgeGraphResponse:
    depth = max(0, min(depth, 4))
    max_nodes = max(1, min(max_nodes, HARD_NODE_LIMIT))
    total_in_scope = len(entries)

    selected = _select_nodes(
        entries=entries,
        edges=all_edges,
        focus_slug=focus_slug,
        depth=depth,
        max_nodes=max_nodes,
    )
    truncated = len(selected) < total_in_scope and len(selected) >= max_nodes
    force_list_view = force_list or len(selected) >= HARD_NODE_LIMIT
    show_banner = len(selected) > SOFT_NODE_LIMIT

    visible_edges = [
        edge for edge in all_edges if edge.source in selected and edge.target in selected
    ]

    degree: dict[str, int] = defaultdict(int)
    for edge in visible_edges:
        degree[edge.source] += 1
        degree[edge.target] += 1

    entry_by_id = {str(entry["id"]): entry for entry in entries}
    nodes: list[KnowledgeGraphNode] = []
    for slug in sorted(selected):
        envelope = build_concept_envelope(entry_by_id[slug])
        nodes.append(
            KnowledgeGraphNode(
                id=envelope.id,
                slug=envelope.slug,
                title=envelope.title,
                knowledge_state=envelope.knowledge_state,
                is_core=envelope.is_core,
                degree=degree.get(slug, 0),
            )
        )

    return KnowledgeGraphResponse(
        focus_slug=focus_slug,
        depth=depth,
        view_mode="list" if force_list_view else "graph",
        nodes=nodes,
        edges=visible_edges,
        limits=KnowledgeGraphLimits(
            visible_count=len(nodes),
            total_in_scope=total_in_scope,
            truncated=truncated,
            force_list_view=force_list_view,
            show_performance_banner=show_banner,
        ),
    )


def build_knowledge_graph(
    *,
    focus_slug: str | None = None,
    depth: int = 1,
    max_nodes: int = DEFAULT_VISIBLE_NODES,
    force_list: bool = False,
) -> KnowledgeGraphResponse:
    entries = _catalog_entries()
    all_edges = _edges_from_source_map(_concept_source_map(entries))
    return _build_graph_response(
        entries=entries,
        all_edges=all_edges,
        focus_slug=focus_slug,
        depth=depth,
        max_nodes=max_nodes,
        force_list=force_list,
    )


async def build_knowledge_graph_for_project(
    project_id: str,
    *,
    focus_slug: str | None = None,
    depth: int = 1,
    max_nodes: int = DEFAULT_VISIBLE_NODES,
    force_list: bool = False,
) -> KnowledgeGraphResponse:
    loaded = await _load_db_graph(project_id)
    if loaded is None:
        return build_knowledge_graph(
            focus_slug=focus_slug,
            depth=depth,
            max_nodes=max_nodes,
            force_list=force_list,
        )
    entries, all_edges = loaded
    return _build_graph_response(
        entries=entries,
        all_edges=all_edges,
        focus_slug=focus_slug,
        depth=depth,
        max_nodes=max_nodes,
        force_list=force_list,
    )
