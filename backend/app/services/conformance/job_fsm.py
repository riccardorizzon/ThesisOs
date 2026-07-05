"""Job FSM observation builder (PX3-EWO-009, SoR §5)."""

from __future__ import annotations

from app.schemas.job_fsm_observation import (
    AggregateToJobFsmRow,
    JobFsmObservationResponse,
    ProjectionJobObservation,
    VocabularyMappingRow,
)
from app.schemas.projection import WaveStatus
from app.services.conformance.projection import build_px3_projection

_AGGREGATE_TO_JOB_FSM: dict[WaveStatus, tuple[str, str]] = {
    "waiting": ("CREATED", "Pre-queue / blocked"),
    "ready": ("READY", "Eligible for claim"),
    "running": ("RUNNING", "Active execution"),
    "pass": ("DONE", "Terminal success (EWO complete)"),
    "fail": ("FAILED", "Terminal failure"),
    "locked": ("LOCKED", "Claim held — scheduler scope"),
}


def build_vocabulary_domains() -> list[VocabularyMappingRow]:
    return [
        VocabularyMappingRow(
            domain="product_lifecycle",
            vocabulary="PX-3 §4 Knowledge lifecycle",
            values=list(
                "candidate validated linked referenced deprecated".split()
            ),
            notes="Displayed on Knowledge Graph nodes — not MB2 Job FSM.",
        ),
        VocabularyMappingRow(
            domain="mb2_aggregate",
            vocabulary="SoR §5.3 projection aggregate roll-up",
            values=list(_AGGREGATE_TO_JOB_FSM.keys()),
            notes="Derived from Program Graph EWO status via §9 projection.",
        ),
        VocabularyMappingRow(
            domain="mb2_job_fsm",
            vocabulary="SoR §5.1 Job FSM (normative subset for display)",
            values=[
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
            ],
            notes="Transition legality is Runtime scope (ADR-0025) — PX-3 observes only.",
        ),
    ]


def build_aggregate_to_job_fsm_rows() -> list[AggregateToJobFsmRow]:
    return [
        AggregateToJobFsmRow(
            aggregate_status=aggregate,
            job_fsm_subset=subset,  # type: ignore[arg-type]
            display_label=label,
        )
        for aggregate, (subset, label) in _AGGREGATE_TO_JOB_FSM.items()
    ]


def _wave_for_job(projection_waves: dict, ewo_id: str) -> str | None:
    for wave_id, wave in projection_waves.items():
        if ewo_id in wave.jobs:
            return wave_id
    return None


def build_job_fsm_observation() -> JobFsmObservationResponse:
    projection = build_px3_projection()
    jobs: list[ProjectionJobObservation] = []
    for ewo_id, job in projection.jobs.items():
        subset, _ = _AGGREGATE_TO_JOB_FSM.get(job.status, ("CREATED", ""))
        jobs.append(
            ProjectionJobObservation(
                ewo_id=ewo_id,
                aggregate_status=job.status,
                job_fsm_subset=subset,  # type: ignore[arg-type]
                wave_id=_wave_for_job(projection.waves, ewo_id),
            )
        )
    jobs.sort(key=lambda row: row.ewo_id)

    return JobFsmObservationResponse(
        vocabulary_domains=build_vocabulary_domains(),
        aggregate_to_job_fsm=build_aggregate_to_job_fsm_rows(),
        projection_jobs=jobs,
    )
