# Architect Authorization — PX-EXEC-EWO-007

Program: px-exec  
Milestone: MB2 — Engineering Runtime (PX-EXEC-P2)  
Role: engineering (platform track)  
Status: **AUTHORIZED**  
Authorized EWO: **PX-EXEC-EWO-007** — Merge Plugin  
Pre-flight: **PASS**  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE PX-EXEC-EWO-007`  
Timestamp: 2026-07-06T04:12:00+02:00  
Repository: `main` @ `26a5d1a`

---

## Intent resolution

```text
intent: authorize
program: px-exec
act: develop
role: engineering
scope: PX-EXEC-EWO-007 Merge Plugin implementation
```

---

## Pre-flight summary

```text
Pre-flight: PASS
  ✓ Program graph loads — .asep/programs/px-exec.yaml
  ✓ Phase 2 dispatch authorized — PX-EXEC-AUTHORIZATION-PHASE-2-DISPATCH-20260706.md
  ✓ Wave A complete — EWO-001…006 IMPLEMENTED
  ✓ MB2-Q4 Plugin Registry PASS — Phase 2 entry gate SATISFIED
  ✓ EWO-007 dependencies satisfied (001, 002, 003, 005)
  ✓ Proposal registered — .asep/proposals/PX-EXEC-EWO-007-merge-plugin.md
  ✓ SoR frozen @ 2026-07-05 (.asep/certificates/MB2-SOR-20260705.yaml)
  ✓ make unit-builder-engine green (157 tests @ 26a5d1a)
  ✓ git working tree clean
```

### `not_authorized` preserved

| Scope | Status |
|-------|--------|
| MB2 promotion / `mb2-complete` tag | **NOT authorized** |
| §13.3 golden path PASS | **NOT authorized** |
| PX-EXEC-EWO-008 Integration Plugin | **NOT authorized** — blocked until EWO-007 PASS |
| PX-EXEC-EWO-009 Qualification Plugin | **NOT authorized** |
| PX-4 | **NOT authorized** |
| Product Plane (`backend/app/**`, `frontend/**`) | **NOT in scope** |

---

## EWO selection

| Field | Value |
|-------|-------|
| **Authorized EWO** | PX-EXEC-EWO-007 |
| **Capability** | `px-exec-7-merge-plugin` |
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-007-merge-plugin.md` |
| **Depends on** | EWO-001, 002, 003, 005 — **satisfied** |
| **Backlog status** | `ready` → `implementing` |

---

## Develop constraints

| Do | Do not |
|----|--------|
| Implement MergePlugin per SoR §8.2 | In-process git merge |
| Emit MergeCompleted / MergeFailed events | Claim §13.3 PASS or MB2 promotion |
| Enforce merge_order (INV-R-03) | Touch Integration/Qualification plugins |
| Register via PluginRegistry | Modify SoR or governance |
| File EWO completion report on PASS | Touch product paths |

---

```text
Authorization Status: AUTHORIZED
Program: px-exec / PX-EXEC-P2
Pre-flight: PASS
Authorized EWO: PX-EXEC-EWO-007
Repository Status: main @ 26a5d1a, working tree clean
Recommended Next Action: implement MergePlugin → verify → report PASS
```
