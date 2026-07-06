# Architect Authorization — PX-EXEC-EWO-008

Program: px-exec  
Milestone: MB2 — Engineering Runtime (PX-EXEC-P2)  
Role: engineering (platform track)  
Status: **AUTHORIZED**  
Authorized EWO: **PX-EXEC-EWO-008** — Integration Plugin  
Pre-flight: **PASS**  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE PX-EXEC-EWO-008 per l'Integration Plugin`  
Timestamp: 2026-07-06T04:21:00+02:00  
Repository: `main` @ `a037bae`

---

## Intent resolution

```text
intent: authorize
program: px-exec
act: develop
role: engineering
scope: PX-EXEC-EWO-008 Integration Plugin implementation
```

---

## Pre-flight summary

```text
Pre-flight: PASS
  ✓ Program graph loads — .asep/programs/px-exec.yaml
  ✓ Phase 2 dispatch authorized — PX-EXEC-AUTHORIZATION-PHASE-2-DISPATCH-20260706.md
  ✓ EWO-007 PASS — .asep/reports/PX-EXEC-EWO-007-merge-plugin.md
  ✓ EWO-008 dependencies satisfied (EWO-007 implemented)
  ✓ Proposal registered — .asep/proposals/PX-EXEC-EWO-008-integration-plugin.md
  ✓ SoR frozen @ 2026-07-05 (.asep/certificates/MB2-SOR-20260705.yaml)
  ✓ make unit-builder-engine green (167 tests @ a037bae)
  ~ git working tree has unrelated doc edits (not in EWO-008 scope)
```

### `not_authorized` preserved

| Scope | Status |
|-------|--------|
| MB2 promotion / `mb2-complete` tag | **NOT authorized** |
| §13.3 golden path PASS | **NOT authorized** |
| PX-EXEC-EWO-009 Qualification Plugin | **NOT authorized** — blocked until EWO-008 PASS |
| PX-4 | **NOT authorized** |
| Product Plane (`backend/app/**`, `frontend/**`) | **NOT in scope** |

---

## EWO selection

| Field | Value |
|-------|-------|
| **Authorized EWO** | PX-EXEC-EWO-008 |
| **Capability** | `px-exec-8-integration-plugin` |
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-008-integration-plugin.md` |
| **Depends on** | EWO-007 — **satisfied** |
| **Backlog status** | `ready` → `implementing` |

---

## Develop constraints

| Do | Do not |
|----|--------|
| Implement IntegrationPlugin per SoR §8.2 | Claim §13.3 PASS or MB2 promotion |
| Emit IntegrationStarted/Passed/Failed events | Touch Qualification plugin (EWO-009) |
| Wire `post-merge-integration` rule hook | Modify merge.py (EWO-007 read-only) |
| Register via PluginRegistry | Modify SoR or governance |
| File EWO completion report on PASS | Touch product paths |

---

```text
Authorization Status: AUTHORIZED
Program: px-exec / PX-EXEC-P2
Pre-flight: PASS
Authorized EWO: PX-EXEC-EWO-008
Repository Status: main @ a037bae, unrelated doc edits present
Recommended Next Action: implement IntegrationPlugin → verify → report PASS
```
