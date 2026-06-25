# ASEP — Behavioral Semantics

- **Status:** Frozen (Architect 2026-06-25)
- **Layer:** Between L1 and L2 — **why objects collaborate**, not what states exist (L0), what laws hold (L1), or what transitions are legal (L2).
- **Scope:** Platform plane only.
- **Authority:** ADR-0029. Sits between `invariant-model.md` (L1) and `global-state-machine.md` (L2).
- **Derivation:** Consolidates intent already implicit in L3 phase definitions, GSM transition pre/post conditions, and DR-001 closure analysis. **No new L0 objects. No new transitions.** Clarifies *semantic intent* behind existing L2 rows.

---

## 1. Purpose

| Layer | Question answered |
|-------|-------------------|
| L0 Meta Model | **Who exists?** |
| L1 Invariants | **What laws hold?** |
| **Behavioral Semantics** | **Why do objects collaborate?** |
| L2 Global State Machine | **What transitions are valid?** |
| L3 Runtime Cycle | **When are transitions invoked?** |
| L4+ Implementation | **How are transitions executed?** |

GSM says `TASK_READY → TASK_CLAIMED` is **permitted**. This document says **why**: exclusive access to shared paths must be granted before a Worker executes, without violating lock invariants.

```text
Engineering Constitution
  L0 + L1 + Behavioral Semantics
        ↓
Engineering Semantics (states + behaviors)
        ↓
Engineering Runtime (L3 cycle + L4 code)
        ↓
Execution Workers (LLM, human — interchangeable)
```

Workers **implement** behaviors; they do not **define** them.

---

## 2. Canonical behaviors

Each behavior defines: **intent**, **collaborating objects**, **invariants**, **L2 transitions**, **L3 phase**, **events**, **observability evidence**.

### 2.1 Scheduling

| Property | Value |
|----------|-------|
| **Intent** | Select ready work and prepare it for exclusive execution without starting Workers yet. |
| **Why** | Parallelism requires a barrier (Wave) and conflict-free path ownership before dispatch. |
| **Objects** | Planner → Task, Wave, Epic; Scheduler → Task, Lock |
| **Invariants** | INV-A5 (deps done), INV-B3, INV-B5, INV-B6 |
| **Transitions** | T-01, T-02, T-03, L-01, W-01, C-05, C-06 |
| **L3 phase** | Plan → Schedule |
| **Events** | `TaskPrepared`, `TaskClaimed`, `TaskScheduled`, `LockAcquired`, `PlanGenerated` |
| **Observability** | `plan_ready` output; dispatch manifest; `file_locks` diff; policy block reason |

### 2.2 Claiming

| Property | Value |
|----------|-------|
| **Intent** | Grant a Task exclusive, auditable access to filesystem paths it owns. |
| **Why** | Prevent two Workers from mutating overlapping paths (data race → inconsistent validation). |
| **Objects** | Scheduler, Task, Lock |
| **Invariants** | INV-B3, INV-B4, INV-B5 |
| **Transitions** | T-02, L-01 |
| **L3 phase** | Schedule |
| **Events** | `TaskClaimed`, `LockAcquired` |
| **Observability** | `STATE.yaml file_locks`; overlap errors from `validate_graph` |

### 2.3 Delegation

| Property | Value |
|----------|-------|
| **Intent** | Hand off a claimed Task to a Worker via dispatch manifest — runtime stops, Worker starts. |
| **Why** | Separate deterministic orchestration (ADR-0023) from non-deterministic execution (LLM). Enables model swap without architecture change. |
| **Objects** | Scheduler → Worker (engagement), Task |
| **Invariants** | INV-B9 (Worker must not write Workflow state) |
| **Transitions** | T-03, K-01, K-02 |
| **L3 phase** | Schedule → Execute |
| **Events** | `ExecutionStarted`, `WorkerDispatched`, `WorkerExecutionStarted` |
| **Observability** | `.builder-engine/last-dispatch-manifest.json`; worktree path |

### 2.4 Promotion

| Property | Value |
|----------|-------|
| **Intent** | Record that a Milestone's gate evidence is complete and the capability is officially delivered. |
| **Why** | Contract-first discipline (Vision §5): subjective "done" causes scope creep across tracks. |
| **Objects** | Validator → Milestone; Promotion Engine → Milestone, Goal |
| **Invariants** | INV-B2 |
| **Transitions** | M-03, M-04, G-02, A-03 (freeze) |
| **L3 phase** | Validate (gate) + governance act |
| **Events** | `MilestoneValidated`, `PromotionCompleted`, `ArtifactFrozen`, `GoalAchieved` |
| **Observability** | `docs/m{n}-promotion.md`; git tag `m{n}-complete`; gate YAML green |

### 2.5 Retry

| Property | Value |
|----------|-------|
| **Intent** | Re-admit a failed Task to the ready queue after explicit debug analysis. |
| **Why** | Failures must not silently reset state (forbidden `RUNNING → RUNNING`). Recovery is a first-class semantic. |
| **Objects** | Planner, Human Operator, Task |
| **Invariants** | INV-A4 (only `DEBUGGING → READY`) |
| **Transitions** | T-08 → T-09 |
| **L3 phase** | Replan |
| **Events** | `TaskDebugStarted`, `TaskRetryScheduled` |
| **Observability** | `integration_notes` on packet; replan log |

### 2.6 Recovery

