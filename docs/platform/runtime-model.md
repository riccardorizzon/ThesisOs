# ASEP — Engineering Runtime Model

- **Status:** Frozen (Architect 2026-06-25)
- **Scope:** The **canonical engineering cycle** executed by ASEP's **Engineering Runtime** and governed by the **Build Control Plane**. This is the "processor" of Era II+ — not a feature list.
- **Authority:** ADR-0026. Implements the loop described directionally in MB1 spec §10.1; **supersedes** the simplified MB1 Phase 2 loop as the target architecture (Phase 2 is a **partial** implementation).
- **Companion:** `docs/platform/era-model.md`

---

## 1. Purpose

The Engineering Runtime repeatedly executes:

```text
Observe State
      │
      ▼
Evaluate Policies
      │
      ▼
Plan
      │
      ▼
Schedule
      │
      ▼
Execute
      │
      ▼
Validate
      │
      ▼
Merge
      │
      ▼
Publish Events
      │
      ▼
Update State
      │
      ▼
Replan ───────────────► (loop to Observe State)
```

Each phase has: **inputs**, **outputs**, **owner**, **failure modes**, and **events emitted**. Implementations (MB2, MB3, …) **translate** this model — they do not redefine it.

---

## 2. Planes and ownership

| Phase group | Primary owner | Deterministic? |
|-------------|---------------|----------------|
| Observe, Evaluate Policies, Plan, Schedule, Validate, Update State, Replan, Publish Events | **Build Control Plane** + **Engineering Runtime** (code in sidecars) | Yes |
| Execute, Merge (code changes) | **Execution workers** (LLM agents, integrator, human) | No (worker output) |
| Merge (git integration) | Worker + runtime **eligibility** checks | Mixed |

**CLI/API surfaces** (`builder-engine status`, `schedule`, `sync`, future dashboard) are **projections** of runtime state — not the runtime itself (ADR-0025).

---

## 3. Phase definitions

### 3.1 Observe State

**Purpose:** Build a consistent read model of project + workflow + environment.

| Input | Output |
|-------|--------|
| `STATE.yaml`, packets, git status, CI status, knowledge drift signals, queue depth | `ObservedSnapshot` (derived, immutable for one cycle) |

**Owner:** Control Plane observability + `GraphLoader` / future unified state reader.

**Failure:** Stale or partial snapshot → cycle aborts before Schedule.

**Events:** `StateObserved` (optional, Era II).

**Era I today:** `lint-graph`, `status`, `validate_graph` — partial observe.

---

### 3.2 Evaluate Policies

**Purpose:** Decide whether the system **may** proceed given rules, not just graph shape.

| Input | Output |
|-------|--------|
| `ObservedSnapshot`, policy set (ADR + YAML) | `PolicyDecision`: allow \| block \| escalate |

> **Amended (ADR-0028):** invariants are **not** part of the policy set. They are
> fail-closed laws enforced separately on every state write — see
> `docs/platform/invariant-model.md` (L1). Policies decide *whether to proceed*;
> invariants decide *whether a state write is legal*.

**Owner:** Policy Engine (Era II); stand-in: `validate_graph` + ADR gates.

**Examples:**

- Product spec not frozen → block M4 embed stages in CheckRunner.
- Implementer without `checks` → block schedule (§8.8).
- Scope creep patterns → block or warn.

**Events:** `PolicyViolated`, `PolicyEscalated`.

**Era I today:** Invariants in `builder_engine/validate.py`; no central policy store.

---

### 3.3 Plan

**Purpose:** Compute **what** should run next — ready set, critical path, recovery tasks.

| Input | Output |
|-------|--------|
| `ObservedSnapshot`, `PolicyDecision`, strategic objective | `Plan`: ordered work units, wave intent, blockers |

**Owner:** Planner (adaptive in Era II; stub in MB1 Phase 2).

**Failure:** Empty plan with open blockers → human escalation.

**Events:** `PlanGenerated`, `PlanEmpty`.

