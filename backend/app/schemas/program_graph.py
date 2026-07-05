"""Program Graph observation schema (PX3-EWO-008, SoR §4.1–§4.2 boundary)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

NodeType = Literal["ewo", "integration"]
EdgeType = Literal["depends_on_wave", "merge_order"]


class ExecutionNodeObservation(BaseModel):
    """ExecutionNode trace — 1:1 Program Graph declaration (INV-R-01)."""

    node_id: str
    node_type: NodeType
    wave_id: str


class GraphEdgeObservation(BaseModel):
    source: str
    target: str
    edge_type: EdgeType
    wave_id: str | None = None


class WaveObservation(BaseModel):
    wave_id: str
    title: str
    depends_on_wave: str | None = None
    execute_in_parallel: bool = False
    merge_order: list[str] = Field(default_factory=list)
    workorders: list[str] = Field(default_factory=list)
    unblocks: str | None = None
    wave_type: str | None = None
    status: str | None = None
    sub_agents: dict[str, str] = Field(default_factory=dict)
    nodes: list[ExecutionNodeObservation] = Field(default_factory=list)


class ProgramGraphObservationV1(BaseModel):
    """Read-only Program Graph observation — structure only (INV-R-12: no ReadySet)."""

    schema_version: Literal[1] = 1
    program_id: str
    parent_program: str
    source: str
    waves: list[WaveObservation] = Field(default_factory=list)
    edges: list[GraphEdgeObservation] = Field(default_factory=list)
