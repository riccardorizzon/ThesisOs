# M2 Memory System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan phase-by-phase. Each phase has explicit promotion criteria — do not start the next phase until the current phase gate passes.

**Goal:** Ship the complete memory foundation — 6-kind editable/versioned memory, `/memory` CRUD API, `MemoryService`, `memory_versions` history, `MemoryUpdated` events, LangGraph `memory_context_node`, minimal UI — without touching frozen M1 seams.

**Architecture:** `memories` (+ new `memory_versions`) is domain truth. `MemoryService` owns all CRUD, optimistic locking, and prompt-context loading. REST handlers are thin. LangGraph extends to `START → memory_context_node → conversation_node → END`; the memory node prepends a system message from DB-loaded editable/pinned memory. No embeddings, no retrieval, no agent-driven `memory_ops` execution in the chat loop.

**Tech Stack:** FastAPI, SQLAlchemy 2 async (psycopg3), Alembic, LangGraph (extend existing graph), Next.js App Router, pytest/httpx.

**Spec:** `docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md`  
**ADRs:** 0015 (ownership), 0017 (versioning), 0018 (query model). ADR-0003 (custom memory) unchanged. ADR-0016 not created (editable memory covered by ADR-0003).

**Branch:** `m2-memory-system` (from `main` @ `m1-complete`).  
**Conventions:** TDD where practical (red→green→commit), additive contract changes only, M0+M1 tests must stay green after every phase.

---

## Phase 1 — Schema & domain models

### Objective
Add `title` column, `memory_versions` table, indexes, and SQLAlchemy models. Alembic migration `0002_memory_system`. Regenerate `contracts/db/schema.sql`.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/migrations/versions/0002_memory_system.py` |
| Modify | `backend/app/db/models.py` — add `MemoryVersion`, `Memory.title` |
| Modify | `contracts/db/schema.sql` — regenerate via drift workflow |
| Create | `backend/tests/test_memory_models.py` |
| Modify | `backend/tests/test_schema_snapshot.py` (if assertions need updating) |

### Risks
- Partial unique indexes for singleton kinds may fail on existing duplicate seed data → migration must run on clean DB first; document idempotent seed in Phase 2.
- Drift test failure if `schema.sql` not regenerated → run model introspection script or manual sync.

### Tests
- `test_memory_models.py` — `Memory` and `MemoryVersion` import, table names, column presence.
- `test_schema_snapshot.py` — green (models ≡ `schema.sql`).
- `test_models_import.py` — includes `memory_versions` if added to expected set.

### Promotion criteria
```yaml
migration_up: green       # alembic upgrade head on fresh docker compose DB
migration_down_up: green  # downgrade 0001 → upgrade head (optional smoke)
drift_test: green
m0_m1_tests: green
```

---

## Phase 2 — MemoryService core

### Objective
Implement `MemoryService` with create, get, list, update, delete, version history, optimistic locking, singleton upsert, and `load_prompt_context()`.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/services/memory/__init__.py` |
| Create | `backend/app/services/memory/service.py` |
| Create | `backend/app/schemas/memory.py` — Pydantic API models |
| Create | `backend/tests/test_memory_service.py` |
| Modify | `backend/tests/conftest.py` — DB fixtures for memory tests if needed |

### Risks
- Race on singleton create → use upsert or catch unique violation and retry as update.
- `write_conflict` semantics must match agent contract for future M5.

### Tests
- Create multi-kind memory → version=1, history row exists.
- Update with correct `expected_version` → version increments, history appended.
- Update with stale version → raises `WriteConflictError`.
- Singleton kinds — second create with same kind/key → 409 or upsert per design.
- List filters: `kind`, `q`, `pinned`, pagination.
- Delete multi-kind → gone; delete singleton → rejected.
- `load_prompt_context()` returns editable + pinned user/thesis.
- **Persistence:** write in test, new session read back same data.
- **Restart recovery:** (integration) write via API/service, restart db container not required — new `AsyncSession` proves durability.

### Promotion criteria
```yaml
memory_service_unit: green
write_conflict: green
singleton_enforcement: green
m0_m1_tests: green
```

---

## Phase 3 — REST API `/memory`

