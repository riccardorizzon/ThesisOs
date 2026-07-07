"""Knowledge Graph builder (PX3-EWO-009; PX4-EWO-005 DB-backed)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import select

from app.db.session_async import AsyncSessionLocal
from app.models.knowledge import Concept, ConceptRelation, ConceptSourceLink
from app.graph.corpus_query import CORPUS_PICKER_SOURCES
from app.schemas.knowledge_graph import (
    CANVAS_DEFAULT_VISIBLE,
    CANVAS_HARD_LIMIT,
    CANVAS_SOFT_LIMIT,
    DEFAULT_VISIBLE_NODES,
    HARD_NODE_LIMIT,
    SOFT_NODE_LIMIT,
    GraphRelationType,
    KnowledgeGraphEdge,
    KnowledgeGraphLimits,
    KnowledgeGraphNode,
    KnowledgeGraphResponse,
)
from app.services.knowledge.catalog import CONCEPT_CATALOG, build_concept_envelope, build_source_envelope
from app.services.knowledge.repository import ConceptRepository


def _author_slug(author_name: str) -> str:
    normalized = author_name.lower().replace(" ", "-")
    allowed = "".join(ch for ch in normalized if ch.isalnum() or ch == "-")
    return f"author-{allowed.strip('-')}"


_CANVAS_DECISION_STUBS: tuple[dict[str, str], ...] = (
    {"id": "decision-aura-repro", "title": "Tensione aura/riproducibilità", "concept_slug": "aura"},
    {"id": "decision-stigmata-scope", "title": "Scope STIGMATA", "concept_slug": "stigmata"},
)

_CANVAS_CHAPTER_STUBS: tuple[dict[str, str], ...] = (
    {"id": "ch-1-intro", "title": "Cap. 1 — Introduzione", "concept_slug": "stigmata"},
    {"id": "ch-2-percezione", "title": "Cap. 2 — Percezione", "concept_slug": "percezione"},
)

_MAX_SATELLITES: dict[str, int] = {
    "source": 40,
    "author": 20,
    "decision": 15,
    "chapter": 10,
}


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
    canvas_profile: bool = False,
) -> KnowledgeGraphResponse:
    depth = max(0, min(depth, 4))
    hard_cap = CANVAS_HARD_LIMIT if canvas_profile else HARD_NODE_LIMIT
    soft_cap = CANVAS_SOFT_LIMIT if canvas_profile else SOFT_NODE_LIMIT
    max_nodes = max(1, min(max_nodes, hard_cap))
    total_in_scope = len(entries)

    selected = _select_nodes(
        entries=entries,
        edges=all_edges,
        focus_slug=focus_slug,
        depth=depth,
        max_nodes=max_nodes,
    )
    truncated = len(selected) < total_in_scope and len(selected) >= max_nodes
    force_list_view = force_list or len(selected) >= hard_cap
    show_banner = len(selected) > soft_cap

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
                kind="concept",
            )
        )

    if canvas_profile:
        satellite_nodes, satellite_edges = _enrich_canvas_satellites(
            concept_slugs=selected,
            concept_edges=visible_edges,
        )
        nodes.extend(satellite_nodes)
        visible_edges = [*visible_edges, *satellite_edges]
        show_banner = len(nodes) > soft_cap

    return KnowledgeGraphResponse(
        focus_slug=focus_slug,
        depth=depth,
        view_mode="list" if force_list_view else "graph",
        nodes=nodes,
        edges=visible_edges,
        limits=KnowledgeGraphLimits(
            default_visible=CANVAS_DEFAULT_VISIBLE if canvas_profile else DEFAULT_VISIBLE_NODES,
            soft_limit=soft_cap,
            hard_limit=hard_cap,
            visible_count=len(nodes),
            total_in_scope=total_in_scope,
            truncated=truncated,
            force_list_view=force_list_view,
            show_performance_banner=show_banner,
        ),
    )


def _source_entry_by_id(source_id: str) -> dict[str, str] | None:
    for raw in CORPUS_PICKER_SOURCES:
        if raw["id"] == source_id:
            return raw
    return None


def _enrich_canvas_satellites(
    *,
    concept_slugs: set[str],
    concept_edges: list[KnowledgeGraphEdge],
) -> tuple[list[KnowledgeGraphNode], list[KnowledgeGraphEdge]]:
    satellite_nodes: list[KnowledgeGraphNode] = []
    satellite_edges: list[KnowledgeGraphEdge] = []
    seen_slugs: set[str] = set()

    source_ids: set[str] = set()
    for concept_slug in concept_slugs:
        for source_id in _source_ids_for_concept_slug(concept_slug):
            source_ids.add(source_id)

    source_count = 0
    for source_id in sorted(source_ids):
        if source_count >= _MAX_SATELLITES["source"]:
            break
        raw = _source_entry_by_id(source_id)
        if raw is None:
            continue
        envelope = build_source_envelope(raw)
        if envelope.slug in seen_slugs:
            continue
        seen_slugs.add(envelope.slug)
        linked_concepts = [
            slug
            for slug in concept_slugs
            if source_id in _source_ids_for_concept_slug(slug)
        ]
        for concept_slug in linked_concepts:
            satellite_edges.append(
                KnowledgeGraphEdge(
                    source=concept_slug,
                    target=envelope.slug,
                    relation="related",
                    link_kind="concept_source",
                )
            )
        satellite_nodes.append(
            KnowledgeGraphNode(
                id=envelope.id,
                slug=envelope.slug,
                title=envelope.title,
                knowledge_state=envelope.knowledge_state,
                is_core=False,
                degree=len(linked_concepts),
                kind="source",
            )
        )
        source_count += 1

    author_to_sources: dict[str, list[str]] = defaultdict(list)
    for source_id in source_ids:
        raw = _source_entry_by_id(source_id)
        if raw is None or not raw.get("author"):
            continue
        author_slug = _author_slug(raw["author"])
        author_to_sources[author_slug].append(source_id)

    author_count = 0
    for author_slug in sorted(author_to_sources):
        if author_count >= _MAX_SATELLITES["author"]:
            break
        if author_slug in seen_slugs:
            continue
        source_id = author_to_sources[author_slug][0]
        raw = _source_entry_by_id(source_id)
        if raw is None:
            continue
        title = str(raw.get("author", author_slug))
        seen_slugs.add(author_slug)
        source_slugs = {node.slug for node in satellite_nodes if node.kind == "source"}
        for linked_source in author_to_sources[author_slug]:
            if linked_source not in source_slugs:
                continue
            satellite_edges.append(
                KnowledgeGraphEdge(
                    source=author_slug,
                    target=linked_source,
                    relation="related",
                    link_kind="author_source",
                )
            )
        satellite_nodes.append(
            KnowledgeGraphNode(
                id=author_slug,
                slug=author_slug,
                title=title,
                knowledge_state="linked",
                is_core=False,
                degree=len(author_to_sources[author_slug]),
                kind="author",
            )
        )
        author_count += 1

    decision_count = 0
    for stub in _CANVAS_DECISION_STUBS:
        if decision_count >= _MAX_SATELLITES["decision"]:
            break
        if stub["concept_slug"] not in concept_slugs or stub["id"] in seen_slugs:
            continue
        seen_slugs.add(stub["id"])
        satellite_edges.append(
            KnowledgeGraphEdge(
                source=stub["concept_slug"],
                target=stub["id"],
                relation="related",
                link_kind="concept_decision",
            )
        )
        satellite_nodes.append(
            KnowledgeGraphNode(
                id=stub["id"],
                slug=stub["id"],
                title=stub["title"],
                knowledge_state="validated",
                is_core=False,
                degree=1,
                kind="decision",
            )
        )
        decision_count += 1

    chapter_count = 0
    for stub in _CANVAS_CHAPTER_STUBS:
        if chapter_count >= _MAX_SATELLITES["chapter"]:
            break
        if stub["concept_slug"] not in concept_slugs or stub["id"] in seen_slugs:
            continue
        seen_slugs.add(stub["id"])
        satellite_edges.append(
            KnowledgeGraphEdge(
                source=stub["concept_slug"],
                target=stub["id"],
                relation="related",
                link_kind="concept_chapter",
            )
        )
        satellite_nodes.append(
            KnowledgeGraphNode(
                id=stub["id"],
                slug=stub["id"],
                title=stub["title"],
                knowledge_state="referenced",
                is_core=False,
                degree=1,
                kind="chapter",
            )
        )
        chapter_count += 1

    return satellite_nodes, satellite_edges


def _source_ids_for_concept_slug(concept_slug: str) -> tuple[str, ...]:
    for entry in CONCEPT_CATALOG:
        if entry["id"] == concept_slug:
            return tuple(str(x) for x in entry.get("related_source_ids", ()))
    return ()


def build_knowledge_graph(
    *,
    focus_slug: str | None = None,
    depth: int = 1,
    max_nodes: int | None = None,
    force_list: bool = False,
    canvas_profile: bool = False,
) -> KnowledgeGraphResponse:
    if max_nodes is None:
        max_nodes = CANVAS_DEFAULT_VISIBLE if canvas_profile else DEFAULT_VISIBLE_NODES
    entries = _catalog_entries()
    all_edges = _edges_from_source_map(_concept_source_map(entries))
    return _build_graph_response(
        entries=entries,
        all_edges=all_edges,
        focus_slug=focus_slug,
        depth=depth,
        max_nodes=max_nodes,
        force_list=force_list,
        canvas_profile=canvas_profile,
    )


async def build_knowledge_graph_for_project(
    project_id: str,
    *,
    focus_slug: str | None = None,
    depth: int = 1,
    max_nodes: int | None = None,
    force_list: bool = False,
    canvas_profile: bool = False,
) -> KnowledgeGraphResponse:
    if max_nodes is None:
        max_nodes = CANVAS_DEFAULT_VISIBLE if canvas_profile else DEFAULT_VISIBLE_NODES
    loaded = await _load_db_graph(project_id)
    if loaded is None:
        return build_knowledge_graph(
            focus_slug=focus_slug,
            depth=depth,
            max_nodes=max_nodes,
            force_list=force_list,
            canvas_profile=canvas_profile,
        )
    entries, all_edges = loaded
    return _build_graph_response(
        entries=entries,
        all_edges=all_edges,
        focus_slug=focus_slug,
        depth=depth,
        max_nodes=max_nodes,
        force_list=force_list,
        canvas_profile=canvas_profile,
    )
