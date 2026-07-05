"""Knowledge Graph builder (PX3-EWO-009, px3-knowledge-experience-v2 §10)."""

from __future__ import annotations

from collections import defaultdict

from app.schemas.knowledge_graph import (
    DEFAULT_VISIBLE_NODES,
    HARD_NODE_LIMIT,
    SOFT_NODE_LIMIT,
    KnowledgeGraphEdge,
    KnowledgeGraphLimits,
    KnowledgeGraphNode,
    KnowledgeGraphResponse,
)
from app.services.knowledge.catalog import CONCEPT_CATALOG, build_concept_envelope


def _concept_source_map() -> dict[str, tuple[str, ...]]:
    return {
        str(entry["id"]): tuple(str(x) for x in entry.get("related_source_ids", ()))
        for entry in CONCEPT_CATALOG
    }


def _build_all_edges() -> list[KnowledgeGraphEdge]:
    source_to_concepts: dict[str, list[str]] = defaultdict(list)
    for concept_id, sources in _concept_source_map().items():
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
    focus_slug: str | None,
    depth: int,
    max_nodes: int,
) -> set[str]:
    all_slugs = {str(entry["id"]) for entry in CONCEPT_CATALOG}
    edges = _build_all_edges()

    if focus_slug is None or focus_slug not in all_slugs:
        core = {str(entry["id"]) for entry in CONCEPT_CATALOG if entry.get("is_core")}
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
                0 if any(str(e["id"]) == slug and e.get("is_core") for e in CONCEPT_CATALOG) else 1,
                slug,
            ),
        )
        selected = set(ordered[:max_nodes])
    return selected


def build_knowledge_graph(
    *,
    focus_slug: str | None = None,
    depth: int = 1,
    max_nodes: int = DEFAULT_VISIBLE_NODES,
    force_list: bool = False,
) -> KnowledgeGraphResponse:
    depth = max(0, min(depth, 4))
    max_nodes = max(1, min(max_nodes, HARD_NODE_LIMIT))
    all_edges = _build_all_edges()
    total_in_scope = len(CONCEPT_CATALOG)

    selected = _select_nodes(focus_slug=focus_slug, depth=depth, max_nodes=max_nodes)
    truncated = len(selected) < total_in_scope and len(selected) >= max_nodes

    force_list_view = force_list or len(selected) >= HARD_NODE_LIMIT
    show_banner = len(selected) > SOFT_NODE_LIMIT

    visible_edges = [
        edge
        for edge in all_edges
        if edge.source in selected and edge.target in selected
    ]

    degree: dict[str, int] = defaultdict(int)
    for edge in visible_edges:
        degree[edge.source] += 1
        degree[edge.target] += 1

    nodes: list[KnowledgeGraphNode] = []
    for slug in sorted(selected):
        envelope = build_concept_envelope(
            next(entry for entry in CONCEPT_CATALOG if entry["id"] == slug)
        )
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
