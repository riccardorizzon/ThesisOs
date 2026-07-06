# PX-EXEC Wave A — Engineering Package

> **Authority:** Engineering design act — Architect review for Wave A authorization  
> **Date:** 2026-07-06  
> **Status:** **PROPOSED** — sufficient for Wave A authorization review; **not** implementation dispatch  
> **Program:** `.asep/programs/px-exec.yaml`  
> **Phase:** PX-EXEC-P1 — Runtime Foundation  
> **SoR revision:** 2026-07-05 (read-only)

---

## Package summary

This document completes the Wave A engineering slice for authorization. It complements:

| Artifact | Path | Status |
|----------|------|--------|
| Wave A backlog | `.asep/reports/PX-EXEC-WAVE-A-BACKLOG.md` | REGISTERED |
| EWO-001 proposal + report | `.asep/proposals/PX-EXEC-EWO-001-event-model.md` | **IMPLEMENTED** PASS |
| EWO-002 proposal | `.asep/proposals/PX-EXEC-EWO-002-rule-engine.md` | **PROPOSED** (this package) |
| EWO-003 proposal | `.asep/proposals/PX-EXEC-EWO-003-dependency-engine.md` | **PROPOSED** (this package) |
| EWO-004…006 proposals | To be drafted at dispatch gate (summaries below) | BLOCKED on deps |

**Explicit boundary:** This package does **not** claim MB2-Q1…Q6 qualification. Gate evidence
is produced in separate qualification acts after Wave A implementation PASS.

---

## 1. Proposals (deliverables 1–2)

Full proposals filed:

- **PX-EXEC-EWO-002** — Rule Engine → `.asep/proposals/PX-EXEC-EWO-002-rule-engine.md`
- **PX-EXEC-EWO-003** — Dependency Engine → `.asep/proposals/PX-EXEC-EWO-003-dependency-engine.md`

EWO-004…006 remain **design summaries** in this package until their dependency EWOs PASS.
Architect may authorize Wave A as a slice (002∥003 dispatch) or full Wave A (002→006) in
one authorization act after reviewing this package.

---

## 2. Wave A dependency analysis (deliverable 3)

### 2.1 Capability DAG

```text
px-exec-1-event-model          [DONE — EWO-001 @ 2026-07-06]
        │
        ├────────────────────────────┬────────────────────────────┐
        ▼                            ▼                            │
px-exec-3-dependency-engine    px-exec-2-rule-engine              │
[EWO-003]                      [EWO-002]                          │
        │                            │                            │
        ▼                            │                            │
px-exec-4-job-queue            │                            px-exec-6-state-projection
[EWO-004]                      │                            [EWO-006]
        │                            │                            │
        └──────────────┬─────────────┘                            │
                       ▼                                          │
              px-exec-5-scheduler                                 │
              [EWO-005]                                           │
                       │                                          │
                       └──────────────────┬───────────────────────┘
                                          ▼
                              Wave A Integration Barrier
                              (all six EWO reports PASS)
```

### 2.2 WorkOrder dependency table

| EWO | Depends on | Blocks | Parallel after | Critical path |
|-----|------------|--------|----------------|---------------|
| **001** Event Model | — | 002, 003, 006 | — | **DONE** |
| **002** Rule Engine | 001 | 005 | 001 | Track B |
| **003** Dependency Engine | 001 | 004 | 001 | Track A (critical) |
| **004** Job Queue | 003 | 005 | 003 | Track A |
| **005** Scheduler | 004, 002 | — | 004 + 002 | Convergence |
| **006** State Projection | 001 | — | 001 (partial); full integration at Wave A exit | Track C |

**Critical path:** `001 → 003 → 004 → 005` (longest chain). EWO-002 and EWO-006 are
parallel branches that must converge before Wave A exit.

### 2.3 Cross-EWO runtime dependencies (logical, not file)

| Consumer | Requires from upstream | Integration point |
|----------|------------------------|-------------------|
| EWO-002 | EWO-001 bus `subscribe()`, catalog, `program_id` | RuleEngine on publish |
| EWO-003 | EWO-001 `ExecutionGraphDerived` catalog + publish | DependencyEngine derive |
| EWO-004 | EWO-003 ready set, ExecutionNode ids | Job materialization + FSM |
| EWO-005 | EWO-004 queue, EWO-002 action descriptors | Scheduler + rule-triggered claim |
| EWO-006 | EWO-001 all Wave A event types | Projection rebuild from log |

