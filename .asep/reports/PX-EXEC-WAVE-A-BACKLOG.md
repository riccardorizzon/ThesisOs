# PX-EXEC Wave A — Backlog Definition

> **Authority:** Architect (platform / MB2 Reference Implementation)  
> **Date:** 2026-07-05  
> **Status:** **REGISTERED** — program graph synced 2026-07-06 (EWO-001 implemented)  
> **Program:** `.asep/programs/px-exec.yaml`  
> **Phase:** PX-EXEC-P1 — Runtime Foundation  
> **SoR revision:** 2026-07-05 (read-only)  
> **Unblocks:** `.asep/reports/stop-20260705-px-exec-no-ewo.md` (empty `workorder_backlog`)

---

## Functional objective (PX-EXEC Phase 1)

Deliver the **Runtime Foundation** for MB2: event bus, rule engine, dependency engine,
job queue, scheduler, and state projection — **no product impact**, no Phase 2 plugins.

**Platform thesis** (ADR-0042 §1–§2):

```text
Governance Layer  →  What is permitted (Supervisor, QC, policies)
Runtime Layer     →  How work executes (events, rules, jobs, projection)
```

Wave A implements all six Phase 1 capabilities in dependency order. Wave A does **not**
claim MB2-Q1…Q6 qualification; it produces Reference Implementation artifacts that
**enable** gate evidence at Phase 1 exit (`implementation_gate: MB2-Q1-pass`).

---

## Authoritative sources (not agent-invented)

| Artifact | Role |
|----------|------|
| `docs/superpowers/specs/mb2-engineering-runtime-spec.md` | SoR §3–§7, §9, §10, §13–§14 (normative) |
| `docs/platform/runtime-model-v2.md` | Structural companion — §3–§6, §8–§9 |
| `decisions/ADR-0042-engineering-runtime.md` | Two-layer split, event-driven execution |
| `.asep/programs/px-exec.yaml` | Phase 1 scope, acceptance, forbidden paths |
| `.asep/capabilities/px-exec.yaml` | Capability DAG, per-node acceptance |
| `.asep/certificates/MB2-SOR-20260705.yaml` | Specification freeze @ 2026-07-05 |
| `.asep/reports/MB2-CONFORMANCE-ASSESSMENT.md` | PX-3 conformance PASS — SoR stable |
| `.asep/reports/PX-EXEC-AUTHORIZATION-20260705.md` | Program AUTHORIZED; EWO selection STOP |

**Deferred to Phase 2+ (not Wave A):** Merge / Integration / Qualification plugins,
dashboard UI, AgentProvider abstraction, multi-program queue, recovery policies.

---

## Wave A DAG

```text
PX-EXEC-EWO-001  Event Model & Bus (§6)
      │
      ├──────────────────────┬──────────────────────┐
      ▼                      ▼                      │
PX-EXEC-EWO-003          PX-EXEC-EWO-002            │
Dependency Engine        Rule Engine                │
(§4.2, §5)               (§7)                       │
      │                      │                      │
      ▼                      │                      │
PX-EXEC-EWO-004            │                      │
Job Queue (§5)             │                      │
      │                      │                      │
      └──────────┬───────────┘                      │
                 ▼                                  │
      PX-EXEC-EWO-005  Scheduler (§8.2)           │
                 │                                  │
                 └──────────────┬───────────────────┘
                                ▼
                   PX-EXEC-EWO-006  State Projection (§9)
```

| EWO | Title | Capability | SoR anchor | Parallel after |
|-----|-------|------------|------------|----------------|
| **PX-EXEC-EWO-001** | Event Model & Bus | `px-exec-1-event-model` | §6 Event model | — (first executable) |
| **PX-EXEC-EWO-002** | Rule Engine | `px-exec-2-rule-engine` | §7 Rule model | 001 |
| **PX-EXEC-EWO-003** | Dependency Engine | `px-exec-3-dependency-engine` | §4.2, §5 Job model | 001 |
| **PX-EXEC-EWO-004** | Job Queue | `px-exec-4-job-queue` | §5, ADR-0025 | 003 |
| **PX-EXEC-EWO-005** | Scheduler | `px-exec-5-scheduler` | §8.2 scheduler plugin | 004 + 002 |
| **PX-EXEC-EWO-006** | State Projection | `px-exec-6-state-projection` | §9 Projection model | 001 (may run ∥ 002–005 after bus stable) |

