"""Conformance projection API (PX3-EWO-005, SoR §9)."""

from fastapi import APIRouter

from app.services.conformance.projection import build_px3_projection

router = APIRouter()


@router.get("/projects/{project_id}/conformance/projection")
async def get_conformance_projection(project_id: str):
    """Read-only MB2 projection snapshot (INV-R-11 — not authoritative)."""
    del project_id
    projection = build_px3_projection()
    return projection.model_dump(mode="json")
