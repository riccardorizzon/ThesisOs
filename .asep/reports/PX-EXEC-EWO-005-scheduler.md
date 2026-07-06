# PX-EXEC-EWO-005 — Scheduler

Program: px-exec  
WorkOrder: PX-EXEC-EWO-005  
Capability: `px-exec-5-scheduler`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-EWO-005-20260706.md`  
SoR: §8.2 Scheduler plugin, §5 Job FSM, §10.1 WAIT behavior  
Verdict: **PASS**  
Timestamp: 2026-07-06T04:00:00+02:00  

---

## Summary

Extended `builder_engine/scheduler.py` with MB2 Scheduler plugin interface per SoR §8.2:
`SupervisorGate` (EXECUTE/WAIT/STOP), `SchedulerHaltedError`, `DispatchManifest` +
`build_manifest`, and `SchedulerPlugin` with `claim`, `release`, `claim_next`, and
`on_action` stub. Era I functions (`compute_ready`, `in_flight_packets`,
`file_locks_for_packet`) retained unchanged.

**Does not satisfy MB2-Q3** — qualification act and MB2-Q-007…009 remain separate.

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/scheduler.py` | Extended — MB2 types + `SchedulerPlugin` |
| `builder_engine/tests/test_scheduler_mb2.py` | New — 9 acceptance tests |
| `builder_engine/tests/fixtures/dispatch_manifest_v1.json` | New — manifest schema stub |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| `SchedulerPlugin.claim` / `release` delegate to `JobQueue` | ✓ |
| WAIT halts new claims — no `JobClaimed` emitted (INV-R-16) | ✓ |
| STOP halts new claims (same as WAIT for Phase 1) | ✓ |
| `build_manifest` produces deterministic JSON for same job set | ✓ |
| `claim_next` respects `JobQueue.ready_queue()` merge_order | ✓ |
| Era I `compute_ready()` tests unchanged | ✓ |
| `on_action` does not mutate queue without explicit claim (stub/log only) | ✓ |
| Manifest written to `.builder-engine/last-dispatch-manifest.json` | ✓ |
| `make unit-builder-engine` | ✓ **132 passed** |
| No MB2-Q3 PASS claim | ✓ |

---

## Traceability

| Req | SoR | Evidence |
|-----|-----|----------|
| REQ-12 | §10.1 WAIT halts progression | `SupervisorGate.WAIT` → `SchedulerHaltedError`; no `JobClaimed` |
| REQ-12 | INV-R-16 | `claim` / `claim_next` gated on `EXECUTE` only |
| REQ-14 | §5 Job FSM claim path | `SchedulerPlugin.claim` → `JobQueue.claim` |
| REQ-09 prep | §8.2 deterministic manifest | `build_manifest` sorted job_ids; fixture + test |
| §8.2 | Scheduler plugin API | `claim`, `release`, `build_manifest`, `claim_next` |
| §7.1 hook | Rule action → scheduler | `on_action` log-only stub |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/scheduler.py` | yes (extend) |
| `builder_engine/tests/test_scheduler_mb2.py` | yes |
| `builder_engine/tests/fixtures/dispatch_manifest_v1.json` | yes |
| `builder_engine/job_queue.py` | no (read-only) |
| `builder_engine/rules.py` | no (read-only `ActionDescriptor`) |
| `builder_engine/projection.py` | no |
| `builder_engine/runtime.py` | no |
| `backend/app/**` | no |
| `frontend/**` | no |
| SoR | no |

---

## Unblocks

- Wave A Integration (with EWO-006 PASS)
- Phase 2 plugin registry wiring to `SchedulerPlugin`
- Future MB2-Q3 evidence (REQ-12, MB2-Q-007…009) — **not claimed here**

---

## WO-TRACE

```text
EWO-004 PASS + EWO-002 PASS
  → PX-EXEC-EWO-005 AUTHORIZED
  → implement SchedulerPlugin → verify PASS
  → next: Wave A Integration (EWO-005 + EWO-006)
  → MB2-Q3 qualification: NOT AUTHORIZED
```
