# M5 Tool Router / Orchestration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Each phase has explicit promotion criteria — do not start the next phase until the current phase gate passes. **Critic + QA mandatory every phase.**

**Goal:** Wire Product Plane orchestration and **deliver a qualified Agent Runtime** — graph topology, task persistence, Runtime Event Bus, subscribers, and runtime contract — **without** writer/critic agents, M12 multi-agent loop, GraphState schema changes, or new REST endpoints.

**Architecture:** Business agents (supervisor → planner → router) + conditional execution subgraph; TaskService via composition-root hook; **Runtime Event Bus** with subscriber pattern for observability (ADR-0027, ADR-0030). Telemetry is a subscriber, not the core abstraction.

**Tech Stack:** FastAPI, LangGraph, SQLAlchemy 2 async, pytest/httpx, fake LLMClient.

**Spec:** `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md` (Frozen 2026-06-25)  
**ADRs:** 0027 (graph topology), 0030 (runtime layer boundaries + Event Bus), 0007 (GraphState frozen), 0014 (RunContext)  
**Runtime contract (onboarding):** `docs/runtime-contract.md` (draft → frozen at M5.6)

**Branch:** `m5-tool-router` (from `main` @ `143f429`).  
**Conventions:** TDD where practical, additive changes only, M0–M4 + builder_engine tests green after every phase.

**Implementation discipline (mandatory):** See `docs/m5-phase1-investigation-report.md` § Implementation discipline.
1. **Shippable phases** — after each step: `make ci` green, M4 regression green, branch merge-ready (no half-wired graph).
2. **No dead code** — every module shipped in a step is fully tested and contract-complete even if not yet wired to `build_graph()`.

**Phase order:** supervisor → planner → router → **M5.2A routing** → **M5.2B graph wiring** → **M5.3 TaskService** → **ADR-0030** → **M5.4 Runtime Event Bus** → **M5.5 Runtime Qualification** → **M5.6 Promotion**.

> **Gate before M5.4:** ADR-0030 accepted. M5.4 delivers the **Event Bus**, not telemetry-first wiring.

**PR discipline (ADR-0030 §4):** Every PR touching `backend/app/` declares **Layer: Business | Runtime | Infrastructure**. Review order: (1) layer placement, (2) contracts, (3) event model, (4) feature.

**Milestone cadence (every sub-milestone):**

1. Implementazione  
2. Test unitari  
3. Integrazione (when applicable)  
4. Regression (`make ci` + `make unit-m4-recovery`)  
5. Commit  
6. Review  

**Frozen milestones:**

| Tag | Commit | Scope |
|-----|--------|-------|
| M5.1 | `9e2aa9b` | supervisor, planner, router, orchestration helpers |
| M5.2A | `c3097ea` | `routing.py`, `route_after_router()` |
| M5.2B | `c1075d1` | `build_graph()` orchestration + conditional routing |
| M5.3 | `c4d5e68` | TaskService, planner hook, lifecycle behavior tests |
| Governance baseline | `05a1249` | Runtime Constitution v1, ADR-0030, runtime contract, ADC checklist |
| M5.4A | `0339643` | Runtime Event Contract (RuntimeEvent, EventType, Protocols) |
| M5.4B | `520d3bb` | Runtime Event Bus (fan-out, non-blocking, zero-subscriber valid) |

Frozen scopes **do not reopen** except demonstrable bugs.

**Logical baseline before M5.4:** `05a1249` (clean tree, `make ci` green). M5.4 splits into A (contract), B (bus), C (subscribers + lifecycle); each ships on the prior, isolated to the runtime.

**M5.2 baseline:** branch `m5-tool-router` @ `9e2aa9b`. M5.2A and M5.2B are separate ASEP cycles with separate commits.

