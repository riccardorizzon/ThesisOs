# Architect Authorization — PX-EXEC-EWO-009

Program: px-exec  
Milestone: MB2 — Engineering Runtime (PX-EXEC-P2)  
Role: engineering (platform track)  
Status: **AUTHORIZED**  
Authorized EWO: **PX-EXEC-EWO-009** — Qualification Plugin  
Pre-flight: **PASS**  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE PX-EXEC-EWO-009`  
Timestamp: 2026-07-06T04:38:00+02:00  
Repository: `main` @ `4d876ec`

---

## Intent resolution

```text
intent: authorize
program: px-exec
act: develop
role: engineering
scope: PX-EXEC-EWO-009 Qualification Plugin implementation
```

---

## Pre-flight summary

```text
Pre-flight: PASS
  ✓ Program graph loads — .asep/programs/px-exec.yaml
  ✓ Phase 2 dispatch authorized — PX-EXEC-AUTHORIZATION-PHASE-2-DISPATCH-20260706.md
  ✓ EWO-008 PASS — .asep/reports/PX-EXEC-EWO-008-integration-plugin.md
  ✓ EWO-009 dependencies satisfied (EWO-008 implemented @ 4d876ec)
  ✓ Proposal registered — .asep/proposals/PX-EXEC-EWO-009-qualification-plugin.md
  ✓ SoR frozen @ 2026-07-05 (.asep/certificates/MB2-SOR-20260705.yaml)
  ✓ make unit-builder-engine green (175 tests @ 4d876ec)
  ✓ git working tree clean
```

### `not_authorized` preserved

| Scope | Status |
|-------|--------|
| MB2 promotion / `mb2-complete` tag | **NOT authorized** |
| §13.3 golden path PASS | **NOT authorized** |
| PX-4 | **NOT authorized** |
| Product Plane (`backend/app/**`, `frontend/**`) | **NOT in scope** |
| Governance auto-approval policy changes | **NOT in scope** |

---

## EWO selection

| Field | Value |
|-------|-------|
| **Authorized EWO** | PX-EXEC-EWO-009 |
| **Capability** | `px-exec-9-qualification-plugin` |
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-009-qualification-plugin.md` |
| **Depends on** | EWO-008 — **satisfied** |
| **Backlog status** | `ready` → `implementing` |

---

## Develop constraints

| Do | Do not |
|----|--------|
| Implement QualificationPlugin per SoR §8.2 | Claim §13.3 PASS or MB2 promotion |
| Emit QwoSpawned/Passed/Failed events | Auto-accept QWO PARTIAL/FAIL |
| Wire `post-integration-qwo` rule hook | Modify integration.py (read-only) |
| Escalate QwoFailed → RuntimeEscalated (WAIT) | Modify SoR or governance |
| Register via PluginRegistry | Touch product paths |

---

```text
Authorization Status: AUTHORIZED
Program: px-exec / PX-EXEC-P2
Pre-flight: PASS
Authorized EWO: PX-EXEC-EWO-009
Repository Status: main @ 4d876ec, working tree clean
Recommended Next Action: implement QualificationPlugin → verify → report PASS
```
