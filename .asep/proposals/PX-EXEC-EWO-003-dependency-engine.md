# Engineering WorkOrder Proposal — PX-EXEC-EWO-003

> **Status:** PROPOSED — pending Architect authorization for dispatch  
> **Prerequisite:** PX-EXEC-EWO-001 **IMPLEMENTED** @ 2026-07-06

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: C
  hypothesis_id: H-02
  success_metric: "Dry-run replay of PX-2 wave shows merge ordering enforced without human merge script"
  exit_id: X-03
  program_mode: rd
```

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P1 — Runtime Foundation |
| **Wave** | Wave A (parallel with EWO-002 after EWO-001) |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-3-dependency-engine` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-003 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on authorization) → `done` (on PASS report) |

---

## Objective

Implement the **Dependency Engine** per SoR §4.2 and runtime-model-v2 §4: derive the
Execution Graph from the Program Graph plus runtime completion state, compute ready sets
and critical path respecting `merge_order` as tie-breaker only, reject orphan nodes, and
emit `ExecutionGraphDerived` events — **without** inventing dependencies absent from the
Program Graph and **without** claiming MB2-Q1 or any MB2-Q pass.

This EWO enables future MB2-Q1 evidence (REQ-02, REQ-03, REQ-04, MB2-Q-001…003); it does
**not** constitute qualification.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-003 deliverable |
|-------|-------------|---------------------|
| **§4.1** Program Graph input | Read `.asep/programs/*.yaml` workorder_backlog / wave definitions | `ProgramGraphLoader` |
| **§4.2** Execution Graph | Materialize nodes, ready set, critical path | `DependencyEngine.derive()` |
| **§5** Job model context | Node preconditions map to job readiness (design hook) | `ExecutionNode` with `ewo_id`, `depends_on`, `state` |
| **§6.3** `ExecutionGraphDerived` | Emit on derivation with content hash | Publish via Event Bus |

### Derivation algorithm (runtime-model-v2 §4.1)

1. Load Program Graph for active `program_id`
2. Filter nodes whose `depends_on` / wave preconditions are satisfied (`DONE` or equivalent)
3. Materialize ready set for current wave or integration stage
4. Apply `merge_order` as topological tie-breaker — **never** invent edges
5. Emit `ExecutionGraphDerived` with snapshot hash

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-02 | Execution Graph derived | MB2-Q1 | MB2-Q-001 |
| REQ-03 | Every node traces to Program Graph | MB2-Q1 | MB2-Q-002 |
| REQ-04 | merge_order enforced | MB2-Q1 | MB2-Q-003 |
| REQ-14 | Job FSM conforms ADR-0025 | MB2-Q1 | MB2-Q-001 (hook for EWO-004) |

### Invariants

| Invariant | EWO-003 enforcement |
|-----------|---------------------|
| **INV-R-01** | Every `ExecutionNode` carries `program_graph_ref` (ewo_id / wave id) |
| **INV-R-02** | No manual Execution Graph editing API; derive-only |
| **INV-R-03** | `merge_order` reorders ready set only; does not add dependencies |
| **INV-R-08** | Derivation publishes `ExecutionGraphDerived` before checkpoint update |

---

## Ownership (exclusive)

```text
builder_engine/dependency.py                         # new — DependencyEngine, ExecutionGraph, ExecutionNode
builder_engine/program_graph.py                      # new — ProgramGraphLoader from .asep/programs YAML
builder_engine/tests/test_dependency_engine.py       # new — derivation + invariant tests
builder_engine/tests/fixtures/px_exec_program_minimal.yaml   # new — test Program Graph
builder_engine/tests/fixtures/px2_parallel_program_excerpt.yaml  # new — merge_order golden fixture
```

**Shared read-only:**

```text
builder_engine/events.py           # publish ExecutionGraphDerived
builder_engine/graph.py            # Era I BuilderGraph — reference only; no structural changes unless minimal shared types approved
builder_engine/yaml_loader.py      # reuse
builder_engine/scheduler.py        # compute_ready — parity test reference; EWO-003 does not modify scheduler
```

**Must NOT modify (EWO-004 owns job queue):**

```text
builder_engine/state_machine.py    # Job FSM implementation deferred to EWO-004
```

Changes outside ownership require explicit Architect approval in EWO report.

---

## Forbidden paths

```text
backend/app/**
frontend/**
builder_engine/rules.py            # EWO-002
builder_engine/job_queue.py          # EWO-004
builder_engine/scheduler.py        # EWO-005 (no edits in EWO-003)
builder_engine/projection.py       # EWO-006
docs/superpowers/specs/mb2-engineering-runtime-spec.md   # SoR — no edits
plans/builder/STATE.yaml           # read-only for Era I parity tests only
.asep/programs/px-exec.yaml        # read-only — test fixtures copy structure; no live graph edits
```

**Behavioral exclusions:**

- Rule pack evaluation (EWO-002)
- Job FSM state transitions (EWO-004)
- Scheduler claim/release (EWO-005)
- Plugin Registry (Phase 2)
- Mutating Program Graph files (Governance-owned)
- MB2-Q qualification report issuance

---

## Scope

### In scope

1. **`ProgramGraph` datamodel** — programs, waves, workorders, `depends_on`, `merge_order`, `execute_in_parallel`
2. **`ProgramGraphLoader`** — load from `.asep/programs/<id>.yaml` `workorder_backlog` + optional `wave_a` blocks; validate schema minimum
3. **`ExecutionNode` / `ExecutionGraph` datamodels** — derived nodes with stable ids, precondition status, wave grouping
4. **`DependencyEngine`:**
   - `derive(program_id, completion_state) -> ExecutionGraph`
   - `ready_set() -> list[ExecutionNode]`
   - `critical_path() -> list[ExecutionNode]` respecting merge_order tie-break
   - Reject orphan executable nodes (no Program Graph ref)