**Prompt discipline (from M5.2 onward):** ASEP is the project's implicit way of working — Observe → Analyze → Strategy → Execute → Verify → Report runs on every milestone without restating it in prompts. Milestone prompts define **scope only** (baseline, in/out, constraints, gates, commit). Cadence remains: implement → unit test → integrate (if applicable) → regression → commit → review.

**Forbidden in all phases:** GraphState new fields, writer/critic/citation nodes, M12 re-entry loop, new REST endpoints, Engineering Runtime imports of `backend.app`.

---

## Phase 1 — Supervisor node + unit tests

### Objective
Implement `make_supervisor_node` only — fake LLM structured JSON; contract-compliant `GraphState` mutations and error handling. **Not wired to graph.**

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/graph/supervisor.py` |
| Create | `backend/tests/test_supervisor_node.py` |

### Node behavior (minimum)
| Node | Happy path | Error path |
|------|------------|------------|
| supervisor | `plan.steps` non-empty, `route` hint set | `no_objective` → empty plan, `route=conversation` |

### Tests
- Fake LLM JSON parsing → correct state writes
- Invalid LLM JSON → safe defaults + no crash
- Only declared `reads_state` / `writes_state` fields touched

### Critic checklist (Phase 1)
- [ ] No graph wiring
- [ ] No GraphState schema changes
- [ ] Contract matches `contracts/agents/supervisor.json`
- [ ] No structural TODOs or unused placeholders

### Promotion criteria
```yaml
supervisor_unit: green
make_ci: green
unit_m4_recovery: green
```

---

## Phase 2 — Planner node + unit tests

### Objective
Implement `make_planner_node` only — **not wired to graph or TaskService yet.**

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/graph/planner.py` |
| Create | `backend/tests/test_planner_node.py` |

### Node behavior (minimum)
| Node | Happy path | Error path |
|------|------------|------------|
| planner | refined `plan`, `TaskRef` set | `unplannable` → `task=None`, error appended |

### Promotion criteria
```yaml
planner_unit: green
make_ci: green
unit_m4_recovery: green
```

---

## Phase 3 — Router node + unit tests

### Objective
Implement `make_router_node` only — final route in M5 vocabulary. **Does not include `routing.py` infrastructure yet** (normalizer tested in Phase 4).

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/graph/router.py` |
| Create | `backend/tests/test_router_node.py` |

### Node behavior (minimum)
| Node | Happy path | Error path |
|------|------------|------------|
| router | final `route ∈ {conversation, grounded_chat}` | `no_route` → `route=conversation`, error appended |

### Promotion criteria
```yaml
router_unit: green
make_ci: green
unit_m4_recovery: green
```

---

## Phase 4 — M5.2A: Routing infrastructure (`routing.py`)

> **Baseline:** `9e2aa9b` (M5.1 frozen). **No `build_graph()` changes in this phase.**

### Objective
LangGraph dispatch helpers — testable in isolation. Reuses M5.1 route vocabulary (`orchestration/constants.py`, silent normalization already in router node).

### ASEP cycle
1. Implement `routing.py`  
2. Unit tests (`test_routing.py`)  
3. *(no graph integration yet)*  
4. `make ci` + `make unit-m4-recovery`  
5. Commit (M5.2A)  
6. Review  

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/graph/routing.py` — `M5_WIRED_ROUTES`, edge key map, `route_after_router(state)` |
| Create | `backend/tests/test_routing.py` |

### `route_after_router` contract
- Input: `GraphState` with `route` set by router node (already wired vocabulary)
- Output: LangGraph conditional edge key (`"conversation"` \| `"grounded_chat"`)
- Unknown/null `route` → `"conversation"` (safe default for graph dispatch only; router node owns `no_route` errors)

### Tests
- `route=conversation` → edge key `conversation`
- `route=grounded_chat` → edge key `grounded_chat`
- `route=None` / unknown → defaults to `conversation` edge
- `build_graph` topology unchanged (grep/assert no new edges in conversation.py)

