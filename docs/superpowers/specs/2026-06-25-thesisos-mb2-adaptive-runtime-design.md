# ASEP — MB2 Adaptive Runtime Design Spec (L4)

- **Date:** 2026-06-25 (rebased 2026-06-25)
- **Status:** **Architect Approved 2026-06-25** — spec frozen; L4 Phase 0 authorized; MB2 D1–D11 after Phase 0 gate.
- **Milestone:** Platform Track **MB2** — L4 implementation of frozen constitution (not a redesign).
- **Scope:** Complete the Engineering Runtime processor head and tail (Observe → Policies → Plan extend → Publish → Replan) and wire event emission into existing Schedule/Validate/Update paths. **Does not modify** L0, L1, BS, L2, L3, or existing ADRs.
- **Authority chain:** Vision → ADR → L0 → L1 → BS → L2 → L3 → ETM → **this spec** → Implementation (`plans/mb2-adaptive-runtime-plan.md` + prerequisite `plans/l2-global-state-machine-plan.md` Ph 1–2).
- **Authors:** ThesisOS Platform Team
- **Builds on:** Era I (`m4-complete`, `docs/mb1-phase2-gate.md`); constitution frozen through DR-001 + ADR-0029

> **Rebase rule (Architect 2026-06-25):** This spec **conforms** to the constitution; it does not extend it. Any gap discovered during implementation → record in §11 → new ADR or DR — **never** amend L0–L3 inside MB2 work.

---

## 1. Vision

| Vision source | MB2 satisfies |
|---------------|---------------|
| `vision.md` §Contract-first, gate-driven | Observe + Policy stub enforce freeze/gate awareness before schedule |
| `vision.md` §Who builds it | Workers remain external; runtime orchestrates Delegation behavior only |
| ADR-0026 §5 lifecycle | MB2 enables systematic Observe→Replan loop (Era II processor completion) |
| ADR-0028 layered constitution | MB2 is **L4** — concretizes L3 phases not yet in Era I code |
| ADR-0029 Behavioral Semantics | Every module implements a named BS behavior — no invented semantics |
| `era-model.md` Era II | Adaptive Workflow Intelligence — event-driven, observable factory |

**Era I delivered:** Schedule → Execute (manifest) → Validate → Update State.

**MB2 delivers:** Observe → Evaluate Policies → Plan (extended) → **Publish Events** → Replan — orchestrated by `EngineeringRuntimeCycle`, without changing packet FSM semantics (ADR-0025).

**Success criterion:** `builder-engine cycle --dry-run` runs C-01→C-05; post-`sync` postflight runs C-12→C-14; typed events append to `.builder-engine/events.jsonl`; failed validation produces `ReplanProposal` (proposal only); M0–M4 + `builder_engine` tests green; **no** `import backend.app`.

---

## 2. Constitutional acceptance criteria

Every MB2 deliverable and PR must pass:

| Criterion | Rule |
|-----------|------|
| **Constitutional Completeness** | Traceable Vision → ADR → L0 → L1 → BS → L2 → L3 without gaps |
| **Constitutional Minimality** | No new L0 objects, L1 invariants, L2 transitions, or BS behaviors |
| **Behavioral Purity** | `Behavior (BS) → Implementation` only — never `Implementation → New Behavior` |
| **Traceability Closure** | ETM row ends with Observability **and** Evidence (verifiable artifact) |

---

## 3. Deliverable traceability matrix (normative)

Columns: **V** Vision · **A** ADR · **M** L0 · **I** L1 · **B** BS · **S** L2 state · **T** L2 transition · **L3** cycle · **E** event · **Mod** module · **O** observability · **Test** · **Evidence**

### D1 — `ObservedSnapshot` / Observe module

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Gate-driven factory | 0028, 0023 | Snapshot | INV-B8 | Observing | `SNAP_*` | S-01,S-02,C-01,C-02 | Observe §3.1 | `SnapshotCreated`, `StateObserved` | `observe.py` | `observe` CLI JSON; `staleness_reasons` | `test_observe.py` | frozen snapshot dataclass; no STATE mutation |

