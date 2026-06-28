# M5 Tool Router / Orchestration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Each phase has explicit promotion criteria — do not start the next phase until the current phase gate passes. **Critic + QA mandatory every phase.**

**Goal:** Wire Product Plane orchestration — `supervisor` → `planner` → `router` LangGraph nodes, conditional routing by `GraphState.route`, `tasks` persistence, and `agent_steps` telemetry — **without** writer/critic agents, M12 multi-agent loop, GraphState schema changes, or new REST endpoints.

**Architecture:** Prepend orchestration chain to existing M4 graph; `route=conversation` skips retriever; `route=grounded_chat` preserves M4 retrieval path; TaskService upserts from `TaskRef`; OrchestrationTelemetry records `agent_steps` per node (ADR-0027).

**Tech Stack:** FastAPI, LangGraph, SQLAlchemy 2 async, pytest/httpx, fake LLMClient.

**Spec:** `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md` (Frozen 2026-06-25)  
**ADRs:** 0027 (graph topology), 0007 (GraphState frozen), 0014 (RunContext), 0009 (interface pattern for telemetry)

**Branch:** `m5-tool-router` (from `main` @ `143f429`).  
**Conventions:** TDD where practical, additive changes only, M0–M4 + builder_engine tests green after every phase.

**Implementation discipline (mandatory):** See `docs/m5-phase1-investigation-report.md` § Implementation discipline.
1. **Shippable phases** — after each step: `make ci` green, M4 regression green, branch merge-ready (no half-wired graph).
2. **No dead code** — every module shipped in a step is fully tested and contract-complete even if not yet wired to `build_graph()`.

**Phase order (11 steps):** supervisor → planner → router → **M5.2A routing infrastructure** → **M5.2B graph wiring** → TaskService → telemetry → `/chat` → eval → dogfood/benchmark → promotion.

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
| M5.1 | `9e2aa9b` | supervisor, planner, router, orchestration helpers — **do not reopen except demonstrable bugs** |

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

## Phase 6 — TaskService + tasks table wiring

### Objective
Persist planner output to `tasks` table; mark done on successful turn finalize.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/services/task/__init__.py` |
| Create | `backend/app/services/task/service.py` |
| Modify | `backend/app/graph/planner.py` — inject TaskService |
| Modify | `backend/app/services/conversation/service.py` — `mark_done` on finalize |
| Create | `backend/tests/test_task_service.py` |

### Public API (service)
| Method | Notes |
|--------|-------|
| `upsert_from_task_ref(task_ref, *, owner_agent, plan_steps)` | INSERT ON CONFLICT UPDATE by id |
| `mark_done(task_id)` | status → `done` |

### Tests
- Planner sets `TaskRef` → row exists in `tasks` with matching id/title
- Successful chat finalize → task status `done`
- Task upsert failure → logged, turn continues

### Critic checklist (Phase 6)
- [ ] No new tables/migrations
- [ ] TaskService is sole writer for `tasks` in M5 scope

### Promotion criteria
```yaml
task_service_unit: green
planner_task_upsert: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 7 — agent_steps telemetry

### Objective
Record one `agent_step` per node execution; pass `RunContext` via LangGraph config.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/services/telemetry/orchestration.py` — step recorder |
| Modify | orchestration + execution nodes — call recorder start/finish |
| Modify | `backend/app/services/conversation/service.py` — pass RunContext in config |
| Create | `backend/tests/test_agent_steps.py` |

### Step schema (per turn)
| agent | phase | When |
|-------|-------|------|
| supervisor | plan | orchestration |
| planner | plan | orchestration |
| router | plan | orchestration |
| memory_context | implement | execution |
| retriever | implement | execution (grounded only) |
| conversation | implement | execution |

### Tests
- Full turn → N agent_steps linked to agent_run_id
- Step write failure → non-blocking, run still finalizes
- Input/output snapshots truncated (no full message dump)

### Critic checklist (Phase 7)
- [ ] RunContext NOT in GraphState checkpoint
- [ ] agent_run still one per turn

### Promotion criteria
```yaml
agent_steps: green
runcontext_boundary: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 8 — Integration + ConversationService polish

### Objective
End-to-end `/chat` with orchestration; update `agent_runs.graph` name; error contract integration tests.

### Files affected
| Action | Path |
|--------|------|
| Modify | `backend/app/services/conversation/service.py` — graph name `orchestrated_conversation` |
| Create | `backend/tests/test_m5_chat_integration.py` |
| Modify | `backend/tests/test_chat_api.py` if needed |

### Tests
- `no_objective`, `unplannable`, `no_route` → user still receives reply
- SSE stream shape unchanged (token + done events)
- Both routes exercised through HTTP layer (fake LLM)

### Critic checklist (Phase 8)
- [ ] External `/chat` contract unchanged
- [ ] 409 conversation_busy still works (M1)

### Promotion criteria
```yaml
chat_integration: green
error_contracts: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 9 — Evaluation dataset + routing benchmark

### Objective
Labeled eval set and KPI harness (`docs/m5-phase1-investigation-report.md` § Quantitative KPIs).

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/tests/fixtures/m5_routing_eval.yaml` |
| Create | `backend/tests/test_m5_routing_eval.py` |

### Promotion criteria
```yaml
eval_harness: green
make_ci: green
unit_m4_recovery: green
```

---

## Phase 10 — Dogfood + latency/token benchmark

### Objective
Conversation-path smoke + existing `make dogfood-m4`; record B_lat / B_ground.

### Files affected
| Action | Path |
|--------|------|
| Create | `bin/dogfood-m5-conversation-run.sh` (or extend dogfood scripts) |
| Modify | benchmark notes in promotion doc |

### Promotion criteria
```yaml
dogfood_conversation: green
dogfood_grounded: green
benchmarks_recorded: true
```

---

## Phase 11 — Promotion gate + tag

### Objective
`docs/m5-promotion.md`, knowledge mirror, tag `m5-complete`.

### Files affected
| Action | Path |
|--------|------|
| Create | `docs/m5-promotion.md` |
| Modify | `knowledge/contracts/graphstate.md` — M5 ownership notes if needed |
| Modify | `knowledge/architecture/graph.md` — topology update |
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
agent_steps: green
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

After Phase 5+, optional `plans/builder/STATE.yaml` epic `m5-tool-router` with packets mirroring phases 1–11.

**Prerequisite:** M4 tag `m4-complete` on branch base.

---

## References

- `decisions/ADR-0027-multi-agent-graph-topology.md`
- `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`
- `contracts/agents/{supervisor,planner,router,retriever}.json`
- `plans/m4-retrieval-system-plan.md` (format reference)
- Tag `m4-complete`
