# Architectural Decisions

> Consolidated from `decisions/ADR-0001..0014`. These are **structural** decisions that shape the whole system. Each is FROZEN; change only via a new superseding ADR. The ADR files are the source of truth.

## Index (all 14 ADRs)

| ADR | Title | Status | Type |
|-----|-------|--------|------|
| 0001 | Contract First | Accepted (M0) | architectural |
| 0002 | Vertex Runtime Only | Accepted (M0) | technical |
| 0003 | Custom Memory | Accepted (M0) | technical |
| 0004 | Cloud Day One | Accepted (M0) | architectural |
| 0005 | Python Backend | Accepted (M0) | architectural |
| 0006 | Event Driven | Accepted (M0) | architectural |
| 0007 | State Contract (GraphState) | Accepted (M0) | architectural |
| 0008 | Dev = Prod | Accepted (M0) | architectural |
| 0009 | Async Jobs | Accepted (M0) | architectural |
| 0010 | Promotion Gates | Accepted (M0) | architectural |
| 0011 | Streaming-First LLM | Accepted (M1) | technical |
| 0012 | External Infrastructure Schemas | Accepted (M1) | architectural |
| 0013 | Runtime Config Minimalism | Accepted (M1) | technical |
| 0014 | RunContext Separation | Accepted (M1) | architectural |

(Technical ADRs 0002/0003/0011/0013 are detailed in `technical-decisions.md`.)

## Architectural ADRs — summary

### ADR-0001 — Contract First
Produce architecture + contracts + schemas before any product code; no feature code
until the gate passes. Forbids chat/RAG/ingestion/agents in M0. **Enables** stable
contracts that every later milestone builds against.

### ADR-0004 — Cloud Day One
GCP from the start (Cloud Run, Cloud SQL, Storage, Secret Manager, Artifact
Registry), Terraform-provisioned. Avoids a "make it production-ready later" rewrite.

### ADR-0005 — Python Backend
Python everywhere server-side (backend, orchestrator, agents, retrieval); TS only in
the Next.js frontend. One server language, one toolchain.

### ADR-0006 — Event Driven
Typed event catalog + in-process dispatcher + `events` outbox table; Pub/Sub-pluggable
later. Catalog: `DocumentUploaded, ChunkCreated, MemoryUpdated, ChapterCreated,
CritiqueCompleted`. M0 ships the interface only.

### ADR-0007 — State Contract (GraphState)
One shared Pydantic `GraphState` is the single state object across all agents; each
agent declares its state mutations in `contracts/agents/*.json`. **Frozen.** See
`contracts/graphstate.md`.

### ADR-0008 — Dev = Prod
Identical container images locally (docker-compose) and in prod (Cloud Run);
`pgvector/pgvector:pg16` locally, Cloud SQL in prod. "Works locally" ⇒ "works in prod."

### ADR-0009 — Async Jobs
Heavy work (ingestion/embedding/OCR/summarize) runs out of the request path via a job
interface; in-process worker stub now, Cloud Run Jobs/Cloud Tasks later. Endpoints
`POST /jobs`, `GET /jobs/{id}`.

### ADR-0010 — Promotion Gates
Each milestone transition is gated by explicit, machine-checkable, evidence-backed
criteria. See `development/promotion-gates.md`.

### ADR-0012 — External Infrastructure Schemas
Distinguish **domain schema** (ThesisOS-owned, `public`, Alembic + drift test) from
**infrastructure schema** (tool-owned, `langgraph`, `PostgresSaver.setup()`, excluded
from domain governance). `contracts: unchanged` = `domain_contracts: unchanged`.

### ADR-0014 — RunContext Separation
Execution metadata (`conversation_id, agent_run_id, trace_id, request_id, user_id,
metadata`) lives in a runtime-only `RunContext`, never in `GraphState`, never in the
checkpoint. Token accounting attaches to `agent_runs`. See `contracts/runcontext.md`.

## How decisions evolve
- ADRs are append-only and frozen on acceptance. To change one, write a new ADR that
  explicitly supersedes it (none have been superseded yet).
- Every ADR records: Status, Context, Decision, Consequences, Alternatives considered.
