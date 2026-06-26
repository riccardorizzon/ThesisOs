# ThesisOS — Architecture Overview

> Human-readable mirror of the frozen M0 design spec
> (`superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md`). This is an
> overview, not a re-derivation. The spec is the source of truth; if they ever
> disagree, the spec wins.

ThesisOS is a **single-user** research and thesis-writing AgentOS: chat,
long-term editable memory, document ingestion (PDF/EPUB/DOCX/**Markdown/Text**),
Retrieval-Augmented Generation, citation management, outline/chapter management,
and multi-agent orchestration — built to run on Google Cloud from day one.

This milestone, **M0 "Foundations,"** is *Contract First*: it establishes the
architecture, contracts, repository skeleton, and infrastructure so every later
milestone (M1–M18) adds one vertical slice against stable contracts. **M0
contains no product feature code.**

---

## 1. System Overview

The runtime is a linear stack from a Next.js frontend down to Vertex AI and
Postgres. The LangGraph orchestrator is *designed* in M0 and *wired* in later
milestones. The ASCII diagram below is reproduced verbatim from spec §4.

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

Cursor agents sit **outside** this runtime: they are the team that builds
ThesisOS (see §2).

---

## 2. Runtime vs Builder

ThesisOS draws a hard line between the system that *runs* and the team that
*builds* it (spec §1, §6; ADR-0002):

- **Runtime LLM = Vertex AI.** A single vendor serves generation and vision
  (Gemini, multimodal) and embeddings (`text-multilingual-embedding-002`, strong
  Italian support). The product talks only to Vertex through the LiteLLM
  abstraction.
- **Builder = Cursor agents (Cursor API).** These are build-time only — they
  write the code, contracts, and infra. They are **not** a runtime dependency:
  no deployed ThesisOS code path calls Cursor. Cursor-as-runtime-generator was
  evaluated and rejected (agent/coding-oriented, no embeddings).

This separation keeps the deployed system dependent on exactly one external LLM
vendor, swappable via configuration without touching callers.

---

## 3. Repository Map

Monorepo; the workspace root is the project root. Reproduced from spec §5.

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

## 4. Data Model Summary

Postgres + pgvector is the single source of truth (spec §7). The full canonical
schema lives at [`../contracts/db/schema.sql`](../contracts/db/schema.sql)
*(forward-looking — created in a later M0 task)*; Alembic ships the initial
migration that creates all tables plus the pgvector extension. No feature writes
rows in M0.

Core tables:

- **`documents`** — uploaded source files (PDF/EPUB/DOCX) with ingestion
  `status`, GCS URI, and metadata.
- **`chunks`** — ordered text segments of a document; carry no embedding column.
- **`embeddings`** — a dedicated, **model-agnostic** table with a polymorphic
  owner (`chunk|note|memory|chapter`). Each row tags its `model` and `dimension`
  so the embedding provider can be swapped without a painful migration.
- **`sources` / `citations`** — canonical CSL-JSON sources driving
  APA7/MLA/Chicago, plus per-chapter citation references with locators.
- **`chapters`** — self-referencing tree (sections/subsections) with status and
  Markdown content; **`notes`** — notes/highlights anchored to documents or
  chapters.
- **`memories`** — six-kind editable, versioned memory
  (`user|thesis|concept|citation|decision|editable`).
- **`conversations` / `messages`** — chat history.
- **`tasks`** — the AgentOS work loop (self-referencing, status, owner agent).
- **`events`** — persisted event log / outbox.
- **`agent_runs` / `agent_steps`** — orchestration run + step tracing.
- **`checkpoints`** — *reserved* for the LangGraph Postgres checkpointer; the
  library manages its schema when orchestration is wired (not M0).

---

## 5. LLM Abstraction

A thin module `backend/app/llm/` exposes three provider-agnostic async functions,
implemented via LiteLLM and configured to Vertex AI (spec §6, ADR-0002):

```python
async def generate(messages, *, model=..., params=...) -> Completion
async def embed(texts: list[str], *, model=...) -> list[Vector]
async def vision(messages_with_images, *, model=...) -> Completion
```

- **Generation / vision** → Gemini on Vertex (the same multimodal vendor covers
  `vision()`).
- **Embeddings** → `text-multilingual-embedding-002`. Dimension is recorded
  per row (see §4), never hardcoded.
- **Single credential** — a GCP **service account** (Vertex AI User); no
  separate API keys.
- **Provider-swap policy** — the provider is swappable later by reconfiguring
  LiteLLM; callers never know or depend on the underlying provider.

---

## 6. Agent Hierarchy & GraphState

The orchestration is a Supervisor-led hierarchy (spec §10, ADR-0007). Designed in
M0, wired later.

```text
Supervisor → Planner → Router → { Retriever · Writer · Critic · Citation · Memory · Document }
```

The **Document Agent** contract exists in M0 though it is implemented in M3.

A single shared Pydantic object, `GraphState`, is passed through the graph:

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

Each per-agent contract under [`../contracts/agents/`](../contracts/agents/)
*(forward-looking — created in a later M0 task)* declares **input**, **output**,
**errors**, and **state mutations** (which `GraphState` fields the node
reads/writes). No node logic exists in M0.

### 6.1 M4 runtime graph (implemented; recovery-hardened 2026-06-26)

As of M4 + recovery sprint, the **chat seam** is a linear graph (M5 will extend
this to Supervisor→Planner→Router):

```text
START → memory_context_node → retriever_node → conversation_node → END
```

| Node | Reads | Writes (GraphState) | Wire effect |
|------|-------|---------------------|-------------|
| `memory_context_node` | `messages`, thread config | prepends transient system prefix to `messages` | M2 memory in prompt |
| `retriever_node` | last user message | `retrieved_context` | — |
| `conversation_node` | `messages`, `retrieved_context` | `messages` (+ assistant), `draft`, `citations` | `compose_prompt_wire()` injects memory + grounding **transiently** |

**Grounding rule (ADR-0024):** chunk text enters the LLM only via
`retrieved_context` → `compose_prompt_wire()` — never persisted in DB messages.
The client receives reference metadata via SSE `sources` events.

**Ingestion → index path:**

```text
upload → parse (Docling primary / PyMuPDF PDF fallback / MarkdownParser for .md)
       → chunks → embed (batched Vertex calls) → status=indexed
```

See `docs/m4-freeze.md` — this pipeline is **frozen**; changes require reproducible
bugs + regression tests.

---

## 7. Event-Driven Design, Jobs & Telemetry

**Event bus (spec §11, ADR-0006).** `services/events/` defines a typed event
catalog and an in-process dispatcher (simple functions now, swappable to Cloud
Pub/Sub later); events are persisted to the `events` table as an outbox. Initial
catalog (`contracts/events/events.json`):

```text
DocumentUploaded · ChunkCreated · MemoryUpdated · ChapterCreated · CritiqueCompleted
```

M0 ships the interface, the catalog, and the `events` table — no producers or
consumers are wired.

**Background jobs (spec §12, ADR-0009).** `services/jobs/` defines a job
interface so heavy work (ingestion, embedding, OCR, summarize) never runs in the
FastAPI request path. M0 ships the interface, the `POST /jobs` + `GET /jobs/{id}`
contracts, and a no-op worker stub. Production target: Cloud Run Jobs / Cloud
Tasks; locally the same interface is backed by an in-process worker.

**Observability (spec §13).** In M0, `services/telemetry/` installs the
OpenTelemetry FastAPI **instrumentation hook** (`FastAPIInstrumentor.instrument_app`)
and `core/logging.py` configures structured JSON logging; `GET /metrics` is served
by `prometheus_client`. A full `TracerProvider` + exporter to Cloud Trace/Logging
(and tracing of the LLM abstraction) is wired in **M1/M11**, not M0 — so that, once agents arrive,
every run/step is traced.

---

## 8. Infrastructure Topology

GCP from day one with dev/prod parity (spec §14; ADR-0004 Cloud Day One,
ADR-0008 Dev = Prod). Provisioned via Terraform (`infra/terraform/`).

**GCP resources:**

- **APIs enabled:** run, sqladmin, secretmanager, storage, artifactregistry,
  aiplatform.
- **Artifact Registry** — Docker image repository.
- **Cloud SQL** — Postgres on **`db-f1-micro`** (cheapest shared-core tier; not
  optimized yet) + database + `pgvector` extension.
- **Secret Manager** — Vertex service-account / config secrets.
- **Cloud Storage** — buckets `documents`, `exports`, `temp`, `logs`.
- **Cloud Run** — services `backend` and `frontend`.
- **Service account** for Cloud Run: Vertex AI User + Cloud SQL Client + Storage
  access.
- **CI/CD** (`infra/ci/`) — build images → Artifact Registry → deploy Cloud Run.

**Dev/prod parity.** `docker-compose.yml` runs the *same* container images as
prod: `pgvector/pgvector:pg16`, the FastAPI backend, and the Next.js frontend,
with Vertex access via Application Default Credentials. A cheaper single-VM
`e2-small` + docker-compose path remains a documented fallback, not chosen.

---

## 9. ADR Index

The ten architecture decisions are frozen in M0 (spec §15). Each links to its
record under `decisions/` *(forward-looking — the ADR files are created in a
later M0 task)*.

| ADR | Title | Record |
|-----|-------|--------|
| ADR-0001 | Contract First — architecture + contracts before any product code | [`../decisions/ADR-0001-contract-first.md`](../decisions/ADR-0001-contract-first.md) |
| ADR-0002 | Vertex Runtime Only — Gemini + multilingual embeddings via LiteLLM; Cursor build-time only | [`../decisions/ADR-0002-vertex-runtime-only.md`](../decisions/ADR-0002-vertex-runtime-only.md) |
| ADR-0003 | Custom Memory — Postgres+pgvector memory layer; no Mem0 in core (defer M15–M16) | [`../decisions/ADR-0003-custom-memory.md`](../decisions/ADR-0003-custom-memory.md) |
| ADR-0004 | Cloud Day One — GCP from the start (Cloud Run, Cloud SQL, Storage, Secret Manager, Artifact Registry) | [`../decisions/ADR-0004-cloud-day-one.md`](../decisions/ADR-0004-cloud-day-one.md) |
| ADR-0005 | Python Backend — Python everywhere server-side; TS only in the Next.js frontend | [`../decisions/ADR-0005-python-backend.md`](../decisions/ADR-0005-python-backend.md) |
| ADR-0006 | Event Driven — typed event catalog + in-process bus + `events` outbox; Pub/Sub-pluggable later | [`../decisions/ADR-0006-event-driven.md`](../decisions/ADR-0006-event-driven.md) |
| ADR-0007 | State Contract — shared Pydantic `GraphState` is the single graph state object | [`../decisions/ADR-0007-state-contract.md`](../decisions/ADR-0007-state-contract.md) |
| ADR-0008 | Dev = Prod — dev/prod parity via identical containers (docker-compose ≈ Cloud Run) | [`../decisions/ADR-0008-dev-equals-prod.md`](../decisions/ADR-0008-dev-equals-prod.md) |
| ADR-0009 | Async Jobs — heavy work out of the request path; worker stub now, Cloud Run Jobs/Tasks later | [`../decisions/ADR-0009-async-jobs.md`](../decisions/ADR-0009-async-jobs.md) |
| ADR-0010 | Promotion Gates — explicit, machine-checkable criteria gate each milestone transition | [`../decisions/ADR-0010-promotion-gates.md`](../decisions/ADR-0010-promotion-gates.md) |
