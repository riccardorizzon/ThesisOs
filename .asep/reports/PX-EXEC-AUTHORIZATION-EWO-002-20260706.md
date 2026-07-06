# Architect Authorization — PX-EXEC-EWO-002

Program: px-exec  
WorkOrder: PX-EXEC-EWO-002  
Capability: `px-exec-2-rule-engine`  
Milestone: MB2 — Engineering Runtime Reference Implementation  
Role: engineering (platform track)  
Status: **AUTHORIZED FOR DISPATCH**  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE PX-EXEC-EWO-002`  
Timestamp: 2026-07-06T02:45:00+02:00  
Repository: `main` @ `aadb265`

---

## Authorization chain

| Step | Artifact | Status |
|------|----------|--------|
| Program authorization | `.asep/reports/PX-EXEC-AUTHORIZATION-20260705.md` | PASS |
| Wave A backlog | `.asep/reports/PX-EXEC-WAVE-A-BACKLOG.md` | REGISTERED |
| Engineering package | `.asep/reports/PX-EXEC-WAVE-A-ENGINEERING-PACKAGE.md` | PASS |
| EWO-002 proposal | `.asep/proposals/PX-EXEC-EWO-002-rule-engine.md` | APPROVED |
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
| **Selected** | PX-EXEC-EWO-002 |
| **Capability** | `px-exec-2-rule-engine` |
| **Title** | Rule Engine |
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-002-rule-engine.md` |
| **Depends on** | PX-EXEC-EWO-001 (satisfied) |
| **SoR anchor** | §7.1–§7.4 |
| **Invariants** | INV-R-07, INV-R-13, INV-R-14, INV-R-15 |

---

## Develop constraints

| Do | Do not |
|----|--------|
| Implement `builder_engine/rules.py` | Evaluate Governance policy (QC, freeze, Constitution) |
| Implement `builder_engine/plugins.py` registry stub | Import plugin implementations directly in core |
| Wire `RuleEngine` to `BuildEventBus.subscribe()` | Mutate product code |
| Load rule packs from YAML per `program_id` | Modify SoR |
| Emit `RuntimeEscalated` on rule failures | Claim MB2-Q2 PASS |
| File EWO completion report | Dispatch EWO-004…006 |

---

## Still not authorized

| Scope | Status |
|-------|--------|
| EWO-003 | Authorized separately |
| EWO-004…006 | BLOCKED — Integration A |
| MB2-Q1…Q6 qualification | NOT authorized |
| PX-4 | NOT authorized |
| Phase 2+ plugins | NOT authorized |

---

## WO-TRACE

```text
AUTHORIZE px-exec → STOP → Wave A design → Architect review PASS
  → PX-EXEC-EWO-002 authorized → implement → report PASS
```
