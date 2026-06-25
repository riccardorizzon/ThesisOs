# ASEP — Invariant Model (L1)

- **Status:** Frozen (Architect 2026-06-25)
- **Layer:** L1 — **laws**. The non-negotiable properties that must hold over the objects of the Engineering Meta Model (L0) at all times.
- **Scope:** Platform plane only. Constrains transitions of `Task`, `Milestone`, `Lock`, and Workflow `State`.
- **Authority:** ADR-0028. Sharpens ADR-0026 §8 (which lumped invariants under "policy"). Invariants are **not** a kind of policy.
- **Derivation:** Era I already separates these *de facto*: in `builder_engine/validate.py`, `ValidationResult.errors` are invariants (fail), `.warnings` are policy hints (advise). L1 makes that split explicit, centralizes it, and fills the gaps.

---

## 1. The core distinction

> A **policy** is a decision you are allowed to change. An **invariant** is a law you are not.

| | **Invariant** | **Policy** |
|--|---------------|-----------|
| Nature | Law of the system | Tunable decision |
| Examples | "a frozen state is never mutated"; "PROMOTED requires VALIDATED" | priority, timeout, builder count, single-flight per wave |
| Violation means | **Bug** — the system is in an illegal state | Suboptimal but legal |
| Enforcement | **Fail-closed**: halt the transition | Allow / block / escalate per config |
| Changeable by | ADR only (added, never relaxed at runtime) | Build Control Plane config, any time |
| Lives in | This document (L1) → guards in code | Policy Engine (L5) |
| Failure mode | `InvariantViolation` → stop | `PolicyDecision: block` → reroute |

**Litmus test (from Era I):** if `validate_graph` raises it as an **error**, it is an invariant. If it raises a **warning**, it is a policy. Example: "in_progress packet without `checks`" is a *warning* → **policy** ("require DoD before sync"), tunable. "dependency not done" is an *error* → **invariant**, never legal.

---

## 2. Two classes of invariant

Not every invariant lives in the same place. Splitting them is what makes them *enforceable* rather than prose.

### Class A — Transition preconditions (live **inside** the state machine)

Guards on a single object's own FSM. They belong in the L2 Global State Machine / ADR-0025 transition table, checked at the transition.

### Class B — Cross-cutting invariants (live in the **dedicated invariant layer**)

Properties spanning multiple objects (locks vs tasks, frozen artifacts, promotion vs validation). Evaluated by a single guard pass on **every** state write, independent of which transition triggered it.

> **Rule:** an invariant documented but not wired to an executable check is **theatre**. Each entry below names its enforcement point. `GAP` = law declared now, check to be implemented in L2/L4 (must ship *with* the code that could violate it, never after).

---

## 3. Invariant catalog

### Class A — transition preconditions (Task FSM, ADR-0025)

| ID | Law | Object | Enforced at | Today |
|----|-----|--------|-------------|-------|
| INV-A1 | A Task may enter `VALIDATING` only from `RUNNING`. | Task | FSM guard | ADR-0025 order; `GAP` (no executable guard) |
| INV-A2 | A Task may enter `MERGED`/`DONE` only after `VALIDATING` passed. | Task | FSM guard + CheckRunner | ADR-0025 §4; partial in `sync()` |
| INV-A3 | A `DONE` Task never returns to `READY` (`DONE` is terminal). | Task | FSM guard | ADR-0025; `GAP` |
| INV-A4 | Recovery is `FAILED → DEBUGGING → READY` only; no other re-entry to `READY`. | Task | FSM guard | ADR-0025; `GAP` |
| INV-A5 | A Task may enter `RUNNING`/`DONE` only if **all** its dependencies are `DONE`. | Task, Epic | graph guard | ✅ `validate.py` (error) |

### Class B — cross-cutting invariants (invariant layer)

| ID | Law | Objects | Enforced at | Today |
|----|-----|---------|-------------|-------|
| INV-B1 | A **frozen** Artifact (spec/ADR) is never mutated except by an explicit governance act. | Artifact | invariant pass + review | prose only; `GAP` |
| INV-B2 | A `Milestone` may be `PROMOTED` only if `VALIDATED` (gate evidence exists). | Milestone | promotion guard | ADR-0010 gates; `GAP` (not in engine) |
| INV-B3 | A Worker may not acquire/claim a Task whose required paths are `LOCKED` by another Task. | Worker, Task, Lock | Schedule guard | partial (`file_locks` overlap); `GAP` at claim time |
| INV-B4 | A `Lock` must be owned by a known Task and be a subset of that Task's `owned_files`. | Lock, Task | invariant pass | ✅ `validate.py` (error) |
| INV-B5 | Two Tasks never own overlapping paths (globally, and within a Wave). | Task | invariant pass | ✅ `validate.py` (error) |
| INV-B6 | An `in_progress`/`blocked` Task's wave equals the active Workflow `wave`. | Task, Wave | invariant pass | ✅ `validate.py` (error) |
| INV-B7 | The Planner never mutates a frozen `State`/Artifact; it proposes, governance disposes. | Planner, State | planner boundary | prose only; `GAP` |
| INV-B8 | Workflow state is written only by the StateWriter, atomically (no partial writes). | State | StateWriter | ✅ atomic rename (`state_io`) |
| INV-B9 | A Worker never authoritatively mutates Workflow state (only emits results). | Worker, State | runtime boundary | ✅ by construction (ADR-0023) |

---

## 4. Enforcement model

```text
                 ┌────────────────────────────────────────────┐
 proposed        │   Invariant Layer (fail-closed)            │
 transition ───▶ │   Class A guards (FSM) + Class B pass      │ ──▶ commit (StateWriter)
                 │                                            │
                 └──────────────┬─────────────────────────────┘
                                │ violation
                                ▼
                        InvariantViolation  →  HALT cycle
                                (never a warning, never skipped)
```

- Invariants are checked **before** every Workflow state write, on the post-transition candidate state.
- A violation is **fail-closed**: the transition is rejected and the cycle halts (or escalates to the Control Plane). It is never downgraded to a warning.
- Invariants are **monotonic**: added via ADR, never relaxed by config. Policies absorb all tunable behaviour so invariants stay stable.

---

## 5. Relationship to the Policy Engine (L5)

Observe → **Evaluate Policies** → Plan (runtime-model §3.2) decides *whether to proceed*. The Invariant Layer is **orthogonal and lower**: it runs on every state write regardless of the policy decision. A policy can say "don't schedule wave 3 yet" (tunable); an invariant says "this state write is illegal" (law). The Policy Engine MUST NOT be able to override an invariant.

---

## 6. Freeze record

- [x] Invariant vs policy distinction fixed (refines ADR-0026 §8)
- [x] Two classes (transition preconditions / cross-cutting) defined
- [x] Catalog derived from `validate.py` errors + ADR-0025 + Architect examples
- [x] Each invariant maps to an enforcement point (✅ or `GAP`)
- [x] Fail-closed enforcement model declared

**Implementation authorized:** L2 wires Class A guards into the Global State Machine; L4 wires the Class B pass into the runtime's Update State phase. `GAP` checks ship with the code that could violate them.

---

## 7. References

- ADR-0028 · ADR-0026 §8 (superseded distinction) · ADR-0025 (Task FSM) · ADR-0010 (gates) · ADR-0023 (sidecar boundary)
- `docs/platform/engineering-meta-model.md` (L0) · `docs/platform/runtime-model.md` (L3)
- `builder_engine/validate.py` (Era I invariants/policies de facto)
