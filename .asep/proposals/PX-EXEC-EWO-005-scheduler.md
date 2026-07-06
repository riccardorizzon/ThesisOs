# Engineering WorkOrder Proposal — PX-EXEC-EWO-005

> **Status:** PROPOSED — pending Architect authorization for dispatch  
> **Prerequisites:** PX-EXEC-EWO-002 **IMPLEMENTED**, PX-EXEC-EWO-004 **IMPLEMENTED** @ 2026-07-06

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P1 — Runtime Foundation |
| **Wave** | Wave A (parallel with EWO-006 — disjoint ownership) |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-5-scheduler` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-005 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on authorization) → `done` (on PASS report) |

---

## Objective

Extend `builder_engine/scheduler.py` with the **MB2 Scheduler plugin interface** (SoR §8.2):
`claim(job)`, `release(job)`, `build_manifest(jobs[])` — wired to `JobQueue`, respecting
Supervisor **WAIT** halt (INV-R-16), optional reactive hooks from `RuleEngine` action
descriptors, and dispatch manifest emission — **without** implementing Phase 2 merge/integration
plugins, AgentProvider dispatch, or claiming MB2-Q3 or any MB2-Q pass.

This EWO completes Wave A convergence (`001 → 003 → 004 → 005`) and enables future MB2-Q3
evidence (REQ-12, MB2-Q-007…009); it does **not** constitute qualification.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-005 deliverable |
|-------|-------------|---------------------|
| **§8.2** Scheduler plugin | `claim`, `release`, `build_manifest` | `SchedulerPlugin` class in `scheduler.py` |
| **§5.1** Job FSM | Claim transitions via queue | Delegates to `JobQueue.claim` / `release` |
| **§6.3** Events | Dispatch / claim correlation | Reuse `JobClaimed`; manifest path in payload or `WorkerDispatched` stub |
| **§10.1** WAIT behavior | Queue paused — no new CLAIM | `SupervisorGate` parameter; WAIT → claim refused |
| **§7.1** (optional hook) | Rule action → scheduler | `SchedulerPlugin.on_action(ActionDescriptor)` no-op or claim stub |

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-12 | WAIT halts autonomous progression | MB2-Q3 | MB2-Q-008 |
| REQ-13 | Escalation to Supervisor | MB2-Q3 | MB2-Q-008 |
| REQ-14 | Job FSM claim path | MB2-Q3 | MB2-Q-007 |
| REQ-09 | Deterministic scheduling decisions | MB2-Q3 | MB2-Q-009 |

### Invariants

| Invariant | EWO-005 enforcement |
|-----------|---------------------|
| **INV-R-16** | `claim()` no-op or `SchedulerHaltedError` when supervisor state is `WAIT` |
| **INV-R-08** | Claim emits `JobClaimed` via existing `JobQueue` bus wiring |
| **INV-R-12** | Scheduler computes manifest; CLI does not invent ready-set independently |

### Era I preservation

| Era I API | EWO-005 rule |
|-----------|--------------|
| `compute_ready(graph)` | **Retained unchanged** — MB2 scheduler is additive module/class |
| `in_flight_packets`, `file_locks_for_packet` | **Retained unchanged** |
| `EngineeringRuntime.schedule()` | **Not modified** in this EWO |

---

## Ownership (exclusive)

```text
builder_engine/scheduler.py                    # extend — SchedulerPlugin + MB2 types
builder_engine/tests/test_scheduler_mb2.py     # new — MB2 scheduler acceptance tests
builder_engine/tests/fixtures/dispatch_manifest_v1.json  # new — optional schema stub
```

**Shared read-only:**

```text
builder_engine/job_queue.py        # JobQueue.claim / release / ready_queue
builder_engine/rules.py            # ActionDescriptor type only
builder_engine/events.py           # publish via queue/bus
builder_engine/executor.py         # reference manifest shape
```

**Integration touch (Supervisor merge at Wave A Integration — not in EWO scope unless minimal):**

```text
builder_engine/cli.py              # optional `schedule-jobs` read-only preview — defer to integration
```

Changes outside ownership require explicit Architect approval in EWO report.

---

## Forbidden paths

```text
backend/app/**
frontend/**
builder_engine/projection.py       # EWO-006
builder_engine/rules.py            # no structural changes
builder_engine/job_queue.py        # EWO-004 — read-only use
builder_engine/dependency.py       # read-only
builder_engine/merge.py            # Phase 2
docs/superpowers/specs/mb2-engineering-runtime-spec.md   # SoR — no edits
.asep/governance/**                # no policy changes
```

**Behavioral exclusions:**

- Plugin Registry full implementation (MB2-Q4 / Phase 2)
- AgentProvider / Cursor task dispatch (Phase 4)
- Merge / integration / QWO plugin execution
- Projection builder (EWO-006)
- CLI scheduling logic that bypasses Runtime (INV-R-12)
- MB2-Q3 qualification report issuance

---

## Scope

### In scope

1. **`SupervisorGate` enum or literal** — `EXECUTE | WAIT | STOP`; passed to scheduler
2. **`DispatchManifest` dataclass** — job entries, program_id, generated_at, manifest_path
3. **`SchedulerPlugin` class:**
   - `__init__(queue: JobQueue, *, supervisor: SupervisorGate = EXECUTE, bus: BuildEventBus | None)`
   - `claim(job_id, *, graph: BuilderGraph | None = None) -> Job` — refuses when WAIT/STOP
   - `release(job_id, *, graph: BuilderGraph | None = None) -> Job`
   - `build_manifest(job_ids: list[str]) -> DispatchManifest` — JSON-serializable entries
   - `claim_next(*, max_claims: int = 1) -> list[Job]` — drain ready_queue in order
   - `on_action(descriptor: ActionDescriptor) -> None` — stub: log only in Phase 1
4. **Lock model (Phase 1 minimum)** — document single-flight per job_id; path locks deferred to Phase 2 merge plugin
5. **Manifest persistence** — write to `.builder-engine/last-dispatch-manifest.json` (same sidecar as Era I)
6. **Tests** — see Acceptance tests
7. **EWO completion report** — `.asep/reports/PX-EXEC-EWO-005-scheduler.md`

### Out of scope

- Replacing `EngineeringRuntime.schedule()` Era I path
- Multi-program concurrency (Phase 4)
- Recovery policies (Phase 4)
- MB2-Q3 Qualification Package
- Wave A Integration report (Supervisor act after 005 + 006)

---

## Acceptance criteria (EWO exit)

- [ ] `SchedulerPlugin.claim` / `release` delegate to `JobQueue`
- [ ] WAIT halts new claims — no `JobClaimed` emitted (INV-R-16)
- [ ] STOP halts new claims (same as WAIT for Phase 1)
- [ ] `build_manifest` produces deterministic JSON for same job set
- [ ] `claim_next` respects `JobQueue.ready_queue()` merge_order
- [ ] Era I `compute_ready()` tests unchanged
- [ ] `on_action` does not mutate queue without explicit claim (stub/log only)
- [ ] `make unit-builder-engine` green
- [ ] EWO report traceability to §8.2, §5, §10.1, REQ-12
- [ ] **No MB2-Q3 PASS claim** in EWO report

---

## Acceptance tests (design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_scheduler_claim_delegates_to_queue` | claim → JobClaimed event | §8.2 |
| `test_scheduler_wait_halts_claim` | WAIT → claim refused, no event | INV-R-16, MB2-Q-008 prep |
| `test_scheduler_stop_halts_claim` | STOP → claim refused | §10.1 |
| `test_build_manifest_deterministic` | Same jobs → same manifest body | MB2-Q-009 prep |
| `test_claim_next_respects_queue_order` | merge_order from JobQueue | §8.2 |
| `test_release_returns_job_to_ready` | release → re-enqueued | §8.2 |
| `test_era_compute_ready_unchanged` | Existing graph tests pass | Era I compat |
| `test_on_action_stub_no_claim` | ActionDescriptor → no implicit claim | §7.1 hook |
| `test_supervisor_gate_default_execute` | Default allows claim | §10.1 |

Future gate tests (**not** part of EWO-005 exit):

- `MB2-Q-007` — single-flight lock per owned path (Phase 2 merge scope)
- `MB2-Q-008` — WAIT integration with Supervisor FSM
- `MB2-Q-009` — full dispatch manifest replay

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-EXEC-EWO-004 Job Queue | **PASS** @ 2026-07-06 |
| PX-EXEC-EWO-002 Rule Engine | **PASS** @ 2026-07-06 |
| PX-EXEC-EWO-001 Event Bus | **PASS** |
| Architect authorization for EWO-005 dispatch | **PENDING** |

**Parallel with:** PX-EXEC-EWO-006 (disjoint ownership — no file conflicts)

**Unblocks:** Wave A Integration (with EWO-006 PASS)

---

## Exit criteria (WorkOrder complete)

| Criterion | Evidence |
|-----------|----------|
| Implementation on branch | Extended `scheduler.py` + tests |
| Verification green | `make unit-builder-engine` log in EWO report |
| Scope honored | Era I APIs preserved; no forbidden paths |
| Traceability | EWO report → §8.2, §10.1, REQ-12 |
| Downstream ready | Scheduler API for Phase 2 plugin registry wiring |
| Qualification boundary | **Does not satisfy MB2-Q3** |

---

## Constraints

- ADR-0042 §2 — Runtime schedules; Governance WAIT is input, not evaluated as rule
- INV-R-16 — WAIT is hard gate on claim
- Smallest correct diff; extend `scheduler.py`, do not replace Era I functions
- Do not dispatch until Architect authorizes after proposal review

---

## WO-TRACE

```text
EWO-004 PASS + EWO-002 PASS
  → PX-EXEC-EWO-005 proposal (this doc)
  → Architect review → AUTHORIZE PX-EXEC-EWO-005
  → implement ∥ EWO-006 → Wave A Integration
```
