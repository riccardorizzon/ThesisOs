"""Read-only MB2 projection builder (PX3-EWO-005, SoR §9)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from app.schemas.projection import (
    GatesProjection,
    IntegrationProjection,
    JobProjection,
    Mb2ProjectionV1,
    QueueProjection,
    SupervisorProjection,
    WaveJobProjection,
    WaveProjection,
    WaveStatus,
)

_EWO_TO_JOB_STATUS: dict[str, WaveStatus] = {
    "implemented": "pass",
    "qualified": "pass",
    "complete": "pass",
    "approved": "ready",
    "in_progress": "running",
    "blocked": "waiting",
    "failed": "fail",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    return loaded if isinstance(loaded, dict) else {}


def _map_ewo_status(raw: str | None) -> WaveStatus:
    if raw is None:
        return "waiting"
    return _EWO_TO_JOB_STATUS.get(str(raw).lower(), "waiting")


def _wave_status(job_statuses: list[WaveStatus]) -> WaveStatus:
    if not job_statuses:
        return "waiting"
    if any(s == "fail" for s in job_statuses):
        return "fail"
    if any(s == "running" for s in job_statuses):
        return "running"
    if all(s == "pass" for s in job_statuses):
        return "pass"
    if any(s in ("ready", "running") for s in job_statuses):
        return "ready"
    return "waiting"


def _iter_workorders(program: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for key, value in program.items():
        if not (key == "workorder_backlog" or key.endswith("_workorder_backlog")):
            continue
        if not isinstance(value, list):
            continue
        for entry in value:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                entries.append(entry)
    return entries


def build_px3_projection(*, root: Path | None = None) -> Mb2ProjectionV1:
    """Deterministic rebuild from Program Graph + parallel program (SoR §9.2)."""
    base = root or repo_root()
    program_path = base / ".asep/programs/thesisos-product-v2.yaml"
    parallel_path = base / ".asep/programs/px3-parallel.yaml"

    program = _load_yaml(program_path)
    parallel = _load_yaml(parallel_path)

    ewo_status: dict[str, WaveStatus] = {}
    for entry in _iter_workorders(program):
        ewo_id = entry["id"]
        if ewo_id.startswith("PX3-"):
            ewo_status[ewo_id] = _map_ewo_status(entry.get("status"))

    waves: dict[str, WaveProjection] = {}
    for wave_id, wave_def in (parallel.get("waves") or {}).items():
        if not isinstance(wave_def, dict):
            continue
        workorders = wave_def.get("workorders") or []
        jobs: dict[str, WaveJobProjection] = {}
        statuses: list[WaveStatus] = []
        for ewo_id in workorders:
            if not isinstance(ewo_id, str):
                continue
            status = ewo_status.get(ewo_id, "waiting")
            jobs[ewo_id] = WaveJobProjection(status=status)
            statuses.append(status)
        waves[str(wave_id)] = WaveProjection(status=_wave_status(statuses), jobs=jobs)

    jobs = {
        ewo_id: JobProjection(status=status, ewo_id=ewo_id)
        for ewo_id, status in ewo_status.items()
    }

    post_px2 = program.get("post_px2") or {}
    supervisor_state = str(post_px2.get("supervisor_state", "WAIT"))

    pending = sum(1 for s in ewo_status.values() if s in ("waiting", "ready"))
    in_flight = sum(1 for s in ewo_status.values() if s == "running")
    failed = sum(1 for s in ewo_status.values() if s == "fail")

    coverage_status: str = "unknown"
    if any(s == "pass" for ewo_id, s in ewo_status.items() if ewo_id.startswith("PX3-EWO-00")):
        coverage_status = "pass"

    return Mb2ProjectionV1(
        program_id=str(program.get("id", "thesisos-product-v2")),
        derived_at=datetime.now(tz=UTC),
        supervisor=SupervisorProjection(state=supervisor_state),
        waves=waves,
        integrations={
            "PX3-INTEGRATION-A": IntegrationProjection(
                status=ewo_status.get("PX3-EWO-004", "pass")
            ),
        },
        jobs=jobs,
        queue=QueueProjection(pending=pending, in_flight=in_flight, failed=failed),
        gates=GatesProjection(ci="unknown", coverage=coverage_status),  # type: ignore[arg-type]
    )


def projection_snapshot_yaml(projection: Mb2ProjectionV1) -> str:
    payload = projection.model_dump(mode="json")
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
