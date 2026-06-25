# ASEP — Engineering Traceability Matrix (ETM)

- **Status:** Frozen (Architect 2026-06-25) — **ETM v1.1** (Event + Observability columns; ADR-0029)
- **Authority:** DR-001 §7; ADR-0028; ADR-0029
- **Purpose:** Every runtime element must answer *"Why does this exist?"* by tracing upward to Vision. Prevents orphan components.
- **Companion:** `docs/platform/DR-001-constitutional-review.md`, `docs/platform/behavioral-semantics.md`

---

## 0. Glossary (patterns — not L0 objects)

| Pattern | Definition | Where it lives |
|---------|------------|----------------|
| **Behavior** | Named collaboration intent (*why*) | `behavioral-semantics.md` |
| **Transition** | Legal state change (L2 row ID) | GSM §5 |
| **Command / Trigger** | Intent that invokes a transition | GSM Trigger column |
| **Event** | Typed semantic fact emitted by a transition | GSM §7; build bus (L4) |
| **Observability** | Evidence the behavior occurred (proof) | tests, logs, gates, projections — **distinct from Event** |
| **Transaction** | Atomic state commit after invariant pass | StateWriter + INV-B8 |
| **Projection** | Read-only view of GSM state (not authoritative) | CLI, YAML `status`, `lint-graph` |
| **Evaluation** | Per-cycle policy decision (not entity state) | C-03, C-04 |

**Traceability chain (normative — Architect approved 2026-06-25):**

```text
Vision
  ↓
ADR
  ↓
Meta Model (L0)
  ↓
Invariant (L1)
  ↓
Behavior (BS)
  ↓
State
  ↓
Transition (L2)
  ↓
Event
  ↓
Module (L4)
  ↓
Observability
  ↓
Tests
```

If any code path cannot complete this chain, it is **orphan debt** (DR-001).

**Column legend (§2):** V=Vision · A=ADR · M=L0 · I=L1 · B=Behavior · S=State · T=Transition · E=Event · O=Observability · Mod=Module · Test=Tests

---

## 1. Vision anchors

| Vision source | Statement | Platform plane expression |
|---------------|-----------|---------------------------|
| `vision.md` §Contract-first | Freeze before implement | Freezing behavior; M-01, INV-B7 |
| `vision.md` §Who builds it | Cursor agents = build-time workers | Delegation behavior; INV-B9 |
| `vision.md` §North star | Self-improving assistant (M18) | Replanning + Observability |
| ADR-0026 §5 | Vision → Spec → ADR → Freeze → Impl → Gate | Promotion behavior |
| ADR-0028 | Constitution before features | L0–L2 + BS before L4 |
| ADR-0029 | Why before what | Behavioral Semantics layer |

---

## 2. Master traceability matrix

### 2.1 Governance & freeze-first

| V | A | M | I | B | S | T | E | Mod | O | Test |
|---|---|---|---|---|---|---|---|-----|---|------|
| Contract-first | ADR-0010, 0026 §5 | Milestone, Artifact | INV-B1,B2,B7 | Freezing | `MS_*`, `ART_FROZEN` | M-01, A-03 | `ArtifactFrozen`, `MilestoneSpecFrozen` | promotion docs | freeze §12; ADR Accepted | gate YAML |
| Platform constitution | ADR-0028, 0029 | all L0 | INV-A*,B* | all BS §2 | all §3 | all §5 | per §7 | `docs/platform/*` | DR-001 record | DR-001 |
| Sidecar isolation | ADR-0023 | Worker, Task | INV-B9 | Delegation | `TASK_*` | K-02,K-03 | `WorkerReported` | `builder_engine/` | no `backend.app` import | import lint |

### 2.2 Strategic intent (L2.1 Goal guards)

| V | A | M | I | B | S | T | E | Mod | O | Test |
|---|---|---|---|---|---|---|---|-----|---|------|
| Directed work | ADR-0028 | Goal | INV-B8 | Escalation | `GOAL_*` | G-01–G-05 | `GoalActivated`… | `/goal`, knowledge | context/current-state | `[ ]` |
| Goal activate | ADR-0029 | Goal, Milestone | INV-B8 | — | `GOAL_ACTIVE` | G-01 | `GoalActivated` | knowledge | ≥1 milestone linked | `[ ]` |
| Goal suspend | ADR-0029 | Goal, Task | INV-B6 | Escalation | `GOAL_SUSPENDED` | G-03 | `GoalSuspended` | operator | no in-flight tasks | `[ ]` |
| Goal abandon | ADR-0029 | Goal, Task | INV-B8 | Recovery | `GOAL_ABANDONED` | G-05 | `GoalAbandoned` | operator | all tasks terminal | `[ ]` |

### 2.3 Workflow execution (Era I)

