# ThesisOS — M5 "Tool Router / Orchestration" Design Spec

- **Date:** 2026-06-25
- **Status:** Frozen (Architect 2026-06-25) — **no M5 implementation until this spec + ADR-0027 are merged and Critic sign-off recorded.**
- **Scope:** Milestone M5 only — Product Plane orchestration: wire `supervisor`, `planner`, and `router` LangGraph nodes; conditional routing by `GraphState.route`; persist `tasks` rows and `agent_steps` per node. **NOT** writer (M6), critic (M9), citation (M7), or full M12 multi-agent loop.
- **Authors:** ThesisOS Builder Team
- **Builds on:** M4 Retrieval (`retriever`, `retrieved_context`, tag `m4-complete`), M2 Memory (`memory_context_node`), M1 Conversation seam; frozen `GraphState.plan` / `route` / `task`, `contracts/agents/{supervisor,planner,router}.json`, ADR-0007/0009/0014
- **New ADR:** ADR-0027 Multi-Agent Graph Topology (M5 scope)

---

## 1. Vision

M5 closes the loop between **retrieval (M4)** and **specialized agents (M6+)** by introducing the orchestration spine designed in M0:

```text
Acquire (M3) → Index (M4) → Plan & Route (M5) → Execute (M5: chat/retrieval path) → Write (M6+)
```

Today the Product Plane graph is linear:

```text
START → memory_context_node → retriever_node → conversation_node → END
```

M5 **prepends** the Supervisor → Planner → Router chain and **branches** after Router on `route` — without adding GraphState fields (ADR-0007) and without breaking the M1 `/chat` seam.

**Success criterion:** A user turn runs through supervisor → planner → router; `plan`, `task`, and `route` are populated per contracts; conditional edges dispatch to the correct execution subgraph; `tasks` and `agent_steps` rows are written; plain chat and grounded (retrieval) chat both work; **no change to GraphState field list**; M0–M4 suites stay green.

---

## 2. Scope & non-goals

### 2.1 In scope (M5 MUST ship)

| # | Deliverable |
|---|-------------|
| 1 | **`supervisor` node** — reads `messages, task`; writes `plan, route`; error `no_objective` |
| 2 | **`planner` node** — reads `messages, plan`; writes `plan, task`; error `unplannable` |
| 3 | **`router` node** — reads `plan, messages`; writes `route`; error `no_route` |
| 4 | **Multi-node graph topology** — prepend orchestration chain; conditional edges after router (ADR-0027) |
| 5 | **`TaskService` (minimal)** — upsert `tasks` row from `GraphState.task` (`TaskRef`) |
| 6 | **`agent_steps` recording** — one step per orchestration + execution node per turn, linked to `agent_runs` |
| 7 | **Route vocabulary (M5)** — frozen enum of route strings (§6.2); no M6/M9 routes wired |
| 8 | **Tests** — routing decisions, plan/task creation, `no_objective` / `no_route` / `unplannable`, E2E graph traversal (fake LLM) |
| 9 | **Knowledge + promotion** — `docs/m5-promotion.md`, knowledge mirror |

### 2.2 Non-goals (hard boundary)

| Forbidden | Deferred to |
|-----------|-------------|
| Writer agent / chapter drafting | M6 |
| Critic agent / critique loop | M9 |
| Citation agent / bibliography | M7 |
| Full Supervisor-led multi-agent re-entry loop | M12 |
| Parallel agent execution / fan-out | M12 |
| Per-agent token accounting beyond existing `agent_runs.output.usage` | M12 / T013 |
| New GraphState fields | Frozen ADR-0007 |
| New REST endpoints (orchestration is graph-internal) | — |
| Mem0 / auto task decomposition | M15–M16 |
| Build Control Plane / Engineering Runtime changes | Platform Track (MB*) |

```yaml
writer: false
critic: false
citation: false
multi_agent_loop: false
graphstate_new_fields: false
new_rest_endpoints: false
platform_track_changes: false
```

---

## 3. Architecture

### 3.1 Component model (Product Plane)

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                    THESISOS PRODUCT RUNTIME (M5)                          │
│                                                                           │
│  POST /chat ──► ConversationService.stream_turn()                           │
│                         │                                                 │
│                         ├── agent_runs (one per turn, ADR-0014)           │
│                         ├── agent_steps (one per node, M5)                │
│                         └── LangGraph StateGraph(GraphState)              │
│                                   │                                       │
│  START ──► supervisor_node ──► planner_node ──► router_node             │
│                                   │                                       │
│                    conditional on GraphState.route                        │
│                    ┌──────────────┼──────────────┐                      │
│                    ▼              ▼              ▼                      │
│            memory_context    (same path)    error_sink (optional)        │
│                    │              │                                       │
│                    ▼              ▼                                       │
│              conversation    retriever ──► conversation                   │
│                    │              │                                       │
│                    └──────► END ◄─┘                                       │
│                                                                           │
│  planner_node ──► TaskService.upsert_from_task_ref() ──► tasks table    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Service boundaries (normative)

