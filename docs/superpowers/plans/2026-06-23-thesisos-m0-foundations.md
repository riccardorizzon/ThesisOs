# ThesisOS M0 "Foundations" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the ThesisOS skeleton, contracts, and GCP infrastructure (no product features) so that M1–M18 add vertical slices against frozen contracts.

**Architecture:** Python FastAPI backend + Next.js frontend in a monorepo; Postgres+pgvector (Cloud SQL `db-f1-micro`); LangGraph orchestration designed but not wired; runtime LLM via LiteLLM→Vertex (interface only in M0); GCP via Terraform with dev/prod parity through docker-compose.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, pytest; Next.js 15 (App Router) + Tailwind + Zustand; Postgres 16 + pgvector; Terraform; Docker; OpenTelemetry.

**Source spec:** `docs/superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md` (frozen).

**Global rules (ADR-0001 Contract First, ADR-0010 Promotion Gates):**
- FORBIDDEN in M0: chat, LangGraph runtime, RAG, ingestion, memory engine, UI feature logic, any agent implementation.
- ALLOWED: scaffolding, contracts, schemas, stubs that raise `NotImplementedError`, infra, `/health` `/ready` `/metrics`.
- Follow the strict build order; do not start a task before the prior one is committed.

**Note on "tests" for M0:** This milestone is mostly contracts/infra. Where there is real Python, write pytest tests. Where the deliverable is a doc/config, the "verification" step is a validator command (`terraform validate`, `docker compose config`, `alembic upgrade head`, `curl`). Both are first-class.

---

### Task 0: Repository bootstrap

**Files:**
- Create: `README.md`
- Create: `.env.example`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `frontend/package.json`

- [ ] **Step 1: Create `README.md`**

```markdown
# ThesisOS

Single-user research & thesis-writing AgentOS. Runtime LLM: Vertex AI (Gemini + multilingual
embeddings). Storage: Postgres + pgvector. Runs on GCP (Cloud Run + Cloud SQL).

## Status
M0 (Foundations): architecture, contracts, scaffolding, infra. No product features yet.

## Layout
- `backend/`  — FastAPI app (Python)
- `frontend/` — Next.js app
- `contracts/` — OpenAPI, agent I/O, DB schema, events
- `decisions/` — ADRs
- `infra/` — Terraform + CI/CD
- `docs/` — architecture + specs/plans

## Local dev
    cp .env.example .env
    docker compose up --build
    curl localhost:8000/health   # {"status":"ok"}
```

- [ ] **Step 2: Create `.env.example`**

```bash
# Backend
DATABASE_URL=postgresql+psycopg://thesisos:thesisos@db:5432/thesisos
APP_ENV=local
LOG_LEVEL=INFO

# Vertex (used from M1 onward; not called in M0)
GOOGLE_CLOUD_PROJECT=
VERTEX_LOCATION=europe-west1
GEMINI_MODEL=gemini-2.5-pro
EMBEDDING_MODEL=text-multilingual-embedding-002

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

- [ ] **Step 3: Create `backend/pyproject.toml`**

```toml
[project]
name = "thesisos-backend"
version = "0.0.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.34",
  "pydantic>=2.9",
  "pydantic-settings>=2.5",
  "sqlalchemy>=2.0",
  "psycopg[binary]>=3.2",
  "alembic>=1.13",
  "pgvector>=0.3",
  "prometheus-client>=0.21",
  "opentelemetry-sdk>=1.27",
  "opentelemetry-instrumentation-fastapi>=0.48b0",
  "structlog>=24.4",
]

