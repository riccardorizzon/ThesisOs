# M5 Tool Router / Orchestration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Each phase has explicit promotion criteria — do not start the next phase until the current phase gate passes. **Critic + QA mandatory every phase.**

**Goal:** Wire Product Plane orchestration — `supervisor` → `planner` → `router` LangGraph nodes, conditional routing by `GraphState.route`, `tasks` persistence, and `agent_steps` telemetry — **without** writer/critic agents, M12 multi-agent loop, GraphState schema changes, or new REST endpoints.

**Architecture:** Prepend orchestration chain to existing M4 graph; `route=conversation` skips retriever; `route=grounded_chat` preserves M4 retrieval path; TaskService upserts from `TaskRef`; OrchestrationTelemetry records `agent_steps` per node (ADR-0027).

**Tech Stack:** FastAPI, LangGraph, SQLAlchemy 2 async, pytest/httpx, fake LLMClient.

**Spec:** `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md` (Frozen 2026-06-25)  
**ADRs:** 0027 (graph topology), 0007 (GraphState frozen), 0014 (RunContext), 0009 (interface pattern for telemetry)

**Branch:** `m5-tool-router` (from `main` @ `m4-complete`).  
**Conventions:** TDD where practical, additive changes only, M0–M4 + builder_engine tests green after every phase.

**Forbidden in all phases:** GraphState new fields, writer/critic/citation nodes, M12 re-entry loop, new REST endpoints, Engineering Runtime imports of `backend.app`.

---

## Phase 1 — Orchestration node stubs + unit tests

### Objective
Implement `make_supervisor_node`, `make_planner_node`, `make_router_node` with fake LLM returning structured JSON; assert contract-compliant `GraphState` mutations and error handling.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/graph/supervisor.py` |
| Create | `backend/app/graph/planner.py` |
| Create | `backend/app/graph/router.py` |
| Create | `backend/app/graph/routing.py` — `route_after_router`, `M5_ROUTES` constant |
| Create | `backend/tests/test_supervisor_node.py` |
| Create | `backend/tests/test_planner_node.py` |
| Create | `backend/tests/test_router_node.py` |

### Node behavior (minimum)
| Node | Happy path | Error path |
|------|------------|------------|
| supervisor | `plan.steps` non-empty, `route` hint set | `no_objective` → empty plan, `route=conversation` |
| planner | refined `plan`, `TaskRef` set | `unplannable` → `task=None`, error appended |
| router | final `route ∈ {conversation, grounded_chat}` | `no_route` → `route=conversation`, error appended |

### Tests
- Fake LLM JSON parsing → correct state writes
- Invalid LLM JSON → safe defaults + no crash
- Reserved route (`writer`) → normalized per spec §6.2
- Only declared `reads_state` / `writes_state` fields touched

### Critic checklist (Phase 1)
- [ ] No graph wiring yet (isolated node tests)
- [ ] No GraphState schema changes
- [ ] Contracts match `contracts/agents/*.json`

### Promotion criteria
```yaml
supervisor_unit: green
planner_unit: green
router_unit: green
m0_m1_m2_m3_m4_tests: green
unit_builder_engine: green
```

---

## Phase 2 — Graph topology + conditional edges

### Objective
Wire ADR-0027 topology in `build_graph`; add `route_after_router` conditional edges; preserve M4 paths.

### Files affected
| Action | Path |
|--------|------|
| Modify | `backend/app/graph/conversation.py` — `build_graph` topology |
| Modify | `backend/app/graph/routing.py` — edge map |
| Create | `backend/tests/test_m5_graph_topology.py` |
| Modify | `backend/tests/test_conversation_graph.py` |
| Modify | `backend/tests/test_retriever_node.py` — grounded path only |

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

### Critic checklist (Phase 2)
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

## Phase 3 — TaskService + tasks table wiring

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

### Critic checklist (Phase 3)
- [ ] No new tables/migrations
- [ ] TaskService is sole writer for `tasks` in M5 scope

### Promotion criteria
```yaml
task_service_unit: green
planner_task_upsert: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 4 — agent_steps telemetry

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

### Critic checklist (Phase 4)
- [ ] RunContext NOT in GraphState checkpoint
- [ ] agent_run still one per turn

### Promotion criteria
```yaml
agent_steps: green
runcontext_boundary: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 5 — Integration + ConversationService polish

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

### Critic checklist (Phase 5)
- [ ] External `/chat` contract unchanged
- [ ] 409 conversation_busy still works (M1)

### Promotion criteria
```yaml
chat_integration: green
error_contracts: green
m0_m1_m2_m3_m4_tests: green
```

---

## Phase 6 — Promotion gate + tag

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

After Phase 2+, optional `plans/builder/STATE.yaml` epic `m5-tool-router` with packets mirroring phases. Use `builder-engine schedule` / `sync` for implementer packets with `checks: ["unit", "drift"]`.

**Prerequisite:** M4 tag `m4-complete` on branch base.

---

## References

- `decisions/ADR-0027-multi-agent-graph-topology.md`
- `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`
- `contracts/agents/{supervisor,planner,router,retriever}.json`
- `plans/m4-retrieval-system-plan.md` (format reference)
- Tag `m4-complete`