| Concern | Owner | M5 access |
|---------|-------|-----------|
| `GraphState.plan` / `route` / `task` | orchestration nodes | read/write per `contracts/agents/*.json` |
| `GraphState.messages` | ConversationService (caller) | nodes read-only; `conversation_node` appends assistant |
| `GraphState.retrieved_context` | retriever node (M4) | unchanged |
| `tasks` table | TaskService | planner triggers upsert from `TaskRef` |
| `agent_runs` | ConversationService | one row per `/chat` turn (existing) |
| `agent_steps` | OrchestrationTelemetry (new helper) | append per node execution |
| LLM calls for orchestration | nodes via injected `LLMClient` | structured JSON output → state fields |

### 3.3 Relationship to Build Control Plane (ADR-0026)

M5 **Product Track** orchestration nodes share names with Builder agents (Supervisor, Planner, Router) but are **distinct populations**:

| Term | Plane | Runs in |
|------|-------|---------|
| Runtime `supervisor` / `planner` / `router` | Product Plane | LangGraph inside `/chat` |
| Builder Planner / Architect | Build Control Plane | Cursor agents, `plans/builder/` |

No Engineering Runtime code may import `backend.app` to drive product routing (ADR-0023 boundary preserved).

---

## 4. Interfaces

### 4.1 Agent contracts (frozen — no changes)

Per `contracts/agents/supervisor.json`:

```json
{
  "agent": "supervisor",
  "input": { "reads_state": ["messages", "task"] },
  "output": { "writes_state": ["plan", "route"] },
  "errors": ["no_objective"],
  "state_mutations": { "plan": "set", "route": "set" }
}
```

Per `contracts/agents/planner.json`:

```json
{
  "agent": "planner",
  "input": { "reads_state": ["messages", "plan"] },
  "output": { "writes_state": ["plan", "task"] },
  "errors": ["unplannable"],
  "state_mutations": { "plan": "set", "task": "set" }
}
```

Per `contracts/agents/router.json`:

```json
{
  "agent": "router",
  "input": { "reads_state": ["plan", "messages"] },
  "output": { "writes_state": ["route"] },
  "errors": ["no_route"],
  "state_mutations": { "route": "set" }
}
```

### 4.2 LangGraph node factories

| Factory | Signature | Notes |
|---------|-----------|-------|
| `make_supervisor_node(llm, *, telemetry?)` | `GraphState → partial` | Produces `Plan(steps=[...])` + coarse `route` hint |
| `make_planner_node(llm, *, task_service?, telemetry?)` | `GraphState → partial` | Refines plan; sets `TaskRef(id, title)`; calls TaskService |
| `make_router_node(llm, *, telemetry?)` | `GraphState → partial` | Final `route` from M5 vocabulary (§6.2) |
| `route_after_router(state) → str` | conditional edge fn | Returns LangGraph edge key matching `state.route` |

**LLM output shape (normative):** each orchestration node prompts for JSON matching the fields it writes. Parsing failure → append contract error to `errors` and apply safe defaults (`route="conversation"`, empty plan steps).

**Streaming:** orchestration nodes do **not** stream tokens to the user unless they produce user-visible prose (forbidden in M5). Debug/plan summaries may stream as `{"type":"trace","agent":"planner",...}` via custom stream — optional, not required for promotion.

### 4.3 TaskService (minimal)

| Method | Responsibility |
|--------|----------------|
| `upsert_from_task_ref(task_ref: TaskRef, *, owner_agent: str \| None, plan_steps: list[str])` | INSERT or UPDATE `tasks` by `id`; set `title`, `status='in_progress'`, `owner_agent`, `payload={"plan_steps": [...]}` |
| `mark_done(task_id: str)` | Set `status='done'` after successful turn (called from ConversationService finalize) |

**Invariant:** `GraphState.task.id` MUST match `tasks.id` UUID when planner sets `task`.

### 4.4 OrchestrationTelemetry (agent_steps)

Helper invoked at start/end of each node (pattern: ADR-0009 interface style — thin wrapper, swappable later):

| Field | Value |
|-------|-------|
| `agent_run_id` | from `RunContext` (passed via LangGraph config metadata, not GraphState) |
| `agent` | node name (`supervisor`, `planner`, `router`, `retriever`, …) |
| `phase` | `plan` for orchestration nodes; `implement` for execution nodes |
| `input` | snapshot of relevant `reads_state` fields (truncated) |
| `output` | snapshot of `writes_state` fields |
| `status` | `done` \| `error` |