5. **`CompletionState` adapter** — map EWO status from program graph or test fixture (`implemented`, `ready`, `blocked`, `done`)
6. **Event emission** — `ExecutionGraphDerived` with payload: `program_id`, `graph_hash`, `ready_count`, `node_ids[]`
7. **Era I parity test** — optional bridge: derive from `BuilderGraph` packet deps vs `compute_ready()` for same fixture (document divergence if any)
8. **PX-2 parallel excerpt fixture** — validate merge_order [003, 004, 006] tie-break without inventing edges
9. **Tests** — see Acceptance tests
10. **EWO completion report** — `.asep/reports/PX-EXEC-EWO-003-dependency-engine.md`

### Out of scope

- Persistent checkpoint storage (EWO-004)
- Job queue enqueue from ready set (EWO-004)
- Integration / wave aggregate state roll-up (EWO-006 projection)
- Live px-exec program mutation
- MB2-Q1 Qualification Package

---

## Acceptance criteria (EWO exit)

- [ ] Program Graph loads from px-exec-style YAML; unknown nodes rejected
- [ ] Execution Graph derived only from Program Graph + completion state (INV-R-02)
- [ ] Every execution node traces to a Program Graph workorder (INV-R-01)
- [ ] `merge_order` reorders ready output only; does not create `depends_on` edges (INV-R-03)
- [ ] Orphan node (executable without program ref) rejected with clear error
- [ ] `ExecutionGraphDerived` published with stable content hash on derive
- [ ] Ready set empty when upstream dependencies incomplete
- [ ] PX-2 parallel excerpt: ready set ordering matches `merge_order` when deps satisfied
- [ ] Era I `compute_ready()` parity documented for BuilderGraph fixture (pass or documented gap)
- [ ] `make unit-builder-engine` green
- [ ] EWO report with traceability to §4.1–§4.2, §5, REQ-02/03/04
- [ ] **No MB2-Q1 PASS claim** in EWO report

---

## Acceptance tests (design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_program_graph_loads_px_exec_backlog` | Load minimal fixture mirroring px-exec workorder_backlog | §4.1 |
| `test_derive_only_from_program_graph` | Mutating completion state changes ready set; graph structure fixed | INV-R-02, MB2-Q-001 prep |
| `test_no_orphan_nodes` | Node without program ref raises | INV-R-01, MB2-Q-002 prep |
| `test_merge_order_tiebreak_only` | Reordering merge_order changes order, not dependency edges | INV-R-03, MB2-Q-003 prep |
| `test_blocked_until_deps_done` | EWO-004 blocked until EWO-003 done in fixture | §4.2 |
| `test_execution_graph_derived_event` | Derive publishes typed event with hash | §6.3, INV-R-08 |
| `test_parallel_wave_ready_set` | Multiple nodes ready when `execute_in_parallel` and deps met | §4.2 |
| `test_illegal_program_graph_rejected` | Circular depends_on in program yaml fails closed | §4.1 |
| `test_px2_merge_order_excerpt` | [003, 004, 006] ordering when all ready | §7.3 context / INV-R-03 |

Future gate tests (**not** part of EWO-003 exit):

- `MB2-Q-001` — full checkpoint-integrated derivation
- `MB2-Q-002` — orphan detection at scale
- `MB2-Q-003` — merge plugin integration (Phase 2)

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-EXEC-EWO-001 Event Model & Bus | **PASS** @ 2026-07-06 |
| MB2 SoR frozen @ 2026-07-05 | **PASS** |
| Program `AUTHORIZE px-exec` | **PASS** |
| Wave A engineering package | **PENDING** |
| Architect authorization for EWO-003 dispatch | **PENDING** |

**Unblocks:** PX-EXEC-EWO-004 (Job Queue requires derived graph + ready set)

**Parallel with:** PX-EXEC-EWO-002 (disjoint ownership)

---

## Exit criteria (WorkOrder complete)

| Criterion | Evidence |
|-----------|----------|
| Implementation on branch | `dependency.py`, `program_graph.py`, tests, fixtures |
| Verification green | `make unit-builder-engine` log in EWO report |
| Scope honored | No forbidden paths; no SoR diff; Program Graph files read-only |
| Traceability | EWO report maps deliverables → §4.1–§4.2, REQ-02/03/04 |
| Downstream ready | Ready set API available for EWO-004 job materialization |
| Qualification boundary | Report states: **does not satisfy MB2-Q1** |

---

## Constraints

- ADR-0042 §3 — graph derivation is Runtime-owned; Program Graph is Governance-read-only
- INV-R-03 — merge_order is tie-breaker, not dependency invention
- Do not conflate Era I `BuilderGraph` / STATE.yaml with Program Graph — bridge tests document mapping only
- `sor-compatibility-policy` — clarifications OK; no normative SoR edits
- Smallest correct diff; match `builder_engine/` style

---

## WO-TRACE

```text
PX-EXEC-EWO-001 PASS
  → Wave A engineering package review
  → AUTHORIZE PX-EXEC-EWO-003 (parallel with EWO-002)
  → implement → verify → PX-EXEC-EWO-003 report PASS
  → unblocks EWO-004
```