**First executable EWO:** `PX-EXEC-EWO-001` (no dependencies; proposal drafted separately).

**Parallelism note:** EWO-002 and EWO-003 are disjoint ownership after EWO-001.
EWO-006 may start once the v2 catalog and `program_id` payload are stable (post-001);
integration with rule/queue events completes before Wave A exit.

---

## Execution model

Platform program: `.asep/programs/px-exec.yaml`

```text
AUTHORIZE px-exec (program)     ← DONE @ 2026-07-05
      ↓
STOP — empty workorder_backlog  ← current state
      ↓
Architect review Wave A backlog + PX-EXEC-EWO-001 proposal
      ↓
Register workorder_backlog in px-exec.yaml
      ↓
AUTHORIZE PX-EXEC-EWO-001 (or re-AUTHORIZE px-exec)
      ↓
PX-EXEC-EWO-001 → … → PX-EXEC-EWO-006
      ↓
Phase 1 exit gate: MB2-Q1-pass (separate qualification act — not Wave A design)
```

**Scope guard:** `builder_engine/**`, `docs/platform/**`, `.asep/reports/PX-EXEC-*`,
`.asep/proposals/PX-EXEC-*` only. No `backend/app/**`, no `frontend/**`, no SoR edits.

---

## Per-EWO summary (proposals to follow)

### PX-EXEC-EWO-001 — Event Model & Bus

| Field | Value |
|-------|-------|
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-001-event-model.md` |
| **Primary SoR** | §6.1–§6.4 |
| **Invariants** | INV-R-08, INV-R-09 |
| **REQ trace** | REQ-01, REQ-08, REQ-18 |
| **Gate enablement** | MB2-Q2 partial (catalog + payload; not full rule replay) |
| **Artifacts** | `builder_engine/events.py`, `builder_engine/tests/test_events.py`, new MB2 catalog tests |

### PX-EXEC-EWO-002 — Rule Engine

| Field | Value |
|-------|-------|
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-002-rule-engine.md` (future) |
| **Primary SoR** | §7.1–§7.4 |
| **Invariants** | INV-R-07, INV-R-13 |
| **Gate enablement** | MB2-Q2 — MB2-Q-004…006 |
| **Artifacts** | `builder_engine/rules.py` (new), rule pack loader, golden PX-2 rules fixture |

### PX-EXEC-EWO-003 — Dependency Engine

| Field | Value |
|-------|-------|
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-003-dependency-engine.md` (future) |
| **Primary SoR** | §4.1–§4.2, §5 |
| **Invariants** | INV-R-01, INV-R-02, INV-R-03 |
| **Gate enablement** | MB2-Q1 — MB2-Q-001…003 |
| **Artifacts** | Extend `builder_engine/graph.py` or dedicated derivation module |

### PX-EXEC-EWO-004 — Job Queue

| Field | Value |
|-------|-------|
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-004-job-queue.md` (future) |
| **Primary SoR** | §5 Job FSM |
| **Invariants** | ADR-0025 alignment |
| **Gate enablement** | MB2-Q1 partial |
| **Artifacts** | Job queue module, FSM transitions, event emission per INV-R-08 |

### PX-EXEC-EWO-005 — Scheduler

