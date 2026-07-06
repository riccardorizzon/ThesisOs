# Architect Authorization — PX-EXEC-EWO-003

Program: px-exec  
WorkOrder: PX-EXEC-EWO-003  
Capability: `px-exec-3-dependency-engine`  
Milestone: MB2 — Engineering Runtime Reference Implementation  
Role: engineering (platform track)  
Status: **AUTHORIZED FOR DISPATCH**  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE PX-EXEC-EWO-003`  
Timestamp: 2026-07-06T02:45:00+02:00  
Repository: `main` @ `aadb265`

---

## Authorization chain

| Step | Artifact | Status |
|------|----------|--------|
| Program authorization | `.asep/reports/PX-EXEC-AUTHORIZATION-20260705.md` | PASS |
| Wave A backlog | `.asep/reports/PX-EXEC-WAVE-A-BACKLOG.md` | REGISTERED |
| Engineering package | `.asep/reports/PX-EXEC-WAVE-A-ENGINEERING-PACKAGE.md` | PASS |
| EWO-003 proposal | `.asep/proposals/PX-EXEC-EWO-003-dependency-engine.md` | APPROVED |
| Architect review decision | `.asep/reports/PX-EXEC-ARCHITECT-DECISION-20260706-WAVE-A-ENGINEERING-PACKAGE.md` | PASS |
| Program graph sync | `.asep/programs/px-exec.yaml` | SYNCED |

---

## Pre-flight summary

```text
Pre-flight: PASS
  ✓ Program graph loads
  ✓ Capability graph loads
  ✓ Dependency PX-EXEC-EWO-001 IMPLEMENTED PASS
  ✓ Proposal approved
  ✓ SoR frozen @ 2026-07-05
  ✓ Scope guard — product paths excluded
  ✓ No MB2-Q qualification claim
```

---

## EWO selection

| Field | Value |
|-------|-------|
| **Selected** | PX-EXEC-EWO-003 |
| **Capability** | `px-exec-3-dependency-engine` |
| **Title** | Dependency Engine |
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-003-dependency-engine.md` |
| **Depends on** | PX-EXEC-EWO-001 (satisfied) |
| **SoR anchor** | §4.1–§4.2, §5 |
| **Invariants** | INV-R-01, INV-R-02, INV-R-03 |

---

## Develop constraints

| Do | Do not |
|----|--------|
| Load Program Graph from `.asep/programs/*.yaml` | Edit Program Graph files programmatically |
| Derive Execution Graph + ReadySet + CriticalPath | Invent nodes not in Program Graph |
| Apply `merge_order` as topological tie-breaker | Use `merge_order` as hard dependency |
| Emit `ExecutionGraphDerived` with content hash | Mutate product code |
| File EWO completion report | Modify SoR |
| Preserve Era I `compute_ready()` parity (document-only) | Claim MB2-Q1 PASS |

---

## Still not authorized

| Scope | Status |
|-------|--------|
| EWO-002 | Authorized separately |
| EWO-004…006 | BLOCKED — Integration A |
| MB2-Q1…Q6 qualification | NOT authorized |
| PX-4 | NOT authorized |
| Phase 2+ plugins | NOT authorized |

---

## WO-TRACE

```text
AUTHORIZE px-exec → STOP → Wave A design → Architect review PASS
  → PX-EXEC-EWO-003 authorized → implement → report PASS
```
