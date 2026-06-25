# ASEP — Engineering Traceability Matrix (ETM)

- **Status:** Frozen (Architect 2026-06-25) — living document; **Tests** column filled as L4 ships
- **Authority:** DR-001 §7; ADR-0028 traceability requirement
- **Purpose:** Every runtime element must answer *"Why does this exist?"* by tracing upward to Vision. Prevents orphan components.
- **Companion:** `docs/platform/DR-001-constitutional-review.md`

---

## 0. Glossary (patterns — not L0 objects)

| Pattern | Definition | Where it lives |
|---------|------------|----------------|
| **Transition** | Legal state change (L2 row ID) | GSM §5 |
| **Command / Trigger** | Intent that invokes a transition | GSM Trigger column |
| **Transaction** | Atomic state commit after invariant pass | StateWriter + INV-B8 |
| **Projection** | Read-only view of GSM state (not authoritative) | CLI, YAML `status`, `lint-graph` |
| **Evaluation** | Per-cycle policy decision (not entity state) | C-03, C-04 |

**Traceability chain (normative):**

```text
Vision → ADR → Meta Model (L0) → Invariant (L1) → State → Transition (L2) → Runtime Module → Tests
```

If any code path cannot complete this chain, it is **orphan debt** (DR-001).

---

## 1. Vision anchors

| Vision source | Statement | Platform plane expression |
|---------------|-----------|---------------------------|
| `vision.md` §Contract-first | Freeze before implement | M-01, INV-B7, freeze-first pipeline |
| `vision.md` §Who builds it | Cursor agents = build-time workers | Worker (L0), INV-B9, ADR-0023 |
| `vision.md` §North star | Self-improving assistant (M18) | Era III–IV; GSM enables observability + replan |
| ADR-0026 §5 | Vision → Spec → ADR → Freeze → Impl → Gate | Milestone FSM M-01–M-04 |
| ADR-0028 | Constitution before features | L0–L2 before L4 |
| `era-model.md` | Agents are workers, not architecture | K-*, Worker engagement overlay |

---

## 2. Master traceability matrix

Columns: **Vision** | **ADR** | **L0** | **L1** | **State** | **Transition** | **Runtime module** | **Tests**

### 2.1 Governance & freeze-first

| Vision | ADR | L0 | L1 | State | Transition | Module | Tests |
|--------|-----|----|----|-------|------------|--------|-------|
| Contract-first gate-driven product | ADR-0010, ADR-0026 §5 | Milestone, Artifact | INV-B1, INV-B2, INV-B7 | `MS_*`, `ART_*` | M-01–M-04, A-03 | Human Operator; `docs/m{n}-promotion.md` | Manual gate YAML |
| Platform constitution | ADR-0028 | All L0 objects | INV-A*, INV-B* | all §3 | all §5 | `docs/platform/*` | DR-001 review |
| Sidecar isolation | ADR-0023 | Worker, Task | INV-B9 | `TASK_*` | K-02, K-03 | `builder_engine/` (no `backend.app`) | import lint |
| Spec before engine semantics | ADR-0025 §6 | Milestone | INV-B7 | `MS_SPEC_FROZEN` | M-02 | CheckRunner stages | M4 embed stage tests |

### 2.2 Strategic intent

| Vision | ADR | L0 | L1 | State | Transition | Module | Tests |
|--------|-----|----|----|-------|------------|--------|-------|
| Directed multi-milestone work | ADR-0028 | Goal | INV-B2 (G-02) | `GOAL_*` | G-01–G-05 | `/goal`, `knowledge/context/` | `[ ]` — DR-001-M02 |
| Goal achievement = promoted milestones | ADR-0010 | Goal, Milestone | INV-B2 | `GOAL_ACHIEVED`, `MS_PROMOTED` | G-02, M-04 | promotion docs, git tags | tag presence |

### 2.3 Workflow execution (Era I implemented)

