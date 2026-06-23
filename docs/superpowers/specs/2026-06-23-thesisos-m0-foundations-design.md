# ThesisOS — M0 "Foundations" Design Spec

- **Date:** 2026-06-23
- **Status:** Frozen by Architect (changes applied; proceeding to writing-plans)
- **Scope:** Milestone M0 only (architecture, contracts, scaffolding, infra). NO feature code.
- **Authors:** CEO/Architect session

---

## 1. Context & Goal

ThesisOS is a single-user research and thesis-writing AgentOS: chat, long-term editable
memory, document ingestion (PDF/EPUB/DOCX), Retrieval-Augmented Generation, citation
management, outline/chapter management, and multi-agent orchestration — built to run on
Google Cloud from day one and to evolve, milestone by milestone, into a self-improving
research assistant.

This document specifies **M0 (Foundations)** only. M0 establishes the architecture,
contracts, repository skeleton, and infrastructure so that every later milestone (M1–M18)
adds one vertical slice against stable contracts. **M0 contains no product feature code.**

The build is driven by Cursor agents (the "builder"). The runtime LLM is a separate concern
(see ADR-0002).

---

## 2. Scope — What M0 IS and IS NOT

**M0 IS (deliverables):**

- System architecture document (`docs/architecture.md`)
- API contracts (OpenAPI) + JSON I/O contracts for every agent
- Database schema + initial migrations (no data flows yet)
- Shared `GraphState` Pydantic contract
- Repository skeleton (backend, frontend, infra) with empty-but-declared modules
- `docker-compose.yml` for dev/prod parity (Postgres+pgvector, backend, frontend)
- Terraform that provisions GCP (Cloud Run, Cloud SQL, Buckets, Secret Manager, Artifact Registry)
- A deployable shell exposing only `GET /health`, `GET /ready`, `GET /metrics`
- ADR-0001 → ADR-0010 documented and frozen

**M0 IS NOT (forbidden in this milestone):**

- Chat implementation
- LangGraph runtime
- RAG / retrieval
- Ingestion
- Memory engine
- UI components / feature pages logic
- Any agent implementation
- Any product feature whatsoever

If it produces a user-visible feature, it does not belong in M0.

---

## 3. Foundational Decisions (locked)

| Topic | Choice |
|-------|--------|
| Usage model | **Single-user**, no auth, no multi-tenancy |
| Deployment | **GCP day-1**: Cloud Run + Cloud SQL (db-f1-micro) + Secret Manager + Storage + Artifact Registry |
| Runtime LLM | **Vertex AI** single-vendor: Gemini (generate + vision) + `text-multilingual-embedding-002` (embed) |
| Builder | **Cursor API / Cursor agents** — build-time only, not a runtime dependency |
| Tooling | **Python everywhere** in backend/orchestrator/agents/retrieval; **Next.js (TS)** only in frontend |
| Embeddings storage | **Model/dimension-tagged** rows → provider-swappable without painful migrations |
| Primary use | A **real thesis** (Italian) → prioritize a usable M0–M6 pipeline |

---

## 4. Architecture Overview

```text
Next.js (App Router, Tailwind, Zustand)         frontend, ChatGPT-style UI
        │  HTTPS / SSE
        ▼
FastAPI (backend, Python, no auth — single user) API contracts
        ▼
LangGraph Orchestrator (designed in M0,          Supervisor→Planner→Router→{agents}
  wired in later milestones)
        ▼
Services: ingestion · retrieval · memory ·       business logic (Python)
  citation · events · jobs · telemetry
        ▼
LLM abstraction (LiteLLM): generate/embed/vision provider-swappable
        ▼
Vertex AI: Gemini + multilingual-embedding       single runtime vendor
        ▼
Postgres + pgvector (Cloud SQL) · Cloud Storage · Secret Manager · Cloud Logging/OTel
```

Cursor agents sit **outside** this runtime: they are the team that builds ThesisOS.

---

## 5. Repository Structure (monorepo; workspace root = project root)

