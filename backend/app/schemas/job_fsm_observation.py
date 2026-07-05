"""Job FSM observation DTOs (PX3-EWO-009, SoR §5)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.projection import WaveStatus

AggregateStatus = WaveStatus
JobFsmSubsetState = Literal[
    "CREATED",
    "READY",
    "CLAIMED",
    "RUNNING",
    "VALIDATING",
    "MERGED",
    "DONE",
    "FAILED",
    "DEBUGGING",
    "CANCELLED",
    "QUALIFYING",
    "QUALIFIED",
    "LOCKED",
]

PRODUCT_LIFECYCLE_STATES = (
    "candidate",
    "validated",
    "linked",
    "referenced",
    "deprecated",
)


class VocabularyMappingRow(BaseModel):
    domain: str
    vocabulary: str
    values: list[str]
    notes: str


class AggregateToJobFsmRow(BaseModel):
    aggregate_status: AggregateStatus
    job_fsm_subset: JobFsmSubsetState
    display_label: str


class ProjectionJobObservation(BaseModel):
    ewo_id: str
    aggregate_status: AggregateStatus
    job_fsm_subset: JobFsmSubsetState
    wave_id: str | None = None


class JobFsmObservationResponse(BaseModel):
    schema_version: Literal[1] = 1
    read_only: Literal[True] = True
    source: str = "conformance/projection"
    vocabulary_domains: list[VocabularyMappingRow] = Field(default_factory=list)
    aggregate_to_job_fsm: list[AggregateToJobFsmRow] = Field(default_factory=list)
    projection_jobs: list[ProjectionJobObservation] = Field(default_factory=list)
    inv_r_11_note: str = (
        "Projection is rebuildable and read-only — product never writes job state (INV-R-11)."
    )
