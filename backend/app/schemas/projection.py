"""MB2 Projection schema v1 (SoR §9)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

WaveStatus = Literal["waiting", "ready", "running", "pass", "fail", "locked"]
GateStatus = Literal["pass", "fail", "unknown"]


class WaveJobProjection(BaseModel):
    status: WaveStatus


class WaveProjection(BaseModel):
    status: WaveStatus
    jobs: dict[str, WaveJobProjection] = Field(default_factory=dict)


class IntegrationProjection(BaseModel):
    status: WaveStatus


class JobProjection(BaseModel):
    status: WaveStatus
    ewo_id: str


class QueueProjection(BaseModel):
    pending: int = 0
    in_flight: int = 0
    failed: int = 0


class GatesProjection(BaseModel):
    ci: GateStatus = "unknown"
    coverage: GateStatus = "unknown"


class SupervisorProjection(BaseModel):
    state: str
    reason: str | None = None


class Mb2ProjectionV1(BaseModel):
    """Read-only observability projection — SoR §9.1; not authoritative (INV-R-11)."""

    schema_version: Literal[1] = 1
    program_id: str
    derived_at: datetime
    cycle_id: str | None = None
    supervisor: SupervisorProjection
    waves: dict[str, WaveProjection] = Field(default_factory=dict)
    integrations: dict[str, IntegrationProjection] = Field(default_factory=dict)
    jobs: dict[str, JobProjection] = Field(default_factory=dict)
    queue: QueueProjection = Field(default_factory=QueueProjection)
    qwo: dict[str, IntegrationProjection] = Field(default_factory=dict)
    gates: GatesProjection = Field(default_factory=GatesProjection)