| Vision | ADR | L0 | L1 | State | Transition | Module | Tests |
|--------|-----|----|----|-------|------------|--------|-------|
| Deterministic build orchestration | ADR-0025 | Task, Epic, Wave | INV-A1–A5, INV-B4–B6 | `TASK_*`, `WAVE_*` | T-02–T-07, W-03 | `state_machine.py`, `runtime.py` | `test_state_machine.py`, `test_runtime.py` |
| Graph structural validity | MB1 §8 | Task, Lock, Wave | INV-B4, INV-B5, INV-B6 | locks, waves | (invariant pass) | `validate.py` | validate unit tests |
| Atomic workflow writes | ADR-0028 | Workflow state | INV-B8 | all workflow | all commits | `state_io.py` | state_io tests |
| Ready set planning | L3 §3.3 | Task, Epic | INV-A5 | `TASK_READY` | T-01 | `planner.py` | planner tests |
| Schedule + dispatch | L3 §3.4 | Task, Lock, Worker | INV-B3, INV-B5 | `TASK_CLAIMED`, `TASK_RUNNING` | T-02, T-03, L-01, K-01 | `runtime.schedule()`, `scheduler.py` | runtime schedule tests |
| Validate + complete | L3 §3.6 | Task | INV-A1, INV-A2 | `TASK_VALIDATING`→`TASK_DONE` | T-04–T-06 | `runtime.sync()`, `checks.py` | sync tests |
| Validation failure | L3 §3.6, §9 | Task | INV-A1, INV-A4 | `TASK_FAILED`, `TASK_DEBUGGING` | T-07–T-09 | `state_machine.py` | `test_failure_recovery_loop` |
| Wave advance | L3 §3.9 | Wave, Epic | INV-B6 | `WAVE_COMPLETED` | W-02, W-03 | `runtime.sync()` wave logic | wave tests |
| CLI projections | ADR-0025 §2 | all workflow | — | projected | — | `cli.py` lint/status/ready/schedule/sync | cli tests |

### 2.4 Workflow container

| Vision | ADR | L0 | L1 | State | Transition | Module | Tests |
|--------|-----|----|----|-------|------------|--------|-------|
| Bounded platform work body | ADR-0026 | Epic | INV-A3 (E-02) | `EPIC_*` | E-01–E-03 | `STATE.yaml` epic, status | `[ ]` — DR-001-M04 |
| Epic open | ADR-0026 §3 tracks | Epic, Milestone | INV-B8 (proposed E-01) | `EPIC_OPEN` | E-01 | STATE.yaml | `[ ]` |
| Epic close | Era I closure | Epic | INV-A3 | `EPIC_CLOSED` | E-03 | STATE `status: closed` | manual |

### 2.5 Resources

| Vision | ADR | L0 | L1 | State | Transition | Module | Tests |
|--------|-----|----|----|-------|------------|--------|-------|
| Produced outputs | ADR-0001 | Artifact | INV-B1 | `ART_*` | A-01–A-03 | git, filesystem | `[ ]` |
| Exclusive file access | MB1 §8.6 | Lock, Task | INV-B3, INV-B4 | `LOCK_*` | L-01, L-02 | `file_locks`, scheduler | validate tests |
| Observe read model | L3 §3.1 | Snapshot | INV-B8 | `SNAP_*` | S-01, S-02 | `[planned] observe.py` | `[ ]` MB2 Ph4 |
| Worker dispatch | ADR-0023 | Worker, Task | INV-B9 | `WK_*` | K-01–K-04 | manifest, executor | `[ ]` |

### 2.6 Engineering cycle (L3 → L2 binding)

