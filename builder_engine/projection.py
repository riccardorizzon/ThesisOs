"""State projection builder — read-only fold over event log (MB2 SoR §9)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from builder_engine.events import BuildEvent, BuildEventBus, DEFAULT_PROGRAM_ID, event_now
from builder_engine.state_io import atomic_write_text
from builder_engine.yaml_loader import load_simple_yaml

SCHEMA_VERSION = 1
WAVE_STATUSES = frozenset({"waiting", "ready", "running", "pass", "fail", "locked"})
GATE_STATUSES = frozenset({"pass", "fail", "unknown"})

EXECUTION_TO_PROJECTION: dict[str, str] = {
    "created": "waiting",
    "ready": "ready",
    "claimed": "running",
    "running": "running",
    "validating": "running",
    "merged": "running",
    "done": "pass",
    "failed": "fail",
    "debugging": "fail",
    "cancelled": "locked",
}


def default_projection_path(repo_root: Path) -> Path:
    return repo_root.resolve() / ".builder-engine" / "projection.yaml"


def _empty_document(*, program_id: str = DEFAULT_PROGRAM_ID) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "program_id": program_id,
        "derived_at": "",
        "cycle_id": None,
        "supervisor": {"state": "unknown", "reason": None},
        "waves": {},
        "integrations": {},
        "jobs": {},
        "queue": {"pending": 0, "in_flight": 0, "failed": 0},
        "qwo": {},
        "gates": {"ci": "unknown", "coverage": "unknown"},
    }


def _map_execution_state(state: str) -> str:
    mapped = EXECUTION_TO_PROJECTION.get(state, state)
    if mapped in WAVE_STATUSES:
        return mapped
    return "waiting"


def _rollup_wave_status(job_statuses: list[str]) -> str:
    if not job_statuses:
        return "waiting"
    if any(status == "fail" for status in job_statuses):
        return "fail"
    if any(status == "locked" for status in job_statuses):
        return "locked"
    if any(status == "running" for status in job_statuses):
        return "running"
    if all(status == "pass" for status in job_statuses):
        return "pass"
    if any(status == "ready" for status in job_statuses):
        return "ready"
    return "waiting"


def _recompute_queue(jobs: dict[str, dict[str, Any]]) -> dict[str, int]:
    pending = sum(1 for job in jobs.values() if job.get("status") == "ready")
    in_flight = sum(1 for job in jobs.values() if job.get("status") == "running")
    failed = sum(1 for job in jobs.values() if job.get("status") == "fail")
    return {"pending": pending, "in_flight": in_flight, "failed": failed}


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        if not value:
            return '""'
        if any(c in value for c in ':"[]{}#&*!|>%@`'):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return value
    return repr(value)


def _dump_yaml_value(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        if not value:
            return [f"{prefix}{{}}"]
        lines: list[str] = []
        for key, item in sorted(value.items()):
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(_dump_yaml_value(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{prefix}[]"]
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(_dump_yaml_value(item, indent + 2))
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
        return lines
    return [f"{prefix}{_yaml_scalar(value)}"]


def dump_projection(data: dict[str, Any]) -> str:
    lines: list[str] = []
    for key in (
        "schema_version",
        "program_id",
        "derived_at",
        "cycle_id",
        "supervisor",
        "waves",
        "integrations",
        "jobs",
        "queue",
        "qwo",
        "gates",
    ):
        value = data.get(key)
        if isinstance(value, (dict, list)):
            lines.append(f"{key}:")
            lines.extend(_dump_yaml_value(value, 2))
        else:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    return "\n".join(lines).rstrip() + "\n"


@dataclass
class ProjectionDocument:
    schema_version: int = SCHEMA_VERSION
    program_id: str = DEFAULT_PROGRAM_ID
    derived_at: str = ""
    cycle_id: str | None = None
    supervisor: dict[str, Any] = field(default_factory=lambda: {"state": "unknown", "reason": None})
    waves: dict[str, Any] = field(default_factory=dict)
    integrations: dict[str, Any] = field(default_factory=dict)
    jobs: dict[str, Any] = field(default_factory=dict)
    queue: dict[str, int] = field(default_factory=lambda: {"pending": 0, "in_flight": 0, "failed": 0})
    qwo: dict[str, Any] = field(default_factory=dict)
    gates: dict[str, str] = field(default_factory=lambda: {"ci": "unknown", "coverage": "unknown"})

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "program_id": self.program_id,
            "derived_at": self.derived_at,
            "cycle_id": self.cycle_id,
            "supervisor": dict(self.supervisor),
            "waves": {wave_id: dict(wave) for wave_id, wave in self.waves.items()},
            "integrations": {key: dict(value) for key, value in self.integrations.items()},
            "jobs": {job_id: dict(job) for job_id, job in self.jobs.items()},
            "queue": dict(self.queue),
            "qwo": {key: dict(value) for key, value in self.qwo.items()},
            "gates": dict(self.gates),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectionDocument:
        queue = data.get("queue") or {}
        gates = data.get("gates") or {}
        return cls(
            schema_version=int(data.get("schema_version") or SCHEMA_VERSION),
            program_id=str(data.get("program_id") or DEFAULT_PROGRAM_ID),
            derived_at=str(data.get("derived_at") or ""),
            cycle_id=data.get("cycle_id"),
            supervisor=dict(data.get("supervisor") or {"state": "unknown", "reason": None}),
            waves={str(k): dict(v) for k, v in (data.get("waves") or {}).items()},
            integrations={str(k): dict(v) for k, v in (data.get("integrations") or {}).items()},
            jobs={str(k): dict(v) for k, v in (data.get("jobs") or {}).items()},
            queue={
                "pending": int(queue.get("pending") or 0),
                "in_flight": int(queue.get("in_flight") or 0),
                "failed": int(queue.get("failed") or 0),
            },
            qwo={str(k): dict(v) for k, v in (data.get("qwo") or {}).items()},
            gates={
                "ci": str(gates.get("ci") or "unknown"),
                "coverage": str(gates.get("coverage") or "unknown"),
            },
        )

    def to_yaml(self) -> str:
        return dump_projection(self.to_dict())


@dataclass
class ProjectionBuilder:
    """Deterministic fold over BuildEvent stream — observability only (INV-R-11, INV-R-12)."""

    repo_root: Path | None = None
    bus: BuildEventBus | None = None
    _data: dict[str, Any] = field(default_factory=_empty_document, init=False)
    graph_hash: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.repo_root is not None:
            self.repo_root = self.repo_root.resolve()

    @property
    def document(self) -> ProjectionDocument:
        return ProjectionDocument.from_dict(self._data)

    def apply(self, event: BuildEvent) -> None:
        if event.type == "ProjectionUpdated":
            return

        if event.program_id:
            self._data["program_id"] = event.program_id
        if event.cycle_id is not None:
            self._data["cycle_id"] = event.cycle_id
        if event.timestamp:
            self._data["derived_at"] = event.timestamp

        handler = _EVENT_HANDLERS.get(event.type)
        if handler is not None:
            handler(self, event)
        self._data["queue"] = _recompute_queue(self._data["jobs"])

    def rebuild(self, events: list[BuildEvent]) -> ProjectionDocument:
        self._data = _empty_document()
        self.graph_hash = None
        for event in events:
            self.apply(event)
        doc = self.document
        if self.repo_root is not None:
            write_projection(default_projection_path(self.repo_root), doc)
        if self.bus is not None:
            path = (
                str(default_projection_path(self.repo_root))
                if self.repo_root is not None
                else ".builder-engine/projection.yaml"
            )
            self.bus.publish(
                event_now(
                    "ProjectionUpdated",
                    {
                        "path": path,
                        "content_hash": self.content_hash(),
                        "program_id": doc.program_id,
                    },
                    program_id=doc.program_id,
                    cycle_id=doc.cycle_id,
                )
            )
        return doc

    def content_hash(self) -> str:
        payload = self.document.to_dict()
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


def write_projection(path: Path, document: ProjectionDocument) -> None:
    atomic_write_text(path, document.to_yaml())


def read_projection(path: Path) -> ProjectionDocument:
    data = load_simple_yaml(path.read_text(encoding="utf-8"))
    return ProjectionDocument.from_dict(data)


def load_projection(repo_root: Path) -> ProjectionDocument | None:
    path = default_projection_path(repo_root)
    if not path.is_file():
        return None
    return read_projection(path)


def _ensure_wave(builder: ProjectionBuilder, wave_id: str) -> dict[str, Any]:
    waves = builder._data["waves"]
    if wave_id not in waves:
        waves[wave_id] = {"status": "waiting", "jobs": {}}
    return waves[wave_id]


def _update_job(
    builder: ProjectionBuilder,
    *,
    job_id: str,
    ewo_id: str,
    status: str,
    wave_id: str | None,
) -> None:
    builder._data["jobs"][job_id] = {"status": status, "ewo_id": ewo_id}
    if wave_id:
        wave = _ensure_wave(builder, wave_id)
        wave["jobs"][ewo_id] = {"status": status}
        wave["status"] = _rollup_wave_status(
            [entry["status"] for entry in wave["jobs"].values()]
        )


def _handle_execution_graph_derived(builder: ProjectionBuilder, event: BuildEvent) -> None:
    payload = event.payload
    program_id = payload.get("program_id")
    if program_id:
        builder._data["program_id"] = str(program_id)
    graph_hash = payload.get("graph_hash")
    if graph_hash:
        builder.graph_hash = str(graph_hash)
    for node_id in payload.get("node_ids") or []:
        ewo_id = str(node_id)
        if ewo_id not in builder._data["jobs"]:
            builder._data["jobs"][ewo_id] = {"status": "waiting", "ewo_id": ewo_id}


def _handle_job_ready(builder: ProjectionBuilder, event: BuildEvent) -> None:
    payload = event.payload
    job_id = str(payload.get("job_id") or payload.get("ewo_id") or "")
    ewo_id = str(payload.get("ewo_id") or job_id)
    wave_id = payload.get("wave_id")
    status = _map_execution_state(str(payload.get("state") or "ready"))
    _update_job(builder, job_id=job_id, ewo_id=ewo_id, status=status, wave_id=wave_id)


def _handle_job_claimed(builder: ProjectionBuilder, event: BuildEvent) -> None:
    payload = event.payload
    job_id = str(payload.get("job_id") or payload.get("ewo_id") or "")
    ewo_id = str(payload.get("ewo_id") or job_id)
    wave_id = payload.get("wave_id")
    status = _map_execution_state(str(payload.get("state") or "claimed"))
    _update_job(builder, job_id=job_id, ewo_id=ewo_id, status=status, wave_id=wave_id)


def _handle_ewo_completed(builder: ProjectionBuilder, event: BuildEvent) -> None:
    payload = event.payload
    ewo_id = str(payload.get("ewo_id") or payload.get("job_id") or "")
    job_id = str(payload.get("job_id") or ewo_id)
    existing = builder._data["jobs"].get(job_id) or builder._data["jobs"].get(ewo_id) or {}
    wave_id = None
    for wave_key, wave in builder._data["waves"].items():
        if ewo_id in wave.get("jobs", {}):
            wave_id = wave_key
            break
    _update_job(
        builder,
        job_id=job_id,
        ewo_id=str(existing.get("ewo_id") or ewo_id),
        status="pass",
        wave_id=wave_id,
    )


def _handle_runtime_escalated(builder: ProjectionBuilder, event: BuildEvent) -> None:
    payload = event.payload
    builder._data["supervisor"] = {
        "state": "WAIT",
        "reason": str(payload.get("reason") or "runtime escalation"),
    }
    job_id = payload.get("job_id")
    ewo_id = payload.get("ewo_id")
    if job_id or ewo_id:
        resolved_job = str(job_id or ewo_id)
        resolved_ewo = str(ewo_id or job_id)
        wave_id = None
        for wave_key, wave in builder._data["waves"].items():
            if resolved_ewo in wave.get("jobs", {}):
                wave_id = wave_key
                break
        _update_job(
            builder,
            job_id=resolved_job,
            ewo_id=resolved_ewo,
            status="fail",
            wave_id=wave_id,
        )


_EVENT_HANDLERS = {
    "ExecutionGraphDerived": _handle_execution_graph_derived,
    "JobReady": _handle_job_ready,
    "JobClaimed": _handle_job_claimed,
    "EwoCompleted": _handle_ewo_completed,
    "RuntimeEscalated": _handle_runtime_escalated,
}