[project.optional-dependencies]
dev = ["pytest>=8.3", "pytest-asyncio>=0.24", "httpx>=0.27", "ruff>=0.6", "mypy>=1.11"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 4: Create empty `backend/app/__init__.py`** (empty file)

- [ ] **Step 5: Create `frontend/package.json`**

```json
{
  "name": "thesisos-frontend",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start -p 3000"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "zustand": "^5.0.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "typescript": "^5.6.0",
    "@types/react": "^19.0.0",
    "@types/node": "^22.0.0"
  }
}
```

- [ ] **Step 6: Commit**

```bash
git add README.md .env.example backend/pyproject.toml backend/app/__init__.py frontend/package.json
git commit -m "chore(m0): repository bootstrap (backend/frontend manifests, env example)"
```

---

### Task 1: Architecture document

**Files:**
- Create: `docs/architecture.md`

- [ ] **Step 1: Write `docs/architecture.md`**

Document, with these sections (content drawn from the frozen spec §4–§14):
1. System overview + the ASCII diagram from spec §4.
2. Runtime vs builder distinction (Vertex runtime; Cursor agents build).
3. Repository map (spec §5).
4. Data model summary + link to `contracts/db/schema.sql`.
5. LLM abstraction (`generate/embed/vision`) and provider-swap policy.
6. Agent hierarchy + `GraphState` (link to `contracts/agents/`).
7. Event-driven design + jobs + telemetry.
8. Infrastructure topology (Cloud Run, Cloud SQL `db-f1-micro`, buckets, Secret Manager, Artifact Registry) and dev/prod parity.
9. ADR index table (link each to `decisions/ADR-000X-*.md`).

Keep it to one screen per section; this is the human-readable mirror of the spec.

- [ ] **Step 2: Verify links resolve**

Run: `rg -o 'decisions/ADR-00[0-9]+-[a-z-]+\.md' docs/architecture.md | sort -u`
Expected: lists ADR-0001 … ADR-0010 paths (files created in Task 2 — this check is re-run after Task 2).

- [ ] **Step 3: Commit**

```bash
git add docs/architecture.md
git commit -m "docs(m0): add architecture overview"
```

---

### Task 2: Architecture Decision Records (ADR-0001 … ADR-0010)

**Files (create all):**
- `decisions/ADR-0001-contract-first.md`
- `decisions/ADR-0002-vertex-runtime-only.md`
- `decisions/ADR-0003-custom-memory.md`
- `decisions/ADR-0004-cloud-day-one.md`
- `decisions/ADR-0005-python-backend.md`
- `decisions/ADR-0006-event-driven.md`
- `decisions/ADR-0007-state-contract.md`
- `decisions/ADR-0008-dev-equals-prod.md`
- `decisions/ADR-0009-async-jobs.md`
- `decisions/ADR-0010-promotion-gates.md`

- [ ] **Step 1: Use this ADR template for every file**

```markdown
# ADR-000X: <Title>

- Status: Accepted (frozen 2026-06-23)
- Context: <why this decision is needed>
- Decision: <what we decided>
- Consequences: <trade-offs, what it enables, what it forbids>
- Alternatives considered: <rejected options + why>
```

- [ ] **Step 2: Fill each ADR with this content**

- **0001 Contract First** — Decision: produce architecture, contracts, schemas before any product code; no feature code until M0 gate passes. Forbids: chat/RAG/ingestion/agents in M0.
- **0002 Vertex Runtime Only** — Decision: runtime LLM = Vertex AI Gemini (generate/vision) + `text-multilingual-embedding-002` (embed) behind LiteLLM; Cursor API is build-time only; embeddings are model/dimension-tagged for swap. Alternatives: Cursor-API-as-runtime (rejected: no embeddings, coding-oriented), multi-provider LiteLLM (deferred).
- **0003 Custom Memory** — Decision: memory layer on Postgres+pgvector with 6 editable, versioned kinds; no Mem0 in core (defer M15–M16). Rationale: structured + manually editable + versioned + doc references + full control.
- **0004 Cloud Day One** — Decision: GCP from the start: Cloud Run, Cloud SQL (`db-f1-micro`), Cloud Storage, Secret Manager, Artifact Registry, provisioned via Terraform.
- **0005 Python Backend** — Decision: Python everywhere server-side (backend, orchestrator, agents, retrieval); TypeScript only in the Next.js frontend.
- **0006 Event Driven** — Decision: typed event catalog + in-process dispatcher + `events` outbox table; Pub/Sub-pluggable later. Events: DocumentUploaded, ChunkCreated, MemoryUpdated, ChapterCreated, CritiqueCompleted.
- **0007 State Contract** — Decision: one shared Pydantic `GraphState` is the single state object across all agents; each agent declares its state mutations in `contracts/agents/*.json`.
- **0008 Dev = Prod** — Decision: identical container images locally (docker-compose) and in prod (Cloud Run); Postgres via `pgvector/pgvector:pg16` locally, Cloud SQL in prod.
- **0009 Async Jobs** — Decision: heavy work (ingestion/embedding/OCR/summarize) runs out of the request path via a job interface; in-process worker stub now, Cloud Run Jobs/Cloud Tasks later. Endpoints `POST /jobs`, `GET /jobs/{id}`.
- **0010 Promotion Gates** — Decision: each milestone transition is gated by explicit machine-checkable criteria (see spec §17). M0→M1 requires: architecture approved, contracts frozen, adr complete, terraform apply success, docker-compose green, cloud-run deployed, health green, db migrations green, zero feature debt.

- [ ] **Step 3: Verify all ten exist**

Run: `ls decisions/ | wc -l`
Expected: `10`

- [ ] **Step 4: Re-run Task 1 link check**

Run: `for f in $(rg -o 'decisions/ADR-00[0-9]+-[a-z-]+\.md' docs/architecture.md | sort -u); do test -f "$f" && echo "OK $f" || echo "MISSING $f"; done`
Expected: all `OK`.

- [ ] **Step 5: Commit**

```bash
git add decisions/
git commit -m "docs(m0): freeze ADR-0001..0010"
```

---

### Task 3: REST contract (OpenAPI)

**Files:**
- Create: `contracts/openapi/openapi.yaml`

- [ ] **Step 1: Write `contracts/openapi/openapi.yaml`**

OpenAPI 3.1 document. Implemented-in-M0 paths: `/health`, `/ready`, `/metrics`, `/jobs` (POST), `/jobs/{id}` (GET). Declared-but-deferred paths (with `x-milestone` extension): `/chat` (M1), `/upload` `/documents` (M3), `/search` (M4), `/summarize` (M3/M6), `/outline` `/chapters` (M8/M6), `/memory` (M2), `/citations` `/bibliography` (M7). Define schemas: `Health`, `Ready`, `Job`, `JobCreate`, `Error`.

```yaml
openapi: 3.1.0
info: { title: ThesisOS API, version: 0.0.0 }
paths:
  /health:
    get:
      summary: Liveness
      responses: { "200": { description: OK, content: { application/json: { schema: { $ref: "#/components/schemas/Health" } } } } }
  /ready:
    get:
      summary: Readiness (db + config)
      responses:
        "200": { description: ready, content: { application/json: { schema: { $ref: "#/components/schemas/Ready" } } } }
        "503": { description: not ready }
  /metrics:
    get: { summary: Prometheus metrics, responses: { "200": { description: OK } } }
  /jobs:
    post:
      summary: Enqueue a background job (contract only in M0)
      requestBody: { required: true, content: { application/json: { schema: { $ref: "#/components/schemas/JobCreate" } } } }
      responses: { "202": { description: accepted, content: { application/json: { schema: { $ref: "#/components/schemas/Job" } } } } }
  /jobs/{id}:
    get:
      summary: Job status
      parameters: [ { name: id, in: path, required: true, schema: { type: string } } ]
      responses: { "200": { description: OK, content: { application/json: { schema: { $ref: "#/components/schemas/Job" } } } } }
components:
  schemas:
    Health: { type: object, properties: { status: { type: string, enum: [ok] } }, required: [status] }
    Ready:
      type: object
      properties: { status: { type: string }, db: { type: boolean }, config: { type: boolean } }
      required: [status, db, config]
    JobCreate:
      type: object
      properties: { type: { type: string }, payload: { type: object } }
      required: [type]
    Job:
      type: object
      properties:
        id: { type: string }
        type: { type: string }
        status: { type: string, enum: [pending, in_progress, done, error] }
      required: [id, type, status]
    Error:
      type: object
      properties: { code: { type: string }, message: { type: string } }
      required: [code, message]
```

- [ ] **Step 2: Validate the spec parses**

Run: `python -c "import yaml,sys; yaml.safe_load(open('contracts/openapi/openapi.yaml')); print('valid yaml')"`
Expected: `valid yaml`

- [ ] **Step 3: Commit**

```bash
git add contracts/openapi/openapi.yaml
git commit -m "contracts(m0): add OpenAPI rest contract (health/ready/metrics/jobs + deferred paths)"
```

---

### Task 4: GraphState + agent contracts + event catalog

**Files:**
- Create: `backend/app/schemas/graph_state.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `contracts/agents/{supervisor,planner,router,retriever,writer,critic,citation,memory,document}.json`
- Create: `contracts/events/events.json`
- Test: `backend/tests/test_graph_state.py`

- [ ] **Step 1: Write the failing test `backend/tests/test_graph_state.py`**

```python
from app.schemas.graph_state import GraphState

def test_graph_state_defaults():
    s = GraphState(messages=[])
    assert s.plan is None
    assert s.retrieved_context == []
    assert s.errors == []

def test_graph_state_roundtrip():
    s = GraphState(messages=[], route="writer", draft="hello")
    assert GraphState.model_validate_json(s.model_dump_json()).route == "writer"
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `cd backend && pytest tests/test_graph_state.py -v`
Expected: FAIL (`ModuleNotFoundError: app.schemas.graph_state`).

- [ ] **Step 3: Implement `backend/app/schemas/graph_state.py`**

```python
from __future__ import annotations
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str
    content: str

class Plan(BaseModel):
    steps: list[str] = []

class RetrievedChunk(BaseModel):
    chunk_id: str
    score: float
    content: str

class CitationRef(BaseModel):
    source_id: str
    locator: str | None = None

class MemoryOp(BaseModel):
    op: str          # upsert | delete
    kind: str        # user|thesis|concept|citation|decision|editable
    key: str
    content: str | None = None

class Critique(BaseModel):
    issues: list[str] = []
    passed: bool = False

class TaskRef(BaseModel):
    id: str
    title: str

class AgentError(BaseModel):
    agent: str
    message: str

class GraphState(BaseModel):
    messages: list[Message]
    plan: Plan | None = None
    route: str | None = None
    retrieved_context: list[RetrievedChunk] = Field(default_factory=list)
    draft: str | None = None
    citations: list[CitationRef] = Field(default_factory=list)
    memory_ops: list[MemoryOp] = Field(default_factory=list)
    critique: Critique | None = None
    task: TaskRef | None = None
    errors: list[AgentError] = Field(default_factory=list)
```

Also create empty `backend/app/schemas/__init__.py`.

- [ ] **Step 4: Run the test to confirm it passes**

Run: `cd backend && pytest tests/test_graph_state.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Write the 9 agent contracts in `contracts/agents/`**

Each file documents `input`, `output`, `errors`, `state_mutations` (GraphState fields read/written). Example `writer.json`:

```json
{
  "agent": "writer",
  "milestone": "M6",
  "input": { "reads_state": ["plan", "retrieved_context", "messages"] },
  "output": { "writes_state": ["draft", "citations"] },
  "errors": ["empty_context", "generation_failed"],
  "state_mutations": { "draft": "set", "citations": "append" }
}
```

Apply the same shape to the others with these specifics:
- `supervisor.json` (M5): reads `messages,task`; writes `plan,route`; errors `["no_objective"]`.
- `planner.json` (M5): reads `messages,plan`; writes `plan,task`; errors `["unplannable"]`.
- `router.json` (M5): reads `plan,messages`; writes `route`; errors `["no_route"]`.
- `retriever.json` (M4): reads `messages,route`; writes `retrieved_context`; errors `["embed_failed","no_results"]`.
- `critic.json` (M9): reads `draft,retrieved_context`; writes `critique`; errors `["hallucination","redundancy"]`.
- `citation.json` (M7): reads `draft,citations`; writes `citations`; errors `["unresolved_source"]`.
- `memory.json` (M2): reads `messages,memory_ops`; writes `memory_ops`; errors `["write_conflict"]`.
- `document.json` (M3): reads `task`; writes `errors`; errors `["parse_failed","unsupported_format"]`.

- [ ] **Step 6: Write `contracts/events/events.json`**

```json
{
  "version": 1,
  "events": [
    { "name": "DocumentUploaded", "milestone": "M3", "payload": { "document_id": "string" } },
    { "name": "ChunkCreated", "milestone": "M3", "payload": { "chunk_id": "string", "document_id": "string" } },
    { "name": "MemoryUpdated", "milestone": "M2", "payload": { "memory_id": "string", "kind": "string" } },
    { "name": "ChapterCreated", "milestone": "M8", "payload": { "chapter_id": "string" } },
    { "name": "CritiqueCompleted", "milestone": "M9", "payload": { "agent_run_id": "string", "passed": "boolean" } }
  ]
}
```

- [ ] **Step 7: Validate agent + event JSON parses**

Run: `python -c "import json,glob; [json.load(open(f)) for f in glob.glob('contracts/agents/*.json')+['contracts/events/events.json']]; print('all json valid')"`
Expected: `all json valid` (and 9 agent files present: `ls contracts/agents | wc -l` → `9`).

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/ backend/tests/test_graph_state.py contracts/agents/ contracts/events/
git commit -m "contracts(m0): GraphState model, agent I/O contracts, event catalog"
```

---

### Task 5: Database models, schema snapshot, initial migration

**Files:**
- Create: `backend/app/db/__init__.py`, `backend/app/db/base.py`, `backend/app/db/models.py`, `backend/app/db/session.py`
- Create: `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/versions/0001_initial.py`
- Create: `contracts/db/schema.sql`
- Test: `backend/tests/test_models_import.py`

- [ ] **Step 1: Write failing test `backend/tests/test_models_import.py`**

```python
def test_all_tables_registered():
    from app.db.base import Base
    import app.db.models  # noqa: F401
    names = set(Base.metadata.tables.keys())
    expected = {
        "documents","chunks","embeddings","sources","citations","chapters",
        "notes","memories","conversations","messages","tasks","events",
        "agent_runs","agent_steps",
    }
    assert expected.issubset(names), expected - names
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `cd backend && pytest tests/test_models_import.py -v`
Expected: FAIL (`ModuleNotFoundError: app.db.base`).

- [ ] **Step 3: Implement `backend/app/db/base.py`**

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

- [ ] **Step 4: Implement `backend/app/db/models.py`**

Define SQLAlchemy 2.0 models for every table in spec §7 (`documents, chunks, embeddings, sources, citations, chapters, notes, memories, conversations, messages, tasks, events, agent_runs, agent_steps`). Use `pgvector.sqlalchemy.Vector` for `embeddings.embedding` with a configurable dimension constant `EMBEDDING_DIM = 768` (documented as the active model's dim; the row also stores `model` + `dimension`). Use `JSONB`, `UUID` PKs (`server_default=text("gen_random_uuid()")`), `TIMESTAMP(timezone=True)` with `now()` defaults, and self-FKs for `chapters.parent_id` and `tasks.parent_task_id`. Do NOT create the LangGraph `checkpoints` tables (library-managed later). Example for the trickiest two:

```python
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.base import Base

EMBEDDING_DIM = 768

class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    owner_type: Mapped[str] = mapped_column(String(16))   # chunk|note|memory|chapter
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    model: Mapped[str] = mapped_column(String(128))
    dimension: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    content_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Chapter(Base):
    __tablename__ = "chapters"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("chapters.id"), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="planned")
    content_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