**Era I today:** `plan_ready()` / `compute_ready()` — ready set only, no replan.

---

### 3.4 Schedule

**Purpose:** **Claim** work, assign locks, produce dispatch manifest — no worker execution yet.

| Input | Output |
|-------|--------|
| `Plan`, `ObservedSnapshot` | Updated workflow state (CLAIMED), `DispatchManifest`, file locks |

**Owner:** Scheduler + StateWriter (atomic).

**Failure:** Concurrent in-flight packets → abort (single-flight per wave policy).

**Events:** `TaskScheduled`, `LockAcquired`.

**Era I today:** `WorkflowRuntime.schedule()` — implemented.

---

### 3.5 Execute

**Purpose:** Workers perform implementation, review, research, integration in isolated contexts.

| Input | Output |
|-------|--------|
| `DispatchManifest`, worker type (builder/reviewer/…) | Code/docs changes in worktrees; worker reports completion |

**Owner:** Execution workers (Cursor Task, human). Runtime **does not** write product code (ADR-0023).

**Failure:** Worker timeout, merge conflict prep — reported to Validate/Replan.

**Events:** `TaskStarted`, `TaskCompleted`, `TaskFailed`.

**Era I today:** External to engine; manifest at `.builder-engine/last-dispatch-manifest.json`.

---

### 3.6 Validate

**Purpose:** Run evidence gates — tests, lint, drift, milestone-specific stages.

| Input | Output |
|-------|--------|
| In-flight work units, packet `checks`, CheckRunner stages | Pass/fail per check; VALIDATING → MERGED or FAILED |

**Owner:** Validator (`CheckRunner` + CI).

**Failure:** Failed checks → packet FAILED/DEBUGGING; no DONE without pass (ADR-0025).

**Events:** `ValidationPassed`, `ValidationFailed`.

**Era I today:** `WorkflowRuntime.sync()` + `make ci` stages including M4 `embed`, `search-smoke`.

---

### 3.7 Merge

**Purpose:** Integrate worker output into integration branch / mainline per wave policy.

| Input | Output |
|-------|--------|
| Passed validation, worktree paths, ownership | Git merge result; integration notes |

**Owner:** Integrator worker; runtime sets **eligibility** only.

**Failure:** Merge conflict → block wave; `integration_notes`; Replan.

**Events:** `MergeAccepted`, `MergeRejected`.

**Era I today:** Manual/prose in orchestrate-builders skill — **not** in engine.

---

### 3.8 Publish Events

**Purpose:** Append-only notification for reactive components — **no direct coupling**.

| Input | Output |
|-------|--------|
| Outcomes of Validate, Merge, Promotion | Typed events on build bus (and optionally product outbox if cross-cutting) |

**Owner:** Event publisher in Control Plane / Runtime.

**Consumers:** Observability, Replan, audit, future UI.

**Rule:** Downstream reacts to events; phases do not call each other ad hoc for cross-cutting concerns (ADR-0006 pattern extended to build-time).

**Events:** All §3 event types.

**Era I today:** Product `events` table only; build cycle uses direct calls.

---

### 3.9 Update State

**Purpose:** Persist authoritative workflow transitions atomically.

| Input | Output |
|-------|--------|
| Validation/merge outcomes | Updated `STATE.yaml`: packet status, wave, locks, blockers |

**Owner:** StateWriter (`state_io.save_raw_state`).

**Failure:** Partial write prevented by atomic rename.

**Events:** `StateUpdated`, `WaveAdvanced`.

**Era I today:** Implemented in `sync()`; wave advance on wave complete.

---

### 3.10 Replan

**Purpose:** Close the adaptive loop — recompute plan after failure, promotion, or drift.

| Input | Output |
|-------|--------|
| Published events, new `ObservedSnapshot` | Revised `Plan`; may spawn recovery packets |

**Owner:** Adaptive Planner (MB1 Phase 4 direction; Era II full).

**Examples:**

