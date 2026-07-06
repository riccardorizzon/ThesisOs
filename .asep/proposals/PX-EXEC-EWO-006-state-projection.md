# Engineering WorkOrder Proposal — PX-EXEC-EWO-006

> **Status:** PROPOSED — pending Architect authorization for dispatch  
> **Prerequisite:** PX-EXEC-EWO-001 **IMPLEMENTED** @ 2026-07-06  
> **Integration note:** Cross-module tests defer until EWO-005 PASS (Wave A Integration)

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P1 — Runtime Foundation |
| **Wave** | Wave A (parallel with EWO-005 — disjoint ownership) |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-6-state-projection` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-006 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on authorization) → `done` (on PASS report) |

---

## Objective

Implement the **State Projection Builder** per SoR §9: schema v1 document, deterministic
rebuild from append-only event log (+ optional checkpoint snapshot hook), read-only consumer
API, and `ProjectionUpdated` emission — **without** computing scheduling decisions (INV-R-12),
mutating authoritative queue state, or claiming MB2-Q5 or any MB2-Q pass.

This EWO completes Wave A observability foundation and enables future MB2-Q5 evidence
(REQ-11, MB2-Q-013…015); it does **not** constitute qualification.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-006 deliverable |
|-------|-------------|---------------------|
| **§9.1** Schema v1 | Normative YAML/JSON projection shape | `ProjectionDocument` dataclass + serializer |
| **§9.2** Rebuild | Event log → identical projection | `ProjectionBuilder.rebuild(events)` |
| **§9.3** Consumer rules | Read-only; no ready-set compute | `load_projection()` / `read_projection()` API |
| **§6.3** `ProjectionUpdated` | Emit on rebuild | Publish via Event Bus |
| **§5.3** Aggregate roll-up | `waiting\|ready\|running\|pass\|fail\|locked` | Derived from job events in projection |

### Schema v1 fields (normative minimum)

Implement all top-level keys from SoR §9.1:

```yaml
schema_version: 1
program_id: string
derived_at: ISO8601
cycle_id: string?
supervisor: { state, reason? }
waves: { <wave_id>: { status, jobs } }
integrations: { ... }
jobs: { <job_id>: { status, ewo_id } }
queue: { pending, in_flight, failed }
qwo: { ... }
gates: { ci, coverage }
```

Phase 1 may populate stubs (`unknown`) for integrations/qwo/gates until Phase 2 plugins exist.

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-11 | Projection read-only | MB2-Q5 | MB2-Q-013 |
| REQ-11 | Rebuild deterministic | MB2-Q5 | MB2-Q-013 |
| REQ-20 | Dashboard/CLI view-only | MB2-Q5 | MB2-Q-014 |

### Invariants

| Invariant | EWO-006 enforcement |
|-----------|---------------------|
| **INV-R-11** | Projection never owns state — rebuild only from events |
| **INV-R-12** | No `compute_ready` or scheduler logic in projection module |
| **INV-R-08** | `ProjectionUpdated` emitted after rebuild commit |

---

## Ownership (exclusive)

```text
builder_engine/projection.py                           # new — builder, document, I/O
builder_engine/tests/test_projection.py                # new — unit + rebuild tests
builder_engine/tests/fixtures/projection_event_sequence.jsonl  # new — synthetic event log
builder_engine/tests/fixtures/projection_schema_v1.yaml        # new — schema reference fixture
```

**Shared read-only:**

```text
builder_engine/events.py           # BuildEvent, replay/tail, catalog types
builder_engine/job_queue.py        # ExecutionState values for status mapping (types only)
```

**Integration touch (Supervisor at Wave A Integration — optional minimal):**

```text
builder_engine/cli.py              # `builder-engine projection show` read-only — if ≤20 lines
```

Changes outside ownership require explicit Architect approval in EWO report.

---

## Forbidden paths

```text
backend/app/**
frontend/**
builder_engine/scheduler.py        # EWO-005 — no edits
builder_engine/rules.py              # read-only
builder_engine/job_queue.py          # no mutation APIs called from projection
builder_engine/dependency.py         # no ready-set derivation in projection
docs/superpowers/specs/mb2-engineering-runtime-spec.md   # SoR — no edits
plans/builder/STATE.yaml             # projection replaces read model eventually — not in this EWO
```

**Behavioral exclusions:**

- Dashboard UI (Phase 3)
- Scheduling or claim logic (INV-R-12)
- Plugin Registry (Phase 2)
- Checkpoint persistence implementation (design hook only)
- MB2-Q5 qualification report issuance

---

## Scope

### In scope

1. **`ProjectionDocument` dataclass** — mirrors §9.1; `to_dict()` / `from_dict()` / YAML serialize
2. **`ProjectionBuilder` class:**
   - `apply(event: BuildEvent) -> None` — incremental fold
   - `rebuild(events: list[BuildEvent]) -> ProjectionDocument` — deterministic full rebuild
   - `content_hash() -> str` — stable hash for idempotency tests
3. **Event handlers (Phase 1 minimum):**
   - `ExecutionGraphDerived` — update program scope / graph_hash metadata
   - `JobReady`, `JobClaimed` — update `jobs`, `queue` counters, wave roll-up
   - `EwoCompleted`, `RuntimeEscalated` — status transitions
   - `ProjectionUpdated` — ignored on input (avoid recursion); emitted on output only
   - Era I events — no-op or metadata-only (preserve rebuild stability)
4. **Persistence** — write/read `.builder-engine/projection.yaml` (sidecar, not authoritative)
5. **`ProjectionUpdated` emission** — on rebuild when bus provided
6. **Synthetic fixture tests** — full rebuild from JSONL without requiring EWO-005 live events
7. **Deferred integration tests** — marked `@pytest.mark.integration` for post-005 merge (optional skip in EWO exit)
8. **EWO completion report** — `.asep/reports/PX-EXEC-EWO-006-state-projection.md`

### Out of scope

- CLI `status` command rewrite to use projection (Wave A Integration)
- Web dashboard (Phase 3)
- Checkpoint atomic write (EWO-004 hook documented only)
- MB2-Q5 Qualification Package

---

## Acceptance criteria (EWO exit)

- [ ] Schema v1 all top-level keys present (stubs OK for unused Phase 2 sections)
- [ ] `rebuild()` deterministic: same events → identical `content_hash`
- [ ] `ProjectionUpdated` published on rebuild when bus configured
- [ ] No import from `scheduler.py` or `compute_ready`
- [ ] `jobs` and `queue` counters update from `JobReady` / `JobClaimed` synthetic fixtures
- [ ] Projection file write/read round-trip
- [ ] Era I tests unchanged (`make unit-builder-engine` green)
- [ ] EWO report traceability to §9.1–§9.3, REQ-11, REQ-20
- [ ] **No MB2-Q5 PASS claim** in EWO report

---

## Acceptance tests (design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_schema_v1_required_keys` | All §9.1 top-level keys present | §9.1, MB2-Q-015 prep |
| `test_rebuild_deterministic` | Replay twice → same hash | §9.2, INV-R-11, MB2-Q-013 prep |
| `test_job_ready_updates_projection` | JobReady → job status + queue.pending | §9.1 jobs/queue |
| `test_job_claimed_updates_projection` | JobClaimed → in_flight increment | §9.1 queue |
| `test_execution_graph_derived_metadata` | graph_hash stored | §9.1 waves/jobs hook |
| `test_projection_updated_emitted` | rebuild publishes event | §6.3, INV-R-08 |
| `test_no_scheduler_import` | projection.py AST — no scheduler import | INV-R-12, MB2-Q-014 prep |
| `test_persistence_round_trip` | write YAML → read → equal document | §9.3 |
| `test_era_events_noop_stable` | CycleStarted does not corrupt rebuild | Era I compat |

Future gate tests (**not** part of EWO-006 exit):

- `MB2-Q-013` — full event log + checkpoint replay
- `MB2-Q-014` — CLI reads projection only (Wave A Integration)
- `MB2-Q-015` — schema validation against golden fixture

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-EXEC-EWO-001 Event Model & Bus | **PASS** @ 2026-07-06 |
| MB2 SoR frozen @ 2026-07-05 | **PASS** |
| Architect authorization for EWO-006 dispatch | **PENDING** |

**Parallel with:** PX-EXEC-EWO-005 (disjoint ownership)

**Cross-module integration:** Wave A Integration merges 005 → 006 (merge order per engineering package)

---

## Exit criteria (WorkOrder complete)

| Criterion | Evidence |
|-----------|----------|
| Implementation on branch | `projection.py` + tests + fixtures |
| Verification green | `make unit-builder-engine` log in EWO report |
| Scope honored | No scheduler logic; no forbidden paths |
| Traceability | EWO report → §9.1–§9.3, REQ-11, REQ-20 |
| Downstream ready | Projection file for Phase 3 dashboard |
| Qualification boundary | **Does not satisfy MB2-Q5** |

---

## Constraints

- ADR-0042 §6 — projection is observability only
- INV-R-11, INV-R-12 — hard boundaries vs queue/scheduler
- Use synthetic fixtures for unit tests; live 005+004 event sequences at Wave A Integration only
- `sor-compatibility-policy` — clarifications OK; no normative SoR edits
- Smallest correct diff; match `builder_engine/` style

---

## WO-TRACE

```text
EWO-001 PASS
  → PX-EXEC-EWO-006 proposal (this doc)
  → Architect review → AUTHORIZE PX-EXEC-EWO-006
  → implement ∥ EWO-005 → Wave A Integration → Wave A PASS
```
