# ThesisOS — Architecture Overview

> **Living architecture document** for the Product Plane runtime.
> Baseline: **`m6-main`** @ `79fb52a` (integrated on `main`, 2026-06-29).
>
> This is the human-readable overview. Authoritative detail lives in:
> - [`architecture/invariants.md`](architecture/invariants.md) — numbered invariants (grows per milestone)
> - [`architecture/capability-inventory.md`](architecture/capability-inventory.md) — capability status table
> - [`runtime-constitution.md`](runtime-constitution.md) — Runtime Platform invariants C1–C8
> - [`runtime-contract.md`](runtime-contract.md) — onboarding + extension points (Frozen v1)
> - [`../knowledge/architecture/graph.md`](../knowledge/architecture/graph.md) — graph topology mirror
>
> M0 design spec remains the historical origin (`superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md`).

ThesisOS is a **single-user** research and thesis-writing AgentOS built on **ASEP**
(Adaptive Software Engineering Platform). As of M6 it delivers: streaming chat,
editable memory, document ingestion, hybrid retrieval, multi-agent orchestration
with conditional routing, grounded drafting, and a versioned chapter workspace.

---

## Architecture at a glance

End-to-end flow from client to persistence:

```text
Client (Next.js)
      │  HTTPS / SSE
      ▼
POST /chat ───────────────────────────── POST /chapters
      │                                        │
      ▼                                        ▼
ConversationService                    ChapterService (sole writer)
      │                                        │
      ▼                                        ▼
LangGraph build_graph()                chapters + chapter_versions
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATION PIPELINE (every turn)                        │
│                                                             │
│  Supervisor → Planner → Router → memory_context_node        │
│       │          │         │                                │
│       │          │         └── route_after_router           │
│       │          │                  │                         │
│       │          │     ┌────────────┼────────────┐           │
│       │          │     ▼            ▼            ▼           │
│       │          │ conversation  grounded_chat   writer      │
│       │          │     │            │            │           │
│       │          │     │            ▼            ▼           │
│       │          │     │       retriever     retriever       │
│       │          │     │            │            │           │
│       │          │     ▼            ▼            ▼           │
│       │          │ conversation  conversation   writer_node  │
│       │          │     │            │            │           │
│       │          │     └────────────┴────────────┘           │
│       │          │                  │                         │
│       ▼          ▼                  ▼                         │
│   plan/route   TaskService    DraftResult / messages         │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
                    Runtime Event Bus → subscribers
                    (agent_steps, structured logging)
                                │
                                ▼
                    Postgres + pgvector · Vertex AI (Gemini + embeddings)
```

**Key separation:** graph nodes produce ephemeral results (`DraftResult`, assistant
messages). Durable chapter content is written only through `ChapterService`.

---

## 1. System stack

```text
Next.js (App Router, Tailwind, Zustand)         Chat + Workspace UI
        │  HTTPS / SSE
        ▼
FastAPI (backend, Python, single user, no auth)
        ▼
LangGraph Orchestrator                          Supervisor → Planner → Router → agents
        ▼
Services (Business layer)                       memory · retrieval · document ·
                                                  task · chapter · conversation
        ▼
Runtime layer                                   Event Bus · instrumentation · lifecycle
        ▼
LLM abstraction (LiteLLM → Vertex AI)           generate() · embed() · vision()
        ▼
Postgres + pgvector · Cloud Storage · Secret Manager · Cloud Logging/OTel
```

Cursor agents sit **outside** this runtime — build-time only (ADR-0002).

---

## 2. ASEP taxonomy

**ASEP** is the whole ecosystem (ADR-0026). ThesisOS Product Plane is one
instance; the **Runtime Platform** (M5) is an ASEP subsystem:

```text
ASEP
├── Governance ............... Constitution, ADRs, promotion gates
├── Runtime Platform ......... Event Bus, contracts, lifecycle, observability (M5)
├── Product capabilities ..... memory, retrieval, writing, … (M2–M6)
└── Engineering Runtime ...... builder_engine/ (build-time; ADR-0023)
```

After M6, ASEP is evolving toward a **general agentic runtime** reusable beyond
ThesisOS (ResearchOS, LegalOS, …). A physical repo split (`asep/` vs `thesis-os/`)
is a medium-term goal (M10–M12 horizon), not current scope.

---

## 3. Core Runtime

### 3.1 Three layers (ADR-0030)

```text
Business   : graph nodes, orchestration/, services/{task,memory,retrieval,document,chapter}/
Runtime    : graph/conversation.py, routing.py, checkpointer.py, services/conversation/,
             runtime/* (events, event_bus, instrumentation, subscribers)
Infrastructure : db/, llm/, core/config.py
```

Dependencies flow **downward only** (Constitution C1). The composition root
(`build_graph()`, `ConversationService`) binds layers.