### Objective
Wire FastAPI routes for full CRUD + version history. Update OpenAPI contract additively.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/api/memory.py` |
| Modify | `backend/app/main.py` — include memory router |
| Modify | `contracts/openapi/openapi.yaml` — realize `/memory`, add `/memory/{id}`, PATCH, DELETE, version paths |
| Create | `backend/tests/test_memory_api.py` |

### Risks
- OpenAPI drift from handlers → generate or manually sync components.
- Error shape must use frozen `Error` schema.

### Tests
- `test_memory_api.py` (httpx AsyncClient):
  - POST create → 201/200 + body fields.
  - GET list with filters.
  - GET by id → 404 unknown.
  - PATCH happy path + 409 conflict.
  - DELETE + 404 after.
  - GET versions list + GET specific version.
- Contract smoke: OpenAPI paths exist for all implemented routes.

### Promotion criteria
```yaml
memory_crud: green
api_tests: green
openapi_sync: true
m0_m1_tests: green
ruff: green
```

---

## Phase 4 — Memory Administration UI ✅

> **Architect naming (2026-06-24):** Not a knowledge workspace — admin tooling to validate M2 infrastructure manually before graph integration.

### Objective
List, create, edit, delete, and inspect version history via `/memory` routes. Centralized `memoryClient` + `useMemoryStore`. Kind badges for manual testing.

### Delivered
- `frontend/lib/memoryClient.ts` — sole HTTP layer
- `frontend/lib/memoryStore.ts` — Zustand admin store
- `frontend/app/memory/page.tsx` — list + `q=` filter
- `frontend/app/memory/new/page.tsx` — create
- `frontend/app/memory/[id]/page.tsx` — detail, edit, delete (confirm), versions (read-only)
- Components: `MemoryList`, `MemoryForm`, `MemoryKindBadge`, `MemoryVersionList`, `MemoryErrorBanner`
- Vitest: 15 tests (client, store, rendering, error codes)

### Not included (by design)
- Prompt context viewer, injection debugger, advanced search, restore version, Notion clone

### Promotion criteria
```yaml
memory_list: green
memory_detail: green
create: green
update: green
delete: green
versions: green
ui_tests: green          # vitest 15/15
frontend_build: green
prompt_context: not_exposed
restore_version: false
scope_creep: false
```

---

## Phase 5 — Knowledge Freeze (next)

Update `knowledge/` with M2 reality: `project-memory.md`, `current-state.md`, `completed-work.md`, `next-actions.md`, promotion doc.

---

## Phase 6 — LangGraph integration (`memory_context_node`)

After UI validation and knowledge update. Wire `load_prompt_context()` into graph pre-turn node.

---

## Phase 7 — Events & observability (was Phase 4)

### Objective
Wire `MemoryUpdated` event on create/update/delete. Minimal in-process event bus persistence to `events` table. Add structured logging/spans on MemoryService.

### Files affected
| Action | Path |
|--------|------|
| Modify | `backend/app/services/events/bus.py` — implement publish → INSERT events |
| Modify | `backend/app/services/memory/service.py` — call publish after mutations |
| Create | `backend/tests/test_memory_events.py` |
| Modify | `backend/app/services/telemetry/setup.py` — span helpers if needed |

### Risks
- Event bus stub currently raises → must not break M0 callers; scope publish to memory path first.

### Tests
- Create memory → `events` row with `type=MemoryUpdated`, payload `{memory_id, kind}`.
- Update → second event row.

### Promotion criteria
```yaml
events: green
m0_m1_tests: green
```

---

## Phase 5 — LangGraph extension

### Objective
Add `memory_context_node`; change graph to `START → memory_context_node → conversation_node → END`. Inject editable/pinned memory as system message prefix. **Do not modify** `conversation_node` logic beyond graph wiring.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/graph/memory_context.py` |
| Modify | `backend/app/graph/conversation.py` — export shared `build_graph` or new `build_chat_graph` |
| Modify | `backend/app/services/conversation/service.py` — use extended graph (minimal change: import) |
| Create | `backend/tests/test_memory_graph.py` |
| Modify | `backend/tests/test_conversation_graph.py` — ensure still green |

### Risks
- System message persisted to `messages` → verify ConversationService only persists user/assistant (filter role=system if needed — minimal additive fix).
- Checkpoint size grows with system prefix → acceptable; re-loaded from DB each turn anyway.

### Tests
- Graph with fake LLM: when editable memory exists, wire messages to LLM include system block.
- Graph without editable seed: still works (empty or default system block).
- `test_conversation_graph.py` — still passes.
- `GraphState` unchanged — no new fields test still passes.

### Promotion criteria
```yaml
langgraph_extended: green
graphstate: unchanged
conversation_node: unchanged_logic
m0_m1_tests: green
chat_still_works: green   # manual or smoke POST /chat
```

---

## Phase 6 — Frontend minimal UI

