"""Ready-set computation (orchestrate-builders SKILL §2A) and MB2 Scheduler plugin (SoR §8.2)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from builder_engine.events import BuildEventBus
from builder_engine.graph import BuilderGraph, Packet
from builder_engine.job_queue import Job, JobQueue
from builder_engine.rules import ActionDescriptor

logger = logging.getLogger(__name__)


def compute_ready(graph: BuilderGraph) -> list[Packet]:
    """Packets ready for dispatch in the current wave."""
    ready: list[Packet] = []
    for pkt in graph.packets.values():
        if pkt.status != "ready":
            continue
        if pkt.wave != graph.wave:
            continue
        if not all(graph.packets[dep].status == "done" for dep in pkt.depends_on):
            continue
        ready.append(pkt)
    ready.sort(key=lambda p: p.id)
    return ready


def in_flight_packets(graph: BuilderGraph) -> list[Packet]:
    """Packets currently in_progress (CLAIMED/RUNNING/VALIDATING in ADR-0025)."""
    return sorted(
        (p for p in graph.packets.values() if p.status == "in_progress"),
        key=lambda p: p.id,
    )


def file_locks_for_packet(packet: Packet) -> dict[str, str]:
    """Lock map for owned paths when a packet is scheduled."""
    return {path: packet.id for path in packet.owned_files}


class SupervisorGate(str, Enum):
    """Supervisor halt input — WAIT/STOP block autonomous claim (INV-R-16)."""

    EXECUTE = "execute"
    WAIT = "wait"
    STOP = "stop"


class SchedulerHaltedError(RuntimeError):
    """Raised when claim is attempted while supervisor gate is WAIT or STOP."""


@dataclass(frozen=True)
class DispatchJobEntry:
    job_id: str
    ewo_id: str
    state: str
    wave_id: str | None
    checkpoint_ref: str | None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "job_id": self.job_id,
            "ewo_id": self.ewo_id,
            "state": self.state,
            "wave_id": self.wave_id,
            "checkpoint_ref": self.checkpoint_ref,
        }


@dataclass(frozen=True)
class DispatchManifest:
    program_id: str
    generated_at: str
    manifest_path: Path
    entries: tuple[DispatchJobEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "program_id": self.program_id,
            "generated_at": self.generated_at,
            "manifest_path": str(self.manifest_path),
            "entries": [entry.to_dict() for entry in self.entries],
        }


def _entry_from_job(job: Job) -> DispatchJobEntry:
    return DispatchJobEntry(
        job_id=job.job_id,
        ewo_id=job.ewo_id,
        state=job.state.value,
        wave_id=job.wave_id,
        checkpoint_ref=job.checkpoint_ref,
    )


class SchedulerPlugin:
    """MB2 Scheduler — claim/release/manifest over JobQueue (SoR §8.2)."""

    def __init__(
        self,
        queue: JobQueue,
        *,
        supervisor: SupervisorGate = SupervisorGate.EXECUTE,
        bus: BuildEventBus | None = None,
    ) -> None:
        self.queue = queue
        self.supervisor = supervisor
        self.bus = bus or queue.bus
        self._repo_root = (
            self.bus.repo_root.resolve() if self.bus is not None else None
        )

    def claim(self, job_id: str, *, graph: BuilderGraph | None = None) -> Job:
        """Claim a ready job; refuses when supervisor gate is WAIT or STOP."""
        self._require_execute("claim")
        return self.queue.claim(job_id, graph=graph)

    def release(self, job_id: str, *, graph: BuilderGraph | None = None) -> Job:
        """Release a claimed job back to READY."""
        return self.queue.release(job_id, graph=graph)

    def build_manifest(
        self,
        job_ids: list[str],
        *,
        generated_at: str | None = None,
    ) -> DispatchManifest:
        """Build a deterministic dispatch manifest and persist to the engine sidecar."""
        ordered_ids = sorted(job_ids)
        jobs: list[Job] = []
        for job_id in ordered_ids:
            job = self.queue.get(job_id)
            if job is None:
                raise KeyError(f"unknown job: {job_id}")
            jobs.append(job)

        if not jobs:
            raise ValueError("build_manifest requires at least one job_id")

        program_id = jobs[0].program_id
        entries = tuple(_entry_from_job(job) for job in jobs)
        ts = generated_at or datetime.now(UTC).isoformat()

        manifest_path = self._manifest_path()
        manifest = DispatchManifest(
            program_id=program_id,
            generated_at=ts,
            manifest_path=manifest_path,
            entries=entries,
        )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        return manifest

    def claim_next(
        self,
        *,
        max_claims: int = 1,
        graph: BuilderGraph | None = None,
    ) -> list[Job]:
        """Drain ready_queue in merge_order up to max_claims."""
        self._require_execute("claim_next")
        claimed: list[Job] = []
        for job_id in self.queue.ready_queue()[:max_claims]:
            claimed.append(self.claim(job_id, graph=graph))
        return claimed

    def on_action(self, descriptor: ActionDescriptor) -> None:
        """Rule-engine hook stub — log only; no implicit queue mutation (Phase 1)."""
        logger.info(
            "scheduler on_action stub: plugin=%s rule_id=%s params=%s",
            descriptor.plugin,
            descriptor.rule_id,
            descriptor.params,
        )

    def _require_execute(self, operation: str) -> None:
        if self.supervisor == SupervisorGate.EXECUTE:
            return
        raise SchedulerHaltedError(
            f"{operation} refused: supervisor gate is {self.supervisor.value}"
        )

    def _manifest_path(self) -> Path:
        if self._repo_root is None:
            raise RuntimeError("repo_root required for manifest persistence")
        return self._repo_root / ".builder-engine" / "last-dispatch-manifest.json"
