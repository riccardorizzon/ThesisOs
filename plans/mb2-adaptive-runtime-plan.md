# MB2 Adaptive Runtime — Implementation Plan

> **⚠️ ON HOLD — rebase required (ADR-0028, 2026-06-25).** A platform constitution
> (L0 `engineering-meta-model.md`, L1 `invariant-model.md`) was frozen above the
> runtime model. Before executing this plan, rebase it so each phase concretizes
> an L0 object and wires the relevant L1 invariants, and rename
> `WorkflowRuntime` → `EngineeringRuntime`. The next authorized platform work is
> **L2 (Global State Machine)**, not this plan.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Each phase has explicit promotion criteria — do not start the next phase until the current phase gate passes. **Architect + Critic mandatory every phase.**

**Goal:** Translate frozen `docs/platform/runtime-model.md` into Engineering Runtime modules — Observe, Policy stub, extended Plan, build event bus, minimal Replan — **without** a global project FSM, Product LangGraph changes, or `backend.app` imports.

**Architecture:** Sidecar modules in `builder_engine/`; `EngineeringRuntimeCycle` orchestrates preflight/postflight around existing `WorkflowRuntime.schedule()` / `sync()`; append-only build bus at `.builder-engine/events.jsonl`; packet FSM (ADR-0025) unchanged.

**Tech Stack:** Python 3.11+, dataclasses, Typer CLI, pytest, subprocess git, existing CheckRunner stages.

**Spec:** `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` (Frozen 2026-06-25)  
**ADRs:** 0026 (terminology), 0025 (packet FSM), 0023 (sidecar isolation)

**Branch:** `mb2-adaptive-runtime` (from `main` @ Era I closure / `m4-complete`).  
**Conventions:** TDD where practical, additive CLI only, M0–M4 + `builder_engine` tests green after every phase.

**Forbidden in all phases:** `import backend.app`, Product LangGraph edits, auto-mutating `STATE.yaml` from replan, global project FSM, observability web UI.

---

## Phase 1 — Observe State: `ObservedSnapshot`

### Objective
Implement unified read model aggregating `BuilderGraph`, git status, CI stub, and queue depth.

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

## Phase 2 — Evaluate Policies: stub engine

### Objective
`PolicyEngine` returns `PolicyDecision` after Observe; wraps `validate_graph` + optional `plans/builder/policies.yaml`.

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
- [ ] Policies are declarative file — no hard-coded M5+ product logic
- [ ] `validate_graph` remains source of structural invariants

### Promotion criteria
```yaml
policy_unit: green
policies_yaml_loads: green
unit_builder_engine: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 3 — Extend Plan: critical path + blockers

### Objective
`build_plan()` produces `Plan` with wave intent, critical-path heuristic, and blocker surfacing; parity with `compute_ready()`.

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

## Phase 4 — Build event bus

### Objective
Typed append-only event log; publish/replay API; no cross-phase callbacks.

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
- Event types cover catalog from spec §4.8
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

## Phase 5 — Wire runtime: cycle + event emission

### Objective
`EngineeringRuntimeCycle` preflight; `schedule`/`sync` publish events; `StateUpdated` / `WaveAdvanced` after saves.

### Files affected
| Action | Path |
|--------|------|
| Create | `builder_engine/cycle.py` — `EngineeringRuntimeCycle` |
| Modify | `builder_engine/runtime.py` — optional `bus: BuildEventBus`, emit on schedule/sync |
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

## Phase 6 — Replan minimal + merge eligibility stub

### Objective
`minimal_replan()` produces `ReplanProposal` on validation failure; merge eligibility CLI stub; postflight integration.

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

## Phase 7 — Promotion gate + knowledge

### Objective
`docs/mb2-phase-gate.md`, knowledge mirror, optional `plans/builder/STATE.yaml` epic `mb2-adaptive-runtime`.

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
merge_eligibility_stub: green
no_backend_imports: green
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

- `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md`
- `docs/platform/runtime-model.md`
- `docs/platform/era-model.md`
- `decisions/ADR-0026-platform-model-terminology.md`
- `docs/mb1-phase2-gate.md`
- Tag `m4-complete`