```text
docs/
  architecture.md
  superpowers/specs/                 # this spec lives here
contracts/
  openapi/openapi.yaml               # REST contract (curated)
  agents/                            # per-agent I/O contracts
    supervisor.json  planner.json  router.json
    retriever.json   writer.json    critic.json
    citation.json    memory.json    document.json
  db/schema.sql                      # canonical schema snapshot
  events/events.json                 # event catalog
decisions/
  ADR-0001-contract-first.md         ADR-0002-vertex-runtime-only.md
  ADR-0003-custom-memory.md          ADR-0004-cloud-day-one.md
  ADR-0005-python-backend.md         ADR-0006-event-driven.md
  ADR-0007-state-contract.md         ADR-0008-dev-equals-prod.md
  ADR-0009-async-jobs.md             ADR-0010-promotion-gates.md
backend/                             # Python only
  app/
    api/            # FastAPI routers (health/ready/metrics + jobs stub in M0)
    core/           # config, settings, logging bootstrap
    llm/            # LiteLLM→Vertex abstraction: generate() / embed() / vision()
    schemas/        # Pydantic models incl. GraphState
    db/             # SQLAlchemy models, Alembic migrations, session
    agents/         # graph definition + node stubs (contracts only in M0)
    services/
      events/       # in-process event bus (functions now; Pub/Sub later)
      jobs/         # background job interface (worker stub; Cloud Run Jobs/Tasks later)
      telemetry/    # OpenTelemetry + structured logs + traces
      ingestion/    # docling / marker / pymupdf / ocr   (stubs in M0)
      retrieval/    # rag / hybrid search                (stubs in M0)
      memory/       # user/thesis/concept/citation/decision/editable (stubs in M0)
      citation/     # CSL-JSON → APA7/MLA/Chicago          (stubs in M0)
  tests/
  pyproject.toml
frontend/
  app/
    chat/  workspace/  library/  memory/  outline/  settings/   # placeholder routes
  components/  lib/ (zustand store, api client)
  package.json
infra/
  terraform/        # cloud run, cloud sql, buckets, secret manager, artifact registry
  ci/               # build & deploy pipeline (Cloud Build or GitHub Actions)
docker/
  backend.Dockerfile  frontend.Dockerfile
docker-compose.yml  .env.example  README.md
```

---

## 6. LLM Abstraction (ADR-0002)

A thin module `backend/app/llm/` exposes three provider-agnostic functions, implemented via
LiteLLM and configured to Vertex AI:

```python
async def generate(messages, *, model=..., params=...) -> Completion
async def embed(texts: list[str], *, model=...) -> list[Vector]
async def vision(messages_with_images, *, model=...) -> Completion
```

- Generation/vision → Gemini on Vertex (multimodal covers `vision()` with the same vendor).
- Embeddings → `text-multilingual-embedding-002` (strong Italian support). Dimension is
  recorded per row (see §7), not hardcoded, so the model can be swapped.
- Single credential: a GCP **service account** (Vertex AI User) — no separate API keys.
- Provider is swappable later by reconfiguring LiteLLM; callers never know the provider.

---

## 7. Data Model (Postgres + pgvector)

Single source of truth. Embeddings live in a **dedicated, model-agnostic table** with a
polymorphic owner so chunks, notes, memories, and chapters can each carry embeddings, and the
embedding provider/dimension can change without a painful migration.

