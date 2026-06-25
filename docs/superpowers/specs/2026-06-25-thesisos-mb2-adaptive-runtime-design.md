# ASEP — MB2 "Adaptive Runtime" Design Spec

- **Date:** 2026-06-25
- **Status:** Frozen (Architect 2026-06-25) — **no MB2 implementation until this spec is merged and Planner plan delivered.**
- **Scope:** Platform Track milestone **MB2** only — translate `docs/platform/runtime-model.md` into Engineering Runtime + Build Control Plane hooks. **NOT** a global project FSM ticket; **NOT** Product Plane work.
- **Authors:** ThesisOS Platform Team
- **Builds on:** Era I closure (`m4-complete`, `docs/mb1-phase2-gate.md`), frozen `docs/platform/runtime-model.md`, `docs/platform/era-model.md`, ADR-0026
- **New ADR:** None required unless build-bus persistence choice becomes irreversible (default: filesystem append-only under `.builder-engine/`)

---

## 1. Vision

Era I delivered a **vertical slice** of the Engineering Runtime: Schedule → Execute (manifest) → Validate → Update State. Era II MB2 **completes the processor head and tail** so the Build Control Plane can react to outcomes without heroic operator intervention:

```text
Observe State ──► Evaluate Policies ──► Plan (extended) ──► … existing MB1 loop …
                                                              │
                                                              ▼
                                                    Publish Events (build bus)
                                                              │
                                                              ▼
                                                    Replan (minimal) ──► Observe
```

**Success criterion:** A single `builder-engine cycle` (or equivalent orchestration entry) runs Observe → Policies → Plan before `schedule`, and Publish → Replan after `sync`; typed build events append to a local bus; failed validation triggers a minimal replan proposal; **packet-level FSM (ADR-0025) unchanged**; M0–M4 product suites and `builder_engine` tests stay green.

**MB2 meaning:** Implement the frozen **Engineering Runtime** phases as modules and tests — translate `runtime-model.md`, do **not** invent a parallel "Agent OS" or global workflow FSM.

---

## 2. Scope & non-goals

### 2.1 In scope (MB2 MUST ship)

| # | Deliverable |
|---|-------------|
| 1 | **`ObservedSnapshot`** — unified derived read model (STATE + git + CI stub + queue depth) |
| 2 | **Policy stub** — `PolicyDecision` after Observe; wraps `validate_graph` + declarative YAML rules |
| 3 | **Extended `Plan`** — ready set + wave intent + surfaced blockers + critical-path hints (not full optimizer) |
| 4 | **Build event bus** — typed, append-only, filesystem-backed; producers in Validate/Schedule/State/Replan |
| 5 | **Minimal Replan** — on `ValidationFailed`, propose recovery (unblock dependents, suggest fix packet metadata) |
| 6 | **`EngineeringRuntimeCycle`** — orchestrates Observe→Policies→Plan before schedule; Publish→Replan after sync |
| 7 | **CLI projections** — `observe`, `plan`, `events` (tail), extend `status` with snapshot summary |
| 8 | **Tests** — unit per module + integration cycle test with fixture STATE |
| 9 | **Promotion** — `docs/mb2-phase-gate.md`, knowledge mirror |

### 2.2 Non-goals (hard boundary)

| Forbidden | Rationale |
|-----------|-----------|
| Product LangGraph topology / new graph nodes | Product Plane — M5+ specs |
| `import backend.app` or product DB access from `builder_engine/` | ADR-0023, ADR-0026 |
| Global project FSM replacing packet FSM | ADR-0025 remains authoritative for packet execution |
| Full Policy Engine (Era II late / MB3) | MB2 ships **stub** only |
| Observability dashboard / web UI | MB3+ |
| Automated git merge / Integrator worker | Merge eligibility hook only; execution stays external |
| Auto-editing ADRs, specs, or `STATE.yaml` recovery packets | Architect / human gate |
| Product event outbox coupling | Build bus is sidecar-local unless future ADR |

```yaml
product_langgraph: false
backend_app_imports: false
global_project_fsm: false
auto_merge: false
auto_spec_edits: false
```

---

## 3. Architecture

