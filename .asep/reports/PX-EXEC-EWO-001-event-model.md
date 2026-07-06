# PX-EXEC-EWO-001 — Event Model & Bus

Program: px-exec  
WorkOrder: PX-EXEC-EWO-001  
Capability: `px-exec-1-event-model`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-20260706.md`  
Proposal: `.asep/proposals/PX-EXEC-EWO-001-event-model.md`  
SoR: §6.1–§6.4 @ 2026-07-05  
Verdict: **PASS**  
Timestamp: 2026-07-06T02:31:00+02:00  
Repository: `main` @ `e171423` (+ EWO-001 implementation uncommitted)

---

## Summary

Extended `builder_engine/events.py` with MB2 §6.3 catalog (14 events), §6.4
`program_id` payload field, subscriber dispatch for at-least-once delivery within
process, and `replay()` / `redeliver()` helpers. Era I §6.2 catalog retained with
backward-compatible legacy JSONL lines (default `program_id: builder`).

**Does not satisfy MB2-Q2** — Rule Engine and MB2-Q-004 remain EWO-002 scope.

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/events.py` | ERA_I + MB2_EXTENSION catalogs; `program_id`; `subscribe` / `redeliver` / `replay` |
| `builder_engine/tests/test_mb2_event_catalog.py` | New — 10 acceptance tests |
| `builder_engine/tests/test_events.py` | `program_id` round-trip |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| All §6.2 Era I names in catalog | ✓ |
| All §6.3 MB2 extensions (14) in catalog | ✓ |
| `program_id` serialized + round-trip | ✓ |
| Unknown type rejected | ✓ |
| Append-only publish | ✓ |
| `subscribe()` on publish | ✓ |
| Idempotent redelivery contract (`redeliver`) | ✓ |
| Era I integration tests | ✓ |
| `make unit-builder-engine` | ✓ **75 passed** |
| No MB2-Q2 claim | ✓ |

---

## Traceability

| Req | SoR | Evidence |
|-----|-----|----------|
| REQ-01 | §6 event-driven | Catalog + bus dispatch hook |
| REQ-08 | INV-R-08 | Typed publish API; handlers on publish |
| REQ-18 | INV-R-09 | `redeliver()` + idempotency test |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/events.py` | yes |
| `builder_engine/tests/*` | yes |
| `backend/app/**` | no |
| `frontend/**` | no |
| SoR | no |

---

## Unblocks

- **PX-EXEC-EWO-002** Rule Engine (depends on event catalog + dispatch)
- **PX-EXEC-EWO-003** Dependency Engine (depends on `ExecutionGraphDerived` catalog)
- **PX-EXEC-EWO-006** State Projection (depends on bus + `ProjectionUpdated` catalog)

**Program graph:** synced 2026-07-06 — EWO-001 `implemented`; EWO-002/003 `ready`.

---

## WO-TRACE

```text
AUTHORIZE px-exec → PX-EXEC-EWO-001 → PASS → program graph sync
  → next: Architect review → AUTHORIZE EWO-002 | EWO-003
```
