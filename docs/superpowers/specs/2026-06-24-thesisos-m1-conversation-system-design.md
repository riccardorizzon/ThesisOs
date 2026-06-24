# ThesisOS — M1 "Conversation System" Design Spec

- **Date:** 2026-06-24
- **Status:** Approved by Architect (proceeding to writing-plans)
- **Scope:** Milestone M1 only — a complete conversational system on the final orchestration seam. NO agents, RAG, tools, ingestion, or memory engine.
- **Authors:** CEO/Architect session
- **Builds on:** M0 Foundations (frozen contracts, tag `m0-complete`)
- **New ADRs:** 0011 (streaming-first LLM), 0012 (external infra schemas), 0013 (runtime config minimalism), 0014 (RunContext separation)

---

## 1. Context & Goal

M0 froze the architecture, contracts, schema, and a deployed health shell on GCP. M1 delivers
the first vertical slice: a **working chat** — user message → Gemini (Vertex AI) → token
streaming over SSE → React — with **persistent multi-turn history**.

The objective of M1 is **not** "have agents early." It is to **freeze the orchestration
architecture early**: every chat turn runs through LangGraph (a single node today) so that
M2+ *extend* the graph instead of *rewriting* `/chat`, `ConversationService`, the node, or the
frontend. This is the seam-first strategy that pays for itself across M2–M18.

---

## 2. Scope — What M1 IS and IS NOT

**M1 IS (deliverables):**

- `POST /chat` returning a Server-Sent Events stream (replaces the M0 `501` stub).
- `ConversationService` orchestrating persistence + graph invocation + SSE mapping.
- LangGraph app: `START → conversation_node → END` (one node) compiled with a `PostgresSaver`.
- `LiteLLMClient` (real Vertex/Gemini client) behind the existing `LLMClient` seam, with the
  **additive** `astream()` + `TokenChunk` (ADR-0011).
- `RunContext` execution object, separate from `GraphState` (ADR-0014).
- Persistence on existing `conversations` / `messages` tables; checkpoints in the `langgraph`
  schema owned by PostgresSaver (ADR-0012).
- Frontend: `ChatPage`, `ConversationList`, `MessageBubble`, `InputBox`, an SSE client in
  `lib/api.ts`, and an extended store in `lib/store.ts`.
- OpenAPI `/chat` upgraded from stub to real definition.
- Tests covering streaming, multi-turn, persistence, history reload, restart recovery,
  GraphState serialization, token accounting, checkpoint recovery.

**M1 IS NOT (forbidden — hard list):**

- Planner / Router / Retriever / Writer / Critic / Memory / Citation agents
- Multi-agent execution, tool router, tools
- RAG / retrieval, document ingestion, uploads, Docling
- A `users`/`accounts` table or a `thesisos` schema rename
- Any change to frozen domain contracts (`GraphState`, domain DB models, ADR-0001..0010)
- Any feature creep beyond the chat loop

If it is not on the "IS" list, it does not belong in M1.

---

## 3. Architecture (the frozen seam)

```text
React ChatPage
  │  POST /chat            (request: { conversation_id?, message })
  │  ◄── text/event-stream (events: token, done, error)
  ▼
FastAPI  app/api/chat.py   → StreamingResponse(media_type="text/event-stream")
  ▼
ConversationService        persist user msg · build RunContext · open AgentRun ·
  │                        invoke graph (stream) · map to SSE · persist assistant msg
  ▼
LangGraph app              StateGraph(GraphState): START → conversation_node → END
  │                        compiled with PostgresSaver (thread_id = conversation_id)
  ▼
conversation_node          async for chunk in llm.astream(state.messages): yield chunk
  ▼
LiteLLMClient.astream()    litellm.acompletion(model="vertex_ai/gemini-2.5-pro", stream=True)
  ▼
Vertex AI (ADC)            token · token · token …
  ▲
  └── each token rises: node → service → SSE `event: token` → React `assistant += token`
```

One node. The node already produces a stream. M5/M7/M12 add nodes **around** it; this path
does not change.

---

## 4. Components & Boundaries

Each unit has one purpose, a well-defined interface, and is testable in isolation.

### 4.1 Backend

- **`app/llm/base.py`** (extend, additive) — `LLMClient` Protocol gains
  `astream(messages, *, model=None, params=None) -> AsyncIterator[TokenChunk]`; add
  `TokenChunk` **frozen to exactly three fields**: `text: str` (required), `finish_reason: str |
  None = None`, `metadata: dict = {}`. No other fields may be added in M1. `generate/embed/vision`
  unchanged. `NotConfiguredLLM` implements `astream` (raises not-configured).