**Forbidden:** persisting `RunContext` into GraphState checkpoint (ADR-0014).

### 4.5 Graph topology (target — ADR-0027)

```text
START
  → supervisor_node
  → planner_node
  → router_node
  → [conditional: route_after_router]
        ├─ route=conversation ──► memory_context_node ──► conversation_node ──► END
        └─ route=grounded_chat ──► memory_context_node ──► retriever_node ──► conversation_node ──► END
```

- **Default route:** `conversation` when router cannot classify (degraded, not hard fail).
- **`no_route` error:** append to `errors`, force `route=conversation`, continue (user still gets a reply).
- **`no_objective` / `unplannable`:** append to `errors`, continue with empty/minimal plan and default route.

M5 does **not** add edges to writer, critic, or citation nodes.

---

## 5. Data flow

### 5.1 Turn lifecycle (`POST /chat`)

```text
User message persisted (ConversationService)
        │
        ▼
GraphState(messages=[...history])     # plan/route/task default None
        │
        ▼
supervisor_node
  READ messages, task
  LLM → objective + coarse plan + route hint
  WRITE plan, route
  RECORD agent_step(supervisor)
        │
        ▼
planner_node
  READ messages, plan
  LLM → refined plan.steps + TaskRef
  WRITE plan, task
  TaskService.upsert_from_task_ref()
  RECORD agent_step(planner)
        │
        ▼
router_node
  READ plan, messages
  LLM → final route ∈ {conversation, grounded_chat}
  WRITE route (overwrites supervisor hint)
  RECORD agent_step(router)
        │
        ▼
route_after_router(state)
        │
        ├── conversation ──► memory_context → conversation → END
        └── grounded_chat ──► memory_context → retriever → conversation → END
        │
        ▼
Assistant message persisted; agent_run finalized; task marked done (if task set)
```

### 5.2 Checkpoint interaction

- `thread_id = conversation_id` (unchanged, ADR-0012).
- Orchestration fields (`plan`, `route`, `task`) are **working state** in the checkpoint for the turn; they may carry forward for multi-turn planning in M12 but M5 only requires per-turn correctness.
- `messages` remain DB-authoritative; checkpoint `messages` replaced each turn by caller (M1 invariant).

### 5.3 Retrieval path (unchanged semantics)

When `route=grounded_chat`, `retriever_node` behavior is identical to M4: last user message as query, hybrid search, populate `retrieved_context`. `conversation_node` may prepend retrieved + memory context to wire (transient — not persisted as user messages).

When `route=conversation`, skip `retriever_node`; `retrieved_context` stays `[]`.

---

## 6. State machines

### 6.1 Routing state machine (M5)

```text
                    ┌─────────────────┐
                    │  TURN_START     │
                    │  route=None     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
               ┌───│  SUPERVISOR     │─── no_objective ──► errors+=, plan=empty
               │   │  sets plan,     │
               │   │  route (hint)   │
               │   └────────┬────────┘
               │            │
               │            ▼
               │   ┌─────────────────┐
               │   │  PLANNER        │─── unplannable ──► errors+=, task=None
               │   │  refines plan,  │
               │   │  sets task      │
               │   └────────┬────────┘
               │            │
               │            ▼
               │   ┌─────────────────┐
               │   │  ROUTER         │─── no_route ──► errors+=, route=conversation
               │   │  sets route     │
               │   └────────┬────────┘
               │            │
               │     ┌──────┴──────┐
               │     ▼             ▼
               │ conversation   grounded_chat
               │     │             │
               │     ▼             ▼
               │ mem→conv      mem→retr→conv
               │     │             │
               └─────┴──────► END ◄┘
```

**Terminal states:** `END` with assistant message persisted; `agent_run.status ∈ {done, error, cancelled}`.

### 6.2 Route vocabulary (frozen for M5)

| Route | Execution subgraph | When |
|-------|-------------------|------|
| `conversation` | memory_context → conversation | General chat, no corpus grounding required |
| `grounded_chat` | memory_context → retriever → conversation | Question benefits from indexed corpus (M4) |

**Reserved (not wired in M5):**

| Route | Milestone |
|-------|-----------|
| `writer` | M6 |
| `critic` | M9 |
| `citation` | M7 |
| `document` | M3 jobs (not chat graph) |

Router MUST NOT emit reserved routes in M5. If LLM returns a reserved route, normalize to `grounded_chat` when retrieval keywords detected, else `conversation`, and append `AgentError(agent="router", message="route_normalized")`.

### 6.3 Task lifecycle (DB)

```text
(none) ── planner sets TaskRef ──► pending
                                      │
                               turn starts ──► in_progress
                                      │
                               turn success ──► done
                               turn error   ──► failed (optional M5; minimum: leave in_progress)
```

