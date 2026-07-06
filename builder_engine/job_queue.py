"""Job Queue — materialize, enqueue, claim/release (MB2 SoR §5)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from builder_engine.dependency import DependencyEngine, ExecutionGraph, ExecutionNode
from builder_engine.program_graph import DONE_STATUSES
from builder_engine.events import BuildEventBus, event_now
from builder_engine.graph import BuilderGraph
from builder_engine.gsm_task import transition as gsm_transition
from builder_engine.state_machine import (
    ExecutionState,
    TransitionError,
    execution_from_yaml_status,
)


@dataclass
class Job:
    job_id: str
    program_id: str
    ewo_id: str
    state: ExecutionState
    wave_id: str | None = None
    checkpoint_ref: str | None = None


def _initial_job_state(node: ExecutionNode) -> ExecutionState:
    if node.ready:
        return ExecutionState.READY
    if node.state in DONE_STATUSES:
        return ExecutionState.DONE
    if node.state == "ready":
        return ExecutionState.CREATED
    return execution_from_yaml_status(node.state)


def job_transition(
    job: Job,
    event: str,
    *,
    graph: BuilderGraph | None = None,
    bus: BuildEventBus | None = None,
    cycle_id: str | None = None,
    emit_escalation: bool = True,
) -> Job:
    """Apply a legal Task FSM transition; optionally escalate illegal moves."""
    prior = job.state
    try:
        job.state = gsm_transition(
            job.state,
            event,
            graph=graph,
            packet_id=job.ewo_id,
        )
    except TransitionError as exc:
        if emit_escalation and bus is not None:
            bus.publish(
                event_now(
                    "RuntimeEscalated",
                    {
                        "job_id": job.job_id,
                        "ewo_id": job.ewo_id,
                        "from_state": prior.value,
                        "event": event,
                        "reason": str(exc),
                    },
                    program_id=job.program_id,
                    cycle_id=cycle_id,
                )
            )
        raise

    if bus is not None:
        if job.state == ExecutionState.READY and prior != ExecutionState.READY:
            bus.publish(
                event_now(
                    "JobReady",
                    _job_event_payload(job),
                    program_id=job.program_id,
                    cycle_id=cycle_id,
                )
            )
        if job.state == ExecutionState.CLAIMED:
            bus.publish(
                event_now(
                    "JobClaimed",
                    _job_event_payload(job),
                    program_id=job.program_id,
                    cycle_id=cycle_id,
                )
            )
    return job


def _job_event_payload(job: Job) -> dict[str, str | None]:
    return {
        "job_id": job.job_id,
        "ewo_id": job.ewo_id,
        "state": job.state.value,
        "wave_id": job.wave_id,
        "checkpoint_ref": job.checkpoint_ref,
    }


@dataclass
class JobQueue:
    """In-memory job queue with recoverable state listing."""

    bus: BuildEventBus | None = None
    cycle_id: str | None = None
    _jobs: dict[str, Job] = field(default_factory=dict)
    _ready_queue: list[str] = field(default_factory=list)

    def materialize(
        self,
        engine: DependencyEngine,
        graph: ExecutionGraph,
        *,
        job_id_factory: Callable[[str], str] | None = None,
    ) -> list[Job]:
        """Create jobs from ExecutionGraph; enqueue and emit JobReady for ready nodes."""
        factory = job_id_factory or (lambda ewo_id: ewo_id)
        created: list[Job] = []

        for node in graph.nodes.values():
            if any(j.ewo_id == node.ewo_id for j in self._jobs.values()):
                continue
            job = Job(
                job_id=factory(node.ewo_id),
                program_id=graph.program_id,
                ewo_id=node.ewo_id,
                state=_initial_job_state(node),
                wave_id=node.wave,
            )
            self._jobs[job.job_id] = job
            created.append(job)

        for node in engine.ready_set(graph):
            job = self._jobs.get(node.ewo_id)
            if job is not None and job.state == ExecutionState.READY:
                self._enqueue(job, emit_ready=job.job_id not in self._ready_queue)

        return created

    def materialize_ready(
        self,
        engine: DependencyEngine,
        graph: ExecutionGraph,
        *,
        job_id_factory: Callable[[str], str] | None = None,
    ) -> list[Job]:
        """Create jobs only for DependencyEngine ready_set nodes."""
        factory = job_id_factory or (lambda ewo_id: ewo_id)
        created: list[Job] = []
        existing_ewo = {j.ewo_id for j in self._jobs.values()}

        for node in engine.ready_set(graph):
            if node.ewo_id in existing_ewo:
                continue
            job = Job(
                job_id=factory(node.ewo_id),
                program_id=graph.program_id,
                ewo_id=node.ewo_id,
                state=ExecutionState.READY,
                wave_id=node.wave,
            )
            self._jobs[job.job_id] = job
            created.append(job)
            self._enqueue(job)

        return created

    def enqueue(self, job: Job) -> None:
        """Enqueue a READY job; emits JobReady when bus is configured."""
        if job.state != ExecutionState.READY:
            raise TransitionError(f"enqueue requires READY, got {job.state.value}")
        self._jobs[job.job_id] = job
        self._enqueue(job)

    def claim(self, job_id: str, *, graph: BuilderGraph | None = None) -> Job:
        """Claim a ready job (READY → CLAIMED)."""
        job = self._require_job(job_id)
        if job_id in self._ready_queue:
            self._ready_queue.remove(job_id)
        job_transition(
            job,
            "claim",
            graph=graph,
            bus=self.bus,
            cycle_id=self.cycle_id,
        )
        return job

    def release(self, job_id: str, *, graph: BuilderGraph | None = None) -> Job:
        """Release a claimed job back to READY (CLAIMED → READY via abort_claim)."""
        job = self._require_job(job_id)
        job_transition(
            job,
            "abort_claim",
            graph=graph,
            bus=self.bus,
            cycle_id=self.cycle_id,
        )
        self._enqueue(job, emit_ready=False)
        return job

    def list_jobs(self, *, state: ExecutionState | None = None) -> list[Job]:
        """Recoverable listing hook — filter jobs by execution state."""
        if state == ExecutionState.READY:
            return [
                self._jobs[job_id]
                for job_id in self._ready_queue
                if self._jobs[job_id].state == ExecutionState.READY
            ]
        jobs = list(self._jobs.values())
        if state is not None:
            jobs = [job for job in jobs if job.state == state]
        return sorted(jobs, key=lambda j: j.job_id)

    def ready_queue(self) -> list[str]:
        """Ordered job_ids awaiting claim."""
        return list(self._ready_queue)

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def _require_job(self, job_id: str) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"unknown job: {job_id}")
        return job

    def _enqueue(self, job: Job, *, emit_ready: bool = True) -> None:
        if job.job_id not in self._ready_queue:
            self._ready_queue.append(job.job_id)
        if emit_ready and self.bus is not None:
            self.bus.publish(
                event_now(
                    "JobReady",
                    _job_event_payload(job),
                    program_id=job.program_id,
                    cycle_id=self.cycle_id,
                )
            )
