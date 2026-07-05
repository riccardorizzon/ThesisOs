"""Conformance observability API (PX3-EWO-005 §9, PX3-EWO-008 §4.2)."""

from fastapi import APIRouter

from app.services.conformance.program_graph import build_program_graph_observation
from app.services.conformance.projection import build_px3_projection

router = APIRouter()


@router.get("/projects/{project_id}/conformance/projection")
async def get_conformance_projection(project_id: str):
    """Read-only MB2 projection snapshot (INV-R-11 — not authoritative)."""
    del project_id
    projection = build_px3_projection()
    return projection.model_dump(mode="json")


@router.get("/projects/{project_id}/conformance/program-graph")
async def get_conformance_program_graph(project_id: str):
    """Read-only Program Graph trace (INV-R-01 / INV-R-12 — no ReadySet)."""
    del project_id
    graph = build_program_graph_observation()
    return graph.model_dump(mode="json")