```

Implement the remaining 12 models following spec §7 column lists with the same conventions.

- [ ] **Step 5: Implement `backend/app/db/session.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
```

(Note: `app.core.config` is created in Task 6; this import is satisfied before running migrations.)

- [ ] **Step 6: Run the model test to confirm it passes**

Run: `cd backend && pytest tests/test_models_import.py -v`
Expected: PASS.

- [ ] **Step 7: Configure Alembic (`alembic.ini`, `migrations/env.py`)**

`migrations/env.py` must `from app.db.base import Base` and `import app.db.models`, set `target_metadata = Base.metadata`, and read the URL from `settings.database_url`.

- [ ] **Step 8: Write `migrations/versions/0001_initial.py`**

The upgrade must: `CREATE EXTENSION IF NOT EXISTS vector;` then create all tables (use `op.create_table` mirroring the models). No HNSW index yet (deferred to M4 retrieval; documented in spec §19). Downgrade drops all tables.

- [ ] **Step 9: Generate the canonical `contracts/db/schema.sql`**

Run (after a local DB is up in Task 8, or against a throwaway container now):
`cd backend && alembic upgrade head && pg_dump --schema-only "$DATABASE_URL" > ../contracts/db/schema.sql`
Expected: `schema.sql` contains all 14 tables + `CREATE EXTENSION ... vector`.

- [ ] **Step 10: Commit**

```bash
git add backend/app/db/ backend/alembic.ini backend/migrations/ backend/tests/test_models_import.py contracts/db/schema.sql
git commit -m "feat(m0): db models, alembic initial migration, schema snapshot"
```

---

### Task 6: Backend FastAPI skeleton (health/ready/metrics, jobs stub, llm interface, telemetry, service stubs)

**Files:**
- Create: `backend/app/core/config.py`, `backend/app/core/logging.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`, `backend/app/api/system.py`, `backend/app/api/jobs.py`
- Create: `backend/app/llm/__init__.py`, `backend/app/llm/base.py`
- Create: `backend/app/services/{events,jobs,telemetry,ingestion,retrieval,memory,citation}/__init__.py`
- Create: `backend/app/services/telemetry/setup.py`, `backend/app/services/jobs/queue.py`, `backend/app/services/events/bus.py`
- Test: `backend/tests/test_system_endpoints.py`

- [ ] **Step 1: Write failing test `backend/tests/test_system_endpoints.py`**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200

def test_jobs_contract_not_implemented():
    r = client.post("/jobs", json={"type": "noop"})
    assert r.status_code in (202, 501)
```

