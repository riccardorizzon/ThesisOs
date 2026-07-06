# PX-EXEC-EWO-006 — State Projection

Program: px-exec  
WorkOrder: PX-EXEC-EWO-006  
Capability: `px-exec-6-state-projection`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-EWO-006-20260706.md`  
SoR: §9 Projection model @ 2026-07-05  
Verdict: **PASS**  
Timestamp: 2026-07-06T04:15:00+02:00  

---

## Summary

Implemented State Projection Builder per SoR §9: `ProjectionDocument` schema v1,
`ProjectionBuilder` with deterministic `apply()` / `rebuild()` / `content_hash()`,
Phase 1 event handlers, YAML persistence at `.builder-engine/projection.yaml`, and
`ProjectionUpdated` emission on rebuild when bus is configured.

**Does not satisfy MB2-Q5** — qualification act and MB2-Q-013…015 remain separate.

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/projection.py` | New — document, builder, I/O |
| `builder_engine/tests/test_projection.py` | New — 14 acceptance tests |
| `builder_engine/tests/fixtures/projection_event_sequence.jsonl` | New — synthetic event log |
| `builder_engine/tests/fixtures/projection_schema_v1.yaml` | New — schema v1 golden fixture |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| Schema v1 all top-level keys present (stubs OK) | ✓ |
| `rebuild()` deterministic — same events → same `content_hash` | ✓ |
| `ProjectionUpdated` published on rebuild when bus configured | ✓ |
| No import from `scheduler.py` or `compute_ready` (AST check) | ✓ |
| `JobReady` / `JobClaimed` update jobs + queue counters | ✓ |
| `ExecutionGraphDerived` stores `graph_hash` metadata | ✓ |
| `EwoCompleted` / `RuntimeEscalated` status transitions | ✓ |
| Projection file write/read round-trip | ✓ |
| Era I events (CycleStarted) no-op — rebuild stable | ✓ |
| `ProjectionUpdated` ignored on input (no recursion) | ✓ |
| `make unit-builder-engine` projection tests | ✓ **14 passed** |
| No MB2-Q5 claim | ✓ |

---

## Verification

```text
pytest tests/test_projection.py  → 14 passed
make unit-builder-engine         → 131 passed, 1 failed (EWO-005 parallel)
```

The single suite failure is `tests/test_scheduler_mb2.py::test_era_compute_ready_unchanged`
— owned by PX-EXEC-EWO-005 (`scheduler.py`), outside EWO-006 exclusive write scope.
All EWO-006 acceptance tests pass; Era I tests excluding the parallel EWO-005 file: **123 passed**.

---

## Traceability

| Req | SoR | Evidence |
|-----|-----|----------|
| REQ-11 | §9.1 schema v1 | `ProjectionDocument.to_dict()` — all top-level keys |
| REQ-11 | §9.2 rebuild deterministic | `test_rebuild_deterministic`, `content_hash()` |
| REQ-11 | §9.3 read-only consumer | `load_projection()` / `read_projection()` — no queue mutation |
| REQ-20 | §9.3 CLI/dashboard prep | Persistence sidecar `.builder-engine/projection.yaml` |
| INV-R-11 | Projection never owns state | Rebuild-only from events |
| INV-R-12 | No scheduler logic | AST import guard; no `compute_ready` |
| INV-R-08 | `ProjectionUpdated` on rebuild | `test_projection_updated_emitted` |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/projection.py` | yes |
| `builder_engine/tests/test_projection.py` | yes |
| `builder_engine/tests/fixtures/projection_*` | yes |
| `builder_engine/scheduler.py` | no |
| `builder_engine/job_queue.py` | no (read-only types via events) |
| `builder_engine/dependency.py` | no |
| `builder_engine/cli.py` | no |
| `backend/app/**` | no |
| `frontend/**` | no |
| SoR | no |

---

## Unblocks

- Wave A Integration — CLI `status` can read projection (EWO-005 merge)
- Phase 3 dashboard — projection sidecar ready
- MB2-Q5 evidence collection (REQ-11, MB2-Q-013…015) — **not claimed by this EWO**