### Promotion criteria
```yaml
routing_unit: green
make_ci: green
unit_m4_recovery: green
build_graph_unchanged: true
m5_1_unmodified: true   # except bugfixes with evidence
```

---

## Phase 5 — M5.2B: Graph integration (conditional edges)

> **Prerequisite:** M5.2A commit green. **Only phase that modifies `build_graph()`.**

### Objective
Wire ADR-0027 topology in `build_graph`; conditional edges via M5.2A `route_after_router`; preserve M4 execution node bodies.

### ASEP cycle
1. Modify `build_graph()` only  
2. Graph topology unit tests  
3. Integration tests (InMemorySaver E2E both routes)  
4. `make ci` + `make unit-m4-recovery` + graph integration suite  
5. Commit (M5.2B)  
6. Review  

### Files affected
| Action | Path |
|--------|------|
| Modify | `backend/app/graph/conversation.py` — `build_graph` topology only |
| Create | `backend/tests/test_m5_graph_topology.py` |
| Modify | `backend/tests/test_conversation_graph.py` |
| Modify | `backend/tests/test_grounding.py` if needed — explicit grounded path |

### Target topology
```text
START → supervisor → planner → router → conditional
  conversation:    memory_context → conversation → END
  grounded_chat:   memory_context → retriever → conversation → END
```

### Tests
- `route=conversation` → retriever NOT invoked (mock/assert)
- `route=grounded_chat` → retriever invoked, `retrieved_context` populated
- Full graph E2E with InMemorySaver + fake LLM (all orchestration + execution nodes)
- GraphState field list unchanged

### Critic checklist (Phase 5 / M5.2B)
- [ ] M4 retriever behavior unchanged on grounded path
- [ ] No writer/critic nodes added
- [ ] `/chat` still compiles graph successfully

### Promotion criteria
```yaml
graph_topology: green
conditional_routing: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 6 — M5.3: TaskService + tasks table wiring

### Objective
Persist planner output to `tasks` table; mark done on successful turn finalize. Planner uses `PlannerTaskPersistHook` only — **no** concrete `TaskService` import in `planner.py` (ADR-0030).

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/services/task/__init__.py` |
| Create | `backend/app/services/task/service.py` |
| Create | `backend/app/graph/orchestration/task_persistence.py` — `PlannerTaskPersistHook` |
| Modify | `backend/app/graph/planner.py` — optional `on_task_ref` hook |
| Modify | `backend/app/graph/conversation.py` — wire hook → `TaskService` in `build_graph` |
| Modify | `backend/app/services/conversation/service.py` — `mark_done` on finalize; injectable `task_service` |
| Create | `backend/tests/test_task_service.py` |
| Create | `backend/tests/test_conversation_task_lifecycle.py` — stream behavior gate |

### Public API (service)
| Method | Notes |
|--------|-------|
| `upsert_from_task_ref(task_ref, *, owner_agent, plan_steps)` | INSERT ON CONFLICT UPDATE by id |
| `mark_done(task_id)` | status → `done` |

### Behavior tests (freeze gate)
| Scenario | Expected |
|----------|----------|
| Turn completes | task `done`, run `done` |
| Mid-stream exception | task `in_progress`, run `error`, no `mark_done` |
| Client disconnect | task not `done`, run `cancelled` |
| `mark_done` failure | turn still completes, task `in_progress` |

### Critic checklist (Phase 6 / M5.3)
- [ ] No new tables/migrations
- [ ] TaskService is sole writer for `tasks` in M5 scope
- [ ] Planner does not import `TaskService` or `app.db`