### 2.4 External dependencies (satisfied)

| Prerequisite | Status |
|--------------|--------|
| MB2 SoR frozen @ 2026-07-05 | PASS |
| PX-3 COMPLETE + MB2-CONFORMANCE-ASSESSMENT | PASS |
| Program AUTHORIZE px-exec | PASS |
| EWO-001 IMPLEMENTED | PASS @ 2026-07-06 |

### 2.5 Era I coexistence

| Era I module | Wave A relationship |
|--------------|---------------------|
| `builder_engine/graph.py` + `compute_ready()` | Parity reference for EWO-003; not replaced in Wave A |
| `builder_engine/policy.py` | Governance — must remain separate from EWO-002 Rule Engine |
| `builder_engine/cycle.py` | Optional additive subscriber wiring; no semantic change to Era I cycle |
| `plans/builder/STATE.yaml` | Unchanged authority for Era I; Program Graph is `.asep/programs/*.yaml` |

---

## 3. Ownership matrix (deliverable 4)

Exclusive write ownership per EWO. Supervisor enforces at merge barriers.

| EWO | Exclusive write paths | Shared read-only | Must NOT touch |
|-----|----------------------|------------------|----------------|
| **001** ✅ | `events.py`, `test_events.py`, `test_mb2_event_catalog.py` | `cycle.py`, `runtime.py` (minimal program_id) | rules, dependency, queue, scheduler, projection |
| **002** | `rules.py`, `test_rules.py`, `fixtures/*rules*.yaml` | `events.py`, `yaml_loader.py` | `policy.py`, dependency, queue, scheduler |
| **003** | `dependency.py`, `program_graph.py`, `test_dependency_engine.py`, test fixtures | `events.py`, `graph.py`, `scheduler.py` (read) | `rules.py`, queue, scheduler, projection |
| **004** | `job_queue.py`, `test_job_queue.py`, FSM extensions in dedicated module | `dependency.py`, `events.py`, `state_machine.py` (coordinate) | rules, scheduler, projection |
| **005** | `scheduler.py` (MB2 extensions), `test_scheduler_mb2.py` | `job_queue.py`, `rules.py`, `events.py` | dependency, projection, merge plugins |
| **006** | `projection.py`, `test_projection.py`, projection schema fixture | `events.py` (all catalog types) | scheduler, rules evaluation, queue mutation |

### Integration-only touch (Supervisor merge)

| Path | Owner at integration | Rule |
|------|---------------------|------|
| `builder_engine/__init__.py` | Supervisor | Export new public APIs only |
| `builder_engine/cycle.py` | Supervisor + owning EWO | Additive subscriber wiring with dual sign-off |
| `builder_engine/cli.py` | EWO-006 or Supervisor | Read-only projection commands only |

### Conflict matrix (parallel tracks)

| Pair | Conflict risk | Mitigation |
|------|---------------|------------|
| 002 ∥ 003 | **None** — disjoint files | Parallel dispatch authorized |
| 006 ∥ 002–005 | **Low** — disjoint modules | 006 may start after 001; defers event types from 004/005 until integration |
| 004 ∥ 002 | **None** — sequential (004 after 003) | N/A |
| 005 | **Convergence** — reads 002 + 004 | Sync barrier before EWO-005 dispatch |

---

## 4. Parallel execution plan (deliverable 5)

### 4.1 Execution phases