### D2 — Policy stub

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Contract-first | 0028, 0026 §8 | Policy | (eval not inv) | Escalation | `CYCLE_POLICY_EVAL` | C-03,C-04 | Evaluate §3.2 | `PolicyAllowed`, `PolicyBlocked` | `policy.py` | `PolicyDecision.outcome`; violations list | `test_policy.py` | block when implementer lacks `checks` (policy hint per L1 litmus) |
| Sidecar isolation | 0023 | — | INV-B8 on commit | — | — | — | — | — | `policies.yaml` | YAML load log | policy YAML sample | file exists under `plans/builder/` |

> **Note:** `validate_graph` **errors** are L1 invariants (fail-closed via D-prereq `invariants.py`), not policy. Policy stub evaluates **warnings** + declarative YAML rules only.

### D3 — Extended `Plan`

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Deterministic orchestration | 0025 | Task, Epic | INV-A5, INV-B7 | Scheduling | `TASK_READY` | T-01,C-05 | Plan §3.3 | `PlanGenerated`, `PlanEmpty` | `planner.py` | `plan` CLI; ready set listing | planner tests | `ready_packets` == `compute_ready()` parity |

### D4 — Build event bus

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Observable factory | 0028, 0006 pattern | Event | — | (emission) | `CYCLE_PUBLISHING` | C-12 | Publish §3.8 | `EventsPublished` + per-type §7 | `events.py` | `events --tail N` | `test_events.py` | `.builder-engine/events.jsonl` append-only lines |

**Event catalog (MB2 minimum — must match L2 §7):**  
`StateObserved`, `PolicyAllowed`, `PolicyBlocked`, `PlanGenerated`, `PlanEmpty`, `TaskScheduled`, `LockAcquired`, `ValidationPassed`, `ValidationFailed`, `StateUpdated`, `WaveAdvanced`, `MergeAccepted`, `MergeRejected`, `Replanned`, `RecoveryTaskCreated`, `WorkerDispatched`, `WorkerReported`, `CycleStarted`, `CycleHalted`

No events outside L2 §7 without constitution amendment.

### D5 — Minimal Replan

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Self-improving direction | 0029 | Task, Epic | INV-A4, INV-B7 | Replanning, Recovery | `CYCLE_REPLANNING` | C-14,C-15,T-09 | Replan §3.10 | `Replanned`, `RecoveryTaskCreated` | `replan.py` | proposal JSON; no STATE auto-write | `test_replan.py` | `ReplanProposal` after `ValidationFailed` fixture |

### D6 — `EngineeringRuntimeCycle`

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Era II processor | 0028 | Snapshot, Event, Policy | INV-B8 | Observing…Replanning | `CYCLE_*` | C-01–C-15 | all §3 | per phase | `cycle.py` | `cycle --dry-run` trace | `test_cycle.py` | preflight returns (Snapshot, PolicyDecision, Plan) |

### D7 — CLI projections (additive)

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADR-0025 projections | 0025 §2 | all workflow | — | — | projected | — | — | — | `cli.py` | stdout tables | cli tests | existing commands unchanged semantics |

Commands: `observe`, `plan`, `cycle`, `events`, `merge-check` — **projections only**, not authoritative state.

### D8 — Merge eligibility stub

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Evidence before merge | 0025 §4 | Task, Artifact | INV-A2 | Merging | `CYCLE_MERGING` | C-10,C-11,T-06 | Merge §3.7 | `MergeAccepted`, `MergeRejected` | `merge.py` | `merge-check` CLI | merge stub test | always `deferred`; **no git mutations** |

### D9 — Wire Schedule / Validate / Update (event emission)

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MB1 parity + observability | 0025 | Task, Lock, Wave | INV-A*, INV-B* | Scheduling, Validating | `TASK_*`, `WAVE_*` | T-02–T-07,W-03,L-01,L-02 | Schedule, Validate, Update | `TaskScheduled`, `ValidationPassed`, `StateUpdated`, `WaveAdvanced` | `runtime.py`, `scheduler.py`, `checks.py`, `state_io.py` | schedule/sync CLI; CheckRunner output | existing + new emit tests | MB1 Phase 2 behavior preserved |