- [ ] **Step 2: Run to confirm it fails**

Run: `cd backend && pytest tests/test_system_endpoints.py -v`
Expected: FAIL (`ModuleNotFoundError: app.main`).

- [ ] **Step 3: Implement `backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://thesisos:thesisos@localhost:5432/thesisos"
    google_cloud_project: str = ""
    vertex_location: str = "europe-west1"
    gemini_model: str = "gemini-2.5-pro"
    embedding_model: str = "text-multilingual-embedding-002"

settings = Settings()
```

- [ ] **Step 4: Implement `backend/app/llm/base.py` (interface only — no Vertex calls in M0)**

```python
from typing import Protocol

class LLMClient(Protocol):
    async def generate(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> str: ...
    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]: ...
    async def vision(self, messages: list[dict], *, model: str | None = None) -> str: ...

class NotConfiguredLLM:
    """M0 placeholder. Concrete Vertex/LiteLLM client lands in M1 (ADR-0002)."""
    async def generate(self, *a, **k): raise NotImplementedError("LLM wired in M1")
    async def embed(self, *a, **k): raise NotImplementedError("LLM wired in M1")
    async def vision(self, *a, **k): raise NotImplementedError("LLM wired in M1")
```

- [ ] **Step 5: Implement service stubs**

`services/events/bus.py`:
```python
async def publish(event_name: str, payload: dict) -> None:
    """In-process stub (ADR-0006). Persistence + consumers wired later."""
    raise NotImplementedError("event bus wired post-M0")
```
`services/jobs/queue.py`:
```python
async def enqueue(job_type: str, payload: dict) -> str:
    """ADR-0009. Returns job id. Worker wired post-M0."""
    raise NotImplementedError("job queue wired post-M0")
```
`services/telemetry/setup.py`:
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def init_telemetry(app) -> None:
    FastAPIInstrumentor.instrument_app(app)
