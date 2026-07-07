"""Knowledge Graph DTOs (PX3-EWO-009, px3-knowledge-experience-v2 §10)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.knowledge import KnowledgeState

GraphRelationType = Literal["related", "supports", "extends", "contradicts"]
GraphViewMode = Literal["graph", "list"]
CanvasNodeKind = Literal["concept", "source", "author", "decision", "chapter"]
CanvasLinkKind = Literal[
    "concept_source",
    "concept_decision",
    "concept_chapter",
    "author_source",
]

DEFAULT_VISIBLE_NODES = 15
SOFT_NODE_LIMIT = 50
HARD_NODE_LIMIT = 100

CANVAS_DEFAULT_VISIBLE = 80
CANVAS_SOFT_LIMIT = 150
CANVAS_HARD_LIMIT = 300


class KnowledgeGraphNode(BaseModel):
    id: str
    slug: str
    title: str
    knowledge_state: KnowledgeState
    is_core: bool = False
    degree: int = 0
    kind: CanvasNodeKind = "concept"


class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relation: GraphRelationType = "related"
    link_kind: CanvasLinkKind | None = None


class KnowledgeGraphLimits(BaseModel):
    default_visible: int = DEFAULT_VISIBLE_NODES
    soft_limit: int = SOFT_NODE_LIMIT
    hard_limit: int = HARD_NODE_LIMIT
    visible_count: int
    total_in_scope: int
    truncated: bool = False
    force_list_view: bool = False
    show_performance_banner: bool = False


class KnowledgeGraphResponse(BaseModel):
    schema_version: Literal[1] = 1
    focus_slug: str | None = None
    depth: int = 1
    view_mode: GraphViewMode = "graph"
    nodes: list[KnowledgeGraphNode] = Field(default_factory=list)
    edges: list[KnowledgeGraphEdge] = Field(default_factory=list)
    limits: KnowledgeGraphLimits