### D10 — `EngineeringRuntime` rename

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ASEP terminology | 0028, 0029 | Engineering Runtime | — | Delegation | — | — | — | — | rename `WorkflowRuntime` | grep | regression | zero `WorkflowRuntime` in `builder_engine/` |

### D11 — Tests & promotion

| V | A | M | I | B | S | T | L3 | E | Mod | O | Test | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Gate-driven | 0010 | Milestone `mb2` | — | Promotion | `MS_*` | M-03 (manual) | Validate gate | `MilestoneValidated` | `docs/mb2-phase-gate.md` | gate YAML | integration cycle test | `mb2-phase-gate.md` all green |

---

## 4. Prerequisites (not MB2 scope — constitutional minimality)

These deliverables live in `plans/l2-global-state-machine-plan.md` and **must complete before D9 wire runtime**:

| Prereq | B | T | Mod | Evidence |
|--------|---|---|-----|----------|
| L2 Ph1 Executable Task FSM | Validating, Claiming | T-01–T-12 | `gsm_task.py` | `test_gsm_task.py` green |
| L2 Ph2 Class B invariant pass | all commits | INV-B* | `invariants.py` | `InvariantViolation` on illegal commit |

If prerequisite work reveals a constitution gap → §11 log → stop MB2 → DR/ADR separately.

---

## 5. Scope & non-goals

### 5.1 In scope

Deliverables **D1–D11** only.

### 5.2 Non-goals (unchanged — constitutional boundaries)

| Forbidden | Rationale | If needed |
|-----------|-----------|-----------|
| New L0/L1/BS/L2/L3 artifacts | Minimality | DR + constitution amendment |
| Product LangGraph / `backend.app` | ADR-0023 | M5 Product spec |
| Global project FSM replacing packet FSM | ADR-0025 | Already in L2 |
| Full Policy Engine | MB3+ | ADR when scope frozen |
| Observability web UI | MB3+ | Separate spec |
| Auto git merge / Integrator worker | Merge behavior external | C-10/C-11 eligibility only |
| Auto-editing STATE/ADRs from replan | INV-B7, BS Replanning | Human Operator |
| Auto recovery packet creation | Q-MB2-3 resolution | Proposal only |

```yaml
product_langgraph: false
backend_app_imports: false
global_project_fsm: false
auto_merge: false
auto_spec_edits: false
new_constitution_objects: false
new_l2_transitions: false
```

---

## 6. Architecture

### 6.1 Component model (L4 modules → BS behaviors)

```text
Build Control Plane (rules only — policies.yaml, governance)
        │
        ▼
Engineering Runtime (builder_engine/)
  observe.py    → Observing
  policy.py     → Escalation (evaluation)
  planner.py    → Scheduling (extended Plan)
  events.py     → (emission infrastructure)
  replan.py     → Replanning, Recovery
  merge.py      → Merging (stub)
  cycle.py      → C-01…C-15 orchestration
  runtime.py    → EngineeringRuntime (rename) — Schedule, Validate, Update
  gsm_task.py   → [prerequisite] L2 transitions
  invariants.py → [prerequisite] L1 enforcement
        │
        ▼
Execution Workers (external — replaceable LLM/human)
```

### 6.2 Sidecar boundary

| Concern | Owner | MB2 access |
|---------|-------|------------|
| `STATE.yaml` | Workflow state | read/write via `state_io` + invariant pass |
| `.builder-engine/events.jsonl` | Build event bus | append-only |
| `backend/app/*` | Product Plane | **forbidden** |

---

## 7. L3 phase mapping (implementation targets)

| L3 §3 | BS | MB2 deliverable | Status Era I |
|-------|-----|-----------------|------------|
| Observe | Observing | D1 | partial (`lint-graph`, `status`) |
| Evaluate Policies | Escalation | D2 | `validate_graph` only |
| Plan | Scheduling | D3 | `compute_ready` only |
| Schedule | Scheduling, Claiming | D9 wire | ✅ MB1 |
| Execute | Delegation | external | ✅ manifest |
| Validate | Validating | D9 wire | ✅ sync |
| Merge | Merging | D8 stub | manual |
| Publish Events | — | D4, D9 | none |
| Update State | — | D9 wire | partial |
| Replan | Replanning | D5, D6 | none |