```
Create empty `__init__.py` for ingestion/retrieval/memory/citation packages.

- [ ] **Step 6: Implement `backend/app/api/system.py`**

```python
from fastapi import APIRouter, Response
from sqlalchemy import text
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.db.session import engine

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/ready")
def ready():
    db_ok = True
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    status_code = 200 if db_ok else 503
    return Response(content=f'{{"status":"{"ready" if db_ok else "degraded"}","db":{str(db_ok).lower()},"config":true}}',
                    media_type="application/json", status_code=status_code)

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

- [ ] **Step 7: Implement `backend/app/api/jobs.py` (contract stub)**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/jobs")

class JobCreate(BaseModel):
    type: str
    payload: dict = {}

@router.post("", status_code=501)
def create_job(_: JobCreate):
    raise HTTPException(status_code=501, detail="job execution wired post-M0 (ADR-0009)")

@router.get("/{job_id}", status_code=501)
def get_job(job_id: str):
    raise HTTPException(status_code=501, detail="job execution wired post-M0 (ADR-0009)")
```

- [ ] **Step 8: Implement `backend/app/main.py`**

```python
from fastapi import FastAPI
from app.api import system, jobs
from app.services.telemetry.setup import init_telemetry

app = FastAPI(title="ThesisOS API", version="0.0.0")
app.include_router(system.router)
app.include_router(jobs.router)
init_telemetry(app)
```

- [ ] **Step 9: Run tests to confirm they pass**

Run: `cd backend && pip install -e ".[dev]" && pytest -v`
Expected: PASS (graph_state + models_import + system_endpoints).

- [ ] **Step 10: Commit**

```bash
git add backend/app backend/tests/test_system_endpoints.py
git commit -m "feat(m0): backend skeleton (health/ready/metrics, jobs+llm+services stubs, telemetry)"
```

---

### Task 7: Frontend Next.js skeleton (placeholder routes, api client, store)

**Files:**
- Create: `frontend/app/layout.tsx`, `frontend/app/page.tsx`
- Create: `frontend/app/{chat,workspace,library,memory,outline,settings}/page.tsx`
- Create: `frontend/lib/api.ts`, `frontend/lib/store.ts`
- Create: `frontend/tailwind.config.ts`, `frontend/postcss.config.js`, `frontend/app/globals.css`, `frontend/tsconfig.json`, `frontend/next-env.d.ts`

- [ ] **Step 1: Root layout + home**

`app/layout.tsx` imports `globals.css`, renders a sidebar linking the 6 routes + `{children}`. `app/page.tsx` redirects to `/chat`.

- [ ] **Step 2: Six placeholder routes**

Each `app/<name>/page.tsx` renders a heading + "Coming in M<n>" note (chat→M1, memory→M2, library→M3, outline→M8, workspace→M6, settings→M0). No feature logic (ADR-0001).

- [ ] **Step 3: `lib/api.ts` (typed health ping only)**

```typescript
const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export async function getHealth(): Promise<{ status: string }> {
  const r = await fetch(`${BASE}/health`, { cache: "no-store" });
  if (!r.ok) throw new Error(`health ${r.status}`);
  return r.json();
}
```

- [ ] **Step 4: `lib/store.ts` (zustand, minimal)**

```typescript
import { create } from "zustand";
type UIState = { activeRoute: string; setActiveRoute: (r: string) => void };
export const useUIStore = create<UIState>((set) => ({
  activeRoute: "chat",
  setActiveRoute: (r) => set({ activeRoute: r }),
}));
```

- [ ] **Step 5: Tailwind/TS config + globals.css** (standard Next 15 + Tailwind setup).

- [ ] **Step 6: Verify it builds**

Run: `cd frontend && npm install && npm run build`
Expected: build succeeds; routes `/chat /workspace /library /memory /outline /settings` listed.

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat(m0): frontend skeleton (placeholder routes, api client, zustand store)"
```

