# Technical Decisions

> Consolidated from `decisions/ADR-0002/0003/0011/0013` plus implementation-level choices recorded in `plans/builder/STATE.yaml`, `docs/m1-promotion.md`, and the M0/M1 plans. ADRs are the source of truth; the non-ADR choices below are engineering decisions made during the build.

## Technical ADRs

### ADR-0002 — Vertex Runtime Only
Runtime LLM = Vertex AI: Gemini (generate + vision) + `text-multilingual-embedding-002`
(embed), behind a **LiteLLM seam**. Single credential (GCP service account / ADC), no
API keys. Embeddings are **model/dimension-tagged** for provider swap. Cursor is
build-time only, never a runtime dependency. Provider swappable by reconfiguring
LiteLLM; callers never know the provider.

### ADR-0003 — Custom Memory
Memory is a custom layer on Postgres+pgvector with 6 editable, versioned kinds
(`user|thesis|concept|citation|decision|editable`); the `editable` kind is injected
into the system prompt. **No Mem0 in core**; Mem0-style auto-extraction deferred to
M15–M16. Rationale: structured + manually editable + versioned + doc references +
full control. See `architecture/memory.md`.

### ADR-0011 — Streaming-First LLM
Extend the `LLMClient` Protocol **additively**: keep `generate/embed/vision`
byte-for-byte; add `astream(...) -> AsyncIterator[TokenChunk]`. `TokenChunk` is
**frozen to exactly 3 fields** (`text`, `finish_reason`, `metadata`). `NotConfiguredLLM`
also implements `astream`. Enables real streaming without breaking frozen contracts.

### ADR-0013 — Runtime Config Minimalism
Authenticate to Vertex with **ADC only**; read project/location/model from env +
`config.py`. The `vertex-config` secret is **not** populated/read in M1. `config.py`
is the single source of truth for runtime LLM config. YAGNI — the LiteLLM seam keeps
richer config open for later.

## Engineering decisions (non-ADR, recorded during the build)

| Decision | Detail | Source |
|----------|--------|--------|
| LangGraph pinned to 1.x | APIs verified against the pinned version | STATE P-B |
| `AsyncPostgresSaver` (aio) | async checkpointer to match the async streaming path | M1 plan T7 |
| `sqlalchemy[asyncio]` + greenlet | required for the async engine (psycopg3) | STATE P-B, commit `9ae5e4a` |
| Async DB driver = psycopg3 | `postgresql+psycopg` for both sync & async engines | M1 plan T6 |
| No `add_messages` reducer | caller builds `messages` from DB (system of record) → keeps `GraphState` frozen | M1 spec §5, `conversation.py` |
| Usage via custom stream writer | `writer({"type":"usage",...})` instead of a `GraphState` field | `conversation.py`, M1 plan T8/T9 |
| Token accounting on `agent_runs` | not on `messages` | M1 spec §5 |
| Per-conversation in-process lock | single-active-run guard; whole-turn lock incl. new conversations | M1 spec §8, `locks.py`, `chat.py` |
| SSE heartbeat `ping=15` | `sse-starlette` keeps the connection alive | M1 spec §7 |
| `503` fail-fast for not-configured LLM | before opening the stream (sync 503) | `chat.py`, review M4/M2 |
| Message validation `1..32000` | Pydantic `Field(min_length, max_length)` | `chat.py` (C1 review) |
| CRLF-safe SSE framing | client parser fixed + regression test | commit `f26885c` |
| AgentRun finalized on every path | success/error/disconnect via `asyncio.shield` | `service.py` (I1 review) |
| `database-url` DSN owned by Terraform | rendered from `db_password` + connection name → single source of truth | `secrets.tf`, runbook §4a |
| Cloud Run private by default | `allow_public_invoker=false` (no app auth) | runbook §3 |
| Buildx amd64 fallback for CI | when Cloud Build hit PERMISSION_DENIED | m0-promotion |

## Known technical debt (tracked)
- Token usage not captured on Vertex streaming (needs
  `stream_options={"include_usage": True}`) — M2 follow-up.
- `ConversationService.stream_turn` lacks an end-to-end unit test.
- Frontend `NEXT_PUBLIC_API_BASE_URL` not declared as a Docker `ARG`.
See `memory/known-risks.md` and `context/next-actions.md`.