- **`app/llm/litellm_client.py`** (new) — `LiteLLMClient` implementing the Protocol via LiteLLM
  → Vertex (ADC). `astream` wraps `litellm.acompletion(..., stream=True)` and yields
  `TokenChunk`. `generate` provided for non-streaming callers/tests.
- **`app/llm/factory.py`** (new) — `get_llm_client()` returns `LiteLLMClient` when
  `google_cloud_project` is set, else `NotConfiguredLLM`. Single place that decides real vs stub.
- **`app/schemas/run_context.py`** (new) — `RunContext` (ADR-0014):
  `conversation_id, agent_run_id, trace_id, request_id, user_id=None, metadata`.
- **`app/graph/checkpointer.py`** (new) — builds/owns `PostgresSaver`; `setup()` at startup;
  targets the `langgraph` schema (ADR-0012).
- **`app/graph/conversation.py`** (new) — `build_graph()`: `StateGraph(GraphState)` with the
  single `conversation_node`; compiled with the checkpointer.
- **`app/services/conversation.py`** (new) — `ConversationService`: create/fetch conversation,
  persist user message, build `RunContext`, open `AgentRun`, stream the graph, emit SSE events,
  persist the full assistant message + close `AgentRun` (with token accounting) at stream end.
- **`app/api/chat.py`** (new) — `POST /chat` → `StreamingResponse`. Registered in `app/main.py`.

### 4.2 Frontend (only these)

- `app/chat/page.tsx` — chat screen: message list + streaming assembly + input.
- `components/ConversationList.tsx`, `components/MessageBubble.tsx`, `components/InputBox.tsx`.
- `lib/api.ts` — add `postChatStream(...)` consuming SSE (`token`/`done`/`error`).
- `lib/store.ts` — extend with conversation/messages/streaming state.
- Routes `library`, `memory`, `outline`, `workspace` remain empty (freeze the layout).

---

## 5. Data Flow & Persistence

- **Domain truth:** `conversations(id, title, created_at)` and
  `messages(id, conversation_id, role, content, tool_calls, created_at)` — unchanged schema.
  The UI/history reads from `messages`.
- **Orchestration state:** `GraphState` with **only `messages` populated** in M1; all other
  fields keep explicit defaults (`plan=None`, `route=None`, `retrieved_context=[]`, `draft=None`,
  `critique=None`, `citations=[]`, `memory_ops=[]`, `task=None`, `errors=[]`) for robust
  (de)serialization.
- **Checkpoints:** PostgresSaver in the `langgraph` schema, `thread_id = conversation_id`.
  `messages` is the **system of record** for domain/UI/history. The checkpoint holds the graph's
  *working state* (which includes `GraphState.messages` for model context) and is treated as
  derived/rebuildable from the system of record — it provides restart recovery and lets a new
  turn resume thread state, but it is not a second source of truth for the conversation.
- **Token accounting:** recorded on `agent_runs` (via `RunContext`), **not** on `messages`, so
  future per-agent token consumption attaches without touching domain rows.
- **RunContext is runtime-only (ADR-0014):** passed via the graph invocation config, it MUST NOT
  be persisted into the LangGraph checkpoint or embedded in `GraphState`. Checkpoints carry domain
  working state only; execution metadata (trace/request/run ids) lives for the duration of the run.
- **Conversation title:** created as the literal `"New Conversation"`; automatic titling is
  deferred to M2 (YAGNI — no LLM title generation in M1).
- **Single active run per conversation:** M1 assumes `per_conversation_single_active_run = true`
  (one open stream per conversation at a time); see §8 for how a second concurrent run is rejected.

A turn: persist user `message` → invoke graph (stream) → accumulate assistant tokens → on
`done`, persist assistant `message` and finalize `agent_run`.

---

## 6. Contracts

- **OpenAPI `/chat`:** from `501` stub to real definition. Request
  `{ conversation_id?: string, message: string }`; response `text/event-stream`. This realizes
  the `x-milestone: M1` stub — additive, breaks nothing frozen.
- **Unchanged (frozen):** `GraphState`, domain DB models, ADR-0001..0010.
- **New ADRs:** 0011, 0012, 0013, 0014 (summarized in §1; full text in `decisions/`).

---

## 7. SSE Protocol

Named events so future signals slot in without breaking the client:

```text
event: token   data: {"text": "<delta>"}
event: ping    data: {}                                  # heartbeat every 15-20s
event: done    data: {"conversation_id": "...", "message_id": "...", "usage": {...}}
event: error   data: {"code": "...", "message": "..."}
```

