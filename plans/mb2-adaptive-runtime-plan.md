# MB2 Adaptive Runtime — Implementation Plan

> **Status:** Rebased on constitution (2026-06-25). Implements MB2 spec §3 deliverables D1–D11.
> **Prerequisite:** `plans/l2-global-state-machine-plan.md` **Phases 1–2** (GSM + invariant pass) MUST complete before Phase 5.
> **Constitutional rules:** Completeness · Minimality · Behavioral Purity · Traceability Closure (spec §2).
> **No constitution changes** during implementation — gaps → MB2 spec §11 → DR/ADR.

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Each phase must cite **MB2 spec §3 row** (D#) and **ETM** columns in PR description.

**Goal:** L4 implementation of rebased MB2 spec — concretize L3 phases Observe, Evaluate Policies, Plan extend, Publish, Replan; wire events into existing Schedule/Validate/Update.

**Architecture:** Sidecar `builder_engine/`; `EngineeringRuntimeCycle` orchestrates C-01–C-15 preflight/postflight; `EngineeringRuntime` (renamed) preserves packet FSM; build bus at `.builder-engine/events.jsonl`.

**Spec:** `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` (rebased — pending Architect sign-off)  
**Prerequisite plan:** `plans/l2-global-state-machine-plan.md` Ph 1–2  
**ADRs:** 0029, 0028, 0026, 0025, 0023

**Branch:** `mb2-adaptive-runtime` (from `main` after spec sign-off).

**Traceability per phase:** V → ADR → L0 → L1 → BS → T → L3 → E → Mod → O → Test → Evidence (see spec §3).

---

## Phase 0 — Prerequisite: L2 GSM + invariants (NOT MB2 D#)

Execute `plans/l2-global-state-machine-plan.md` Phases 1–2 before Phase 5.

| Deliverable | BS | T | Mod | Evidence |
|-------------|----|---|-----|----------|
| Executable Task FSM | Validating, Claiming | T-01–T-12 | `gsm_task.py` | `test_gsm_task.py` |
| Class B invariant pass | all commits | INV-B* | `invariants.py` | `test_invariants.py` |

**Gate:** Phase 0 complete when prerequisite promotion criteria green.

---

## Phase 1 — Observe State (MB2 **D1**)

**Traceability:** BS Observing · T S-01,S-02,C-01,C-02 · L3 Observe · E `StateObserved` · Evidence: immutable snapshot, no STATE write

### Files affected
| Action | Path |
|--------|------|
| Create | `builder_engine/observe.py` — `StateObserver`, `ObservedSnapshot` |
| Modify | `builder_engine/cli.py` — add `observe` command |
| Create | `builder_engine/tests/test_observe.py` |
| Create | `builder_engine/tests/fixtures/state_minimal.yaml` (if needed) |

### Public API
| Symbol | Notes |
|--------|-------|
| `StateObserver(repo_root, state_path)` | Constructor |
| `observe() -> ObservedSnapshot` | Immutable snapshot; abort reasons in `staleness_reasons` |
| `snapshot.is_complete -> bool` | False when stale |

### Tests
- Snapshot includes all packets, locks, blockers from fixture STATE
- Git fields populated (or `None`/`False` when not a git repo — test with mock)
- `ready_count` / `in_flight_count` match graph statuses
- Unreadable STATE → raises / `staleness_reasons` contains error
- CLI `observe` prints table/JSON without mutating STATE

### Critic checklist (Phase 1)
- [ ] No `backend.app` imports
- [ ] Observe is read-only (no STATE writes)
- [ ] Snapshot is frozen/immutable dataclass

### Promotion criteria
```yaml
observe_unit: green
observe_cli: green
m0_m1_m2_m3_m4_tests: green
unit_builder_engine: green
isolation: green
```

---

## Phase 2 — Evaluate Policies (MB2 **D2**)

**Traceability:** BS Escalation · T C-03,C-04 · L3 Evaluate Policies · E `PolicyAllowed`/`PolicyBlocked` · Evidence: block without checks

### Objective
`PolicyEngine` returns `PolicyDecision` after Observe; evaluates **warnings** + `plans/builder/policies.yaml`. Structural **errors** from `validate_graph` are L1 invariants (via Phase 0 `invariants.py`), not policy.

### Files affected
| Action | Path |
|--------|------|
| Create | `builder_engine/policy.py` — `PolicyEngine`, `PolicyDecision` |
| Create | `plans/builder/policies.yaml` — sample declarative rules (documented defaults) |
| Create | `builder_engine/tests/test_policy.py` |

### Public API
| Symbol | Notes |
|--------|-------|
| `PolicyEngine(repo_root, policies_path?)` | Loads YAML if present |
| `evaluate(snapshot) -> PolicyDecision` | `allow` \| `block` \| `escalate` |

### Tests
- Invalid graph → `block` with violations
- Implementer packet `ready` without `checks` → `block` (§8.8)
- Warnings-only graph → `allow`
- YAML rule: missing gate doc → `block` (use test fixture path)
- `escalate` emits violation list but allows continue (test hook)

### Critic checklist (Phase 2)
- [ ] Invariants enforced by Phase 0 pass — policy does not override INV-*
- [ ] Policies are declarative file — no hard-coded M5+ product logic

### Promotion criteria
```yaml
policy_unit: green
policies_yaml_loads: green
unit_builder_engine: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 3 — Extend Plan (MB2 **D3**)

**Traceability:** BS Scheduling · T T-01,C-05 · L3 Plan · E `PlanGenerated` · Evidence: ready set parity

### Files affected
| Action | Path |
|--------|------|
| Modify | `builder_engine/planner.py` — `Plan`, `build_plan()`, `critical_path()` |
| Modify | `builder_engine/cli.py` — add `plan` command (keep `ready` as thin alias) |
| Create | `builder_engine/tests/test_plan_extended.py` |

### Public API
| Symbol | Notes |
|--------|-------|
| `build_plan(snapshot, policy) -> Plan` | Requires `policy.outcome != block` |
| `critical_path(graph) -> tuple[str, ...]` | Longest dependency chain heuristic |

### Tests
- Ready set matches `compute_ready()` for fixture graphs
- Dependency chain `a→b→c` yields critical path containing `c`
- Blockers copied from snapshot/graph
- Empty ready + incomplete wave → `Plan.empty is True`
- `plan` CLI renders Plan table

### Critic checklist (Phase 3)
- [ ] No replan logic in planner (stays in Phase 6)
- [ ] `plan_ready()` preserved for backward compatibility

### Promotion criteria
```yaml
plan_extended_unit: green
ready_parity: green
plan_cli: green
unit_builder_engine: green
```

---

## Phase 4 — Build event bus (MB2 **D4**)

**Traceability:** L3 Publish · T C-12 · E `EventsPublished` + catalog · Evidence: append-only jsonl

### Files affected
| Action | Path |
|--------|------|
| Create | `builder_engine/events.py` — `EventType`, `BuildEvent`, `BuildEventBus` |
| Modify | `builder_engine/cli.py` — add `events --tail N` |
| Create | `builder_engine/tests/test_events.py` |

### Storage
- Path: `.builder-engine/events.jsonl`
- Format: one JSON object per line (`type`, `timestamp`, `payload`, `cycle_id`)

### Tests
- Publish appends line; tail returns last N in order
- Corrupt line skipped with warning
- Event types must match L2 §7 / spec §3 D4 catalog — no new event names
- Concurrent publish from single process serialized (file lock or append atomicity)
- CLI `events --tail` read-only

### Critic checklist (Phase 4)
- [ ] Append-only — no rewrite/truncate in normal operation
- [ ] Bus is sidecar-local — no product DB

### Promotion criteria
```yaml
event_bus_unit: green
event_replay: green
events_cli: green
unit_builder_engine: green
```

---

## Phase 5 — Wire runtime + cycle (MB2 **D6**, **D8**, **D9**)

**Traceability:** BS Scheduling, Validating, Merging · T T-02–T-07,C-01–C-13 · Evidence: MB1 parity + events

**Requires Phase 0 complete.**

### Objective
`EngineeringRuntimeCycle` preflight; `EngineeringRuntime.schedule()`/`sync()` publish events; merge eligibility stub.

### Files affected
| Action | Path |
|--------|------|
| Create | `builder_engine/cycle.py` — `EngineeringRuntimeCycle` |
| Modify | `builder_engine/runtime.py` — rename class to `EngineeringRuntime`; optional `bus`, emit on schedule/sync |
| Modify | `builder_engine/cli.py` — add `cycle --dry-run`, wire bus into schedule/sync |
| Create | `builder_engine/tests/test_cycle.py` |
| Modify | `builder_engine/tests/test_runtime.py` — assert events on schedule/sync |

### Public API
| Symbol | Notes |
|--------|-------|
| `EngineeringRuntimeCycle.run_preflight()` | Observe → Policies → Plan |
| `EngineeringRuntimeCycle.run_postflight(sync_result)` | Publish tail + optional replan hook (Phase 6) |

### Tests
- Preflight `block` prevents schedule (integration with mocked runtime)
- Successful schedule emits `TaskScheduled`, `LockAcquired`
- Sync pass/fail emits `ValidationPassed` / `ValidationFailed`
- Wave advance emits `WaveAdvanced`
- MB1 schedule/sync behavior unchanged (existing tests green)
- `cycle --dry-run` runs preflight without STATE mutation

### Critic checklist (Phase 5)
- [ ] Packet FSM transitions unchanged in `state_machine.py`
- [ ] Event publish after successful `save_raw_state`

### Promotion criteria
```yaml
cycle_preflight: green
runtime_events: green
schedule_sync_parity: green
unit_builder_engine: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 6 — Replan minimal (MB2 **D5**)

**Traceability:** BS Replanning, Recovery · T C-14,T-09 · E `Replanned` · Evidence: proposal without STATE write

### Files affected
| Action | Path |
|--------|------|
| Create | `builder_engine/replan.py` — `ReplanProposal`, `minimal_replan()` |
| Create | `builder_engine/merge.py` — `merge_eligibility()` stub |
| Modify | `builder_engine/cycle.py` — `run_postflight` calls replan |
| Modify | `builder_engine/cli.py` — add `merge-check` |
| Create | `builder_engine/tests/test_replan.py` |
| Create | `builder_engine/tests/test_merge_stub.py` |
| Create | `builder_engine/tests/test_mb2_integration.py` — full dry cycle fixture |

### Tests
- `ValidationFailed` event → proposal with fix packet YAML snippet
- Proposal does **not** write STATE (assert file unchanged)
- Dependents listed in `suggested_actions`
- `Replanned` / `RecoveryTaskCreated` events published
- `merge-check` always `deferred` with external integrator reason
- Integration: observe → plan → schedule (fixture) → sync dry-run → replan proposal

### Critic checklist (Phase 6)
- [ ] No auto packet creation in STATE
- [ ] Replan is advisory only

### Promotion criteria
```yaml
replan_unit: green
merge_stub: green
mb2_integration: green
unit_builder_engine: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 7 — Promotion + CLI completion (MB2 **D7**, **D10**, **D11**)

**Traceability:** BS Promotion · Evidence: `docs/mb2-phase-gate.md` all green; zero `WorkflowRuntime` in tree

### Objective
Complete CLI projections; `EngineeringRuntime` rename audit; `docs/mb2-phase-gate.md`; knowledge mirror.

### Files affected
| Action | Path |
|--------|------|
| Create | `docs/mb2-phase-gate.md` |
| Modify | `knowledge/context/current-state.md` — Era II MB2 complete |
| Modify | `knowledge/context/next-actions.md` |
| Optional | `plans/builder/STATE.yaml` — MB2 epic packets mirroring phases |

### Promotion criteria
```yaml
observed_snapshot: green
policy_stub: green
extended_plan: green
build_event_bus: green
cycle_preflight: green
cycle_postflight: green
schedule_sync_parity: green
event_emission: green
engineering_runtime_rename: green
constitutional_traceability: green
etm_rows_complete: green
m0_m1_m2_m3_m4_tests: green
builder_engine_tests: green
documentation: complete
knowledge_updated: true
mb2_gate: docs/mb2-phase-gate.md
```

---

## Wave / operator integration

Operators use existing orchestrate-builders skill with additive commands:

```bash
builder-engine observe --repo-root .
builder-engine plan --repo-root .
builder-engine cycle --dry-run --repo-root .
builder-engine schedule --repo-root .
# ... workers ...
builder-engine sync --repo-root .
builder-engine events --tail 20 --repo-root .
```

Packet `checks` should include `unit-builder-engine` and `isolation` after Phase 5.

---

## References

- MB2 spec (rebased): `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md`
- Constitution: L0, L1, `behavioral-semantics.md`, L2, L3
- `engineering-traceability-matrix.md` · DR-001 · ADR-0029
- Prerequisite: `plans/l2-global-state-machine-plan.md`
- `docs/mb1-phase2-gate.md`