```text
Phase 0 — COMPLETE
  PX-EXEC-EWO-001 → PASS @ 2026-07-06

Phase 1 — Parallel foundation (authorized after this package review)
  ├── Sub-agent / builder A → PX-EXEC-EWO-003 (Dependency Engine)   [critical path]
  └── Sub-agent / builder B → PX-EXEC-EWO-002 (Rule Engine)

Phase 1 sync barrier — Integration A
  Merge: 003 → 002 (merge_order; critical path first)
  Verify: make unit-builder-engine; no cross-import violations
  Report: .asep/reports/PX-EXEC-INTEGRATION-A.md

Phase 2 — Queue
  Sub-agent C → PX-EXEC-EWO-004 (Job Queue) — after Integration A PASS

Phase 2 parallel (optional overlap)
  Sub-agent D → PX-EXEC-EWO-006 (State Projection) — may start after 001;
  defers integration tests until 004/005 events exist

Phase 3 — Convergence
  Sub-agent E → PX-EXEC-EWO-005 (Scheduler) — after 004 PASS + 002 PASS

Phase 3 sync barrier — Wave A Integration
  Merge: 004 → 005 → 006 (if not merged earlier)
  Full MB2 Wave A test suite
  Report: .asep/reports/PX-EXEC-INTEGRATION-WAVE-A.md
```

### 4.2 Dispatch mode

| Phase | Mode | Rationale |
|-------|------|-----------|
| 1 (002 + 003) | **Parallel** | Disjoint ownership; longest pole is 003 |
| 2 (004) | Serial | Depends on 003 |
| 2 (006 partial) | Parallel with 004 | Disjoint files; integration deferred |
| 3 (005) | Serial | Depends on 004 + 002 |

### 4.3 Merge order (strict)

```text
003 → 002 → 004 → 005 → 006
```

| Order | EWO | Rationale |
|-------|-----|-----------|
| 1 | **003** | Critical path; job queue consumes its API |
| 2 | **002** | Rule engine independent; merge before queue wiring tests |
| 3 | **004** | Job FSM + queue |
| 4 | **005** | Scheduler consumes queue + rules |
| 5 | **006** | Projection consumes all event types |

### 4.4 Sub-agent assignment (recommended)

| Sub-agent | EWO | Track |
|-----------|-----|-------|
| A | PX-EXEC-EWO-003 | Critical path |
| B | PX-EXEC-EWO-002 | Parallel rules |
| C | PX-EXEC-EWO-004 | Queue |
| D | PX-EXEC-EWO-006 | Projection |
| E | PX-EXEC-EWO-005 | Scheduler |
| Supervisor | Integration A + Wave A Integration | Merge + CI |

### 4.5 Authorization commands (post-review)

```text
# Wave A slice — Phase 1 parallel dispatch
ASEP: AUTHORIZE PX-EXEC-EWO-002
ASEP: AUTHORIZE PX-EXEC-EWO-003

# Or combined Wave A engineering authorization (Architect discretion)
ASEP: AUTHORIZE px-exec wave-a
```

---

## 5. Integration plan (deliverable 6)

### 5.1 Integration A — Post EWO-002 + EWO-003

**Gate:** Both EWO reports PASS; `make unit-builder-engine` green on merged tree.

| Step | Action | Owner |
|------|--------|-------|
| 1 | Merge worktrees/branches in order 003 → 002 | Supervisor |
| 2 | Verify no duplicate Event Bus subscribers | Supervisor |
| 3 | Verify RuleEngine does not import PolicyEngine | Supervisor |
| 4 | Verify DependencyEngine publishes `ExecutionGraphDerived` only on derive | Supervisor |
| 5 | Run `make unit-builder-engine` | Supervisor |
| 6 | Write `.asep/reports/PX-EXEC-INTEGRATION-A.md` | Supervisor |

**Unblocks:** EWO-004 dispatch.

### 5.2 Integration B — Mid-wave (optional)

If EWO-006 completes before EWO-005:

| Step | Action |
|------|--------|
| 1 | Merge 006 to integration branch (no scheduler dependency for unit tests) |
| 2 | Projection unit tests use synthetic event fixtures only |
| 3 | Defer cross-module tests until EWO-005 PASS |

### 5.3 Wave A Integration — Final

**Gate:** EWO-001…006 each report PASS.

| Step | Action | Evidence |
|------|--------|----------|
| 1 | Merge remaining EWOs in order 004 → 005 → 006 | Clean working tree |
| 2 | Run full Wave A test module suite | `make unit-builder-engine` log |
| 3 | Verify INV-R-08: transitions in scope emit typed events | Trace matrix in integration report |
| 4 | Verify Era I regression | Existing cycle/MB2 integration tests |
| 5 | Verify no forbidden paths touched | Scope table |
| 6 | Write `.asep/reports/PX-EXEC-INTEGRATION-WAVE-A.md` | PASS / STOP |
| 7 | Update capability graph lifecycle nodes | `.asep/capabilities/px-exec.yaml` |

