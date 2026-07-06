# Architect Decision — PX-EXEC Wave A Engineering Package

> **Date:** 2026-07-06  
> **Authority:** Architect  
> **Program:** PX-EXEC — Execution Orchestration Platform  
> **Phase:** PX-EXEC-P1 — Runtime Foundation  
> **SoR revision:** 2026-07-05 (frozen)  
> **Artifacts reviewed:**  
> - `.asep/reports/PX-EXEC-WAVE-A-ENGINEERING-PACKAGE.md`  
> - `.asep/proposals/PX-EXEC-EWO-002-rule-engine.md`  
> - `.asep/proposals/PX-EXEC-EWO-003-dependency-engine.md`  
> **Prerequisite:** PX-EXEC-EWO-001 **IMPLEMENTED** PASS @ 2026-07-06  
> **Scope:** Design review and Phase 1 dispatch authorization; no runtime implementation

---

## Decision

```text
1. Wave A Engineering Package:     PASS

2. PX-EXEC-EWO-002 Rule Engine:  APPROVED FOR DISPATCH (Phase 1 parallel)

3. PX-EXEC-EWO-003 Dependency Engine: APPROVED FOR DISPATCH (Phase 1 parallel)

4. Program graph sync (package §10.2): AUTHORIZED

EWO-004…006 dispatch:              NOT AUTHORIZED (Integration A gate required)
MB2-Q1…Q6 qualification:           NOT AUTHORIZED
PX-4 / product plane:              NOT AUTHORIZED
```

---

## Answers (review request)

| # | Question | Verdict |
|---|----------|---------|
| 1 | Wave A engineering package | **PASS** |
| 2 | EWO-002 Rule Engine | **APPROVED FOR DISPATCH** |
| 3 | EWO-003 Dependency Engine | **APPROVED FOR DISPATCH** |
| 4 | Program graph sync §10.2 | **AUTHORIZED** |

---

## Architectural assessment

The engineering package correctly extends the registered Wave A backlog
(`.asep/reports/PX-EXEC-WAVE-A-BACKLOG.md`) with the operational artifacts required
for governed parallel dispatch:

- Dependency analysis matches the registered DAG; critical path `001 → 003 → 004 → 005`
  is correctly identified.
- Ownership matrix enforces disjoint write paths for EWO-002 and EWO-003 — parallel
  dispatch is safe.
- Integration A barrier (merge `003 → 002`) follows the validated PX-2 parallel pattern.
- Qualification strategy preserves the implementation ≠ qualification boundary; no MB2-Q
  claims appear in any reviewed artifact.
- Rollback strategy and risk register (R-WA1…R-WA12) are adequate for Phase 1.

Boundary preservation confirmed:

| Constraint | Verdict |
|------------|---------|
| Design only — no runtime code in package | ✓ |
| No SoR modification | ✓ |
| No product plane work | ✓ |
| No MB2-Q1…Q6 qualification claims | ✓ |
| EWO-001 prerequisite satisfied | ✓ |

---

## EWO-002 assessment (Rule Engine)

| Area | Verdict |
|------|---------|
| SoR §7.1 processing model | Coherent — evaluate-only; action descriptors, no plugin execution |
| SoR §7.2 rule pack schema | Coherent |
| SoR §7.3 golden PX-2 fixture | Coherent — test-only, enables future MB2-Q-006 |
| SoR §7.4 / INV-R-07 governance exclusion | Correctly framed; `PolicyEngine` separation explicit |
| INV-R-13 determinism | Acceptance tests specified |
| Event Bus integration (EWO-001) | Correct dependency on `subscribe()` |
| MB2-Q boundary | Preserved — enables MB2-Q2 evidence only |

**Condition (non-blocking):** Optional `cycle.py` subscriber wiring is Supervisor-owned
at Integration A — implementing agent must not wire without dual sign-off per package §3.

---

## EWO-003 assessment (Dependency Engine)

| Area | Verdict |
|------|---------|
| SoR §4.1 Program Graph input | Coherent — read-only from `.asep/programs/*.yaml` |
| SoR §4.2 Execution Graph derivation | Coherent — derive-only API |
| runtime-model-v2 §4.1 algorithm | Matches five-step derivation spec |
| INV-R-01…03 | Correctly enforced in acceptance tests |
| INV-R-08 `ExecutionGraphDerived` | Catalog ready from EWO-001; emission on derive |
| Era I `compute_ready()` parity | Document-only bridge — no replacement in Wave A |
| MB2-Q boundary | Preserved — enables MB2-Q1 evidence only |

**Condition (non-blocking):** Parity test vs Era I `BuilderGraph` may document divergence;
silent replacement of `compute_ready()` is forbidden.

---

## EWO-004…006 scope note

Design summaries in the engineering package are sufficient for Wave A slice authorization.
Full proposals for EWO-004, EWO-005, and EWO-006 remain **required before dispatch** of
each respective EWO. Integration A PASS is the gate for EWO-004.

---

## Program graph sync (authorized)

Applied per package §10.2:

1. `.asep/programs/px-exec.yaml` — `wave_a.engineering_package`, proposal refs,
   `authorized_for_dispatch` status; EWO-002/003 `proposal:` paths
2. `.asep/capabilities/px-exec.yaml` — proposal refs; `px-exec-2-rule-engine.requires`
   corrected to §7 (was §6.3)

---

## Dispatch state

| Element | Status |
|---------|--------|
| Wave A engineering package | **PASS** |
| EWO-001 Event Model & Bus | **IMPLEMENTED** |
| EWO-002 Rule Engine proposal | **APPROVED FOR DISPATCH** |
| EWO-003 Dependency Engine proposal | **APPROVED FOR DISPATCH** |
| Phase 1 parallel dispatch (002 ∥ 003) | **AUTHORIZED** — operator command required |
| Integration A | **NOT STARTED** |
| EWO-004…006 dispatch | **NOT AUTHORIZED** |
| MB2-Q1…Q6 | **NOT AUTHORIZED** |
| PX-4 | **NOT AUTHORIZED** |

---

## Next gate

Operator may authorize implementation with separate receipts per EWO:

```text
ASEP: AUTHORIZE PX-EXEC-EWO-002
ASEP: AUTHORIZE PX-EXEC-EWO-003
```

Parallel dispatch recommended (disjoint ownership). After both EWO reports PASS:

```text
Supervisor → Integration A → .asep/reports/PX-EXEC-INTEGRATION-A.md
```

Integration A PASS unblocks EWO-004 proposal + dispatch gate.

---

## WO-TRACE

```text
PX-EXEC-EWO-001 PASS (2026-07-06)
  → PX-EXEC-WAVE-A-ENGINEERING-PACKAGE + EWO-002/003 proposals
  → Architect review PASS (this decision)
  → Program graph sync
  → AUTHORIZE PX-EXEC-EWO-002 ∥ PX-EXEC-EWO-003
  → Integration A → EWO-004…
```