```text
documents(id, title, author, source_type[pdf|epub|docx], original_filename,
          gcs_uri, status[uploaded|parsing|parsed|indexed|error],
          page_count, language, metadata jsonb, created_at, updated_at)

chunks(id, document_id→documents, chunk_index, content, token_count,
       page_from, page_to, section_path, metadata jsonb, created_at)
       -- no embedding column; embeddings live in `embeddings`

embeddings(id, owner_type[chunk|note|memory|chapter], owner_id,
           model, dimension, embedding vector, metadata jsonb,
           content_hash, created_at)
           -- model + dimension tagged → swap Vertex/OpenAI/Voyage/Jina freely
           -- index strategy: see §19 (pgvector indexes need a fixed dim → partition by model)

sources(id, document_id→documents NULL, type[book|article|website|…],
        csl_json jsonb,   -- canonical CSL-JSON (drives APA7/MLA/Chicago)
        title, authors jsonb, year, doi, url, created_at)

citations(id, source_id→sources, chapter_id→chapters NULL,
          locator, prefix, suffix, created_at)

chapters(id, parent_id→chapters NULL,   -- self-FK for sections/subsections
         order_index, title, status[planned|drafting|draft|revised|final],
         content_md, summary, word_count, created_at, updated_at)

notes(id, document_id→documents NULL, chapter_id→chapters NULL,
      kind[note|highlight], content, anchor jsonb, created_at)

memories(id, kind[user|thesis|concept|citation|decision|editable],
         key, content, pinned bool, source[user|system|agent],
         version int, metadata jsonb, created_at, updated_at)
         -- editable "Notion page" = memories(kind=editable); versioned

conversations(id, title, created_at)
messages(id, conversation_id→conversations, role, content,
         tool_calls jsonb, created_at)

tasks(id, parent_task_id→tasks NULL, title, description,
      status[pending|in_progress|blocked|done|cancelled],
      owner_agent, priority int, payload jsonb, created_at, updated_at)
      -- drives the AgentOS loop

events(id, type, payload jsonb, source, correlation_id,
       occurred_at, created_at)
       -- persisted event log / outbox; producers/consumers wired later

agent_runs(id, conversation_id→conversations NULL, graph, trigger,
           input jsonb, output jsonb, status, error, started_at, finished_at)

agent_steps(id, agent_run_id→agent_runs, agent,
            phase[observe|hypothesis|plan|implement|test|critic|qa|revise|promote],
            input jsonb, output jsonb, status, started_at, finished_at)

checkpoints  -- RESERVED for LangGraph Postgres checkpointer
             -- (langgraph-checkpoint-postgres). Schema managed by the library;
             -- created when orchestration is wired (not M0).
```

Migrations: Alembic. M0 ships the initial migration that creates all tables + the pgvector
extension. No rows are written by any feature in M0. The LangGraph checkpoint tables are
created by the library's setup, reserved here so the contract is acknowledged.

---

## 8. Memory Model (ADR-0003) — custom, no Mem0 in core

Six memory kinds, all in `memories` with a `kind` discriminator, all manually editable and
versioned:

- **user** — preferences, language, style
- **thesis** — title, scope, outline summary
- **concept** — authors, theories, definitions
- **citation** — sources, pages, DOI (pointers into `sources`)
- **decision** — choices made during the work
- **editable** — the Notion-like page always injected into the system prompt
  (e.g. *"Use APA7. Do not cite Wikipedia. Academic register."*)

Mem0-style automatic extraction is explicitly deferred to M15–M16.

---

## 9. API Contracts (FastAPI / OpenAPI)

Defined as contracts in M0; only `health`/`ready`/`metrics` are implemented.

```text
GET  /health        # liveness
GET  /ready          # readiness (db reachable, config present)
GET  /metrics        # Prometheus/OpenMetrics
POST /jobs           # enqueue a background job        (contract M0, impl later)
GET  /jobs/{id}      # job status                        (contract M0, impl later)
POST /chat           # SSE stream                        (impl M1)
POST /upload         # document → ingestion job          (impl M3)
GET  /documents      GET /documents/{id}                 (impl M3)
POST /search         # hybrid retrieval                  (impl M4)
POST /summarize                                          (impl M3/M6)
GET|PUT  /outline    POST|PATCH /chapters               (impl M8/M6)
GET|POST|PATCH|DELETE /memory                            (impl M2)
POST /citations      GET /bibliography?style=apa7        (impl M7)
```

---

## 10. Agent Hierarchy & GraphState (ADR-0007)

