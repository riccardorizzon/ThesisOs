# Backend Architecture

> Sources: `backend/app/**`, `backend/pyproject.toml`, M0 spec §6/§9/§12/§13, M1 spec §4.1, ADR-0002/0005/0009/0011/0013/0014.

## Stack

- **Language:** Python ≥ 3.12 (Python everywhere server-side — ADR-0005).
- **Framework:** FastAPI + Uvicorn.
- **ORM:** SQLAlchemy 2.x (sync `session.py` + async `session_async.py` via
  psycopg3). `sqlalchemy[asyncio]` (greenlet) declared for the async engine.
- **Validation/config:** Pydantic v2 + pydantic-settings.
- **Migrations:** Alembic (`migrations/`, `0001_initial`).
- **Vectors:** `pgvector` (`Vector(768)`).
- **Orchestration:** LangGraph + `langgraph-checkpoint-postgres`.
- **LLM:** LiteLLM → Vertex AI (ADC).
- **Streaming:** `sse-starlette` (`EventSourceResponse`).
- **Observability:** OpenTelemetry FastAPI instrumentation + structlog JSON logs +
  `prometheus_client` `/metrics`.
- **Tests:** pytest + pytest-asyncio (`asyncio_mode=auto`) + httpx; ruff lint.

## Layout (`backend/app/`)

```text
api/        system.py · jobs.py · chat.py            FastAPI routers
core/       config.py · logging.py                   settings + log bootstrap
llm/        base.py · litellm_client.py · factory.py LLM seam (ADR-0002/0011)
schemas/    graph_state.py · run_context.py          Pydantic contracts
graph/      conversation.py · checkpointer.py        LangGraph app + saver
db/         base.py · models.py · session.py · session_async.py
services/   conversation/{service,locks} + stub pkgs (events, jobs, telemetry,
            ingestion, retrieval, memory, citation)
agents/     (empty — runtime nodes added M2+)
main.py     FastAPI app, router wiring, lifespan
```

## The LLM seam (ADR-0002, ADR-0011)

`app/llm/base.py` defines a `Protocol` with `generate`, **`astream`**, `embed`,
`vision`. `TokenChunk` is **frozen to exactly 3 fields**: `text`, `finish_reason`,
`metadata` (ADR-0011) — do not widen it. `NotConfiguredLLM` implements all methods
by raising `NotImplementedError` (its `astream` is an async generator that raises).

- `litellm_client.py`: `LiteLLMClient` wraps `litellm.acompletion(...)`; model is
  `vertex_ai/<gemini_model>`; `vertex_project`/`vertex_location` from settings;
  ADC for auth (no API keys, ADR-0013). `embed`/`vision` raise NotImplemented (M2/M4+).
- `factory.py`: `get_llm_client()` returns `LiteLLMClient` iff
  `settings.google_cloud_project` is set, else `NotConfiguredLLM`. This is the
  single decision point for real-vs-stub.

## Configuration (ADR-0013)

`core/config.py` `Settings` (env-driven, `.env`): `app_env`, `log_level`,
`database_url`, `google_cloud_project`, `vertex_location` (`europe-west1`),
`gemini_model` (`gemini-2.5-pro`), `embedding_model`
(`text-multilingual-embedding-002`). **`config.py` is the single source of truth
for runtime LLM config**; the `vertex-config` secret is intentionally unused.

## API surface (implemented)

- `GET /health` → `{"status":"ok"}`.
- `GET /ready` → `{"status":"ready","db":bool,"config":true}` (503 if DB down).
- `GET /metrics` → Prometheus.
- `POST /jobs`, `GET /jobs/{id}` → `501` (contract only, ADR-0009).
- `POST /chat` → SSE stream (M1). See `architecture/graph.md` + `contracts/api-contracts.md`.

Full contract: `contracts/openapi/openapi.yaml`. Deferred paths carry `x-milestone`.

## Services pattern

- **`conversation/`** is the only implemented service. `service.py`
  (`ConversationService`) is the boundary between HTTP and the graph: it owns
  reads/writes to `conversations`/`messages` (system of record), graph streaming,
  AgentRun lifecycle, and token accounting. `locks.py` (`ConversationLocks`) is an
  in-process single-active-run guard per conversation.
- **Stub services** (`events`, `jobs`, `telemetry`, `ingestion`, `retrieval`,
  `memory`, `citation`) ship interfaces/`NotImplementedError` only; wired in their
  milestones. This is intentional zero-feature-debt scaffolding, not dead code.

## Startup (lifespan)

`main.py` configures logging, then a lifespan hook calls
`ensure_langgraph_schema()` (create `langgraph` schema + `PostgresSaver.setup()`),
swallowing failures with a warning (DB may be down at boot; setup is idempotent
and retried lazily). Routers: `system`, `jobs`, `chat`. `init_telemetry(app)`
instruments FastAPI.

## Backend conventions
- Async DB access on the streaming path (avoid blocking the event loop).
- `AgentRun` is finalized on **every** exit path (success/error/disconnect) so a
  run never stays stuck `running` (see `service.py` `finally` with `asyncio.shield`).
- Errors returned to clients are clean codes (`llm_not_configured`,
  `conversation_busy`, `stream_error`, …) — never stack traces (M1 spec §8).