| Vision | ADR | L0 | L1 | State | Transition | Module | Tests |
|--------|-----|----|----|-------|------------|--------|-------|
| Repeatable engineering loop | L3 §1 | Snapshot, Task, Event | INV-B8 | `CYCLE_*` | C-01–C-15 | `[planned] cycle.py` | `[ ]` MB2 Ph4 |
| Observe | L3 §3.1 | Snapshot | INV-B8 | `SNAP_*`, `CYCLE_OBSERVING` | C-01, C-02, S-* | `[planned] observe.py` | `[ ]` |
| Evaluate policies | L3 §3.2, ADR-0028 | Policy | (not invariant) | `CYCLE_POLICY_EVAL` | C-03, C-04 | `[planned] policy stub` | `[ ]` MB2 |
| Plan | L3 §3.3 | Task, Epic | INV-A5 | `CYCLE_PLANNING` | C-05, T-01 | `planner.py` | planner tests |
| Schedule | L3 §3.4 | Task, Lock | INV-B3–B6 | `CYCLE_SCHEDULING` | C-06 | `runtime.schedule()` | runtime tests |
| Execute | L3 §3.5 | Worker, Artifact | INV-B9 | `CYCLE_EXECUTING` | C-07, K-*, A-* | manifest, workers | `[ ]` |
| Validate | L3 §3.6 | Task | INV-A1, A2 | `CYCLE_VALIDATING` | C-08, C-09, T-04–07 | `runtime.sync()` | sync tests |
| Merge | L3 §3.7 | Task | INV-A2 | `CYCLE_MERGING` | C-10, C-11, T-06 | skill / `[planned]` | `[ ]` |
| Publish events | L3 §3.8 | Event | — | `CYCLE_PUBLISHING` | C-12 | `[planned] events.py` | `[ ]` MB2 Ph5 |
| Update state | L3 §3.9 | Wave, Epic, Lock | INV-B8 | `CYCLE_UPDATING` | C-13, W-*, E-*, L-02 | `state_io`, sync | state tests |
| Replan | L3 §3.10 | Task, Epic | INV-A4 | `CYCLE_REPLANNING` | C-14, C-15, T-09 | `[planned] replan` | `[ ]` MB2 |

### 2.7 Invariants (L1 → enforcement)

| Vision | ADR | L0 | L1 | Enforced on | Transition / pass | Module | Tests |
|--------|-----|----|----|-------------|-------------------|--------|-------|
| No illegal task states | ADR-0025 | Task | INV-A1–A4 | transition | T-04–T-09 | `[planned] gsm_task.py` | `[ ]` Ph1 |
| No done without validation | ADR-0025 §4 | Task | INV-A2 | T-05, T-06 | T-05, T-06 | sync | sync tests |
| Dependency order | MB1 §8 | Task, Epic | INV-A5 | T-02, T-03 | T-02 | validate.py | validate tests |
| Frozen artifacts immutable | ADR-0026 §5 | Artifact | INV-B1 | all writes | A-03 guard | `[planned] invariants.py` | `[ ]` Ph2 |
| Promote only when validated | ADR-0010 | Milestone | INV-B2 | M-04, G-02 | M-04 | promotion docs | gate YAML |
| Lock discipline | MB1 §8.5–8.7 | Lock, Task | INV-B3–B5 | schedule, commit | L-01, T-02 | validate, scheduler | validate tests |
| Wave coherence | MB1 §8.7 | Wave, Task | INV-B6 | in-flight | T-03, W-* | validate.py | validate tests |
| Planner read-only on frozen | ADR-0028 | Artifact, State | INV-B7 | plan | M-01, C-05 | `[planned]` | `[ ]` |
| Atomic writes | ADR-0028 | Workflow state | INV-B8 | every commit | all C-* writes | state_io | `[ ]` Ph2 |
| Worker boundary | ADR-0023 | Worker | INV-B9 | execute | K-02, K-03 | runtime boundary | import lint |

---

## 3. MB2 deliverable traceability (rebase target)

When rebasing `docs/superpowers/specs/…-mb2-adaptive-runtime-design.md`, every row MUST appear:

