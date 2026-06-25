# Completed Work

> What has actually been built and verified. Sources: `git`, promotion gates, code, tests.

## M0 — Foundations ✅ (`m0-complete`)

See prior snapshot — architecture, contracts, 14-table schema, infra on `thesisos-prod`, backend 8/8 tests. Full detail unchanged from M0 promotion.

## M1 — Conversation System ✅ (`m1-complete` on `main`)

Streaming chat on the frozen seam: `POST /chat` SSE, `ConversationService`, single-node LangGraph, `LiteLLMClient`, `RunContext`, chat UI, ADR-0011..0014. Validated locally vs real Vertex; merged and tagged on `main`.

**Still optional follow-ups (non-blocking):** Cloud Run deploy of M1+M2 stack, prod SSE smoke (Q3), token usage capture (Q2).

## M2 — Memory System 🟡 (branch `m2-memory-system`, Phases 1–6)

### Phase 1 — Database
- Alembic `0002_memory_system`: `memories.title`, table `memory_versions`, partial unique indexes for singleton kinds.
- SQLAlchemy `Memory`, `MemoryVersion` models; `contracts/db/schema.sql` regenerated (15 domain tables).
- Tests: `test_memory_models.py`, drift test green.

### Phase 2 — MemoryService (sole writer)
- `app/services/memory/service.py` — CRUD, list/query (`MemoryListFilters`), optimistic lock (`WriteConflictError`), version snapshots, `load_prompt_context()` → `PromptContext`, `apply_ops` hook (unwired in chat).
- `app/services/memory/render.py` — `render_prompt_context()` separate from loader.
- `app/schemas/memory.py` — domain DTOs.
- ADRs: 0015, 0017, 0018.
- Tests: 8 integration tests (docker Postgres): CRUD, version chain, conflict, prompt scope (no concept/citation in context).

### Phase 3 — REST API (thin adapter)
- `app/api/memory.py` — delegates exclusively to `MemoryService`; no direct DB.
- Endpoints: `GET/POST /memory`, `GET/PATCH/DELETE /memory/{id}`, `GET /memory/{id}/versions`.
- Error mapping: `write_conflict`→409, `singleton_exists`→409, `memory_not_found`→404, `cannot_delete_singleton`→400.
- **Not exposed:** `/memory/context`, `/memory/search`, retrieval endpoints.
- OpenAPI: additive realization of M2 `/memory` paths + schemas.
- Tests: 9 delegation + 11 integration (docker).

### Phase 4 — Memory Administration UI
- Routes: `/memory` (list + `q=`), `/memory/new`, `/memory/[id]` (detail, edit, delete confirm, version history read-only).
- `frontend/lib/memoryClient.ts` — centralized HTTP layer.
- `frontend/lib/memoryStore.ts` — Zustand admin store.
- Components: `MemoryList`, `MemoryForm`, `MemoryKindBadge`, `MemoryVersionList`, `MemoryErrorBanner`.
- Vitest: 15 tests (client, store, rendering, error codes).
- **Explicitly not built:** Notion clone, prompt debugger, advanced search, restore version.

### Phase 5 — Knowledge freeze
- Updated `knowledge/context/*`, `knowledge/architecture/memory.md`, `knowledge/project/roadmap.md`, `project-memory.md`.
- Created `docs/m2-promotion.md`, `knowledge/KNOWLEDGE-HEALTH-REPORT.md` v2.

### Phase 6 — Graph (`memory_context_node`)
- `app/graph/memory_context.py` — pre-turn loader; calls `MemoryService.load_prompt_context()` + `render_prompt_context()`.
- Graph topology: `START → memory_context_node → conversation_node → END` (`app/graph/conversation.py`).
- **Transient only:** prepends `role=system` to wire messages; no GraphState fields added; `ConversationService` still persists user/assistant only.
- Operational kinds only (`editable`, pinned `user`/`thesis`); no concept/citation/decision injection.
- Tests: `test_memory_context_node.py` (4 unit + 1 integration skip without DB); `test_conversation_graph.py` updated with stub memory service.
- **Frozen seams unchanged:** `GraphState`, `RunContext`, `LLMClient`, `ConversationService`, OpenAPI additive only.

### Architect decisions recorded (M2)
- **Memory ≠ knowledge:** operational (`user`, `thesis`, `decision`, `editable`) vs knowledge items (`concept`, `citation`); `temporary_unified_model: true`; future extraction candidates documented.
- **Service-first sequencing:** Service → API → Admin UI → Knowledge → Graph.
- **Prompt context:** `transient_only`; not a public API; operational kinds only in graph (Phase 6).

## M3 — Document System 🟢 (branch `m3-document-system`, Phases 1–6)

### Phase 1 — Database
- Alembic `0003_document_system`: `documents`, `document_versions`, `chunks` extensions.
- Drift test green.

### Phase 2 — DocumentService (sole writer)
- `app/services/document/service.py` — upload, parse, reparse, CRUD, versioning.
- Storage: `LocalStorageAdapter` / `GCSStorageAdapter`.
- Parsers: Docling primary, PyMuPDF PDF fallback; `chunk_hash` on every chunk.
- ADRs: 0020, 0021, 0022.

### Phase 3 — REST API
- `app/api/documents.py` — thin adapter; background parse after upload.
- OpenAPI additive (`/upload`, `/documents/*`).

### Phase 4 — Document Administration UI
- Routes: `/documents`, `/documents/upload`, `/documents/[id]`, `/documents/[id]/chunks`.
- `documentClient.ts`, `documentStore.ts`, six components; vitest coverage.

### Phase 5 — Events
- `app/services/events/bus.py` — catalog-validated publish → `events` outbox.
- `DocumentUploaded` on upload; `ChunkCreated` per chunk on successful parse.
- Additive `chunk_hash` in events catalog.

### Phase 6 — Knowledge freeze + promotion
- `docs/m3-promotion.md`, knowledge mirror updated.
- **Frozen seams unchanged:** GraphState, ConversationService, memory_context_node.

## Not yet done
- M3: merge + tag `m3-complete`; DB integration validation (Docker).
- M4+.
