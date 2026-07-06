# PX-EXEC — Reference Implementation Coverage

> **Metric:** SoR section implementation via px-exec EWOs — not MB2-Q qualification.  
> **SoR:** `docs/superpowers/specs/mb2-engineering-runtime-spec.md` (2026-07-05)  
> **Program:** `.asep/programs/px-exec.yaml`  
> **Updated:** 2026-07-06 — EWO-001 graph sync

---

## Scope boundary

| Track | Role |
|-------|------|
| **PX-3** | Conformance — product observes SoR (`.asep/reports/MB2-CONFORMANCE-COVERAGE.md`) |
| **px-exec** | Reference Implementation — `builder_engine/` under Wave A EWOs |

MB2-Q1…Q6 gates remain **not authorized** until separate qualification acts.

---

## Wave A EWO progress

| EWO | Capability | SoR | Status | Report |
|-----|------------|-----|--------|--------|
| PX-EXEC-EWO-001 | Event Model & Bus | §6 | **implemented** | `.asep/reports/PX-EXEC-EWO-001-event-model.md` |
| PX-EXEC-EWO-002 | Rule Engine | §7 | ready | — |
| PX-EXEC-EWO-003 | Dependency Engine | §4.2, §5 | ready | — |
| PX-EXEC-EWO-004 | Job Queue | §5 | blocked | — |
| PX-EXEC-EWO-005 | Scheduler | §8.2 | blocked | — |
| PX-EXEC-EWO-006 | State Projection | §9 | blocked | — |

---

## §6 Event model (EWO-001)

| Requirement | SoR | RI evidence |
|-------------|-----|-------------|
| Append-only log | §6.1 | `BuildEventBus.publish` — report PASS |
| Closed catalog §6.2 + §6.3 | §6.2, §6.3 | `ERA_I_EVENT_TYPES` + `MB2_EXTENSION_EVENT_TYPES` |
| Payload `program_id` | §6.4 | `BuildEvent.program_id` |
| At-least-once delivery hook | §6.1 | `subscribe()` / `redeliver()` |
| Idempotent handlers (contract) | INV-R-09 | Test + API — not MB2-Q-004 |

**MB2-Q2:** not claimed — Rule Engine (EWO-002) required for MB2-Q-004…006.

---

## Next ready (pending Architect authorization)

```text
PX-EXEC-EWO-002  Rule Engine       (§7)
PX-EXEC-EWO-003  Dependency Engine  (§4.2, §5)
```

Parallel after EWO-001 PASS; disjoint ownership per Wave A backlog.

---

## WO-TRACE

```text
EWO-001 implemented → program graph sync → Architect review → AUTHORIZE EWO-002 | EWO-003
```