**Does not include:** MB2-Q1…Q6 qualification runs.

### 5.4 EWO-004…006 design summaries (for full Wave A scope)

| EWO | Title | Primary SoR | Key artifacts | Depends on |
|-----|-------|-------------|---------------|------------|
| **004** | Job Queue | §5 Job FSM, ADR-0025 | `job_queue.py`, FSM tests, `JobReady`/`JobClaimed` emission | 003 |
| **005** | Scheduler | §8.2 scheduler plugin | Extend `scheduler.py`, WAIT halt, manifest emission | 004, 002 |
| **006** | State Projection | §9 Projection model | `projection.py`, schema v1, `ProjectionUpdated`, rebuild tests | 001 (+ integration) |

Full proposals for 004…006 to be drafted at their dispatch gates using EWO-001/002/003
proposals as templates.

---

## 6. Qualification strategy (deliverable 7)

### 6.1 Boundary statement

```text
Wave A IMPLEMENTATION  ≠  MB2 QUALIFICATION

Wave A produces Reference Implementation artifacts that ENABLE gate evidence.
MB2-Q1…Q6 require separate Architect-authorized qualification acts per SoR §13.
```

This package and all Wave A EWO reports MUST NOT claim MB2-Q PASS.

### 6.2 Gate enablement map

| MB2 Gate | SoR | Enabled by Wave A EWO | Qualification act (separate) |
|----------|-----|----------------------|------------------------------|
| **MB2-Q1** | §4.2, §5 | EWO-003 (+ partial 004) | `.asep/reports/MB2-Q1-*.md` + MB2-Q-001…003 |
| **MB2-Q2** | §7 | EWO-001 (partial) + EWO-002 | `.asep/reports/MB2-Q2-*.md` + MB2-Q-004…006 |
| **MB2-Q3** | §5, §8.2 | EWO-004 + EWO-005 | `.asep/reports/MB2-Q3-*.md` + MB2-Q-007…009 |
| **MB2-Q4** | §8 | Phase 2 plugins — **not Wave A** | Deferred |
| **MB2-Q5** | §9 | EWO-006 (partial) | `.asep/reports/MB2-Q5-*.md` + MB2-Q-013…015 |
| **MB2-Q6** | §12 | Phase 4 recovery — **not Wave A** | Deferred |

### 6.3 Phase 1 exit gate

Program `implementation_gate: MB2-Q1-pass` requires:

1. Wave A PASS (all six EWO reports)
2. Separate MB2-Q1 qualification act with MB2-Q-001…003 evidence
3. Architect authorization for qualification (currently in `not_authorized`)

### 6.4 Test strategy (implementation phase — not qualification)

| Layer | When | Command |
|-------|------|---------|
| Per-EWO unit tests | Each EWO verify | `make unit-builder-engine` |
| Integration A | After 002+003 merge | same |
| Wave A integration | After 006 | same + new `test_mb2_wave_a.py` (TBD at EWO-006) |
| Qualification | **After Wave A PASS only** | Dedicated MB2-Q test modules + gate reports |

### 6.5 QC / Supervisor

| Role | Wave A responsibility |
|------|----------------------|
| Implementing agent | EWO-scoped tests + EWO report |
| Supervisor | Integration reports; merge order; STOP on scope violation |
| QC certificate | Optional per EWO; not MB2-Q |
| Architect | Authorize dispatch; authorize qualification separately |

---

## 7. Acceptance criteria (deliverable 8)

### 7.1 Wave A engineering package (this authorization act)

Wave A package review **PASS** when:

- [ ] EWO-002 and EWO-003 proposals complete with SoR traceability
- [ ] Dependency analysis, ownership, parallel plan, integration plan documented
- [ ] Qualification boundary explicit — no MB2-Q claims
- [ ] Rollback strategy and risk register present
- [ ] Consistent with `.asep/reports/PX-EXEC-WAVE-A-BACKLOG.md` DAG
- [ ] EWO-001 PASS confirmed as prerequisite