M5 promotion minimum: `in_progress` on upsert; `done` on successful finalize.

---

## 7. Acceptance criteria (promotion gate preview)

```yaml
supervisor_node: green         # writes plan, route per contract
planner_node: green            # writes plan, task; upserts tasks row
router_node: green             # writes route; conditional edges work
graph_topology: green          # ADR-0027 topology wired
routing_state_machine: green   # conversation + grounded_chat paths
error_contracts: green         # no_objective, unplannable, no_route handled
tasks_table: green             # TaskRef ↔ tasks.id aligned
agent_steps: green             # one step per node per turn
graphstate: unchanged          # field list frozen
retriever_unchanged: green     # M4 behavior preserved on grounded_chat
conversation_seam: green       # /chat SSE unchanged externally
scope_creep: false             # no writer/critic/M12 loop
m0_m1_m2_m3_m4_tests: green
documentation: complete
knowledge_updated: true
m5_tag: m5-complete
```

---

## 8. Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| LLM returns invalid JSON | parse error | Contract error appended; safe defaults; continue |
| `no_objective` | empty/ambiguous user intent | Error in `errors`; minimal plan; `route=conversation` |
| `unplannable` | planner cannot decompose | Error in `errors`; `task=None`; continue |
| `no_route` | router indecision | Error in `errors`; `route=conversation` |
| Reserved route emitted | validation | Normalize + `route_normalized` error |
| Task upsert fails | DB exception | Log; append error; graph continues (task optional) |
| agent_step write fails | DB exception | Log; non-blocking (run still finalizes) |
| Retrieval on empty corpus | M4 `no_results` | Existing M4 behavior; conversation still replies |
| Scope creep: writer node | PR review | Reject |

---

## 9. Migration strategy

| Phase | Deliverable |
|-------|-------------|
| **1 — Nodes (stubs)** | supervisor/planner/router node factories + unit tests (fake LLM) |
| **2 — Graph wiring** | Conditional edges; ADR-0027 topology in `build_graph` |
| **3 — TaskService** | `tasks` upsert + finalize hook |
| **4 — Telemetry** | `agent_steps` per node; RunContext via config |
| **5 — Integration** | E2E graph tests; ConversationService graph name bump |
| **6 — Promotion** | Gate doc, knowledge mirror, tag `m5-complete` |

**Order:** Spec freeze (this doc) → ADR-0027 → implementation phases → promotion.

No DB migration required for M5 (tables exist from M0).

---

## 10. Relationship to M12 (Multi-Agent)

M5 delivers the **static spine** (Supervisor → Planner → Router → one execution path per turn). M12 adds:

- Re-entry to Supervisor after execution
- Parallel fan-out and merge
- Routes for writer/critic/qa
- Per-agent RunContext accounting

M5 MUST NOT implement re-entry loops or conditional return to Supervisor — that would blur the M5/M12 boundary and complicate testing.

---

## 11. Open questions (resolved in this spec)

| ID | Question | Resolution |
|----|----------|------------|
| Q-O1 | Graph insertion point | Prepend orchestration before `memory_context_node` (ADR-0027) |
| Q-O2 | Skip retriever for simple chat? | Yes — `route=conversation` bypasses retriever |
| Q-O3 | New GraphState fields? | None — use `plan`, `route`, `task` (ADR-0007) |
| Q-O4 | tasks table writer | TaskService, triggered by planner node |
| Q-O5 | agent_steps phase mapping | `plan` for orchestration nodes; `implement` for execution |
| Q-O6 | REST changes? | None — orchestration is internal to graph |
| Q-O7 | Writer route in M5? | Forbidden — reserved for M6 |

---

## 12. Freeze record

- [x] M4 handoff honored (`retriever` preserved; `grounded_chat` route uses M4 path)
- [x] ADR-0027 accepted
- [x] GraphState frozen — no new fields
- [x] Product Plane terminology (ADR-0026)
- [x] Critic conditions: no writer/critic nodes; no M12 re-entry loop; `/chat` seam preserved

- [ ] Critic sign-off: _pending_
- [x] Planner plan: `plans/m5-tool-router-plan.md` (2026-06-25)

**Implementation authorized after:** Critic sign-off line above marked complete.

---

## 13. References

- ADR-0007 GraphState · ADR-0009 Async Jobs · ADR-0014 RunContext · ADR-0024 Retrieval · ADR-0026 Platform Terminology · ADR-0027 Graph Topology
- `docs/superpowers/specs/2026-06-25-thesisos-m4-retrieval-system-design.md`
- `contracts/agents/{supervisor,planner,router,retriever}.json`
- `backend/app/graph/conversation.py` (current topology)
- `knowledge/contracts/graphstate.md`
- Tag `m4-complete` (prerequisite)