### 3.1 Component model

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    BUILD CONTROL PLANE (hooks only)                      │
│  strategic objectives · ADR/spec authority · policy YAML (declarative)   │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ supplies rules + intent
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ENGINEERING RUNTIME (builder_engine/)               │
│                                                                          │
│  observe.py ──► ObservedSnapshot                                         │
│       │                                                                  │
│       ▼                                                                  │
│  policy.py ──► PolicyDecision (allow | block | escalate)               │
│       │                                                                  │
│       ▼                                                                  │
│  planner.py ──► Plan (extended; wraps compute_ready)                     │
│       │                                                                  │
│       ├──► scheduler.py + runtime.schedule()  [MB1 ✅]                   │
│       ├──► executor.py manifest              [MB1 ✅]                   │
│       ├──► checks.py + runtime.sync()        [MB1 ✅]                   │
│       │                                                                  │
│       ▼                                                                  │
│  events.py ──► BuildEventBus (.builder-engine/events.jsonl)             │
│       │                                                                  │
│       ▼                                                                  │
│  replan.py ──► ReplanProposal (minimal)                                  │
│                                                                          │
│  cycle.py ──► EngineeringRuntimeCycle (orchestrator, not a new FSM)      │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    Execution workers (external — Cursor Task, human)
```

### 3.2 Sidecar boundary (normative)

| Concern | Owner | MB2 access |
|---------|-------|------------|
| `plans/builder/STATE.yaml` | Workflow state (filesystem) | read/write via `state_io` only |
| `.builder-engine/events.jsonl` | Build event bus | append-only writes |
| `.builder-engine/last-dispatch-manifest.json` | Execute projection | read (existing) |
| `backend/app/*` | Product Plane | **forbidden import** |
| Git working tree | Authority for merge | read-only status in Observe |

---

## 4. Phase mapping — all 10 Engineering Runtime phases

Each row traces `runtime-model.md` §3 to modules. **MB2 implements** rows marked 🟢; **carry forward** rows marked ⚪ (wire + events only).

### 4.1 Observe State 🟢

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/observe.py` — `StateObserver`, `ObservedSnapshot` |
| **CLI projection** | `builder-engine observe`, enriched `status` |
| **Inputs** | `STATE.yaml` (via `BuilderGraph`), optional `git` porcelain status, CI status stub (`checks.run_stage("ci")` exit code cache or `unknown`), `.builder-engine/` queue depth (in-flight + ready counts), knowledge drift flag (file mtime stub) |
| **Outputs** | `ObservedSnapshot` — immutable dataclass: `observed_at`, `graph`, `git_branch`, `git_dirty`, `ci_status`, `ready_count`, `in_flight_count`, `blockers`, `staleness_reasons` |
| **Events** | `StateObserved` (published when cycle starts Observe) |
| **Failure** | Partial snapshot (`staleness_reasons` non-empty) → cycle aborts before Schedule |
| **Acceptance** | Snapshot includes all packets + locks; git/CI fields present; second observe in same second produces new immutable instance; abort if STATE unreadable |

### 4.2 Evaluate Policies 🟢

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/policy.py` — `PolicyEngine` (stub), `PolicyDecision` |
| **Config** | `plans/builder/policies.yaml` (optional; default rules embedded) |
| **Inputs** | `ObservedSnapshot`, policy set (YAML + `validate_graph` invariants) |
| **Outputs** | `PolicyDecision`: `allow` \| `block` \| `escalate` + `violations: list[str]` |
| **Events** | `PolicyViolated`, `PolicyEscalated` |
| **Failure** | `block` → cycle stops before Plan; `escalate` → emit event, continue with warning |
| **Acceptance** | Implementer without `checks` → `block` (§8.8); invalid graph → `block`; frozen spec gate example rule (YAML): `product_spec_frozen: m4` blocks embed-stage scheduling if M4 gate doc missing; `validate_graph` warnings alone → `allow` |

### 4.3 Plan 🟢 (extend)

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/planner.py` — extend with `Plan`, `build_plan()` |
| **CLI projection** | `builder-engine plan` (replaces/aliases `ready` detail) |
| **Inputs** | `ObservedSnapshot`, `PolicyDecision`, optional strategic objective string from STATE metadata |
| **Outputs** | `Plan`: `ready_packets`, `wave_intent`, `blockers`, `critical_path_packet_ids` (longest dependency chain heuristic), `empty: bool` |
| **Events** | `PlanGenerated`, `PlanEmpty` |
| **Failure** | Empty plan with open blockers → `escalate` policy path |
| **Acceptance** | `build_plan()` ready set equals `compute_ready()` for same graph; critical path non-empty when deps exist; `PlanEmpty` when no ready and wave incomplete |

### 4.4 Schedule ⚪

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/scheduler.py`, `builder_engine/runtime.py` — `WorkflowRuntime.schedule()` |
| **Inputs** | `Plan.ready_packets` (or graph), `ObservedSnapshot` |
| **Outputs** | CLAIMED state, `DispatchManifest`, file locks |
| **Events** | `TaskScheduled`, `LockAcquired` (MB2: emit via bus on schedule) |
| **Failure** | Concurrent in-flight → abort (existing) |
| **Acceptance** | MB1 Phase 2 behavior preserved; events appended on successful schedule |

### 4.5 Execute ⚪

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/executor.py` — manifest only |
| **Inputs** | `DispatchManifest`, worker type |
| **Outputs** | External worker artifacts; `.builder-engine/last-dispatch-manifest.json` |
| **Events** | `TaskStarted`, `TaskCompleted`, `TaskFailed` (MB2: **no emitter** — workers external; manifest read by operator) |
| **Acceptance** | No runtime code changes except bus docs; manifest schema unchanged |

### 4.6 Validate ⚪

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/checks.py`, `builder_engine/runtime.py` — `WorkflowRuntime.sync()` |
| **Inputs** | In-flight packets, `checks` stages |
| **Outputs** | Pass/fail per packet; VALIDATING → DONE or FAILED |
| **Events** | `ValidationPassed`, `ValidationFailed` (MB2: emit on sync) |
| **Acceptance** | Failed checks emit `ValidationFailed` with packet id + failed stage list |

### 4.7 Merge ⚪ (gap — eligibility only)

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/merge.py` — `merge_eligibility(snapshot, packet)` stub |
| **Inputs** | Passed validation, integration notes |
| **Outputs** | `MergeEligibility`: `eligible` \| `deferred` \| `rejected` + reason |
| **Events** | `MergeAccepted`, `MergeRejected` (MB2: emit only when operator invokes `builder-engine merge-check` stub CLI) |
| **Failure** | Not eligible → event + replan input |
| **Acceptance** | Stub always `deferred` with reason "integrator external"; no git mutations |

### 4.8 Publish Events 🟢

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/events.py` — `BuildEvent`, `BuildEventBus`, `EventType` enum |
| **Storage** | `.builder-engine/events.jsonl` (append-only, one JSON object per line) |
| **Inputs** | Outcomes from Observe, Policies, Plan, Schedule, Validate, Update State, Replan |
| **Outputs** | Persisted typed events; in-memory fan-out to registered handlers (tests only) |
| **Events** | All §4 event types (catalog below) |
| **Rule** | Phases call `bus.publish()`; no cross-phase direct callbacks for audit/replan |
| **Acceptance** | Publish is append-only; replay returns ordered events; consumers idempotent; crash between write and publish prevented by write-before-emit |

**Event catalog (MB2 minimum):**

`StateObserved`, `PolicyViolated`, `PolicyEscalated`, `PlanGenerated`, `PlanEmpty`, `TaskScheduled`, `LockAcquired`, `ValidationPassed`, `ValidationFailed`, `StateUpdated`, `WaveAdvanced`, `MergeAccepted`, `MergeRejected`, `Replanned`, `RecoveryTaskCreated`

### 4.9 Update State ⚪

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/state_io.py`, `builder_engine/runtime.py` — `save_raw_state` in schedule/sync |
| **Inputs** | Validation outcomes |
| **Outputs** | Updated `STATE.yaml` |
| **Events** | `StateUpdated`, `WaveAdvanced` (MB2: emit after successful save) |
| **Acceptance** | Atomic rename preserved; wave advance emits `WaveAdvanced` |

### 4.10 Replan 🟢 (minimal)

| Property | Value |
|----------|-------|
| **Module** | `builder_engine/replan.py` — `ReplanProposal`, `minimal_replan()` |
| **Inputs** | Recent bus events (esp. `ValidationFailed`), fresh `ObservedSnapshot` |
| **Outputs** | `ReplanProposal`: `suggested_actions: list[str]`, `recovery_packet_template: dict | None`, `revised_ready: list[str]` |
| **Events** | `Replanned`, `RecoveryTaskCreated` |
| **Failure** | Does not auto-mutate STATE — proposal only |
| **Acceptance** | On validation failure: dependents unblocked in *proposal*; suggests fix packet YAML snippet; emits `Replanned`; human applies changes |

---

## 5. Gap closure vs runtime-model §4

| Runtime phase | MB1 Phase 2 | MB2 closure |
|---------------|-------------|-------------|
| Observe State | `lint-graph`, `status` | Unified `ObservedSnapshot` + git/CI aggregate |
| Evaluate Policies | `validate_graph` | `PolicyEngine` stub + `policies.yaml` |
| Plan | `plan_ready` | `Plan` with critical path + blockers |
| Schedule | ✅ | Event emission wired |
| Execute | manifest ✅ | Unchanged |
| Validate | `sync()` ✅ | Event emission wired |
| Merge | — | Eligibility stub + CLI; no auto-merge |
| Publish Events | direct calls | `BuildEventBus` |
| Update State | `sync()` partial | `StateUpdated` / `WaveAdvanced` events |
| Replan | — | `minimal_replan()` proposal path |

---

## 6. Interfaces

### 6.1 `ObservedSnapshot` (Python)

```python
@dataclass(frozen=True)
class ObservedSnapshot:
    observed_at: datetime
    graph: BuilderGraph
    git_branch: str | None
    git_dirty: bool
    ci_status: Literal["green", "red", "unknown"]
    ready_count: int
    in_flight_count: int
    blockers: dict[str, str]
    staleness_reasons: tuple[str, ...]
```

### 6.2 `PolicyDecision`

```python
@dataclass(frozen=True)
class PolicyDecision:
    outcome: Literal["allow", "block", "escalate"]
    violations: tuple[str, ...]
```

### 6.3 `Plan`

```python
@dataclass(frozen=True)
class Plan:
    ready_packets: tuple[Packet, ...]
    wave_intent: int
    blockers: dict[str, str]
    critical_path_packet_ids: tuple[str, ...]
    empty: bool
```

### 6.4 `BuildEvent`

```python
@dataclass(frozen=True)
class BuildEvent:
    type: EventType
    timestamp: datetime
    payload: dict[str, Any]
    cycle_id: str | None = None
```

### 6.5 CLI commands (additive)

| Command | Runtime phase | Notes |
|---------|---------------|-------|
| `observe` | Observe | Print snapshot JSON/table |
| `plan` | Plan | Show `Plan` after policies |
| `cycle --dry-run` | Full processor | Observe→Policies→Plan; optional `--sync` tail |
| `events --tail N` | Publish (read) | Tail build bus |
| `merge-check` | Merge stub | Eligibility only |

Existing `schedule`, `sync`, `lint-graph`, `status`, `ready`, `check` remain projections.

### 6.6 `EngineeringRuntimeCycle`

```python
class EngineeringRuntimeCycle:
    def run_preflight(self) -> tuple[ObservedSnapshot, PolicyDecision, Plan]: ...
    def run_postflight(self, sync_result: SyncResult) -> ReplanProposal | None: ...
```

`WorkflowRuntime` may delegate to cycle for event emission; **packet FSM transitions stay in `runtime.py`**.

---

## 7. Data flow

### 7.1 Preflight (before schedule)

```text
STATE.yaml + git + CI stub
        │
        ▼
StateObserver.observe() → ObservedSnapshot
        │
        ▼
PolicyEngine.evaluate() → PolicyDecision
        │ (block → stop)
        ▼
build_plan() → Plan
        │
        ▼
bus.publish(PlanGenerated | PlanEmpty)
```

### 7.2 Existing execution slice (unchanged semantics)

```text
WorkflowRuntime.schedule() → manifest
        │ bus: TaskScheduled, LockAcquired
        ▼
[external workers]
        │
        ▼
WorkflowRuntime.sync() → STATE update
        │ bus: ValidationPassed|Failed, StateUpdated, WaveAdvanced
```

### 7.3 Postflight (after sync)

```text
bus tail + fresh Observe
        │
        ▼
minimal_replan() → ReplanProposal
        │
        ▼
bus: Replanned, RecoveryTaskCreated (if template)
        │
        ▼
operator / Architect applies proposal (no auto STATE write)
```

---

## 8. Acceptance criteria (promotion gate preview)

```yaml
observed_snapshot: green       # unified read model with git/CI fields
policy_stub: green             # block implementer-without-checks; YAML rule loads
extended_plan: green           # critical path + ready set parity with compute_ready
build_event_bus: green         # append-only jsonl; replay ordering
cycle_preflight: green         # observe→policies→plan integrated
cycle_postflight: green        # validation failure → replan proposal
schedule_sync_parity: green    # MB1 behavior unchanged
event_emission: green          # schedule/sync emit typed events
merge_eligibility_stub: green  # deferred external integrator
no_backend_imports: green      # isolation check in CI
m0_m1_m2_m3_m4_tests: green
builder_engine_tests: green
documentation: complete
knowledge_updated: true
mb2_gate: docs/mb2-phase-gate.md
```

---

## 9. Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Stale STATE mid-cycle | `staleness_reasons` | Abort preflight; operator refresh |
| Policy block | `PolicyDecision.block` | Emit `PolicyViolated`; no schedule |
| Empty plan with blockers | `Plan.empty` + blockers | `PlanEmpty` + escalate |
| Event bus corrupt line | replay parser | Skip line + warn; test guards |
| Replan overreach | QA review | Proposal only — no auto packet creation |
| Scope creep: global FSM | ADR-0025 review | Reject PR |
| `backend.app` import | `make isolation` / lint | Reject PR |

---

## 10. Migration strategy

| Phase | Deliverable |
|-------|-------------|
| **1 — Observe** | `observe.py`, tests, CLI `observe` |
| **2 — Policies** | `policy.py`, `policies.yaml` sample, tests |
| **3 — Plan extend** | `Plan`, `build_plan()`, tests, CLI `plan` |
| **4 — Event bus** | `events.py`, jsonl storage, tests |
| **5 — Wire runtime** | cycle preflight/postflight; schedule/sync emit events |
| **6 — Replan** | `replan.py`, merge stub, integration test |
| **7 — Promotion** | gate doc, knowledge mirror |

**Order:** Spec freeze (this doc) → `plans/mb2-adaptive-runtime-plan.md` → implementation on branch `mb2-adaptive-runtime`.

---

## 11. Relationship to Product Track (M5+)

MB2 does **not** block M5 spec freeze. Product milestones may register new CheckRunner stages; MB2 policy stub may reference gate doc presence (e.g. `docs/m5-promotion.md`) but must not import product services.

Per ADR-0025 sequencing: if Platform schedule must understand new Product job semantics, **Product spec freezes first**.

---

## 12. Open questions (resolved in this spec)

| ID | Question | Resolution |
|----|----------|------------|
| Q-MB2-1 | Is MB2 a global FSM? | **No** — processor orchestration + packet FSM (ADR-0025) |
| Q-MB2-2 | Build bus storage | Filesystem `.builder-engine/events.jsonl` |
| Q-MB2-3 | Auto recovery packets | **No** — `ReplanProposal` only |
| Q-MB2-4 | Full policy engine | Deferred MB3; stub in MB2 |
| Q-MB2-5 | Merge automation | Eligibility stub; integrator external |
| Q-MB2-6 | CI signal in Observe | Stub via last `check ci` exit or `unknown` |

---

## 13. Freeze record

- [x] All 10 runtime phases mapped to modules, I/O, events, acceptance
- [x] MB2 scope: Observe, Policies stub, Plan extend, Publish bus, Replan minimal, §4 gaps
- [x] Non-goals: Product LangGraph, `backend.app` imports, global FSM
- [x] Promotion gate preview defined
- [x] Aligns with ADR-0026, `runtime-model.md`, `era-model.md`
- [x] Planner plan: `plans/mb2-adaptive-runtime-plan.md` (2026-06-25)

**Implementation authorized:** Architect freeze + Planner plan delivered.

---

## 14. References

- ADR-0026 Platform Model & Terminology
- ADR-0025 Builder Execution State Machine
- ADR-0023 Build Workflow Engine
- ADR-0006 Event-Driven Architecture (product pattern extended build-side)
- `docs/platform/runtime-model.md`
- `docs/platform/era-model.md`
- `docs/mb1-phase2-gate.md`
- `builder_engine/runtime.py`, `planner.py`, `validate.py`, `cli.py`