| Field | Value |
|-------|-------|
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-005-scheduler.md` (future) |
| **Primary SoR** | §8.2 scheduler plugin |
| **Invariants** | INV-R-16 (WAIT halts claims) |
| **Gate enablement** | MB2-Q3 — MB2-Q-007…009 |
| **Artifacts** | `builder_engine/scheduler.py` |

### PX-EXEC-EWO-006 — State Projection

| Field | Value |
|-------|-------|
| **Proposal** | `.asep/proposals/PX-EXEC-EWO-006-state-projection.md` (future) |
| **Primary SoR** | §9 Projection model |
| **Invariants** | INV-R-11, INV-R-12 |
| **Gate enablement** | MB2-Q5 partial — MB2-Q-013…015 |
| **Artifacts** | Projection builder, schema v1, `ProjectionUpdated` emission |

---

## Wave A exit criteria (PASS)

Wave A is **PASS** only when **all** of:

1. **PX-EXEC-EWO-001…006** each report PASS with EWO completion reports under `.asep/reports/`
2. `make unit-builder-engine` green including new MB2 test modules introduced by Wave A
3. Era I event catalog retained — no breaking changes to existing cycle tests
4. v2 MB2 catalog events (SoR §6.3) defined and enforced in `ALLOWED_EVENT_TYPES`
5. Every Runtime state transition in Wave A scope emits typed events (INV-R-08)
6. **No N-class SoR deviation** recorded — clarifications via `sor-compatibility-policy` only
7. **No MB2-Q1…Q6 qualification claim** in Wave A reports — gate reports are separate acts

Wave A does **not** satisfy `implementation_gate: MB2-Q1-pass` by itself; that gate
requires `.asep/reports/MB2-Q1-*.md` with MB2-Q-001…003 evidence after EWO-003+.

---

## Explicit exclusions

| Exclusion | Reason |
|-----------|--------|
| `backend/app/**`, `frontend/**` | px-exec platform scope; product is PX-3/PX-4 |
| SoR amendment | Frozen @ 2026-07-05; N-class requires Architect |
| MB2-Q full qualification run | Separate qualification acts per §13 |
| Phase 2 plugins (merge, integration, QWO) | PX-EXEC-P2 |
| PX-4 product milestone | Out of scope |
| Supervisor auto-delegation to Runtime | §10 — Phase 1 partial only |
| Dashboard / CLI scheduling logic | NG-5; projection read-only |

---

## Registration (post-review — not done in this design act)

After Architect approves this backlog and EWO-001 proposal, operator or Architect syncs:

```yaml
# .asep/programs/px-exec.yaml — workorder_backlog (illustrative)
workorder_backlog:
  - id: PX-EXEC-EWO-001
    capability: px-exec-1-event-model
    proposal: .asep/proposals/PX-EXEC-EWO-001-event-model.md
    status: proposed
  - id: PX-EXEC-EWO-002
    capability: px-exec-2-rule-engine
    depends_on: [PX-EXEC-EWO-001]
    status: blocked
  # … EWO-003…006 per DAG above
```

Then: `ASEP: AUTHORIZE PX-EXEC-EWO-001` or `ASEP: AUTHORIZE px-exec`.

---

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R-A1 | `program_id` payload migration breaks Era I tests | Medium | Medium | EWO-001 preserves Era I fields; additive schema only |
| R-A2 | Premature MB2-Q claim | Low | High | Wave A exit criteria forbid qualification claims |
| R-A3 | Rule engine scope creep into Governance | Medium | High | EWO-002 explicit INV-R-07 exclusion; MB2-Q-005 test |
| R-A4 | Parallel EWO file conflicts | Medium | Medium | Disjoint ownership per proposal; sync barrier between waves |

---

## WO-TRACE

```text
MB2 SoR FREEZE (2026-07-05)
  → PX-3 COMPLETE + MB2-CONFORMANCE-ASSESSMENT PASS
  → AUTHORIZE px-exec → STOP (empty backlog)
  → PX-EXEC-WAVE-A-BACKLOG (this doc) + PX-EXEC-EWO-001 proposal
  → Architect review → backlog registration → EWO-001 dispatch
  → … → Wave A PASS → MB2-Q gates (separate)
```