### 3.2 GraphState (frozen — ADR-0007)

Single Pydantic object threaded through LangGraph. **No field changes since M0.**

```python
class GraphState(BaseModel):
    messages: list[Message]
    plan: Plan | None = None
    route: str | None = None
    retrieved_context: list[RetrievedChunk] = []
    draft: str | None = None
    citations: list[CitationRef] = []
    memory_ops: list[MemoryOp] = []
    critique: Critique | None = None
    task: TaskRef | None = None
    errors: list[AgentError] = []
```

Full field ownership: [`../knowledge/contracts/graphstate.md`](../knowledge/contracts/graphstate.md).

### 3.3 RunContext (ADR-0014)

Execution metadata rides LangGraph `config.configurable.run_context` — **never**
GraphState. Includes `conversation_id`, `agent_run_id`, `trace_id`, `request_id`.

### 3.4 Checkpointer (ADR-0012)

`AsyncPostgresSaver` in schema `langgraph`. `thread_id = conversation_id`.
Checkpoint is derived working state; DB messages are system of record.

---

## 4. Orchestrated graph (M5 + M6)

Wired in `backend/app/graph/conversation.py::build_graph`.

### 4.1 Fixed pipeline (every turn)

```text
START → supervisor_node → planner_node → router_node → memory_context_node
```

### 4.2 Conditional routes (`route_after_router`)

| Route | After router | After retriever | Terminal |
|-------|--------------|-----------------|----------|
| `conversation` | `conversation_node` | — | END |
| `grounded_chat` | `retriever_node` | `conversation_node` | END |
| `writer` | `retriever_node` | `writer_node` | END |

```text
memory_context_node
        │
        ▼
 route_after_router(state.route)
        │
        ├─ conversation ──────► conversation_node ──► END
        │
        ├─ grounded_chat ─────► retriever_node ──► route_after_retriever ──► conversation_node ──► END
        │
        └─ writer ────────────► retriever_node ──► route_after_retriever ──► writer_node ──► END
```

M5 conversation and grounded_chat paths are **byte-for-byte unchanged** since M6
(Constitution C6). Route vocabulary is additive (ADR-0027).

### 4.3 Node I/O summary

| Node | Reads | Writes (GraphState) |
|------|-------|---------------------|
| `supervisor_node` | `messages` | `plan`, `route` |
| `planner_node` | `messages`, `plan` | `plan`, `task` |
| `router_node` | `messages`, `plan`, `route` | `route` (normalized) |
| `memory_context_node` | `messages`, thread config | transient prefix on `messages` |
| `retriever_node` | last user message | `retrieved_context` |
| `conversation_node` | `messages`, `retrieved_context` | `messages`, `draft`, `citations` |
| `writer_node` | `messages`, `retrieved_context`, `plan`, `task` | `draft`, `citations`, `errors` |

**Grounding rule (ADR-0024):** chunk text enters the LLM only via
`retrieved_context` → prompt wire — never persisted in DB messages.

---

## 5. Tool Router & Planner

### Supervisor

Reads user intent, produces initial `plan` and suggested `route`.

### Planner

Refines `plan`, emits `TaskRef`. Persists task via **`PlannerTaskPersistHook`**
wired at composition root — planner does **not** import `TaskService` directly.

### Router

Normalizes route string to closed vocabulary (`conversation`, `grounded_chat`,
`writer`, …). Silent normalization (no error on unknown → fallback).

### TaskService

`upsert_from_task_ref` + `mark_done`. Tasks table mirrors planner output for the
AgentOS work loop.

---

## 6. Writer route & capability (M6)

The writer is a **port**, not a monolithic node (Constitution C8, ADR-0031):

```text
WriterCapability.write_grounded(brief: WriterBrief) → DraftResult
        │
        ▼
make_writer_node(writer, stream_writer_factory=…)  ← adapter
        │
        ▼
GraphState partial: { draft, citations, errors }   ← writer.json contract only
```

`DraftResult` fields:

| Field | GraphState | Stream / Event Bus |
|-------|------------|-------------------|
| `draft` | ✓ | ✓ |
| `citations` | ✓ | ✓ |
| `metadata` | — | ✓ |
| `reasoning` | — | ✓ |
| `metrics` | — | ✓ |

**Citation discipline:** `citations.source_id ⊆ retrieved_context` (no invented sources).

Default implementation: `LLMWriter` in `backend/app/graph/writer.py`. Swappable at
`build_graph()` without topology change.

---

## 7. Chapter store (M6)

`ChapterService` is the **sole writer** for chapters (ADR-0032, ADR-0033):

- Lifecycle: `draft` → `review` → `approved` → `published` (M6 wires draft/review)
- Versioning: append-only `chapter_versions` change stream
- `change_kind ∈ {WRITE, EDIT, PROMOTE, MERGE, RESTORE}`
- Optimistic lock: `expected_version` mismatch → HTTP 409

