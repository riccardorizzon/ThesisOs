"""Flatten ContextGraph to ContextPacket — presentation hint for UI only."""

from __future__ import annotations

from app.schemas.context import (
    CONTEXT_PACKET_VERSION,
    DEFAULT_TOKEN_BUDGET,
    ContextGraph,
    ContextPacket,
    ContextRequest,
)


def flatten_context_packet(request: ContextRequest, graph: ContextGraph) -> ContextPacket:
    """Map graph nodes to API packet. All nodes assembled; UI filters via presentation."""
    return ContextPacket(
        schema_version=CONTEXT_PACKET_VERSION,
        project_context=request.project,
        presentation=request.presentation,
        project=graph.workspace.project,
        entity=graph.workspace.entity,
        relevant_sources=list(graph.knowledge.sources),
        concepts=list(graph.knowledge.concepts),
        decisions=list(graph.decisions.binding),
        definitions=list(graph.knowledge.definitions),
        citations_available=list(graph.knowledge.citations),
        corpus_constraints=list(graph.constraints.corpus),
        writing_rules=list(graph.constraints.writing_rules),
        memory_proposals_pending=graph.session.memory_proposals_pending,
        recent_activity=list(graph.session.recent_activity),
        token_budget=DEFAULT_TOKEN_BUDGET,
    )
