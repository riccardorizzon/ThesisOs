# How to Add a Tool / Service / Endpoint

> For adding backend capabilities: a service module, an API endpoint, a background job, or an event. Sources: `backend/app/services/*`, `backend/app/api/*`, `contracts/`, ADR-0006/0009, M0 plan Task 6, M1 plan Tasks 10/12.

"Tools" in ThesisOS are backend services exposed via endpoints and/or wired into
the graph, plus background jobs and events. All follow the same Contract-First,
additive pattern.

## A. Add an API endpoint
1. **Contract first:** define/realize the path in `contracts/openapi/openapi.yaml`.
   New milestone paths are usually pre-declared as `x-milestone` 501 stubs — change
   the stub to a real definition (request/response/error codes). Additive only.
2. **Router:** add a router in `backend/app/api/<name>.py` (FastAPI `APIRouter`),
   include it in `app/main.py`.
3. **Validation + errors:** validate the request body (Pydantic `Field` constraints,
   like `/chat`'s `message` 1..32000); return the contract `Error{code,message}` on
   failure — never a stack trace.
4. **TDD:** failing endpoint test (`TestClient`) → implement → green. (Pattern:
   `test_chat_endpoint.py`.)
5. Commit `feat(m{n}): <path> endpoint`; update the gate.

## B. Add a service module
1. Create/flesh out `backend/app/services/<area>/` (the stub packages
   `ingestion/retrieval/memory/citation/events/jobs/telemetry` already exist).
2. Keep the service the **boundary** between HTTP/graph and the DB (like
   `ConversationService`): it owns reads/writes, lifecycle, and accounting.
3. Use the async session on request/stream paths.
4. Unit-test the pure logic; integration-test the DB path (skip if no DB).

## C. Add a background job (ADR-0009)
- Heavy work (ingestion/embedding/OCR/summarize) must run **out of the request
  path**. Use the job interface (`services/jobs/`), `POST /jobs` + `GET /jobs/{id}`.
- M0 ships the interface + a no-op worker stub; production target is Cloud Run
  Jobs / Cloud Tasks. Don't run heavy work inline in FastAPI.

## D. Add an event (ADR-0006)
1. Add it to `contracts/events/events.json` (name, milestone, payload shape).
2. Publish via the in-process bus (`services/events/`); it persists to the `events`
   outbox table. Pub/Sub is pluggable later.
3. Existing catalog: `DocumentUploaded, ChunkCreated, MemoryUpdated, ChapterCreated,
   CritiqueCompleted`.

## E. Wire an LLM capability
- Always go through the seam (`app/llm/`): `generate`/`astream`/`embed`/`vision`.
- `embed`/`vision` are currently `NotImplementedError` (M2/M4+); implement them in
  the `LiteLLMClient` when their milestone arrives, keeping the Protocol stable.
- Config comes from `core/config.py` only (ADR-0013); auth via ADC.

## Hard rules
- Contract-first: the OpenAPI/event/agent contract changes **before or with** the
  code, additively.
- Keep `config.py` the single config source of truth; no ad-hoc env reads, no new
  secrets without a concrete need (ADR-0013).
- Update `contracts/`, the relevant `knowledge/` doc, and the milestone gate.