```text
Supervisor → Planner → Router → { Retriever · Writer · Critic · Citation · Memory · Document }
```

The **Document Agent** contract exists in M0 though it is implemented in M3.

Shared Pydantic state, the single object passed through the graph:

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

Each `contracts/agents/<name>.json` declares **input**, **output**, **errors**, and
**state mutations** (which `GraphState` fields the node reads/writes). No node logic in M0.

---

## 11. Event Bus (ADR-0006)

`services/events/` defines a typed event catalog and an in-process dispatcher
(simple functions now, swappable to Cloud Pub/Sub later); events are persisted to the
`events` table (outbox). Catalog (`contracts/events/events.json`):

```text
DocumentUploaded · ChunkCreated · MemoryUpdated · ChapterCreated · CritiqueCompleted
```

M0 ships the interface, the catalog, and the `events` table; no producers/consumers are wired.

---

## 12. Background Jobs (ADR-0009)

`services/jobs/` defines a job interface so heavy work (ingestion, embedding, OCR,
summarize) never runs in the FastAPI request path. M0 ships the interface, the
`POST /jobs` + `GET /jobs/{id}` contracts, and a no-op worker stub. Production target:
Cloud Run Jobs / Cloud Tasks. Local: same interface backed by an in-process worker.

---

## 13. Observability

`services/telemetry/` bootstraps OpenTelemetry (traces + metrics) and structured JSON logging
from day one, exporting to Cloud Logging/Trace in prod and console locally, and backs the
`GET /metrics` endpoint. Wired into the FastAPI app and the LLM abstraction so that, once
agents arrive, every run/step is traced. (Operational standard; supports the M0→M1
promotion gates in ADR-0010.)

> **M0 reality:** M0 ships the FastAPI instrumentation hook + structured JSON logging +
> a `prometheus_client`-backed `/metrics`. The `TracerProvider` + Cloud Trace/Logging
> exporter (and tracing of the LLM abstraction) land in M1/M11.

---

## 14. Infrastructure (ADR-0004 Cloud Day One, ADR-0008 Dev = Prod) — Terraform

**Local (`docker-compose.yml`)** — identical container images to prod:

- `pgvector/pgvector:pg16` (Postgres + pgvector)
- backend (FastAPI, Python)
- frontend (Next.js)
- Vertex access via Application Default Credentials.

**GCP via Terraform (`infra/terraform/`):**

- Enable APIs: run, sqladmin, secretmanager, storage, artifactregistry, aiplatform
- **Artifact Registry** (Docker repo)
- **Cloud SQL** Postgres **`db-f1-micro`** (minimal tier; do not optimize yet) + database + `pgvector` extension
- **Secret Manager** (Vertex SA / config secrets)
- **Cloud Storage** buckets: `documents`, `exports`, `temp`, `logs`
- **Cloud Run** services: `backend`, `frontend`
- Service account for Cloud Run: Vertex AI User + Cloud SQL Client + Storage access
- CI/CD pipeline (`infra/ci/`) building images → Artifact Registry → deploying Cloud Run

**Cost note:** `db-f1-micro` is the cheapest shared-core tier. (Cheaper single-VM `e2-small`
+ docker-compose remains a documented fallback, not chosen.)

---

## 15. ADR Index (frozen)

- **ADR-0001 Contract First** — architecture + contracts before any product code
- **ADR-0002 Vertex Runtime Only** — Gemini (generate/vision) + multilingual embeddings via LiteLLM; Cursor API is build-time only; embeddings model/dimension-tagged for swap
- **ADR-0003 Custom Memory** — Postgres+pgvector memory layer; no Mem0 in core (defer M15–M16)
- **ADR-0004 Cloud Day One** — GCP from the start (Cloud Run, Cloud SQL, Storage, Secret Manager, Artifact Registry)
- **ADR-0005 Python Backend** — Python everywhere server-side (backend, orchestrator, agents, retrieval); TS only in the Next.js frontend
- **ADR-0006 Event Driven** — typed event catalog + in-process bus + `events` outbox; Pub/Sub-pluggable later
- **ADR-0007 State Contract** — shared Pydantic `GraphState` is the single graph state object
- **ADR-0008 Dev = Prod** — dev/prod parity via identical containers (docker-compose ≈ Cloud Run)
- **ADR-0009 Async Jobs** — heavy work out of the request path; worker stub now, Cloud Run Jobs/Tasks later
- **ADR-0010 Promotion Gates** — explicit, machine-checkable criteria gate each milestone transition