### Promotion criteria
```yaml
task_service_unit: green
planner_task_upsert: green
task_lifecycle_behavior: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 6b — ADR-0030: Agent Runtime Layer Boundaries

### Objective
Formalize Business / Runtime / Infrastructure layers, dependency rules, and canonical event model **before** M5.4. No product code changes required unless a violation is found during review.

### Deliverable
| Action | Path |
|--------|------|
| Create | `decisions/ADR-0030-agent-runtime-layer-boundaries.md` |
| Modify | `plans/m5-tool-router-plan.md` — M5.4–M5.6 roadmap |
| Modify | `decisions/ADR-0027-multi-agent-graph-topology.md` — §4.1 hook wording |

### Promotion criteria
```yaml
adr_0030: accepted
layer_violations_in_m5_scope: none_or_documented
m5_4_blocked_until: adr_0030_accepted
```

---

## Phase 7 — M5.4 Runtime Observability (split A/B/C)

> **Prerequisite:** M5.3 committed + ADR-0030 accepted. Split into shippable sub-milestones:
> **M5.4A** Event Contract (`0339643`, done) · **M5.4B** Event Bus (`520d3bb`, done) ·
> **M5.4C** Observability subscribers + lifecycle emission (next).

### M5.4A — Runtime Event Contract — DONE (`0339643`)
`app/runtime/events.py` (RuntimeEvent + EventType vocabulary) and `app/runtime/contracts.py`
(RuntimeSubscriber, RuntimeEventEmitter Protocols). Contract only — no bus, no wiring.

### M5.4B — Runtime Event Bus — DONE (`520d3bb`)
`app/runtime/event_bus.py` — `RuntimeEventBus` fans out to subscribers, implements
`RuntimeEventEmitter`, depends only on the contracts (no concrete subscriber), zero-subscriber
runtime stays valid/silent, subscriber failure non-blocking (R6). Bus only — no subscribers, no wiring.

### M5.4C — Observability subscribers + lifecycle emission — NEXT
Concrete subscribers (`agent_steps`, logging), RunContext in LangGraph config, and event
emission at composition-root/node wrappers. Scope below.

### Objective (M5.4C)
Wire the Event Bus into the runtime: emit canonical events at lifecycle boundaries with pluggable subscribers. Telemetry, logging, and future tracing/UI are subscribers; the Event Bus does not know what subscribers do with events (ADR-0030 R6, R8).

### Architecture

```text
Runtime composition  →  emit(event)  →  Event Bus  →  Subscriber (interface)
                                                          ├── AgentStepsSubscriber
                                                          ├── LoggingSubscriber
                                                          └── (future) OpenTelemetrySubscriber
```

### Hard rule (M5.4 invariant)

> **The Event Bus MUST NOT know any concrete subscriber.** It depends only on a
> subscriber **interface/Protocol**. Concrete subscribers (`AgentStepsSubscriber`,
> `LoggingSubscriber`, future `OpenTelemetrySubscriber`) are constructed and
> **registered at the composition root** — never imported by the bus itself.
> Removing all subscribers MUST leave a valid (silent) runtime. (Constitution C4; ADR-0030 R6/R8.)

### Canonical events (ADR-0030 §6)

```text
RunStarted → NodeStarted → RouteSelected → TaskPersisted → NodeCompleted → RunCompleted
```

(`NodeFailed` on error paths.)

### Files affected (M5.4C)
| Action | Path |
|--------|------|
| Done (M5.4A) | `backend/app/runtime/__init__.py`, `events.py`, `contracts.py` |
| Done (M5.4B) | `backend/app/runtime/event_bus.py` |
| Create | `backend/app/runtime/subscribers/agent_steps.py` — maps node events → `agent_steps` |
| Create | `backend/app/runtime/subscribers/logging.py` — structured log subscriber |
| Modify | `build_graph` / `ConversationService` — emit events at lifecycle boundaries; node wrappers |
| Modify | `backend/app/services/conversation/service.py` — pass `RunContext` in LangGraph config |
| Create | `backend/tests/test_agent_steps.py` |

### Tests
- Event sequence order valid for a full turn
- Subscriber failure → non-blocking, run still finalizes (R6)
- Business nodes do not import Event Bus or subscribers (R8)
- `agent_steps` rows produced via subscriber, linked to `agent_run_id`
- Input/output snapshots truncated
- RunContext NOT in GraphState checkpoint

### Critic checklist (M5.4)
- [ ] Primary deliverable is Event Bus, not scattered telemetry calls
- [ ] Event Bus imports no concrete subscriber (depends only on interface/Protocol)
- [ ] Runtime with zero subscribers still completes a turn (silent, valid)
- [ ] ADR-0030 R1–R8 satisfied
- [ ] Event enum stable — new subscribers do not require Business changes

### Promotion criteria
```yaml
runtime_event_bus: green
runtime_events: green
agent_steps_subscriber: green
runcontext_in_config: green
r8_no_business_telemetry: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 8 — M5.5: Runtime Qualification

