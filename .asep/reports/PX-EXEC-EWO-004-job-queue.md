# PX-EXEC-EWO-004 — Job Queue

Program: px-exec  
WorkOrder: PX-EXEC-EWO-004  
Capability: `px-exec-4-job-queue`  
Authorization: Wave A Phase 2 (after EWO-003 PASS)  
SoR: §5 Job FSM, ADR-0025 @ 2026-07-05  
Verdict: **PASS**  
Timestamp: 2026-07-06T03:45:00+02:00  

---

## Summary

Implemented Job Queue per SoR §5: `Job` dataclass, `JobQueue` materialize/enqueue/claim/release
API, `job_transition` wrapping `gsm_task.transition`, `JobReady` / `JobClaimed` event emission,
`RuntimeEscalated` on illegal transitions, and recoverable `list_jobs(state=…)` hook.

**Does not satisfy MB2-Q1** — qualification act and MB2-Q-001…003 remain separate.

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/job_queue.py` | New — `Job`, `JobQueue`, `job_transition` |
| `builder_engine/tests/test_job_queue.py` | New — 8 acceptance tests |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| `Job` dataclass (job_id, program_id, ewo_id, state, wave_id, checkpoint_ref) | ✓ |
| Materialize from `DependencyEngine` + `ExecutionGraph` | ✓ |
| Enqueue ready jobs in merge_order | ✓ |
| Claim / release API (READY ↔ CLAIMED) | ✓ |
| `job_transition` uses `gsm_task.transition` (not ad hoc FSM) | ✓ |
| Illegal transition raises `TransitionError` | ✓ |
| `RuntimeEscalated` on illegal transition (optional bus) | ✓ |
| `JobReady` emitted when job enters READY | ✓ |
| `JobClaimed` emitted on claim | ✓ |
| Recoverable `list_jobs(state=…)` hook | ✓ |
| Integration with `px_exec_program_minimal.yaml` fixture | ✓ |
| `make unit-builder-engine` | ✓ **109 passed** |
| No MB2-Q1 claim | ✓ |

---

## Traceability

| Req | SoR | Evidence |
|-----|-----|----------|
| REQ-14 | §5 Job FSM | `job_transition` → `gsm_task.transition` |
| REQ-14 | §5 claim/release | `JobQueue.claim` / `release` |
| REQ-14 | §6.3 events | `JobReady`, `JobClaimed`, `RuntimeEscalated` |
| REQ-02 hook | §4.2 ready set | `materialize` / `materialize_ready` |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/job_queue.py` | yes |
| `builder_engine/tests/test_job_queue.py` | yes |
| `builder_engine/dependency.py` | no (read-only) |
| `builder_engine/events.py` | no |
| `builder_engine/state_machine.py` | no |
| `builder_engine/rules.py` | no |
| `builder_engine/scheduler.py` | no |
| `backend/app/**` | no |
| `frontend/**` | no |
| SoR | no |

---

## Unblocks

- **PX-EXEC-EWO-005** Scheduler (reads `job_queue.py`, `JobReady`/`JobClaimed` events)
- Wave A Phase 3 convergence after EWO-002 PASS

---

## WO-TRACE

```text
EWO-003 PASS → EWO-004 implement → verify PASS
  → next: EWO-005 (Scheduler) or EWO-006 (Projection)
  → MB2-Q1 qualification: NOT AUTHORIZED
```
