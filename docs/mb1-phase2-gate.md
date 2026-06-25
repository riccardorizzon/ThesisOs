# MB1 Phase 2 Gate — Status

_As of 2026-06-25. Branch `main`._

```yaml
phase2_runtime:          green    # WorkflowRuntime loop (ADR-0025)
execution_state_machine:   green    # formal transitions + unit tests
cli_projections:         green    # schedule, sync, check as runtime views
check_runner:              green    # named stages + packet checks
dispatch_manifest:         green    # .builder-engine/last-dispatch-manifest.json
graph_invariants:          green    # schedule/sync refuse invalid graph
m0_m1_m2_m3_tests:         green    # make ci
m4_implementation:         blocked  # requires plans/m4-retrieval-system-plan.md
```

## Delivered

| Component | Path |
|-----------|------|
| Execution state machine | `builder_engine/state_machine.py` |
| State I/O (atomic) | `builder_engine/state_io.py` |
| Planner stub | `builder_engine/planner.py` |
| Scheduler (+ locks) | `builder_engine/scheduler.py` |
| Executor (manifest) | `builder_engine/executor.py` |
| Validator | `builder_engine/checks.py` |
| Workflow runtime | `builder_engine/runtime.py` |
| CLI views | `builder_engine/cli.py` — `schedule`, `sync`, `check` |
| Tests | `test_state_machine.py`, `test_runtime.py`, `test_graph_engine.py` |

## Runtime loop

```text
State → Planner → Scheduler → Executor → Validator → StateUpdate
```

CLI commands invoke `WorkflowRuntime` methods; they do not encode transitions directly.

## Evidence

```bash
make unit-builder-engine
builder_engine/.venv/bin/builder-engine schedule --repo-root . --state plans/builder/STATE.yaml
builder_engine/.venv/bin/builder-engine sync --repo-root .
make ci
```

## Next

- **M4 implementation** — Planner packet `plans/m4-retrieval-system-plan.md` + Critic sign-off
- **MB1 Phase 3** — unified `builder state` + knowledge drift
- **MB1 Phase 4** — replanning / critical path

## Product track

- M3 tagged `m3-complete`
- M4 spec frozen (`ADR-0024`, design spec 2026-06-25)