---

## 16. M0 Deliverables & Strict Build Order

**Build order (strict — no step starts before the previous is done):**

```text
1. docs/architecture.md
2. contracts/      (openapi + agents/*.json + events.json)
3. decisions/      (ADR-0001 … ADR-0010)
4. DB schema       (contracts/db/schema.sql + Alembic initial migration)
5. infra/terraform/
6. docker-compose.yml + docker/
7. CI/CD           (infra/ci/)
8. /health (+/ready +/metrics) shell deployed
9. Promote M0
```

**Deliverable checklist:**

- [ ] `docs/architecture.md`
- [ ] `contracts/openapi/openapi.yaml`, `contracts/db/schema.sql`, `contracts/agents/*.json`, `contracts/events/events.json`
- [ ] `decisions/ADR-0001 … ADR-0010` (frozen)
- [ ] `backend/` skeleton: api (health/ready/metrics + jobs stub), core, llm, schemas (incl. GraphState), db (models + initial Alembic migration), agents (stubs), services/{events,jobs,telemetry,ingestion,retrieval,memory,citation} (stubs)
- [ ] `frontend/` skeleton: app router with placeholder routes, api client, zustand store
- [ ] `docker-compose.yml` (Postgres+pgvector, backend, frontend) green locally
- [ ] `infra/terraform/` applies successfully on GCP
- [ ] CI/CD builds images → Artifact Registry → deploys Cloud Run
- [ ] `/health` green on Cloud Run; DB migrations applied on Cloud SQL

---

## 17. Promotion Criteria (M0 → M1) — ADR-0010

M1 must NOT start until ALL are true:

```yaml
architecture: approved
contracts: frozen
adr: complete
terraform_apply: success
docker_compose: green
cloud_run: deployed
health: green
db_migrations: green
zero_feature_debt: true
```

Forbidden until the gate passes: chat implementation, LangGraph runtime, RAG, ingestion,
memory engine, UI feature components.

---

## 18. Roadmap Alignment

M0 unblocks the vertical slices: **M1 chat → M2 memory → M3 ingestion → M4 retrieval →
M5 tool router → M6 writing**. **M0–M6 is already a usable product** for a real thesis.
Everything after (M7 citations, M8 outline, M9 critic, M10 QA, M11 GCP hardening,
M12 multi-agent, M13 research, M14 NotebookLM-like, M15–16 editable KB + Mem0,
M17 voice, M18 autonomous assistant) progressively turns ThesisOS into a self-improving
research AgentOS.

---

## 19. Open Questions / Risks

- **Embedding storage vs pgvector indexing:** the `embeddings` table is model/dimension-tagged
  for provider freedom, but pgvector requires a **fixed dimension to build an HNSW/IVFFlat
  index**. Strategy: index per active model via **table partitioning by `model`** (each
  partition fixed-dim + its own index); swapping models = add a partition + re-embed, not a
  destructive migration. Decide partition-vs-single-index detail in M2/M4 when retrieval is built.
- **Cursor API as runtime generator** was rejected for runtime (agent/coding-oriented, no
  embeddings). Re-evaluate only if Vertex proves insufficient for Italian academic prose.
- **Cloud Run cold starts** for the backend are acceptable for single-user; revisit at M11.
- **Job durability:** in-process worker is fine for M0–M6; durable queue needed before M11.
- **`db-f1-micro` limits:** fine for M0 scaffolding; reassess instance size when ingestion
  and embeddings load arrive (M3/M4).
```
