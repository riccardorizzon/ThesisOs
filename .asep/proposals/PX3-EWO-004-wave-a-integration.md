# Engineering WorkOrder Proposal — PX3-EWO-004

> **Status:** ✅ **IMPLEMENTED** — `.asep/reports/PX3-INTEGRATION-A.md` PASS
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Wave: `px3-parallel/wave_a_integration`  
> Type: Integration EWO (supervisor-owned)

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-004 |
| **Sub-agent** | Supervisor |
| **Type** | **EWO** — Integration |
| **EWO category** | **Infrastructure** |
| **Capability** | `px3-ewo-004-wave-a-integration` |
| **Milestone** | PX-3 Knowledge Experience |
| **Depends on** | PX3-EWO-002, PX3-EWO-003 |

---

## Objective

Integrate Wave A deliverables: merge parallel worktrees, wire cross-module navigation
(Sources ↔ Knowledge), verify regression, and produce integration evidence.

---

## Scope

### In scope

1. **Merge** — worktrees in order: PX3-EWO-002 → PX3-EWO-003
2. **Cross-links** — concept chips on source cards open Knowledge routes; Explorer
   source count links open Sources (UI spec §4 navigation model)
3. **Regression** — `make ci`; spot-check PX-2 cite flow + ContextBar
4. **Report** — `.asep/reports/PX3-INTEGRATION-A.md`
5. **Conformance log** — record any I/S/A/N deviations discovered during integration

### Out of scope

- New product features beyond wiring
- Wave B planning
- QWO / milestone qualification

---

## Acceptance Criteria

- [ ] Integrated tree builds; `make ci` green
- [ ] Sources ↔ Knowledge navigation works per UI spec §4
- [ ] PX3-INTEGRATION-A.md written with PASS/FAIL verdict
- [ ] No open N-class conformance blockers
- [ ] Wave B **not** auto-authorized — remains undefined

---

## WO-TRACE

```text
PX3-EWO-002 + PX3-EWO-003 → PX3-EWO-004 → Wave A complete (WAIT for Architect)
```
