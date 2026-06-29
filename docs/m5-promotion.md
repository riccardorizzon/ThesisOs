# M5 — Tool Router / Orchestration — Promotion

**Branch:** `m5-tool-router` · **Promotion baseline:** `e934c47` (M5.5) →
this doc is M5.6. **Spec:** `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`
(frozen). **ADRs:** 0027 (topology), 0030 (runtime layers + Event Bus), 0014 (RunContext).

## Summary

M5 turned the linear M4 RAG pipeline into an orchestrated **Agent Runtime Platform**:
supervisor → planner → router decide and route every `/chat` turn; conditional dispatch
runs the conversation or grounded path; planner output persists to `tasks`; and the
runtime is observable through a canonical Event Bus with pluggable subscribers — all
without changing `GraphState` (ADR-0007) or the M1 `/chat` seam.

## Capability map (frozen baselines)

| Capability | Milestone | Commit |
|------------|-----------|--------|
| Orchestration nodes (supervisor/planner/router) | M5.1 | `9e2aa9b` |
| Routing infrastructure (`route_after_router`) | M5.2A | `c3097ea` |
| Graph wiring + conditional routing | M5.2B | `c1075d1` |
| TaskService + planner persist hook | M5.3 | `c4d5e68` |
| Governance (Runtime Constitution, ADR-0030, contract) | — | `05a1249` |
| Runtime Event Contract | M5.4A | `0339643` |
| Runtime Event Bus | M5.4B | `520d3bb` |
| Observability subscribers + lifecycle emission | M5.4C | `630d647` |
| Runtime Qualification | M5.5 | `82c3dd3` |

## Promotion gates

Deterministic gates (run in this environment):

```yaml
supervisor_node: green          # test_supervisor_node.py
planner_node: green             # test_planner_node.py
router_node: green              # test_router_node.py
graph_topology: green           # test_m5_graph_topology.py
routing_state_machine: green    # test_routing.py + test_m5_routing_eval.py (accuracy 1.0)
error_contracts: green          # test_m5_chat_integration.py (no_objective/unplannable/no_route reply)
tasks_table: green              # test_task_service.py + test_conversation_task_lifecycle.py
runtime_event_bus: green        # test_runtime_event_bus.py + test_runtime_event_contract.py
runtime_observability: green    # test_runtime_subscribers.py + test_runtime_observability.py
runtime_contract: frozen        # docs/runtime-contract.md (this milestone)
graphstate: unchanged           # asserted: run_context not in GraphState.model_fields
retriever_unchanged: green      # make unit-m4-recovery (43)
conversation_seam: green        # test_chat_endpoint.py (SSE/409/503/422)
scope_creep: false              # make scope (only intentional milestone stubs)
m0_m1_m2_m3_m4_tests: green     # make ci
knowledge_updated: true         # roadmap, agents/README, graphstate, graph.md
documentation: complete         # this doc + runtime-contract frozen
```

Manual gates (require a live stack — `make up` + Vertex ADC; **not** run here):

```yaml
dogfood_conversation: pending   # bin/dogfood-m5-conversation-run.sh
dogfood_grounded: pending       # bin/dogfood-m5-conversation-run.sh
benchmarks_recorded: pending    # B_lat / B_ground from make dogfood-m5
m5_tag: pending                 # tag `m5-complete` — create after live dogfood + explicit approval
```

## Tag procedure (final step)

`m5-complete` is **withheld** until the manual gates are satisfied honestly:

```bash
make up                      # start stack (db, backend, frontend)
make dogfood-m5              # records B_lat / B_ground; must print "DOGFOOD M5 PASS"
# then, on explicit go-ahead:
git tag -a m5-complete -m "M5 Tool Router / Orchestration — promoted" <sha>
```

Do not tag while `benchmarks_recorded` is `pending` — the tag asserts a fully
qualified runtime (verification-before-completion).

## What M5 explicitly did NOT do

Writer/critic/citation nodes (M6/M7/M9), the M12 multi-agent re-entry loop, new
REST endpoints, GraphState schema changes, and OpenTelemetry export (a future Event
Bus subscriber). Routing accuracy is qualified deterministically (routing logic), not
against a live LLM — live behavior is a dogfood/benchmark concern.