| V | A | M | I | B | S | T | E | Mod | O | Test |
|---|---|---|---|---|---|---|---|-----|---|------|
| Build orchestration | ADR-0025 | Task, Wave | INV-A*, B4–B6 | Scheduling | `TASK_*` | T-02–T-07 | `TaskScheduled`… | `runtime.py` | schedule/sync CLI | `test_runtime.py` |
| Task birth | ADR-0029 | Task, Epic | INV-B8 | — | `TASK_CREATED` | T-00 | `TaskCreated` | STATE.yaml edit | packet row exists | `[ ]` |
| Claim paths | MB1 §8 | Task, Lock | INV-B3–B5 | Claiming | `LOCK_ACQUIRED` | T-02, L-01 | `LockAcquired` | scheduler | `file_locks` | validate tests |
| Delegate to worker | ADR-0023 | Worker, Task | INV-B9 | Delegation | `WK_*` | T-03,K-01,K-02 | `WorkerDispatched` | manifest | `.builder-engine/last-dispatch-manifest.json` | `[ ]` |
| Validate evidence | ADR-0025 §4 | Task | INV-A1,A2 | Validating | `TASK_VALIDATING` | T-04–T-07 | `ValidationPassed/Failed` | `checks.py`, sync | CheckRunner output | sync tests |
| Failure recovery | L2 §9 | Task | INV-A4 | Recovery, Retry | `TASK_DEBUGGING` | T-08,T-09 | `TaskRetryScheduled` | state_machine | blocked→ready path | `test_failure_recovery_loop` |
| Execute cycle split | ADR-0029 | Worker, Task | INV-B9 | Delegation | `CYCLE_EXECUTING` | C-07a,b,c | `WorkerReported` | `[planned] cycle.py` | worker then runtime handoff | `[ ]` |

### 2.4 Engineering cycle (L3)

| V | A | M | I | B | S | T | E | Mod | O | Test |
|---|---|---|---|---|---|---|---|-----|---|------|
| Observe | L3 §3.1 | Snapshot | INV-B8 | Observing | `SNAP_*` | S-01,S-02,C-01,C-02 | `StateObserved` | `[planned] observe.py` | snapshot sealed | `[ ]` |
| Policy eval | L3 §3.2 | Policy | (eval) | Escalation | `CYCLE_POLICY_EVAL` | C-03,C-04 | `PolicyBlocked` | policy stub | block reason | `[ ]` |
| Publish facts | L3 §3.8 | Event | — | — | `CYCLE_PUBLISHING` | C-12 | `EventsPublished` | `[planned] events.py` | JSONL append | `[ ]` |
| Replan | L3 §3.10 | Task, Epic | INV-A4,B7 | Replanning | `CYCLE_REPLANNING` | C-14,C-15,T-09 | `Replanned` | `[planned] replan` | plan diff | `[ ]` |

### 2.5 Invariants → observability

| I | B | T | E | O (evidence invariant holds) | Test |
|---|----|---|----|------------------------------|------|
| INV-A1 | Validating | T-04,T-07 | `ValidationStarted` | sync only from in_progress | state_machine |
| INV-A4 | Retry | T-09 | `TaskRetryScheduled` | only from DEBUGGING | recovery test |
| INV-B2 | Promotion | M-04 | `PromotionCompleted` | tag + gate doc | manual |
| INV-B8 | all | all commits | `StateUpdated` | atomic rename | state_io |
| INV-B9 | Delegation | K-* | `WorkerReported` | runtime never writes STATE from worker | boundary test |

---

## 3. MB2 rebase template (mandatory columns)

Every rebased MB2 deliverable row MUST fill **all** columns:

| MB2 deliverable | B | T | E | Mod | O | Test |
|-----------------|---|---|---|-----|---|------|
| `ObservedSnapshot` | Observing | S-01,S-02,C-01,C-02 | `StateObserved` | `observe.py` | snapshot dump | `test_observe.py` |
| Policy stub | Escalation | C-03,C-04 | `PolicyBlocked` | policy stub | decision log | `test_policy.py` |
| Event bus | (all) | §7 all | all events | `events.py` | `.builder-engine/events.jsonl` | `test_events.py` |
| `EngineeringRuntimeCycle` | Scheduling…Replanning | C-01–C-15 | per phase | `cycle.py` | cycle trace | `test_cycle.py` |
| GSM guards | Validating, Claiming | T-*, INV-A* | per T-* | `gsm_task.py` | TransitionError on illegal | `test_gsm_task.py` |
| Invariant pass | all | commits | `InvariantViolation` | `invariants.py` | halt on violation | `test_invariants.py` |
| Recovery CLI | Retry, Recovery | T-08,T-09 | `TaskRetryScheduled` | cli debug/retry | blocked packet recovery | recovery tests |
| Rename runtime | Delegation | all | — | `EngineeringRuntime` | grep no WorkflowRuntime | regression |

**Rebase rule:** empty **T** or **B** column → remove deliverable or amend L2 first.

---

## 4. Orphan prevention

Before merging any `builder_engine/` PR:

1. Add or extend an ETM §2 row with **all** columns populated.
2. PR description: `ETM §2.x · Behavior · Transition · Event`.
3. **Observability ≠ Event:** event = fact emitted; observability = proof (test assertion, log, gate file).

---

## 5. DR-001 / Architect sign-off

| Item | Status |
|------|--------|
| DR-001 | ✅ Approved |
| ETM v1.1 | ✅ Approved |
| L2.1 + BS (ADR-0029) | ✅ Frozen |
| **MB2 spec rebase** | ✅ Architect Approved 2026-06-25 (§13; spec only) |
| **L4 Phase 0** | ✅ Approved — `docs/l4-phase0-gate.md`; tag `l4-phase0-complete` |
| L4 MB2 D1–D11 | 🟢 **MB2 Phase 1 (D1 Observe) authorized** — after Phase 0 baseline committed |

---

## 6. Product plane boundary

Platform ETM does not trace Product LangGraph, GraphState, or `/chat` — see M-series specs. Shared object: **Milestone** only.

---

## 7. References

- DR-001 · ADR-0028 · ADR-0029
- L0 · L1 · `behavioral-semantics.md` · L2 · L3
- `plans/l2-global-state-machine-plan.md`
