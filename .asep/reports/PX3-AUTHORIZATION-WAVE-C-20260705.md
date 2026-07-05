# Architect Authorization — PX-3 Wave C Dispatch

Program: thesisos-product-v2  
Milestone: PX-3 Knowledge Experience  
Wave: **C — Execution & Job State Observation**  
Role: conformance  
Status: **DISPATCH AUTHORIZED (EWO-008 only)**  
Authorized EWO: **PX3-EWO-008**  
Pending EWOs: **PX3-EWO-009**, **PX3-EWO-010** (await prior PASS)  
Pre-flight: **PASS** (Wave B complete; backlog review PASS)  
SoR revision: 2026-07-05  
Architect decision: `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-C-BACKLOG-REVIEW.md`  
Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`  
Timestamp: 2026-07-05

---

## Authorization scope

Wave C EWOs **008 → 009 → 010** are registered in the Program Graph.

**Only PX3-EWO-008 is authorized for execution** in this act. EWO-009 and EWO-010
require separate authorization after prior EWO PASS evidence.

Product-only conformance program. No SoR modification. No governance modification.
No Runtime Engineering / `builder_engine/` implementation.

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Wave B complete | ✓ Integration B PASS |
| Backlog design | ✓ APPROVED |
| Backlog review | ✓ PASS |
| Wave C backlog registered | ✓ Program Graph + proposals |
| SoR certificate | ✓ `.asep/certificates/MB2-SOR-20260705.yaml` |
| Conformance log | ✓ N=0 |
| First executable EWO | ✓ PX3-EWO-008 |

---

## Wave C DAG

```text
PX3-EWO-008  Execution Graph Observation (§4.2)     ← AUTHORIZED
      ↓
PX3-EWO-009  Job FSM Observation (§5)                ← PENDING
      ↓
PX3-EWO-010  Conformance Integration C             ← PENDING
```

---

## Wave C exit criteria

Wave C PASS requires: all EWOs PASS; Conformance Integration C PASS; no N-class in log;
coverage matrix +≥2 Observable rows (§4.2, §5) vs Wave B baseline; INV-R-12 re-verified.

---

## Constraints

| Constraint | Enforced |
|------------|----------|
| Product-only | ✓ `frontend/`, `backend/app/` |
| No SoR modification | ✓ |
| No governance modification | ✓ |
| No `builder_engine/` | ✓ |
| No ReadySet computation | ✓ INV-R-12 |
| §11 failure | Natural only — never forced |

---

## WO-TRACE

```text
AUTHORIZE PX-3 Wave C → PX3-EWO-008 (STOP after PASS — await authorize for 009)
```