---

### Task 8: Docker + docker-compose (dev/prod parity)

**Files:**
- Create: `docker/backend.Dockerfile`, `docker/frontend.Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 1: `docker/backend.Dockerfile`**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]" || pip install --no-cache-dir .
COPY backend/ ./
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: `docker/frontend.Dockerfile`**

```dockerfile
FROM node:22-slim
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build
CMD ["npm", "run", "start"]
```

- [ ] **Step 3: `docker-compose.yml`**

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: thesisos
      POSTGRES_PASSWORD: thesisos
      POSTGRES_DB: thesisos
    ports: ["5432:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U thesisos"]
      interval: 5s
      timeout: 3s
      retries: 10
  backend:
    build: { context: ., dockerfile: docker/backend.Dockerfile }
    environment:
      DATABASE_URL: postgresql+psycopg://thesisos:thesisos@db:5432/thesisos
    command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    depends_on:
      db: { condition: service_healthy }
    ports: ["8000:8000"]
  frontend:
    build: { context: ., dockerfile: docker/frontend.Dockerfile }
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:8000
    depends_on: [backend]
    ports: ["3000:3000"]
```

- [ ] **Step 4: Validate compose config**

Run: `docker compose config >/dev/null && echo "compose valid"`
Expected: `compose valid`

- [ ] **Step 5: Bring it up and verify health (this also produces `schema.sql` for Task 5 Step 9 if not yet done)**

