# Architect Authorization — PX-EXEC

Program: px-exec  
Milestone: MB2 — Engineering Runtime Reference Implementation  
Role: engineering (platform track)  
Status: **AUTHORIZED** (program) · **STOP** (no executable EWO)  
Authorized EWO: **NONE** — `workorder_backlog` empty  
Pre-flight: **STOP** (EWO selection)  
SoR revision: 2026-07-05  
Operator command: `ASEP: AUTHORIZE px-exec`  
Timestamp: 2026-07-05T21:26:00+02:00  
Repository: `main` @ `f67226c`

---

## Intent resolution

```text
intent: authorize
program: px-exec (Execution Orchestration Platform)
role: engineering
scope: px-exec only — first eligible EWO then report
```

---

## Pre-flight summary

```text
Pre-flight: STOP (no executable EWO)
  ✓ Program graph loads — .asep/programs/px-exec.yaml
  ✓ Capability graph loads — .asep/capabilities/px-exec.yaml
  ✓ SoR frozen @ 2026-07-05 (.asep/certificates/MB2-SOR-20260705.yaml)
  ✓ SoR header revision matches 2026-07-05
  ✓ PX-3 Conformance Program COMPLETE (Architect ratification 2026-07-05)
  ✓ MB2-CONFORMANCE-ASSESSMENT PASS (ratified)
  ✓ No normative SoR changes required (N-class: 0)
  ✓ Prior platform evidence — PX-1/PX-2 frozen; Era I MB2 cycle head/tail green
  ✓ Repository clean — main @ f67226c
  ✓ make ci green (373 backend + 243 frontend + 65 builder_engine + drift/scope/isolation)
  ✓ Scope guard — product paths not in scope; MB2-Q full qualification not invoked
  ✗ workorder_backlog empty — no PX-EXEC-EWO registered
  ✗ No .asep/proposals/PX-EXEC-EWO-*.md proposals exist
```

### `authorized_when` disposition

| Condition | Status |
|-----------|--------|
| PX-3 completed | **PASS** — ratified |
| MB2-CONFORMANCE-ASSESSMENT PASS | **PASS** — ratified |
| no_normative_sor_changes_required | **PASS** |
| MB2-Q1-pass | **Not satisfied** — expected; MB2-Q1 is Phase 1 **exit** gate (`implementation_gate`), not a pre-authorization blocker |

Architect `AUTHORIZE px-exec` satisfies program-level `implementation.status: not_authorized`.
MB2-Q1 remains the Phase 1 completion gate; it is **not** run as part of this authorization act.

---

## EWO selection

From `.asep/programs/px-exec.yaml`:

```yaml
workorder_backlog: []  # populated after MB2 freeze
```

**Result:** No executable EWO. Per `.asep/resolvers/authorize.md` → **STOP** before develop.

**First eligible capability node** (when backlog is populated):

| Node | Title | Phase | Dependencies |
|------|-------|-------|--------------|
| `px-exec-1-event-model` | Event Model & Bus | PX-EXEC-P1 | none |
| `px-exec-3-dependency-engine` | Dependency Engine | PX-EXEC-P1 | none |

Recommended first EWO: **PX-EXEC-EWO-001** → `px-exec-1-event-model` (listed first in Phase 1 DAG; foundation for rule engine, projection, and bus extensions per SoR §6).

---

## Constraints honored

| Constraint | Disposition |
|------------|-------------|
| SoR revision 2026-07-05 | Read-only — no SoR edits |
| Do not modify SoR unless N-class + Architect | No N-class evidence |
| Do not start PX-4 | Not invoked |
| Do not run MB2-Q complete qualification | Not invoked |
| px-exec scope only (`builder_engine/**`, platform docs, `.asep/reports/PX-EXEC-*`) | Honored — no product code touched |
| Stop on first governance violation / red gate / failed pre-flight | **STOP** at empty backlog |

---

## WO-TRACE

```text
PX-3 COMPLETE (ratified)
  → MB2-CONFORMANCE-ASSESSMENT PASS (ratified)
  → Architect: AUTHORIZE px-exec
  → Pre-flight PASS (repo, SoR, CI, PX-3 gates)
  → EWO selection: STOP (empty workorder_backlog)
  → WAIT — spawn PX-EXEC Wave A backlog + first proposal
```
