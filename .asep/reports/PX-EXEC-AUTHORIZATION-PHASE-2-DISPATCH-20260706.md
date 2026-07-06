# Architect Authorization — Phase 2 Plugin Dispatch

Program: px-exec  
Milestone: MB2 — Engineering Runtime (PX-EXEC-P2)  
Role: engineering (platform track)  
Status: **AUTHORIZED**  
Authorized scope: **Phase 2 backlog + EWO-007…009 proposals registered**  
First executable EWO: **PX-EXEC-EWO-007** — Merge Plugin  
Pre-flight: **PASS**  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE Phase 2 plugin dispatch`  
Timestamp: 2026-07-06T06:30:00+02:00  
Repository: `main` @ `8e69731`

---

## Intent resolution

```text
intent: authorize
program: px-exec
act: phase-2-plugin-dispatch
role: engineering
scope: register Phase 2 backlog + EWO proposals; first executable EWO-007
```

---

## Pre-flight summary

```text
Pre-flight: PASS
  ✓ Program graph loads — .asep/programs/px-exec.yaml
  ✓ Capability graph loads — .asep/capabilities/px-exec.yaml
  ✓ Wave A complete — EWO-001…006 IMPLEMENTED
  ✓ MB2-Q1…Q6 PASS — qualification bundle ratified
  ✓ Phase 2 implementation gate MB2-Q4-pass — SATISFIED
  ✓ Promotion review — Phase 2 entry listed as permissible next gate
  ✓ SoR frozen @ 2026-07-05 (.asep/certificates/MB2-SOR-20260705.yaml)
  ✓ make unit-builder-engine green (157 tests @ 8e69731)
  ✓ git working tree clean
  ✓ Scope guard — product paths not in scope; MB2 promotion not pre-authorized
```

### `not_authorized` preserved

| Scope | Status |
|-------|--------|
| MB2 promotion / `mb2-complete` tag | **NOT authorized** |
| §13.3 golden path PASS | **NOT authorized** — separate act |
| PX-4 | **NOT authorized** |
| Phase 3+ observability | **NOT authorized** |
| Phase 4 provider abstraction | **NOT authorized** |

### `not_authorized` lifted

| Scope | Status |
|-------|--------|
| Phase 2 execution plugins (px-exec-7…9) | **AUTHORIZED** — dispatch + proposals |

---

## Registered artifacts

| Artifact | Role |
|----------|------|
| `.asep/reports/PX-EXEC-PHASE-2-BACKLOG.md` | Phase 2 backlog definition |
| `.asep/proposals/PX-EXEC-EWO-007-merge-plugin.md` | Merge Plugin proposal |
| `.asep/proposals/PX-EXEC-EWO-008-integration-plugin.md` | Integration Plugin proposal |
| `.asep/proposals/PX-EXEC-EWO-009-qualification-plugin.md` | Qualification Plugin proposal |

Program graph synced: `workorder_backlog` EWO-007…009; `phase_2` section; capabilities
`px-exec-7-merge-plugin` → `ready`.

---

## EWO selection

| Field | Value |
|-------|-------|
| **First executable** | PX-EXEC-EWO-007 |
| **Capability** | `px-exec-7-merge-plugin` |
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-007-merge-plugin.md` |
| **Depends on** | Wave A (001…006) — **satisfied** |
| **Backlog status** | `ready` |

| EWO | Status | Dispatch |
|-----|--------|----------|
| PX-EXEC-EWO-007 | ready | approved_for_registration — develop requires explicit authorization |
| PX-EXEC-EWO-008 | blocked | until EWO-007 PASS |
| PX-EXEC-EWO-009 | blocked | until EWO-008 PASS |

---

## Develop constraints

| Do | Do not |
|----|--------|
| Register Phase 2 backlog and proposals | Claim §13.3 golden path PASS |
| Mark EWO-007 ready for develop authorization | Implement without per-EWO authorization |
| Preserve serial dependency 007 → 008 → 009 | Touch `backend/app/**`, `frontend/**` |
| File this authorization receipt | Promote MB2 / apply `mb2-complete` tag |

Per-EWO develop authorization:

```text
ASEP: AUTHORIZE PX-EXEC-EWO-007
```

---

## WO-TRACE

```text
MB2-Q1…Q6 PASS → promotion review (§13.3 PARTIAL)
  → AUTHORIZE Phase 2 plugin dispatch
  → backlog + proposals registered
  → EWO-007 ready
  → WAIT: AUTHORIZE PX-EXEC-EWO-007
```

---

```text
Authorization Status: AUTHORIZED
Program: px-exec / PX-EXEC-P2
Pre-flight: PASS
Authorized EWO: PX-EXEC-EWO-007 (ready — develop pending)
Repository Status: main @ 8e69731, working tree clean
Recommended Next Action: ASEP: AUTHORIZE PX-EXEC-EWO-007 → implement Merge Plugin
```