### 7.2 Wave A implementation PASS (future — post-dispatch)

Wave A is **PASS** only when **all** of:

1. **PX-EXEC-EWO-001…006** each have EWO completion reports with verdict PASS
2. `make unit-builder-engine` green including Wave A test modules
3. Era I event catalog retained — no breaking removals from §6.2
4. SoR §6.3 catalog events enforced; Wave A modules emit typed events per INV-R-08
5. Integration A PASS + Wave A Integration PASS reports filed
6. **No N-class SoR deviation** — clarifications via `sor-compatibility-policy` only
7. **No MB2-Q1…Q6 qualification claim** in any Wave A report
8. Capability graph updated: `px-exec-1…6` → `done` / `lifecycle: done`

### 7.3 Per-EWO acceptance (summary)

| EWO | Key acceptance |
|-----|----------------|
| 001 ✅ | Catalog + bus + program_id + subscribe (PASS) |
| 002 | Deterministic rules; INV-R-07; §7.3 fixture; no MB2-Q2 claim |
| 003 | Derived graph only; INV-R-01…03; ExecutionGraphDerived event |
| 004 | Job FSM ⊆ ADR-0025; JobReady/JobClaimed events; recoverable design hook |
| 005 | claim/release; WAIT halts claims (INV-R-16); manifest emission |
| 006 | Schema v1; rebuild from log; CLI read-only; ProjectionUpdated |

Detailed criteria in each proposal.

---

## 8. Rollback strategy (deliverable 9)

### 8.1 Principles

| Principle | Application |
|-----------|-------------|
| Additive Era I | EWO-001 pattern: extend, do not break Era I callers |
| Event log append-only | Rollback does not truncate `.builder-engine/events.jsonl` |
| Branch isolation | Each EWO on feature branch or worktree until integration PASS |
| Program graph truth | Revert capability status in `.asep/capabilities/px-exec.yaml` on STOP |

### 8.2 Per-EWO rollback

| EWO | Rollback trigger | Action |
|-----|------------------|--------|
| 002 | STOP / FAIL report | Revert `rules.py` + tests + fixtures; remove bus subscriber registration |
| 003 | STOP / FAIL report | Revert `dependency.py`, `program_graph.py`; no Program Graph file changes |
| 004 | STOP / FAIL report | Revert queue module; Era I `state_machine.py` unchanged if isolated |
| 005 | STOP / FAIL report | Revert scheduler extensions; preserve Era I `compute_ready()` behavior |
| 006 | STOP / FAIL report | Revert projection module; CLI additions removed |

### 8.3 Integration rollback

| Scenario | Action |
|----------|--------|
| Integration A FAIL | Reset to EWO-001-only baseline; re-dispatch 002/003 |
| Wave A Integration FAIL | Identify last good merge point; revert failing EWO; file STOP report |
| Partial Wave A (002+003 only) | Tag integration branch; block 004 dispatch until root cause cleared |

### 8.4 Data rollback

| Artifact | Rollback |
|----------|----------|
| `.builder-engine/events.jsonl` | **Never delete** — append correction events if needed |
| Checkpoint files (future) | EWO-004 defines; restore from prior checkpoint snapshot |
| Projection document | Rebuild from event log after fix (EWO-006) |
| `.asep/reports/*` | Retain FAIL/STOP reports for audit; do not delete |

### 8.5 Authorization rollback

If Architect revokes Wave A authorization:

1. Set `wave_a.status: stopped` in program graph
2. Mark in-progress EWOs `blocked`
3. File `.asep/reports/stop-<timestamp>-px-exec-wave-a.md` per stop template
4. Preserve EWO-001 `implemented` status (already PASS)

---

## 9. Risk register (deliverable 10)