---

## 8. Interfaces

*(Unchanged from pre-rebase — dataclass shapes preserved.)*

See §6 in prior revision: `ObservedSnapshot`, `PolicyDecision`, `Plan`, `BuildEvent`, `EngineeringRuntimeCycle.run_preflight/postflight`.

**Rename:** `WorkflowRuntime` → `EngineeringRuntime` (D10).

---

## 9. Data flows

### 9.1 Preflight (C-01 → C-05)

```text
StateObserver → ObservedSnapshot (S-01,S-02)
PolicyEngine → PolicyDecision (C-03|C-04)
build_plan → Plan (C-05)
bus.publish(PlanGenerated | PlanEmpty)
```

### 9.2 Execution slice (unchanged semantics)

```text
EngineeringRuntime.schedule() → T-02,T-03,L-01,K-01 + events
[external workers — C-07a,b]
EngineeringRuntime.sync() → T-04…T-07,W-03,L-02 + events
```

### 9.3 Postflight (C-12 → C-14)

```text
bus.publish(EventsPublished)
minimal_replan → ReplanProposal (C-14)
operator applies proposal — no auto STATE write (INV-B7)
```

---

## 10. Promotion gate (`docs/mb2-phase-gate.md`)

```yaml
constitutional_traceability: green   # §3 all rows populated
prerequisite_gsm: green              # l2 plan Ph1-2
observed_snapshot: green
policy_stub: green
extended_plan: green
build_event_bus: green
cycle_preflight: green
cycle_postflight: green
schedule_sync_parity: green
event_emission: green
merge_eligibility_stub: green
engineering_runtime_rename: green
no_backend_imports: green
no_new_constitution_artifacts: green # minimality audit
m0_m1_m2_m3_m4_tests: green
builder_engine_tests: green
etm_rows_complete: green
documentation: complete
knowledge_updated: true
```

---

## 11. Constitutional gap log

| ID | Discovered | Action | MB2 blocked? |
|----|------------|--------|--------------|
| — | *(none at rebase)* | — | — |

**Process:** If implementation finds a gap → add row here → open DR/ADR → **do not** patch L0–L3 in MB2 branch.

---

## 12. Implementation sequencing

```text
Prerequisite: l2-global-state-machine-plan Ph1–2 (gsm + invariants)
Phase 1: D1 Observe
Phase 2: D2 Policy
Phase 3: D3 Plan extend
Phase 4: D4 Event bus
Phase 5: D6 Cycle + D9 wire + D8 merge stub
Phase 6: D5 Replan
Phase 7: D10 rename + D7 CLI + D11 promotion
```

Detail: `plans/mb2-adaptive-runtime-plan.md` (updated for traceability).

---

## 13. Freeze record

- [x] All deliverables trace §3 matrix (Completeness)
- [x] No new constitution artifacts (Minimality)
- [x] Every module maps to BS §2 (Purity)
- [x] Every row has Test + Evidence (Closure)
- [x] Prerequisites separated from MB2 scope
- [x] Constitutional gap log §11 empty
- [x] Aligns with L0, L1, BS, L2, L3, ETM, DR-001, ADR-0029
- [x] **Architect sign-off on rebased spec:** Approved 2026-06-25 (spec only; L4 Phase 0 authorized; no MB2 deliverables until Phase 0 complete)

**Implementation authorized:** L4 Phase 0 (L2 plan Ph1–2: GSM + invariant pass) per Architect conditions. MB2 deliverables D1–D11 after Phase 0 gate.

---

## 14. References

- Constitution: L0, L1, `behavioral-semantics.md`, L2, L3
- DR-001, ADR-0026, ADR-0028, ADR-0029, ADR-0025, ADR-0023, ADR-0010, ADR-0006
- `engineering-traceability-matrix.md` §3
- `plans/l2-global-state-machine-plan.md` (prerequisite)
- `plans/mb2-adaptive-runtime-plan.md`
