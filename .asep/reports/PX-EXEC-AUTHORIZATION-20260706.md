# Architect Authorization — PX-EXEC

Program: px-exec  
Milestone: MB2 — Engineering Runtime Reference Implementation  
Role: engineering (platform track)  
Status: **AUTHORIZED**  
Authorized EWO: **PX-EXEC-EWO-001** — Event Model & Bus  
Pre-flight: **PASS** (working tree dirty — waived by operator authorization)  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE px-exec`  
Timestamp: 2026-07-06T02:09:00+02:00  
Repository: `main` @ `80bb8c9`

---

## Intent resolution

```text
intent: authorize
program: px-exec (Execution Orchestration Platform)
role: engineering
scope: first executable EWO → develop pipeline
```

---

## Pre-flight summary

```text
Pre-flight: PASS
  ✓ Program graph loads — .asep/programs/px-exec.yaml
  ✓ Capability graph loads — .asep/capabilities/px-exec.yaml
  ✓ Wave A backlog registered — workorder_backlog EWO-001…006
  ✓ Architect backlog review PASS — PX-EXEC-ARCHITECT-DECISION-20260705-WAVE-A-BACKLOG-REVIEW.md
  ✓ SoR frozen @ 2026-07-05 (.asep/certificates/MB2-SOR-20260705.yaml)
  ✓ PX-3 COMPLETE + MB2-CONFORMANCE-ASSESSMENT PASS (ratified)
  ✓ Program implementation authorized — PX-EXEC-AUTHORIZATION-20260705.md
  ✓ Proposal — .asep/proposals/PX-EXEC-EWO-001-event-model.md
  ✓ make unit-builder-engine green (65 tests @ 80bb8c9)
  ⚠ git working tree dirty — px-exec graph sync + Wave A artifacts (operator waived)
  ✓ Scope guard — product paths not in scope; MB2-Q not invoked
```

### `not_authorized` preserved

| Scope | Status |
|-------|--------|
| MB2-Q1…Q6 qualification | **NOT authorized** — separate acts |
| PX-4 | **NOT authorized** |
| Phase 2+ plugins | **NOT authorized** |

---

## EWO selection

| Field | Value |
|-------|-------|
| **Selected** | PX-EXEC-EWO-001 |
| **Capability** | `px-exec-1-event-model` |
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-001-event-model.md` |
| **Depends on** | none (satisfied) |
| **Backlog status** | `ready` |

Blocked until EWO-001 PASS: PX-EXEC-EWO-002…006

---

## Develop constraints

| Do | Do not |
|----|--------|
| Implement `builder_engine/events.py` per SoR §6 | Modify SoR |
| Add MB2 catalog tests | Claim MB2-Q2 PASS |
| File EWO completion report | Touch `backend/app/**`, `frontend/**` |
| Run `make unit-builder-engine` | Dispatch EWO-002+ |

---

## WO-TRACE

```text
AUTHORIZE px-exec (2026-07-05) → STOP (empty backlog)
  → Wave A design + graph sync
  → AUTHORIZE px-exec (2026-07-06) → PX-EXEC-EWO-001 authorized → develop
```