| ID | Risk | L | I | Mitigation | Owner |
|----|------|---|---|------------|-------|
| **R-WA1** | Rule Engine scope creep into Governance (`PolicyEngine` merge) | M | H | EWO-002 INV-R-07 tests; forbidden governance keys; separate modules | EWO-002 agent |
| **R-WA2** | Dependency Engine invents edges beyond Program Graph | M | H | INV-R-03 tests; merge_order tie-break only; no graph mutation API | EWO-003 agent |
| **R-WA3** | Parallel 002∥003 merge conflicts | L | M | Disjoint ownership matrix; Integration A barrier | Supervisor |
| **R-WA4** | Premature MB2-Q qualification claim | L | H | Package + EWO report template forbids; Supervisor review | Supervisor |
| **R-WA5** | Era I `compute_ready()` diverges from Dependency Engine | M | M | Parity test in EWO-003; document mapping; no silent replacement | EWO-003 agent |
| **R-WA6** | EWO-006 starts too early — missing event types from 004/005 | M | M | Deferred integration tests; synthetic fixtures until Wave A merge | EWO-006 agent |
| **R-WA7** | Scheduler (005) blocked by incomplete rule action wiring | M | M | Phase 3 dispatch gate requires 002+004 PASS | Supervisor |
| **R-WA8** | `program_id` inconsistency across modules | L | M | EWO-001 contract; all Wave A publishers use explicit program_id | All agents |
| **R-WA9** | SoR N-class deviation discovered during implementation | L | H | STOP; file deviation; Architect decision — no silent SoR edits | Supervisor |
| **R-WA10** | Job FSM drift from ADR-0025 | M | H | EWO-004 trace to §5; illegal transition tests + RuntimeEscalated | EWO-004 agent |
| **R-WA11** | Wave A duration — sequential 004→005 delays | M | L | Accept; critical path is 003→004→005; 006 parallelized | Program mgmt |
| **R-WA12** | Integration test gap at Wave A exit | M | M | Wave A Integration report mandatory; `test_mb2_wave_a.py` at EWO-006 | Supervisor |

*L = Likelihood, I = Impact*

---

## 10. Architect authorization gate

### 10.1 Recommended decision

```text
Wave A Engineering Package: PASS (design)

EWO-002 Proposal: APPROVED FOR REGISTRATION
EWO-003 Proposal: APPROVED FOR REGISTRATION

Wave A Phase 1 Dispatch (002 ∥ 003): AUTHORIZED (on explicit operator command)
Wave A Full Dispatch (004…006): AUTHORIZED AFTER Integration A PASS (sequential gates)

MB2-Q1…Q6 Qualification: NOT AUTHORIZED
```

### 10.2 Required program graph sync (post-approval)

Update `.asep/programs/px-exec.yaml`:

```yaml
wave_a:
  engineering_package: .asep/reports/PX-EXEC-WAVE-A-ENGINEERING-PACKAGE.md
  proposals:
    - .asep/proposals/PX-EXEC-EWO-002-rule-engine.md
    - .asep/proposals/PX-EXEC-EWO-003-dependency-engine.md
  status: authorized_for_dispatch  # after Architect sign-off
```

Update EWO-002/003 entries with `proposal:` paths and `status: ready`.

### 10.3 Next operator commands

```text
# After Architect approves this package:
ASEP: AUTHORIZE PX-EXEC-EWO-002
ASEP: AUTHORIZE PX-EXEC-EWO-003

# Or parallel dispatch via orchestrate-builders after authorization receipts filed
```

---

## WO-TRACE

```text
PX-EXEC-EWO-001 PASS (2026-07-06)
  → PX-EXEC-WAVE-A-ENGINEERING-PACKAGE (this document)
  → EWO-002 + EWO-003 proposals
  → Architect review → Wave A dispatch authorization
  → Phase 1 parallel (002 ∥ 003) → Integration A
  → Phase 2 (004, 006 partial) → Phase 3 (005) → Wave A Integration
  → Wave A implementation PASS
  → MB2-Q gates (separate qualification acts — NOT part of this package)
```

---

## Milestone Status (design act)

```text
Milestone Status: PASS (engineering package complete — pending Architect review)
Repository Status: main @ EWO-001 implemented; proposals untracked until commit
Remaining Scope: Architect review → dispatch authorization → EWO-002…006 implementation
Known Risks: R-WA1…R-WA12 (see §9)
Recommended Next Action: Architect review this package + proposals; authorize Phase 1 dispatch
Qualification: NOT CLAIMED — MB2-Q1…Q6 remain separate acts
```