| Property | Value |
|----------|-------|
| **Intent** | Move from failure to corrective action through explicit intermediate states. |
| **Why** | Hidden recovery creates untraceable state — breaks ETM and audit. |
| **Objects** | Validator, Human Operator, Planner, Task |
| **Invariants** | INV-A1, INV-A4 |
| **Transitions** | T-07 → T-08 → T-09 → T-02…; C-09 → C-14 |
| **L3 phase** | Validate → Replan |
| **Events** | `ValidationFailed`, `TaskDebugStarted`, `Replanned` |
| **Observability** | failed check commands; `ValidationFailed` event; blocked packet status |

### 2.7 Escalation

| Property | Value |
|----------|-------|
| **Intent** | Halt automated progress and require Human Operator when policy blocks or invariants would be violated. |
| **Why** | Fail-closed governance beats silent progress into illegal state. |
| **Objects** | Policy Engine, Human Operator, Invariant layer, Goal |
| **Invariants** | INV-B8; invariant violations never overridden |
| **Transitions** | C-04, C-15; `InvariantViolation` (halt); G-03 (suspend) |
| **L3 phase** | Evaluate Policies; Replan halt |
| **Events** | `PolicyBlocked`, `CycleHalted`, `GoalSuspended` |
| **Observability** | policy decision reason; cycle halt marker; operator skill invocation |

### 2.8 Observing

| Property | Value |
|----------|-------|
| **Intent** | Build an immutable derived view of Project + Workflow + environment for one cycle. |
| **Why** | Plan and policy decisions require consistent snapshot — not stale partial reads. |
| **Objects** | Snapshot, Task, Epic, Wave, Lock (+ git/CI inputs) |
| **Invariants** | INV-B8 (snapshot never authoritative over Workflow state) |
| **Transitions** | S-01, S-02, C-01, C-02 |
| **L3 phase** | Observe State |
| **Events** | `SnapshotCreated`, `StateObserved` |
| **Observability** | `ObservedSnapshot` contents; `lint-graph` / `status` projections |

### 2.9 Freezing

| Property | Value |
|----------|-------|
| **Intent** | Make an Artifact (spec/ADR) immutable by governance act before implementation depends on it. |
| **Why** | Implementation before freeze causes semantic drift (ADR-0026 §5, Vision contract-first). |
| **Objects** | Human Operator, Artifact, Milestone |
| **Invariants** | INV-B1, INV-B7 |
| **Transitions** | A-03, M-01 |
| **L3 phase** | Governance (pre-cycle) |
| **Events** | `ArtifactFrozen`, `MilestoneSpecFrozen` |
| **Observability** | spec freeze record §12; ADR status Accepted |

### 2.10 Validating

| Property | Value |
|----------|-------|
| **Intent** | Collect machine-checkable evidence that a Task's output meets its Definition of Done. |
| **Why** | No Task reaches DONE without proof (ADR-0025 §4). |
| **Objects** | Validator, Task, Artifact |
| **Invariants** | INV-A1, INV-A2 |
| **Transitions** | T-04, T-05, T-07, C-08, C-09 |
| **L3 phase** | Validate |
| **Events** | `ValidationStarted`, `ValidationPassed`, `ValidationFailed` |
| **Observability** | CheckRunner output; `make ci` stages; packet `checks` |

### 2.11 Merging

| Property | Value |
|----------|-------|
| **Intent** | Integrate Worker output into integration branch after validation passes. |
| **Why** | Code exists in worktree until merge — wave completion requires integrated artifacts. |
| **Objects** | Integrator (Worker role), Task, Artifact |
| **Invariants** | INV-A2 |
| **Transitions** | T-06, C-10, C-11 |
| **L3 phase** | Merge |
| **Events** | `MergeAccepted`, `MergeRejected`, `TaskCompleted` |
| **Observability** | git merge result; integration notes |

### 2.12 Replanning

| Property | Value |
|----------|-------|
| **Intent** | Recompute ready set and recovery tasks after failure, promotion, or drift. |
| **Why** | Static plans fail in real engineering — adaptive loop closes Era II. |
| **Objects** | Planner, Task, Epic, Event (consumes published facts) |
| **Invariants** | INV-A4, INV-B7 (planner proposes only) |
| **Transitions** | T-09, C-14, C-15 |
| **L3 phase** | Replan |
| **Events** | `Replanned`, `RecoveryTaskCreated`, `CycleHalted` |
| **Observability** | revised plan diff; new recovery packets |

---

## 3. Behavior ↔ GSM quick map

| Behavior | Primary transitions |
|----------|-------------------|
| Scheduling | T-01, T-02, T-03, C-05, C-06 |
| Claiming | T-02, L-01 |
| Delegation | T-03, K-01, K-02 |
| Promotion | M-03, M-04, G-02 |
| Retry | T-09 |
| Recovery | T-07, T-08, T-09, C-09, C-14 |
| Escalation | C-04, C-15, G-03 |
| Observing | S-01, S-02, C-01, C-02 |
| Freezing | A-03, M-01 |
| Validating | T-04, T-05, T-07, C-08, C-09 |
| Merging | T-06, C-10, C-11 |
| Replanning | C-14, C-15, T-09 |

---

## 4. Non-goals

| Forbidden | Rationale |
|-----------|-----------|
| New L0 objects | L0 is frozen |
| New L2 transitions | Behaviors explain existing rows; new transitions require L2 amendment |
| Product LangGraph semantics | Product plane |
| Worker prompt content | Worker configuration, not platform semantics |

---

## 5. Freeze record

- [x] Twelve canonical behaviors defined with intent + collaboration
- [x] Each behavior maps to L1 invariants, L2 transitions, L3 phase, events, observability
- [x] Workers positioned as implementers, not definers
- [x] No new objects or transitions introduced

**References:** ADR-0029 · L0 · L1 · L2 · L3 · DR-001 · ETM
