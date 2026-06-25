# ADR-0027: Multi-Agent Graph Topology (M5)

- Status: Accepted (frozen 2026-06-25)
- Context: M0–M4 established the Product Plane orchestration seam (LangGraph + frozen `GraphState`, M1 `/chat` path) and wired execution nodes for memory (M2), retrieval (M4), and conversation (M1). The target hierarchy — Supervisor → Planner → Router → specialized agents — was designed in M0 but not wired. M5 must introduce orchestration without adding GraphState fields (ADR-0007), without implementing writer/critic (M6/M9), and without the full multi-agent re-entry loop deferred to M12. A frozen topology decision is required before implementation to prevent ad-hoc graph edits across phases.
- Decision:

  ### 1. M5 graph topology (Product Plane)

  Replace the linear M4 graph:

  ```text
  START → memory_context_node → retriever_node → conversation_node → END
  ```

  with the M5 topology:

  ```text
  START
    → supervisor_node
    → planner_node
    → router_node
    → [conditional: route_after_router]
          ├─ route=conversation ──► memory_context_node ──► conversation_node ──► END
          └─ route=grounded_chat ──► memory_context_node ──► retriever_node ──► conversation_node ──► END
  ```

  Orchestration nodes run **sequentially** on every `/chat` turn before execution subgraph dispatch.

  ### 2. GraphState usage (no schema change)

  M5 uses only existing fields:

  | Field | Nodes | Semantics |
  |-------|-------|-----------|
  | `plan` | supervisor (set), planner (set) | `Plan(steps: list[str])` — turn-level decomposition |
  | `task` | planner (set) | `TaskRef(id, title)` — current work unit; mirrors `tasks` row |
  | `route` | supervisor (set hint), router (set final) | Dispatch key for conditional edges |

  No new fields. No execution metadata in GraphState (ADR-0014).

  ### 3. Route vocabulary (M5)

  Only two routes are **wired** in M5:

  | Route | Path |
  |-------|------|
  | `conversation` | memory_context → conversation (skip retriever) |
  | `grounded_chat` | memory_context → retriever → conversation |

  Routes `writer`, `critic`, `citation`, and `document` are **reserved** and MUST NOT receive graph edges until their milestones. Router normalization rules are defined in the M5 spec (§6.2).

  ### 4. Persistence wiring

  1. **`tasks` table:** `TaskService.upsert_from_task_ref()` called from `planner_node` when `GraphState.task` is set. `tasks.id` MUST equal `TaskRef.id`.
  2. **`agent_runs`:** unchanged — one row per `/chat` turn (ConversationService).
  3. **`agent_steps`:** one row per graph node execution per turn, linked to `agent_run_id` via `RunContext` passed through LangGraph config (not GraphState).

  ### 5. Error handling (continue degraded)

  Contract errors (`no_objective`, `unplannable`, `no_route`) append to `GraphState.errors` and **do not abort the turn**. Default fallback route: `conversation`. The user always receives an assistant reply unless the turn fails at the ConversationService layer (M1 behavior).

  ### 6. Boundaries preserved

  - M1 `/chat` → `ConversationService` → `graph.astream` → SSE seam unchanged externally.
  - M4 `retriever_node` behavior unchanged when on the `grounded_chat` path.
  - Engineering Runtime / Build Control Plane MUST NOT import or drive product graph topology (ADR-0023, ADR-0026).
  - M5 does **not** implement Supervisor re-entry, parallel agents, or writer/critic loops (M12/M6/M9).

- Consequences: Clear, testable graph extension path for M6+ (add route + node + edge). Orchestration is observable via `agent_steps` and `tasks`. Cost: every chat turn pays three LLM calls for orchestration (latency/cost — acceptable for M5; optimization deferred). Checkpoint may accumulate `plan`/`task`/`route` across turns — callers must reset or accept carry-forward until M12 defines multi-turn orchestration semantics.
- Alternatives considered:
  - **Keep linear M4 graph, add orchestration inside `conversation_node`** — rejected; violates agent contracts and prevents conditional retrieval skip.
  - **Router before Planner** — rejected; planner needs supervisor's coarse plan; matches M0 hierarchy.
  - **Always run retriever** — rejected; wastes embed/search on non-grounded chat; routing is the point of M5.
  - **Add `orchestration` GraphState sub-model** — rejected; violates ADR-0007 freeze.
  - **Implement full M12 loop in M5** — rejected; scope creep; breaks milestone gates.

- References: ADR-0007, ADR-0009, ADR-0014, ADR-0024, ADR-0026; `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`; `contracts/agents/{supervisor,planner,router}.json`; `knowledge/architecture/graph.md`.