- Task A failed validation → unblock dependents, insert fix packet.
- Milestone promoted → close epic, open next platform epic.

**Events:** `Replanned`, `RecoveryTaskCreated`.

**Era I today:** Not implemented — human + `/goal` + Architect.

---

## 4. Mapping: MB1 Phase 2 vs this model

| Runtime phase | MB1 Phase 2 | Gap |
|---------------|---------------|-----|
| Observe State | `lint-graph`, `status` | No unified snapshot; no CI/git aggregate |
| Evaluate Policies | `validate_graph` | No policy engine |
| Plan | `plan_ready` | No replan / critical path |
| Schedule | `schedule()` | ✅ |
| Execute | manifest only | ✅ (by design) |
| Validate | `sync()` + CheckRunner | ✅ |
| Merge | — | Skill/manual |
| Publish Events | — | Direct calls |
| Update State | `sync()` writes | ✅ partial |
| Replan | — | Era II |

**Conclusion:** Era I delivered a **vertical slice** through Schedule → Validate → Update State. Era II completes the processor.

---

## 5. Engineering Runtime vs Build Control Plane

```text
Build Control Plane                          Engineering Runtime
─────────────────────                          ───────────────────
Strategic objectives                         Observe → Evaluate Policies
Human /goal / Architect freeze               Plan → Schedule
ADR & spec authority                         Validate eligibility
Policy definitions                           Update State (atomic)
Observability UI (future)                    Publish Events (emitter)
Event consumers (Replan, audit)              Replan triggers (input)
Operator skill (invoke commands)             CLI as projections
```

The **Runtime** runs the cycle. The **Control Plane** supplies intent, rules, and governance. Both live under **ASEP**.

---

## 6. Worker types (execution plane)

| Worker | Role | Manifest field |
|--------|------|----------------|
| Builder | Implement code/docs in worktree | `agent_type: implementer` |
| Reviewer | Critique, security, architecture | future |
| Researcher | Spike, spec draft | `explorer` today |
| Integrator | Merge, cross-package fix | future explicit type |
| Documenter | Specs, ADRs, knowledge | `documenter` |

Workers are **plugins**. The Runtime schedules **work units** (packets), not "agents" as architecture.

---

## 7. Global lifecycle for new capabilities

Any new Runtime or Control Plane capability follows (ADR-0026 §5):

```text
Vision → Spec → ADR → Freeze → Implementation → Gate → Promotion
```

Example for MB2:

1. Vision: complete Observe + Policies + Replan hooks.
2. Spec: `docs/superpowers/specs/…-mb2-….md` derived from **this document**.
3. ADR: only if new irreversible decision.
4. Freeze: Architect sign-off.
5. Implementation: code in `builder_engine/` or new sidecar.
6. Gate: `docs/mb2-phase-gate.md`, tests.
7. Promotion: merge + optional tag.

---

## 8. Non-goals (this document)

| Forbidden | Rationale |
|-----------|-----------|
| Product LangGraph topology | Product Plane — M5+ specs |
| Replacing git or filesystem authority | ADR-0019, ADR-0023 |
| Auto-editing ADRs/specs | Architect gate |
| Defining M5 product features | Product Track specs |

---

## 9. Freeze record

- [x] Canonical 10-phase cycle defined
- [x] Phase I/O, owners, events specified
- [x] MB1 Phase 2 mapped as partial implementation
- [x] MB2 defined as runtime translation, not FSM ticket
- [x] Control Plane vs Engineering Runtime separation

**Implementation authorized:** MB2+ only after MB2 spec explicitly traces each phase to modules and tests.

---

## 10. References

- ADR-0026 Platform Model & Terminology
- ADR-0025 Builder Execution State Machine (packet-level FSM)
- ADR-0023 Build Workflow Engine
- ADR-0006 Event-Driven Architecture (product pattern extended build-side)
- `builder_engine/runtime.py` (Era I partial loop)
- `docs/platform/era-model.md`
