"""Recovery helpers — auditable retry and event-log queue restore (MB2 SoR §12)."""

from __future__ import annotations

from dataclasses import dataclass

from builder_engine.events import BuildEventBus, event_now
from builder_engine.job_queue import Job, JobQueue, job_transition
from builder_engine.state_machine import ExecutionState, TransitionError


@dataclass(frozen=True)
class QueueCheckpoint:
    """Serializable queue snapshot for crash recovery."""

    jobs: tuple[tuple[str, str, str, str, str | None, str | None], ...]
    ready_queue: tuple[str, ...]
    program_id: str
    cycle_id: str | None = None


def retry_failed_job(
    job: Job,
    *,
    bus: BuildEventBus | None = None,
    cycle_id: str | None = None,
) -> Job:
    """FAILED → DEBUGGING → READY with RecoveryTaskCreated audit (§12)."""
    if job.state != ExecutionState.FAILED:
        raise TransitionError(f"retry requires FAILED, got {job.state.value}")

    prior_state = job.state.value
    job = job_transition(job, "debug", bus=bus, cycle_id=cycle_id, emit_escalation=False)
    job = job_transition(job, "retry", bus=bus, cycle_id=cycle_id)

    if bus is not None:
        bus.publish(
            event_now(
                "RecoveryTaskCreated",
                {
                    "job_id": job.job_id,
                    "ewo_id": job.ewo_id,
                    "from_state": prior_state,
                    "to_state": job.state.value,
                    "recovery_type": "retry_job",
                },
                program_id=job.program_id,
                cycle_id=cycle_id,
            )
        )
    return job


def checkpoint_queue(queue: JobQueue) -> QueueCheckpoint:
    """Capture recoverable queue state."""
    jobs = tuple(
        (
            job.job_id,
            job.program_id,
            job.ewo_id,
            job.state.value,
            job.wave_id,
            job.checkpoint_ref,
        )
        for job in sorted(queue.list_jobs(), key=lambda j: j.job_id)
    )
    return QueueCheckpoint(
        jobs=jobs,
        ready_queue=tuple(queue.ready_queue()),
        program_id=jobs[0][1] if jobs else "builder",
        cycle_id=queue.cycle_id,
    )


def restore_queue_from_checkpoint(checkpoint: QueueCheckpoint) -> JobQueue:
    """Restore in-memory queue from a checkpoint snapshot."""
    queue = JobQueue(cycle_id=checkpoint.cycle_id)
    for job_id, program_id, ewo_id, state_value, wave_id, checkpoint_ref in checkpoint.jobs:
        queue._jobs[job_id] = Job(
            job_id=job_id,
            program_id=program_id,
            ewo_id=ewo_id,
            state=ExecutionState(state_value),
            wave_id=wave_id,
            checkpoint_ref=checkpoint_ref,
        )
    queue._ready_queue = [
        job_id for job_id in checkpoint.ready_queue if job_id in queue._jobs
    ]
    return queue


def restore_queue_from_replay(
    bus: BuildEventBus,
    *,
    cycle_id: str | None = None,
) -> JobQueue:
    """Replay JobReady/JobClaimed events to rebuild queue state (§12)."""
    queue = JobQueue(bus=None, cycle_id=cycle_id)
    for event in bus.replay():
        payload = event.payload
        job_id = str(payload.get("job_id") or payload.get("ewo_id") or "")
        if not job_id:
            continue
        ewo_id = str(payload.get("ewo_id") or job_id)
        wave_id = payload.get("wave_id")
        checkpoint_ref = payload.get("checkpoint_ref")

        if event.type == "JobReady":
            queue._jobs[job_id] = Job(
                job_id=job_id,
                program_id=event.program_id,
                ewo_id=ewo_id,
                state=ExecutionState.READY,
                wave_id=wave_id,
                checkpoint_ref=checkpoint_ref,
            )
            if job_id not in queue._ready_queue:
                queue._ready_queue.append(job_id)
        elif event.type == "JobClaimed":
            if job_id in queue._ready_queue:
                queue._ready_queue.remove(job_id)
            job = queue._jobs.get(job_id)
            if job is None:
                job = Job(
                    job_id=job_id,
                    program_id=event.program_id,
                    ewo_id=ewo_id,
                    state=ExecutionState.CLAIMED,
                    wave_id=wave_id,
                    checkpoint_ref=checkpoint_ref,
                )
                queue._jobs[job_id] = job
            else:
                job.state = ExecutionState.CLAIMED
    return queue
