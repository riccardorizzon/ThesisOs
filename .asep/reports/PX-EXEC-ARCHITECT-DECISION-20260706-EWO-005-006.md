# Architect Decision — PX-EXEC EWO-005 + EWO-006

> **Date:** 2026-07-06  
> **Authority:** Architect  
> **Program:** PX-EXEC — Execution Orchestration Platform  
> **Phase:** PX-EXEC-P1 — Runtime Foundation (Wave A convergence)  
> **SoR revision:** 2026-07-05 (frozen)  
> **Artifacts reviewed:**  
> - `.asep/proposals/PX-EXEC-EWO-005-scheduler.md`  
> - `.asep/proposals/PX-EXEC-EWO-006-state-projection.md`  
> **Prerequisites:** EWO-001…004 IMPLEMENTED PASS; Integration A PASS  
> **Scope:** Design review and parallel dispatch authorization

---

## Decision

```text
1. PX-EXEC-EWO-005 Scheduler:           APPROVED FOR DISPATCH

2. PX-EXEC-EWO-006 State Projection:    APPROVED FOR DISPATCH

3. Parallel dispatch (005 ∥ 006):        AUTHORIZED

Wave A Integration (005 → 006 merge):   AUTHORIZED after both EWO reports PASS

MB2-Q3 / MB2-Q5 qualification:          NOT AUTHORIZED
```

---

## EWO-005 assessment

| Area | Verdict |
|------|---------|
| SoR §8.2 scheduler plugin interface | Coherent — claim/release/build_manifest |
| §10.1 WAIT / STOP gate | Correctly framed (INV-R-16) |
| Era I `compute_ready()` preservation | Required and explicit |
| JobQueue integration | Correct dependency on EWO-004 |
| RuleEngine hook (stub) | Phase 1 appropriate |
| MB2-Q boundary | Preserved |

**Condition:** Do not modify `EngineeringRuntime.schedule()` in EWO-005 scope.

---

## EWO-006 assessment

| Area | Verdict |
|------|---------|
| SoR §9.1 schema v1 | Complete field list; stubs OK for Phase 2 sections |
| §9.2 deterministic rebuild | Coherent |
| INV-R-11 / INV-R-12 | Explicit — no scheduler imports |
| Synthetic fixtures for unit tests | Correct; live cross-module at Wave A Integration |
| MB2-Q boundary | Preserved |

**Condition:** `cli.py` changes deferred to Wave A Integration unless ≤20 lines read-only.

---

## Dispatch state

| Element | Status |
|---------|--------|
| EWO-005 proposal | **APPROVED FOR DISPATCH** |
| EWO-006 proposal | **APPROVED FOR DISPATCH** |
| Parallel dispatch | **AUTHORIZED** |
| Wave A Integration | **PENDING** (after 005 + 006 PASS) |
| Wave A implementation PASS | **PENDING** |
| MB2-Q1…Q6 | **NOT AUTHORIZED** |

---

## Next gate

```text
ASEP: AUTHORIZE PX-EXEC-EWO-005
ASEP: AUTHORIZE PX-EXEC-EWO-006
→ parallel sub-agents → merge 005 → 006 → PX-EXEC-INTEGRATION-WAVE-A.md
```
