# Project Memory

> The durable, load-bearing model of ThesisOS. Read this first after `context/current-state.md`. Sources span the whole repo (specs, ADRs, contracts, code, gates). This is a consolidation; sources cited inline.

---

## 1. Current architecture (one screen)

Single-user research/thesis AgentOS on GCP. Runtime stack:

```text
Next.js (App Router, Tailwind, Zustand)  →  FastAPI (no auth, single user)
  →  LangGraph (StateGraph[GraphState]; M2 = memory_context_node + conversation_node)
  →  Services (conversation live; memory live M2 Ph1-4; events/jobs/telemetry/ingestion/retrieval/citation stubs)
  →  LiteLLM seam (generate/astream/embed/vision)  →  Vertex AI (Gemini + multilingual embeddings)
  →  Postgres + pgvector (Cloud SQL) · Cloud Storage · Secret Manager · OTel
```

- **Chat path (M1, live):** `POST /chat` (SSE) → `ConversationService` →
  `graph.astream(stream_mode="custom")` → `memory_context_node` → `conversation_node` → `LiteLLMClient.astream`
  → Vertex; tokens rise back as SSE `event: token`. Persistence on
  `conversations`/`messages` (system of record); checkpoints in the `langgraph`
  schema; token accounting on `agent_runs`.
- **Memory path (M2, branch `m2-memory-system`):** Admin UI / REST →
  `MemoryService` (sole writer) → `memories` + `memory_versions`.
  `load_prompt_context()` → `PromptContext` (operational kinds only) →
  `memory_context_node` prepends transient system wire each turn.
- **Builder side:** Cursor agents (build-time only) using the AgentOS loop +
  orchestrate-builders waves. Never a runtime dependency.

Details: `architecture/*`. Prod: project `thesisos-prod`, region `europe-west1`,
model `gemini-2.5-pro`.

---

## 2. Frozen contracts (do not change without a new ADR)

| Contract | Where | Note |
|----------|-------|------|
| **`GraphState`** | `backend/app/schemas/graph_state.py` | 10 fields; M1 added nothing (ADR-0007) |
| **Domain DB schema** | `contracts/db/schema.sql`, `app/db/models.py` | 15 domain tables (+ `memory_versions` M2); drift-tested |
| **OpenAPI** | `contracts/openapi/openapi.yaml` | additive only; `x-milestone` stubs |
| **Agent I/O contracts (9)** | `contracts/agents/*.json` | reads/writes/errors/mutations per agent |
| **Event catalog (5)** | `contracts/events/events.json` | DocumentUploaded, ChunkCreated, MemoryUpdated, ChapterCreated, CritiqueCompleted |
| **`TokenChunk`** | `app/llm/base.py` | exactly 3 fields (ADR-0011) |
| **`RunContext`** | `app/schemas/run_context.py` | runtime-only, never in GraphState/checkpoint (ADR-0014) |
| **ADR-0001..0018** | `decisions/` | append-only; none superseded |

External (non-domain) infra: `langgraph` schema checkpoint tables, owned by
`AsyncPostgresSaver`, excluded from domain governance (ADR-0012).

---

## 3. ADR summary (18)

Architectural: 0001 Contract-First · 0004 Cloud-Day-One · 0005 Python-Backend ·
0006 Event-Driven · 0007 State-Contract · 0008 Dev=Prod · 0009 Async-Jobs ·
0010 Promotion-Gates · 0012 External-Infra-Schemas · 0014 RunContext-Separation ·
0015 Memory-Ownership · 0017 Memory-Versioning · 0018 Memory-Query-Model.
Technical: 0002 Vertex-Runtime-Only · 0003 Custom-Memory · 0011 Streaming-First-LLM ·
0013 Runtime-Config-Minimalism.

---

## 4. Milestone status

- **M0 Foundations — ✅ complete & promoted** (`m0-complete`). Deployed on
  `thesisos-prod`; gate fully green.
- **M1 Conversation System — ✅ promoted** (`m1-complete` on `main`).
- **M2 Memory — ✅ promoted** (`m2-complete` on `main`).
- **M3 Documents — 🟡 spec frozen + plan** (branch `m3-document-system`): ADR-0020/0021/0022. Implementation not started.
- **M4–M18 ⬜** — require frozen specs before implementation.

---

## 5. Known technical debt

1. **Token usage not captured** — `agent_runs.output = {}`; Vertex streaming needs
   `stream_options={"include_usage": True}`. Accounting fidelity only. (M2)
2. **`ConversationService.stream_turn` untested end-to-end** — only the lock guard is
   unit-tested; the streaming path was validated via live smoke. (M2)
3. **Disconnect→`cancelled` finalize** — reasoned, not exercised in the smoke.
4. **Frontend prod API URL** — `NEXT_PUBLIC_API_BASE_URL` not a Docker `ARG`; prod
   frontend→backend wiring is an M1 follow-up.
5. **Cloud Build CI disabled** — org-policy PERMISSION_DENIED; buildx used instead.
6. **No pgvector index yet** — deferred to **M4** (Q1; M2 explicitly forbids embeddings).
7. **Terraform state holds the DB password** — local-only + gitignored; encrypt if a
   remote backend is ever added.

---

## 6. Important constraints (non-negotiable)

- **Single-user, no auth, no multi-tenancy** (ADR-0001). No `users`/`accounts` table.
- **Runtime LLM = Vertex only, behind LiteLLM** (ADR-0002). One credential (ADC).
- **Python server-side; TS only frontend** (ADR-0005).
- **Postgres+pgvector = single source of truth**; `messages` = chat system of record.
- **`GraphState` frozen; `RunContext` separate; `TokenChunk` 3 fields.**
- **Embeddings model/dimension-tagged** (swap without painful migration).
- **GCP day-one, dev=prod, Terraform-provisioned**; Cloud Run private by default.
- **Contract-First + evidence-backed promotion gates.**
- **Zero feature debt** at a gate (only intentional stubs).
- **Italian thesis is the primary use case** (drives embedding model + UI copy).

---

## 7. Future planned work

- **Next:** **M3 Phase 1** (DB) after plan review → full M3 implementation per plan. **No embeddings/retrieval.**
- **M4–M6** (usable-product line): retrieval → tool router → writing.
- **M7–M11:** citations → outline → critic → QA → GCP hardening (tracing, durable
  jobs, instance sizing, cold starts).
- **M12–M18:** multi-agent → research → NotebookLM-like → editable KB + Mem0 → voice
  → autonomous assistant.
- **Cross-cutting scheduled:** pgvector index strategy (M2/M4), durable job queue
  (pre-M11), full tracing/exporters (M11), re-enable Cloud Build.

See `context/next-actions.md` for the prioritized 100-task backlog.