### Objective
**Qualify the runtime** end-to-end — not validate a single feature. HTTP integration, error contracts, eval harness, dogfood, latency/token benchmarks, full regression suite.

### Files affected
| Action | Path |
|--------|------|
| Modify | `backend/app/services/conversation/service.py` — graph name `orchestrated_conversation` |
| Create | `backend/tests/test_m5_chat_integration.py` |
| Modify | `backend/tests/test_chat_api.py` if needed |
| Create | `backend/tests/fixtures/m5_routing_eval.yaml` |
| Create | `backend/tests/test_m5_routing_eval.py` |
| Create | `bin/dogfood-m5-conversation-run.sh` (or extend dogfood scripts) |

### Qualification gates
- `no_objective`, `unplannable`, `no_route` → user still receives reply
- SSE stream shape unchanged (token + done events)
- Both routes exercised through HTTP layer (fake LLM)
- Event Bus sequence valid under qualification load
- Eval harness KPIs (`docs/m5-phase1-investigation-report.md` § Quantitative KPIs)
- Dogfood conversation + grounded paths; record B_lat / B_ground
- `make ci` + `make unit-m4-recovery` green

### Promotion criteria
```yaml
runtime_qualification: green
chat_integration: green
error_contracts: green
eval_harness: green
dogfood_conversation: green
dogfood_grounded: green
benchmarks_recorded: true
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 9 — M5.6: Promotion + runtime contract

### Objective
Freeze M5 runtime, publish promotion doc and **runtime contract**, update knowledge mirror, tag `m5-complete`.

### Files affected
| Action | Path |
|--------|------|
| Create | `docs/m5-promotion.md` |
| Modify | `docs/runtime-contract.md` — draft → **frozen** (event model, Runtime API, layers, extension points, stability) |
| Modify | `knowledge/contracts/graphstate.md` — M5 ownership notes if needed |
| Modify | `knowledge/architecture/graph.md` — topology + Event Bus |
| Modify | `knowledge/agents/README.md` — M5 status |
| Modify | `knowledge/project/roadmap.md` — M5 status |

### Promotion criteria
```yaml
supervisor_node: green
planner_node: green
router_node: green
graph_topology: green
routing_state_machine: green
error_contracts: green
tasks_table: green
runtime_event_bus: green
runtime_contract: frozen
graphstate: unchanged
retriever_unchanged: green
conversation_seam: green
scope_creep: false
m0_m1_m2_m3_m4_tests: green
documentation: complete
knowledge_updated: true
m5_tag: m5-complete
```

---

## Wave / builder integration

After M5.2B+, optional `plans/builder/STATE.yaml` epic `m5-tool-router` with packets mirroring phases 1–9.

**Prerequisite:** M4 tag `m4-complete` on branch base.

---

## References

- `decisions/ADR-0027-multi-agent-graph-topology.md`
- `decisions/ADR-0030-agent-runtime-layer-boundaries.md`
- `docs/runtime-contract.md`
- `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`
- `contracts/agents/{supervisor,planner,router,retriever}.json`
- `plans/m4-retrieval-system-plan.md` (format reference)
- Tag `m4-complete`
