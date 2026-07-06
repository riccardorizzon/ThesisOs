# Architect Decision — PX-EXEC Wave A Backlog Review

> **Date:** 2026-07-05  
> **Authority:** Architect  
> **Program:** PX-EXEC — Execution Orchestration Platform  
> **Artifacts reviewed:**  
> - `.asep/reports/PX-EXEC-WAVE-A-BACKLOG.md`  
> - `.asep/proposals/PX-EXEC-EWO-001-event-model.md`  
> **Scope:** Design review and registration authorization; no implementation dispatch

---

## Decision

```text
Wave A Backlog Design: PASS

PX-EXEC-EWO-001 Proposal: APPROVED FOR REGISTRATION

Backlog Registration: AUTHORIZED

Implementation Dispatch: NOT AUTHORIZED UNTIL PROGRAM GRAPH SYNC
```

---

## Architectural Assessment

The proposed Wave A correctly defines the PX-EXEC Phase 1 Runtime Foundation:

- Event Model & Bus
- Rule Engine
- Dependency Engine
- Job Queue
- Scheduler
- State Projection

The sequencing is coherent: Event Model & Bus is the correct first executable EWO because
later runtime state changes and projection updates require typed append-only events.

The proposal preserves the required boundary:

- no Product Plane work
- no SoR amendment
- no MB2-Q qualification claim
- no Phase 2 plugin scope
- no PX-4 work

---

## EWO-001 Assessment

`PX-EXEC-EWO-001` is scoped correctly to SoR §6:

| Area | Verdict |
|------|---------|
| §6.1 append-only bus | Coherent |
| §6.2 Era I catalog retention | Required and included |
| §6.3 MB2 event catalog extensions | Required and included |
| §6.4 `program_id` payload field | Required and included |
| INV-R-08 typed emission contract | Correctly framed as contract enablement |
| INV-R-09 idempotent handler contract | Correctly framed as bus/subscriber contract |
| MB2-Q boundary | Preserved |

The EWO must not claim MB2-Q2 PASS. It may only state that catalog, payload, and bus
delivery primitives enable later MB2-Q2 evidence.

---

## Required Program Graph Sync

Before dispatch, the px-exec program graph must be synchronized with the authorization
state and Wave A backlog.

Required updates:

1. `.asep/programs/px-exec.yaml`
   - record that program-level implementation authorization has been granted
   - permit code mutation only under registered EWO scope
   - add `.asep/proposals/PX-EXEC-*.md` to active allowed paths
   - register `PX-EXEC-EWO-001` through `PX-EXEC-EWO-006` in `workorder_backlog`
   - mark `PX-EXEC-EWO-001` as first executable / ready
   - keep downstream EWOs blocked until dependencies pass

2. `.asep/capabilities/px-exec.yaml`
   - mark `px-exec-1-event-model` as ready or implementation-ready
   - preserve later Phase 1 nodes as specified/blocked according to dependencies

3. Reports
   - retain `PX-EXEC-WAVE-A-BACKLOG.md`
   - retain `PX-EXEC-EWO-001-event-model.md`
   - retain this decision as the review authority

---

## Dispatch State

| Element | Status |
|---------|--------|
| PX-EXEC program authorization | Granted at program level |
| Wave A backlog design | **APPROVED** |
| PX-EXEC-EWO-001 proposal | **APPROVED FOR REGISTRATION** |
| Backlog registration | **AUTHORIZED** |
| PX-EXEC-EWO-001 dispatch | **NOT YET AUTHORIZED** |
| PX-EXEC-EWO-002...006 dispatch | **NOT AUTHORIZED** |
| MB2-Q | **NOT AUTHORIZED** |
| PX-4 | **NOT AUTHORIZED** |

---

## Next Gate

After program graph sync, the operator may re-run:

```text
ASEP: AUTHORIZE px-exec
```

or explicitly:

```text
ASEP: AUTHORIZE PX-EXEC-EWO-001
```

The resolver should then select `PX-EXEC-EWO-001` as the first executable WorkOrder.

---

## WO-TRACE

```text
AUTHORIZE px-exec
  → STOP: empty workorder_backlog
  → Draft Wave A backlog + EWO-001 proposal
  → Architect review PASS
  → Register Wave A backlog
  → Re-authorize / dispatch PX-EXEC-EWO-001
```
