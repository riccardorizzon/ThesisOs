# Orchestration / Graph Architecture

> Sources: `backend/app/graph/conversation.py`, `backend/app/graph/checkpointer.py`, `backend/app/services/conversation/service.py`, M1 spec §3–§5, ADR-0007/0011/0012/0014.

## The frozen seam

ThesisOS orchestration is a **LangGraph `StateGraph(GraphState)`**. M1 wired it
with **one node** so future milestones *extend* the graph rather than rewrite the
chat path (M1 spec §1):

```text
START → conversation_node → END        (compiled with AsyncPostgresSaver)
```

The target hierarchy (designed M0, wired progressively) is:

```text
Supervisor → Planner → Router → { Retriever · Writer · Critic · Citation · Memory · Document }
```

M2+ add nodes **around** `conversation_node`; the `/chat` → `ConversationService`
→ graph → `astream` → SSE seam does not change.

## `conversation_node` (M1)

`make_conversation_node(llm)` returns an async node that:
1. `get_stream_writer()` for custom streaming.
2. Maps `state.messages` → wire dicts `{role, content}`.
3. `async for chunk in llm.astream(wire)`: append `chunk.text`, emit
   `writer({"type":"token","text":...})`; capture `chunk.metadata["usage"]`.
4. After the loop, if usage present, `writer({"type":"usage","text":"","usage":...})`.
5. Returns `{"messages": [...history, assistant], "draft": ..., "errors": ...}`.

**Why no `add_messages` reducer:** the caller (`ConversationService`) owns history
from the DB (system of record), so the node uses *replace* semantics. This keeps
`GraphState` frozen (ADR-0007) and avoids unknown-key update errors. Usage is
carried out via the custom stream, **not** via `GraphState`, to keep it frozen.

## Streaming model

`graph.astream(state, cfg, stream_mode="custom")` yields the dicts written by the
node. `ConversationService` maps `{"type":"token"}` → SSE `event: token` and
`{"type":"usage"}` → its `usage` accumulator. `sse-starlette` adds `ping` heartbeats.

## Checkpointer (ADR-0012)

`checkpointer.py`:
- `LANGGRAPH_SCHEMA = "langgraph"`.
- `_psycopg_conn_string(dsn)`: rewrites the SQLAlchemy DSN to a bare `postgresql://`
  psycopg DSN and pins `options=-csearch_path=langgraph,public`.
- `open_checkpointer()`: async context manager yielding
  `AsyncPostgresSaver.from_conn_string(...)`.
- `ensure_langgraph_schema()`: `CREATE SCHEMA IF NOT EXISTS langgraph` then
  `saver.setup()` (idempotent), called at app startup.

`thread_id = conversation_id`. The checkpoint is **derived/rebuildable** working
state — `messages` is the source of truth (M1 spec §5).

## Execution metadata (ADR-0014)

`RunContext { conversation_id, agent_run_id, trace_id, request_id, user_id=None,
metadata }` is **runtime-only**: passed via LangGraph config alongside the invocation,
**never** persisted into the checkpoint and **never** merged into `GraphState`.
Domain fields never enter `RunContext`; execution fields never enter `GraphState`.
Layer boundaries: ADR-0030.

## M5 topology (ADR-0027)

```text
START → supervisor → planner → router → memory_context
         → route_after_router
            conversation → END
            grounded_chat → retriever → conversation → END
```

Task persistence: planner hook → `TaskService` wired in `build_graph` (ADR-0030).
Runtime: **Event Bus** + subscribers — not telemetry-first (M5.4, ADR-0030 §6). Onboarding: `docs/runtime-contract.md`.

## M6 topology (ADR-0031) — writer route

```text
START → supervisor → planner → router → memory_context
         → route_after_router
            conversation → END                                  (M5)
            grounded_chat → retriever → route_after_retriever → conversation → END   (M5)
            writer        → retriever → route_after_retriever → writer → END          (M6)
```

The `writer` route (reserved in ADR-0027) is activated in M6: it shares the
retriever (grounded by construction), then dispatches to `writer_node` via a second
conditional (`route_after_retriever`). The **writer is a capability** —
`WriterCapability.write_grounded(brief) -> DraftResult` (`LLMWriter` default,
swappable at the composition root); `make_writer_node` adapts `DraftResult` →
`draft`/`citations` only (writer.json). It is pure (no db/runtime/persistence/LangGraph
imports); streaming is injected via `stream_writer_factory`. Drafts persist through
`ChapterService` (ADR-0032), never from the node. M5 conversation/grounded paths are
byte-for-byte unchanged (C6).

## Concurrency / safety

- **One active run per conversation** (M1 spec §8/§11): `ConversationLocks`
  (in-process set) guards the whole turn; new conversations get a server id up
  front so they are covered too. A second run → `409 conversation_busy`.
- **AgentRun always finalized**: success → `done`, handled error → `error`,
  client disconnect/cancel → `cancelled` (via `asyncio.shield` in `finally`).

## How to extend the graph (M2+)

See `onboarding/how-to-add-an-agent.md`. In short: add a node function, register it
with `g.add_node`, wire edges, declare its `GraphState` reads/writes in
`contracts/agents/<name>.json`, and **do not** change `GraphState` fields without a
new ADR.
