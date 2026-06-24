# Testing Strategy

> Sources: M0 plan (test tasks), M1 spec §9 + plan Tasks 2–17, `backend/pyproject.toml`, `docs/m0-promotion.md`, `docs/m1-promotion.md`, `backend/tests/`.

## Principles
- **TDD:** every plan task writes a failing test first, then implements to green,
  then commits (red → green → commit).
- **Evidence-backed gates:** the test suite + lint + smoke are part of the promotion
  gate; "green" means a re-runnable command produced the observed output.
- **Determinism:** streaming/LLM tests use a **fake `LLMClient`** (no live Vertex);
  at most one optional, explicitly-marked integration check hits Vertex via ADC.

## Backend (pytest + httpx, `asyncio_mode=auto`)
Run from `backend/`: `.venv/bin/python -m pytest -q` and `.venv/bin/ruff check app`.

**M0 suite (8 tests):** `test_graph_state`, `test_models_import`,
`test_schema_snapshot` (drift), `test_system_endpoints`, telemetry.

**M1 suite (→ 23 passed / 1 skipped):** in addition to M0 —
- `test_llm_protocol` — `TokenChunk` exactly 3 fields; `NotConfiguredLLM.astream` raises.
- `test_litellm_client` — `astream` maps litellm chunks → `TokenChunk` (monkeypatched).
- `test_llm_factory` — real vs `NotConfiguredLLM` selection.
- `test_run_context` — fields + disjoint from `GraphState`.
- `test_async_session` — async session (skips if DB unreachable; the `1 skipped`).
- `test_checkpointer` — DSN shaping / `search_path` to `langgraph`.
- `test_conversation_graph` — fake LLM; streamed tokens + final assistant state.
- `test_conversation_service` — lock guard (single-active-run).
- `test_chat_endpoint` — SSE framing + `409` concurrent run.
- CRLF SSE regression test (review fix C1).
- drift test stays green while **ignoring** `langgraph.*` tables.

> **Coverage gap (recorded):** `ConversationService.stream_turn` is **not**
> unit-tested end-to-end (only the lock guard) — it was validated via the live
> Docker+DB+Vertex smoke. The disconnect→`cancelled` finalize path is reasoned, not
> exercised. See `memory/known-risks.md`.

## Frontend
- `npx tsc --noEmit` (clean) + `npm run build` (`next build` green). No JS unit test
  runner is wired yet; SSE client correctness is covered by the backend SSE tests +
  the live smoke.

## Test types in play
| Type | Where | Example |
|------|-------|---------|
| Unit | pytest | TokenChunk, locks, factory, DSN shaping |
| Contract/drift | `test_schema_snapshot` | models ↔ `schema.sql` |
| Integration | marked/skipped | async DB SELECT 1; optional live Vertex |
| Smoke (manual) | docker compose | `curl /chat` streams real Gemini; checkpoint tables in `langgraph` |
| Validation | CLI | `terraform validate`, `docker compose config`, OpenAPI YAML parse |

## What each milestone must add (forward)
Each milestone's spec carries a `## Testing` section + gate; new agents need
unit tests for their node (fake LLM), state-mutation tests, and an integration smoke.
Cross-cutting future work: a streaming-path integration test for
`ConversationService`, a frontend test runner, and a live `/chat` Cloud Run check.