### Objective
Memory list, detail, create, update pages wired to `/memory` API.

### Files affected
| Action | Path |
|--------|------|
| Modify | `frontend/lib/api.ts` — memory CRUD client functions |
| Modify | `frontend/lib/store.ts` — memory list state (optional) |
| Modify | `frontend/app/memory/page.tsx` — list view |
| Create | `frontend/app/memory/new/page.tsx` |
| Create | `frontend/app/memory/[id]/page.tsx` — detail + edit |
| Create | `frontend/components/MemoryList.tsx`, `MemoryForm.tsx` (minimal) |

### Risks
- 409 conflict UX — show "refresh and retry" message.
- CORS/API base URL — reuse M1 `NEXT_PUBLIC_API_BASE_URL` pattern.

### Tests
- `frontend` build green (`npm run build`).
- Manual smoke: create editable memory → visible in list → edit → chat reflects injection (manual).

### Promotion criteria
```yaml
frontend_build: green
ui_smoke: manual_green
```

---

## Phase 7 — Integration, migration & promotion docs

### Objective
End-to-end verification, promotion gate doc, knowledge system update. Optional: conversation titling heuristic (Q10).

### Files affected
| Action | Path |
|--------|------|
| Create | `docs/m2-promotion.md` |
| Modify | `knowledge/context/current-state.md` |
| Modify | `knowledge/memory/project-memory.md` |
| Modify | `knowledge/project/milestones.md` |
| Modify | `knowledge/context/open-questions.md` — close Q10 if titling shipped |
| Create | `backend/tests/test_memory_integration.py` — restart + full CRUD path |
| Optional | `backend/app/services/conversation/service.py` — titling heuristic |

### Risks
- Scope creep via titling → keep heuristic-only, gate-not-required.

### Tests
- Full backend pytest suite green.
- Docker compose restart → memories survive, `/memory` returns data.
- Drift tests green.
- Explicit unchanged checks:
  - `GraphState.model_fields` count/shape
  - `TokenChunk` three fields
  - `RunContext` fields
  - `/chat` SSE unchanged (existing tests)

### Promotion criteria
See spec §11 — all gate items green:

```yaml
memory_crud: green
versioning: green
tests: green
contracts: additive_only
graphstate: unchanged
llmclient: unchanged
conversation_system: unchanged
scope_creep: false
documentation: complete
knowledge_updated: true
```

---

## Phase summary

| Phase | Deliverable | Gate |
|-------|-------------|------|
| 1 | Schema + migration | drift + migrate |
| 2 | MemoryService | unit tests |
| 3 | REST API | memory_crud + api_tests |
| 4 | Events | MemoryUpdated persisted |
| 5 | LangGraph node | chat still works, GraphState frozen |
| 6 | Frontend UI | build green |
| 7 | Promotion | full M2 gate |

---

## Critic review (pre-merge)

Before tagging `m2-complete`, verify:

- [ ] No `embeddings` inserts in M2 code paths.
- [ ] No `/search` implementation.
- [ ] No Docling/upload/document code.
- [ ] `memory_ops` not executed in chat loop (hook exists, unwired).
- [ ] LangGraph `langgraph` schema untouched.
- [ ] `ConversationService.stream_turn` signature and SSE events unchanged.
- [ ] OpenAPI changes are additive only.
- [ ] ADR-0016 intentionally omitted (documented in spec §1).

---

## File tree (expected after M2)

```text
backend/
  app/
    api/memory.py
    graph/memory_context.py
    schemas/memory.py
    services/memory/service.py
    services/events/bus.py          # implemented
  migrations/versions/0002_memory_system.py
  tests/
    test_memory_models.py
    test_memory_service.py
    test_memory_api.py
    test_memory_events.py
    test_memory_graph.py
    test_memory_integration.py
frontend/
  app/memory/page.tsx
  app/memory/new/page.tsx
  app/memory/[id]/page.tsx
  components/MemoryList.tsx
  components/MemoryForm.tsx
decisions/
  ADR-0015-memory-ownership.md
  ADR-0017-memory-versioning.md
  ADR-0018-memory-query-model.md
docs/
  superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md
  m2-promotion.md
plans/
  m2-memory-system-plan.md
```

---

## Commands reference

```bash
# Backend tests (from backend/)
.venv/bin/python -m pytest -v
.venv/bin/ruff check app

# Migration
docker compose up -d db
.venv/bin/alembic upgrade head

# Frontend
cd frontend && npm run build

# Full stack smoke
docker compose up --build -d
curl -s localhost:8000/memory | jq .
```
