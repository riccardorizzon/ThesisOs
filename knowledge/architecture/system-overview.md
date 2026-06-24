# System Overview

> Sources: `docs/architecture.md` §1–§9; M0 spec §4; M1 spec §3; ADR-0001..0014.

## The runtime stack (top to bottom)

```text
Next.js (App Router, Tailwind, Zustand)          frontend, ChatGPT-style UI
        │  HTTPS / SSE
        ▼
FastAPI (backend, Python, no auth — single user) API contracts
        ▼
LangGraph Orchestrator                            Supervisor→Planner→Router→{agents}
  (seam wired M1: 1 node; agents added M2+)
        ▼
Services: ingestion · retrieval · memory ·        business logic (Python)
  citation · events · jobs · telemetry · conversation
        ▼
LLM abstraction (LiteLLM): generate/astream/embed/vision  provider-swappable
        ▼
Vertex AI: Gemini + multilingual-embedding        single runtime vendor
        ▼
Postgres + pgvector (Cloud SQL) · Cloud Storage · Secret Manager · Cloud Logging/OTel
```

(Verbatim shape from `docs/architecture.md` §1, with M1's `astream` and the
`conversation` service added.)

## Two worlds: Runtime vs Builder

ThesisOS draws a **hard line** between the system that *runs* and the team that
*builds* it (`docs/architecture.md` §2, ADR-0002):

- **Runtime LLM = Vertex AI.** One vendor for generation/vision (Gemini) and
  embeddings (`text-multilingual-embedding-002`). The product talks only to Vertex,
  through LiteLLM.
- **Builder = Cursor agents.** Build-time only. **No deployed code path calls
  Cursor.** Cursor-as-runtime-generator was evaluated and rejected.

This means the deployed system depends on **exactly one** external LLM vendor,
swappable via configuration without touching callers.

## Request lifecycle (M1 chat turn)

> Source: M1 spec §3, §5; `backend/app/api/chat.py`, `backend/app/services/conversation/service.py`.

1. React `ChatPage` → `POST /chat { conversation_id?, message }`.
2. `chat.py`: if LLM not configured → `503`; acquire per-conversation lock (else
   `409`); open an SSE `EventSourceResponse` (heartbeat `ping=15`).
3. `ConversationService.stream_turn`: persist user message + open `AgentRun`
   (status `running`) in one transaction; load history from `messages` (system of
   record); build `GraphState(messages=history)` and a runtime-only `RunContext`.
4. Open `AsyncPostgresSaver` (langgraph schema, `thread_id=conversation_id`); build
   the graph; `graph.astream(state, cfg, stream_mode="custom")`.
5. `conversation_node` streams tokens via `get_stream_writer()`; each token rises:
   node → service → SSE `event: token` → React `assistant += token`.
6. On completion: persist assistant message, finalize `AgentRun` (status `done`,
   usage on `output`), emit `event: done`. On error/disconnect: emit `event: error`
   / finalize `cancelled`. The lock is released in a `finally`.

## Cross-cutting design rules

| Rule | Where | ADR |
|------|-------|-----|
| Contract-First — contracts before code | whole repo | ADR-0001 |
| One LLM vendor behind a seam | `backend/app/llm/` | ADR-0002 |
| Streaming-first LLM (`astream`/`TokenChunk` additive) | `app/llm/base.py` | ADR-0011 |
| Custom memory on Postgres+pgvector | `memories` table | ADR-0003 |
| Event-driven (typed catalog + outbox) | `services/events/`, `events` table | ADR-0006 |
| Shared frozen `GraphState` | `app/schemas/graph_state.py` | ADR-0007 |
| Execution metadata separate (`RunContext`) | `app/schemas/run_context.py` | ADR-0014 |
| Async jobs out of request path | `services/jobs/` | ADR-0009 |
| Dev = Prod (identical images) | `docker/`, Cloud Run | ADR-0008 |
| External infra schemas (langgraph) separate from domain | `langgraph` schema | ADR-0012 |
| Runtime config minimalism (ADC, no vertex-config secret) | `core/config.py` | ADR-0013 |
| Promotion gates per milestone | `docs/m*-promotion.md` | ADR-0010 |

## Component inventory (current code)

> Source: `backend/app/`, `frontend/`.

- **API** (`app/api/`): `system.py` (health/ready/metrics), `jobs.py` (501 stub),
  `chat.py` (M1 SSE).
- **Core** (`app/core/`): `config.py` (pydantic settings), `logging.py`.
- **LLM** (`app/llm/`): `base.py` (Protocol + `TokenChunk` + `NotConfiguredLLM`),
  `litellm_client.py`, `factory.py`.
- **Schemas** (`app/schemas/`): `graph_state.py`, `run_context.py`.
- **Graph** (`app/graph/`): `conversation.py` (node + `build_graph`),
  `checkpointer.py` (`AsyncPostgresSaver`).
- **DB** (`app/db/`): `base.py`, `models.py` (14 tables), `session.py` (sync),
  `session_async.py` (psycopg3 async).
- **Services** (`app/services/`): `conversation/` (service + locks), plus stub
  packages `events`, `jobs`, `telemetry`, `ingestion`, `retrieval`, `memory`,
  `citation`.
- **Agents** (`app/agents/`): empty `__init__.py` — runtime agent nodes are added
  M2+; contracts already exist in `contracts/agents/`.
- **Frontend** (`frontend/`): App Router routes `chat` (live) + `library`,
  `memory`, `outline`, `workspace`, `settings` (placeholders); `lib/api.ts`,
  `lib/store.ts`; `components/`.

See the dedicated `architecture/backend.md`, `frontend.md`, `database.md`,
`graph.md`, `memory.md`, `infrastructure.md`.