Run: `docker compose up -d --build && sleep 25 && curl -s localhost:8000/health`
Expected: `{"status":"ok"}`; `curl -s localhost:8000/ready` → `"db":true`.

- [ ] **Step 6: Commit**

```bash
git add docker/ docker-compose.yml
git commit -m "feat(m0): docker images + compose (dev=prod parity, pgvector)"
```

---

### Task 9: Terraform (GCP provisioning)

**Files:**
- Create: `infra/terraform/{versions.tf,variables.tf,apis.tf,artifact_registry.tf,cloudsql.tf,secrets.tf,storage.tf,iam.tf,cloudrun.tf,outputs.tf}`
- Create: `infra/terraform/terraform.tfvars.example`

- [ ] **Step 1: `versions.tf` + `variables.tf`**

```hcl
# versions.tf
terraform {
  required_version = ">= 1.9"
  required_providers { google = { source = "hashicorp/google", version = "~> 6.0" } }
}
provider "google" {
  project = var.project_id
  region  = var.region
}
```
```hcl
# variables.tf
variable "project_id" { type = string }
variable "region"     { type = string, default = "europe-west1" }
variable "db_tier"    { type = string, default = "db-f1-micro" }
```

- [ ] **Step 2: `apis.tf` — enable services**

Enable: `run.googleapis.com`, `sqladmin.googleapis.com`, `secretmanager.googleapis.com`, `storage.googleapis.com`, `artifactregistry.googleapis.com`, `aiplatform.googleapis.com` via `google_project_service` (with `disable_on_destroy = false`).

- [ ] **Step 3: `artifact_registry.tf`**

`google_artifact_registry_repository` "thesisos" format `DOCKER` in `var.region`.

- [ ] **Step 4: `cloudsql.tf` — Postgres db-f1-micro + database**

```hcl
resource "google_sql_database_instance" "pg" {
  name             = "thesisos-pg"
  database_version = "POSTGRES_16"
  region           = var.region
  settings { tier = var.db_tier }
  deletion_protection = false
}
resource "google_sql_database" "db" {
  name     = "thesisos"
  instance = google_sql_database_instance.pg.name
}
resource "google_sql_user" "user" {
  name     = "thesisos"
  instance = google_sql_database_instance.pg.name
  password = "CHANGE_ME_VIA_SECRET"
}
```
(Note: pgvector extension is enabled by the Alembic migration `CREATE EXTENSION` on first connect; document that Cloud SQL Postgres 16 supports `vector`.)

- [ ] **Step 5: `storage.tf` — four buckets**

`google_storage_bucket` for `documents`, `exports`, `temp`, `logs` (names prefixed with project id; `uniform_bucket_level_access = true`).

- [ ] **Step 6: `secrets.tf`** — `google_secret_manager_secret` for `database-url` and `vertex-config`.

- [ ] **Step 7: `iam.tf` — Cloud Run service account**

Service account `thesisos-run` with roles: `roles/aiplatform.user`, `roles/cloudsql.client`, `roles/secretmanager.secretAccessor`, `roles/storage.objectAdmin`.

- [ ] **Step 8: `cloudrun.tf` — backend + frontend services**

Two `google_cloud_run_v2_service` resources (`thesisos-backend`, `thesisos-frontend`) using images from Artifact Registry, the `thesisos-run` SA, Cloud SQL connection annotation, and env from secrets. Allow unauthenticated invoker for the single-user app (or restrict — note in spec §3).

- [ ] **Step 9: `outputs.tf`** — output Cloud Run URLs + SQL connection name.

- [ ] **Step 10: Validate**

