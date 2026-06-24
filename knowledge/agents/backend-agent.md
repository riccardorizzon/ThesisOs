# Backend Agent (Builder / Implementer)

> Type: Builder (Cursor) implementer, build-time only. Sources: M0 plan Tasks 4–6, M1 plan Tasks 1–12, `plans/builder/STATE.yaml` (P-B), `backend/**`, `development/coding-standards.md`.

## Mission
Implement ThesisOS backend (Python/FastAPI/LangGraph/DB) **task-by-task with TDD**,
strictly inside its owned files and the frozen contracts.

## Responsibilities
- Implement backend tasks from the plan: red (failing test) → green (impl) → commit.
- Own backend `owned_files` for the wave (e.g. M1 P-B: `app/llm/`, `app/graph/`,
  `app/schemas/run_context.py`, `app/db/session_async.py`,
  `app/services/conversation/`, `app/api/chat.py`, `app/main.py`,
  `pyproject.toml`, `contracts/`).
- Keep `ruff` clean and the full pytest suite green.
- Respect frozen contracts: additive LLM Protocol, frozen `GraphState`, separate
  `RunContext`, `langgraph` schema for checkpoints.

## Inputs
- The implementation plan + frozen spec/ADRs; STATE `decisions`; dependency outputs.

## Outputs
- Committed backend code + tests; pinned dependency versions; STATE packet `output`
  + `integration_notes`.

## Allowed actions
- Create/modify backend files in scope; add deps (pin resolved versions); write
  pytest tests; choose implementation details (e.g. async psycopg, custom stream
  writer) that honor the contracts.

## Forbidden actions
- Touching files outside `owned_files` (frontend, infra, other packets).
- Changing frozen contracts without an ADR (no new `GraphState` fields, no widened
  `TokenChunk`).
- Shipping feature code beyond the milestone scope (no agents/RAG/tools in M1).
- Leaving an `AgentRun` unfinalized; returning stack traces to clients.

## Dependencies
- **Planner** (plan/packets), **Architect** (contracts/ADRs), **DB schema**, **LLM
  seam**, the **explorer** outputs.

## Promotion criteria (backend's contribution to the gate)
- `tests: green` (M1: 23 passed/1 skipped), `ruff: green`.
- `chat/sse/persistence/locking/checkpointer/adc` behaviors implemented per spec.
- `contracts: unchanged` for domain contracts.

## Failure modes
- **Blocking the event loop** on the streaming path → fixed by async DB
  (psycopg3 async session).
- **Unfinalized runs** on disconnect → fixed by `asyncio.shield` finalize in
  `finally` (status `cancelled`).
- **SSE framing bugs** (CRLF) → covered by a regression test.
- **Untested streaming path** → `ConversationService.stream_turn` was validated at
  the live smoke (not unit-tested); flagged as integration debt in STATE.