| MB2 deliverable (original) | Transition IDs | L0 | L1 | Planned module | Planned tests |
|----------------------------|----------------|----|----|----------------|---------------|
| `ObservedSnapshot` | S-01, S-02, C-01, C-02 | Snapshot | INV-B8 | `observe.py` | `test_observe.py` |
| Policy stub | C-03, C-04 | Policy | (policy not inv) | policy stub | `test_policy.py` |
| Extended Plan | C-05, T-01 | Task, Epic | INV-A5, INV-B7 | `planner.py` extend | planner tests |
| Build event bus | C-12, §7 all events | Event | — | `events.py` | `test_events.py` |
| Minimal Replan | C-14, T-09 | Task | INV-A4 | `cycle.py` | `test_cycle.py` |
| `EngineeringRuntimeCycle` | C-01–C-15 | Cycle | INV-B8 | `cycle.py` | `test_cycle.py` |
| `WorkflowRuntime` rename | all | Engineering Runtime | — | `runtime.py` rename | regression |
| Class A guards | T-* | Task | INV-A* | `gsm_task.py` | `test_gsm_task.py` |
| Class B pass | all commits | Workflow | INV-B* | `invariants.py` | `test_invariants.py` |
| Recovery CLI | T-08, T-09 | Task | INV-A4 | `cli debug/retry` | recovery tests |

**Rebase rule:** Remove any MB2 deliverable with empty Transition IDs column.

---

## 4. Orphan prevention rules

Before merging any `builder_engine/` PR:

1. Fill a new ETM row or extend an existing row.
2. Link PR description: `ETM §2.x row, Transition T-xx`.
3. If no transition exists → **stop** — add L2 transition first (Architect) or declare governance exemption in DR log.

**Projections** (`cli.py` commands) trace to "Projection of Transition X" — they do not need new L0 objects.

**Worker prompts** (Cursor Task) trace to Worker + Task + Transition K-* / Execute phase — not to new platform objects.

---

## 5. DR-001 action traceability

| DR finding | ETM section | Resolution |
|------------|-------------|------------|
| DR-001-M02 Goal inv gaps | §2.2 | Optional L2 §5.1 patch; G-01 tests `[ ]` |
| DR-001-M03 Task birth | §2.3 | T-00 row or governance exemption note |
| DR-001-M04 Milestone–Epic | §2.4 | E-01 guard row; track metadata in STATE |
| DR-001-M05 Policy lifecycle | §0 Evaluation pattern | Accepted |
| DR-001-m06 C-07 owner | §2.6 | Split: K-03 (Worker) then T-04 (Runtime) |

---

## 6. Product plane boundary (explicit non-trace)

These **do not** appear in Platform ETM rows (Product Track owns its traceability):

| Product concept | Product authority |
|-----------------|-------------------|
| GraphState, LangGraph nodes | M-series specs, ADR-0007 |
| `/chat`, documents, memory | M1–M3 specs |
| Product event outbox | ADR-0006, `events` table |
| Supervisor, Planner, Router agents | M5 spec, ADR-0027 |

**Boundary trace:** Platform `Milestone` (M4, M5, MB2) ↔ Product milestone tags — single shared object per L0 §2.

---

## 7. Freeze record

- [x] Glossary: Transition, Command, Transaction, Projection, Evaluation
- [x] Vision anchors mapped
- [x] Era I implemented modules traced
- [x] L1 invariants traced to modules and transitions
- [x] L3 phases traced to C-* transitions
- [x] MB2 rebase template (§3)
- [x] Orphan prevention rules (§4)
- [x] DR-001 actions cross-referenced (§5)
- [x] Product boundary explicit (§6)

**Living columns:** Tests filled incrementally during L4. Empty `[ ]` = planned, not orphan.

**Next:** Architect sign-off on DR-001 + ETM → MB2 rebase → implementation.

---

## 8. References

- DR-001 `docs/platform/DR-001-constitutional-review.md`
- L0–L3 platform docs · ADR-0025, ADR-0026, ADR-0028, ADR-0010, ADR-0023
- `knowledge/project/vision.md`
- `plans/l2-global-state-machine-plan.md`