Run: `cd infra/terraform && terraform init -backend=false && terraform fmt -check && terraform validate`
Expected: `Success! The configuration is valid.`

- [ ] **Step 11: Commit**

```bash
git add infra/terraform/
git commit -m "feat(m0): terraform for cloud run, cloud sql (f1-micro), buckets, secrets, AR, iam"
```

---

### Task 10: CI/CD pipeline

**Files:**
- Create: `infra/ci/cloudbuild.yaml` (or `.github/workflows/deploy.yml` — pick one; default Cloud Build)

- [ ] **Step 1: Write `infra/ci/cloudbuild.yaml`**

Steps: (1) build backend image → push to Artifact Registry; (2) build frontend image → push; (3) `gcloud run deploy thesisos-backend` with the new image + Cloud SQL connection; (4) deploy frontend. Substitution vars for project/region/repo.

- [ ] **Step 2: Lint the YAML**

Run: `python -c "import yaml; yaml.safe_load(open('infra/ci/cloudbuild.yaml')); print('ci yaml valid')"`
Expected: `ci yaml valid`

- [ ] **Step 3: Commit**

```bash
git add infra/ci/
git commit -m "ci(m0): cloud build pipeline (build->Artifact Registry->Cloud Run)"
```

---

### Task 11: GCP deploy + verify (requires a real GCP project)

**Preconditions:** `gcloud auth login`, `gcloud config set project <id>`, billing enabled.

- [ ] **Step 1: Apply infra**

Run: `cd infra/terraform && terraform init && terraform apply -var project_id=<id>`
Expected: apply complete; outputs show two Cloud Run URLs.

- [ ] **Step 2: Run the CI pipeline (or manual first deploy)**

Run: `gcloud builds submit --config infra/ci/cloudbuild.yaml --substitutions=_PROJECT=<id>,_REGION=europe-west1`
Expected: both images pushed; both Cloud Run services deployed.

- [ ] **Step 3: Verify migrations on Cloud SQL**

Run (via Cloud SQL proxy or a one-off Cloud Run Job): `alembic upgrade head` then confirm 14 tables + `vector` extension exist.
Expected: `alembic current` shows `0001_initial`.

- [ ] **Step 4: Verify health green in prod**

Run: `curl -s "$(terraform -chdir=infra/terraform output -raw backend_url)/health"`
Expected: `{"status":"ok"}`

- [ ] **Step 5: Commit any config fixes**

```bash
git add -A && git commit -m "chore(m0): production deploy config fixes"
```

---

### Task 12: M0 promotion gate

**Files:**
- Create: `docs/m0-promotion.md` (the filled gate checklist)

- [ ] **Step 1: Fill and verify the gate (spec §17 / ADR-0010)**

```yaml
architecture: approved        # docs/architecture.md reviewed
contracts: frozen             # contracts/ + decisions/ committed, unchanged
adr: complete                 # decisions/ has ADR-0001..0010
terraform_apply: success      # Task 11 Step 1
docker_compose: green         # Task 8 Step 5
cloud_run: deployed           # Task 11 Step 2
health: green                 # Task 11 Step 4
db_migrations: green          # Task 11 Step 3 (alembic current == 0001_initial)
zero_feature_debt: true       # grep for NotImplementedError stubs only; no half-built feature
```

- [ ] **Step 2: Prove zero feature debt**

Run: `rg -n "TODO|FIXME|chat|RAG|retriev" backend/app frontend/app --glob '!*test*' | rg -iv "deferred|coming in|wired post-M0|impl M" || echo "no feature debt"`
Expected: only stub/deferred references; no real feature code.

- [ ] **Step 3: Tag and commit**

```bash
git add docs/m0-promotion.md
git commit -m "chore(m0): promotion gate passed; M0 frozen"
git tag m0-complete
```

---

## Self-Review (run after writing; fix inline)

**Spec coverage:** every spec section maps to a task — §4 arch→T1; §5 repo→T0/T6/T7; §6 llm→T6; §7 data→T5; §8 memory→ADR-0003 (T2) + models (T5); §9 api→T3/T6; §10 GraphState/agents→T4; §11 events→T4/T6; §12 jobs→T6; §13 telemetry→T6; §14 infra→T8/T9/T10/T11; §15 ADRs→T2; §16 build order→task order; §17 gates→T12; §19 risks→noted (HNSW index deferred to M4, called out in T5 Step 8).

**Placeholder scan:** no "TBD/TODO/implement later"; stubs raise explicit `NotImplementedError` with milestone references (intentional, not debt).

**Type consistency:** `GraphState` fields in T4 match the agent `state_mutations` in T4 and the spec §10; table names in T5 model test match spec §7; env var names consistent across `.env.example` (T0), config (T6), compose (T8).