A **heartbeat** `event: ping` is emitted every 15–20s while a stream is open. Cloud Run is
generally stable, but the heartbeat guards against intermediate idle timeouts and lets the
client detect a dead connection. The frontend ignores `ping`, appends on `token`, finalizes on
`done`, surfaces a banner on `error`.

Future (not M1, but the channel is ready): `event: tool`, `event: retrieval`, `event: critic`.

---

## 8. Error Handling

- **LLM not configured:** factory returns `NotConfiguredLLM`; `/chat` responds with HTTP `503`
  (or an `event: error` if the stream already opened) carrying
  `{"code": "llm_not_configured", "message": "Vertex runtime unavailable"}` — never a stack trace.
- **Mid-stream failure:** emit `event: error`, set `agent_run.status = "error"` with the message;
  the UI keeps the partial text and shows the banner.
- **Client disconnect:** cancel the streaming task; the checkpoint remains consistent.
- **Concurrent run on same conversation:** M1 enforces one active stream per conversation. A
  second `POST /chat` for a conversation that already has an in-flight run is rejected with HTTP
  `409 Conflict` + `{"code": "conversation_busy", "message": "A response is already streaming"}`.
  The mechanism (in-process lock vs `agent_runs` status guard) is decided in the plan.
- **Validation:** empty/oversized `message` → `422`/`400` with the `Error{code,message}` schema.

---

## 9. Testing (M1 gate)

Backend (pytest), in addition to the M0 suite staying green:

- **chat streaming** — `astream` yields ordered `TokenChunk`s; SSE framing is correct.
- **multi-turn conversation** — second turn sees prior context via the checkpoint.
- **persistence** — user + assistant messages are written to `messages`.
- **history reload** — fetching a conversation returns its messages in order.
- **restart recovery** — a new app/process resumes a thread from the checkpoint.
- **GraphState serialization** — round-trips through the checkpointer with defaults intact.
- **token accounting** — usage lands on `agent_runs`, not on `messages`.
- **checkpoint recovery** — interrupted run is recoverable from the last checkpoint.
- **LLM factory** — real vs `NotConfiguredLLM` selection; not-configured path returns the
  graceful `llm_not_configured` error.
- **drift test** — domain drift test stays green while **ignoring** `langgraph.*` tables.

Streaming tests use a fake `LLMClient` (no live Vertex) for determinism; one optional,
explicitly-marked integration check may hit Vertex via ADC when credentials are present.

---

## 10. Promotion Criteria (M1 → M2)

M2 must NOT start until ALL are true:

```yaml
chat: working              # POST /chat streams a real Gemini response
sse: working               # token/done/error events framed correctly
history: persistent        # messages persisted; reload returns them in order
langgraph: single_node     # START -> conversation_node -> END, nothing more
graphstate: serializable   # round-trips through the checkpointer
checkpointer: working      # PostgresSaver in `langgraph` schema; restart recovery proven
contracts: unchanged       # domain contracts (GraphState, domain models, ADR-0001..0010) intact
adc: working               # Vertex reached via ADC; no vertex-config secret used
tests: green               # M1 suite + M0 suite all pass; ruff clean
scope_creep: false         # nothing from the forbidden list shipped
```

M2 (memory) will **extend** the graph — add nodes/state usage — not rewrite this seam.

---

## 11. Open Questions / Risks

Ranked by risk; each is resolved during planning.

- **[HIGH] Concurrent streams on one conversation:** two simultaneous runs writing the same
  conversation corrupt order and checkpoint state. M1 assumes `per_conversation_single_active_run
  = true` and rejects a second run with `409` (§8). The plan picks the guard (in-process asyncio
  lock keyed by `conversation_id`, and/or an `agent_runs` "active" status check) and how stale
  locks are released after a crash.
- **[MEDIUM] LiteLLM ↔ Vertex streaming shape:** confirm `litellm.acompletion(stream=True)` chunk
  fields map cleanly to `TokenChunk` (delta text + final `finish_reason`/usage) for
  `vertex_ai/gemini-2.5-pro`.
- **[MEDIUM] Async DB driver:** `ConversationService` streaming favors async DB access; confirm
  the session/driver choice (psycopg async) during planning to avoid blocking the event loop.
- **[LOW] PostgresSaver custom schema support:** preference is a dedicated `langgraph` schema; if
  the pinned `langgraph-checkpoint-postgres` version cannot target a non-public schema, fall back
  to documented `public` checkpoint tables (still excluded from Alembic/drift) and revisit.
  Resolve by pinning the version and verifying `.setup()` behavior.
- **[LOW] SSE through Cloud Run:** confirm streaming responses (with the §7 heartbeat) pass Cloud
  Run buffering acceptably for single-user latency; verify locally first (services are private; M1
  dev is local).