**REST:** `POST/GET/PATCH /chapters`, version history endpoints.
**UI:** `frontend/app/workspace/` — save/edit flow.
**Not in M6:** `/outline` (M8), auto-persist from graph, chapter embeddings.

---

## 8. Event flow (Runtime Platform — M5)

```text
Composition root / instrumentation wrappers
        │
        emit(RuntimeEvent)
        ▼
RuntimeEventBus (fan-out, registration order)
        │
        ├── AgentStepsSubscriber → agent_steps table
        └── LoggingSubscriber → structured logs
```

- **7-event vocabulary** in `backend/app/runtime/events.py`
- Business nodes **never emit** (ADR-0030 R8)
- Subscriber failure is **non-blocking** (R6)
- Zero subscribers = valid silent runtime (C4)

Lifecycle events: `RunStarted`, `RunCompleted`, node `NodeStarted`/`NodeCompleted`/`NodeFailed`, route events.

Onboarding detail: [`runtime-contract.md`](runtime-contract.md).

---

## 9. Data model (summary)

Postgres + pgvector. Canonical schema: [`../contracts/db/schema.sql`](../contracts/db/schema.sql).

| Domain | Key tables | Milestone |
|--------|------------|-----------|
| Documents | `documents`, `chunks`, `embeddings` | M3/M4 |
| Memory | `memories` | M2 |
| Chat | `conversations`, `messages` | M1 |
| Orchestration | `tasks`, `agent_runs`, `agent_steps` | M5 |
| Writing | `chapters`, `chapter_versions` | M6 |
| Sources (deferred) | `sources`, `citations` | M7 |
| Events | `events` (outbox) | M0+ |

Embeddings are model-agnostic (polymorphic owner: `chunk|note|memory|chapter`).

---

## 10. External seams

| Seam | Contract | Status |
|------|----------|--------|
| `POST /chat` | SSE streaming, M1 shape | Frozen |
| `POST /chapters` | OpenAPI + ChapterService | M6 stable |
| `/citations`, `/bibliography` | OpenAPI deferred | M7 planned |
| `/outline` | OpenAPI deferred | M8 planned |

---

## 11. Repository map

```text
backend/app/
  api/              FastAPI routers (/chat, /chapters, /memory, …)
  graph/            LangGraph nodes, routing, orchestration helpers
  runtime/          Event Bus, events, instrumentation, subscribers
  services/         Business services (chapter, task, memory, retrieval, …)
  schemas/          GraphState, DraftResult, chapter DTOs
contracts/          OpenAPI, agent JSON contracts, schema.sql, events.json
docs/
  architecture.md           ← this file
  architecture/invariants.md
  architecture/capability-inventory.md
  runtime-constitution.md
  runtime-contract.md
decisions/          ADRs
.asep/              ASEP milestone-runner (capability graph, pipeline)
builder_engine/     Engineering Runtime (isolated from backend.app)
frontend/           Next.js UI (chat, workspace, library, memory, …)
knowledge/          Human mirrors (agents, contracts, roadmap)
```

---

## 12. Promotion baselines & tags

| Milestone | Qualified tag | Main tag | Notes |
|-----------|---------------|----------|-------|
| M4 Retrieval | `m4-complete` | — | Pipeline frozen (`docs/m4-freeze.md`) |
| M5 Runtime Platform | `m5-complete` @ `bf12c13` | — | `runtime-contract.md` Frozen v1 |
| M6 Writing Workspace | `m6-complete` @ `79fb52a` | `m6-main` @ `79fb52a` | Tags immutable; same SHA after FF merge |

Promotion docs: [`m5-promotion.md`](m5-promotion.md), [`m6-promotion.md`](m6-promotion.md).

---

## 13. ADR index (M0–M6 active set)

| ADR | Topic |
|-----|-------|
| 0001 | Contract first |
| 0002 | Vertex runtime only |
| 0007 | GraphState frozen |
| 0011–0014 | Conversation seam, checkpointer, RunContext |
| 0024 | Grounding wire |
| 0027 | Multi-agent graph topology |
| 0030 | Layer boundaries + Event Bus model |
| 0031 | Writer capability & drafting topology |
| 0032 | Chapter ownership & query model |
| 0033 | Chapter versioning as change stream |

Full list under `decisions/`. Per-PR gate: [`architecture-decision-checklist.md`](architecture-decision-checklist.md).

---

## 14. What's next

**M7 — Grounding Engine** (design phase): provenance, evidence, confidence,
validation hooks, and bibliography — citations as one output of a general
traceability system, not a standalone formatter milestone.

See [`../knowledge/project/roadmap.md`](../knowledge/project/roadmap.md).
