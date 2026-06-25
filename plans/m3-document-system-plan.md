# M3 Document System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Each phase has explicit promotion criteria — do not start the next phase until the current phase gate passes. **Critic + QA mandatory every phase.**

**Goal:** Ship document ingestion foundation — upload PDF/EPUB/DOCX, store originals in GCS, parse to chunks with `chunk_hash`, version history, `DocumentService` as sole writer, Document Administration UI — **without** embeddings, retrieval, RAG, or graph/chat integration.

**Architecture:** GCS holds original bytes; Postgres holds `documents`, `document_versions`, `chunks`. `DocumentService` owns all writes and parse orchestration. REST handlers are thin. Docling is **primary** parser; PyMuPDF is **PDF-only fallback** (`both_equal: false`). Status lifecycle: `uploaded → processing → parsed | failed`; `indexed` reserved for M4.

**Tech Stack:** FastAPI, SQLAlchemy 2 async, Alembic, Docling + PyMuPDF, GCS (local adapter for dev), Next.js App Router, pytest/httpx, Vitest.

**Spec:** `docs/superpowers/specs/2026-06-24-thesisos-m3-document-system-design.md` (Frozen 2026-06-24)  
**ADRs:** 0020 (ownership), 0021 (versioning), 0022 (query model + status lifecycle)

**Branch:** `m3-document-system` (from `main` @ `m2-complete`).  
**Conventions:** TDD where practical, additive contract changes only, M0+M1+M2 tests green after every phase.

**Forbidden in all phases:** embeddings writes, `/search`, vector columns on domain tables, graph nodes, chunk injection into `/chat`, setting `status=indexed`.

---

## Phase 1 — Schema & domain models

### Objective
Extend `documents`, add `document_versions`, add `chunks.chunk_hash`, status enum alignment. Alembic `0003_document_system`. Regenerate `contracts/db/schema.sql`.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/migrations/versions/0003_document_system.py` |
| Modify | `backend/app/db/models.py` — `DocumentVersion`, `Document.version`, `Chunk.chunk_hash`, status enum |
| Modify | `contracts/db/schema.sql` |
| Create | `backend/tests/test_document_models.py` |
| Modify | `backend/tests/test_schema_snapshot.py` if needed |

### Migration notes
- Add to `documents`: `version`, `parser`, `parsed_at`, `chunk_count`, `error_message`
- Map legacy status: `parsing`→`processing`, `error`→`failed` if any seed rows exist
- Create `document_versions` per spec §4.4
- Add `chunks.chunk_hash VARCHAR(64) NOT NULL` with backfill strategy for empty table (no-op if no rows)
- Unique indexes: `(document_id, chunk_index)`, `(document_id, chunk_hash)`

### Tests
- `test_document_models.py` — columns, relationships, `DocumentVersion` FK cascade
- `test_schema_snapshot.py` — green
- `test_models_import.py` — includes new model

### Critic checklist (Phase 1)
- [ ] No `embeddings` table changes
- [ ] No vector columns added to `chunks` or `documents`
- [ ] `indexed` not used as default status

### Promotion criteria
```yaml
migration_up: green
drift_test: green
m0_m1_m2_tests: green
```

---

## Phase 2 — DocumentService + storage + parsers

### Objective
Implement `DocumentService` (sole writer), GCS/local storage adapter, parser boundary (Docling primary, PyMuPDF PDF fallback), `chunk_hash` computation, async parse after upload.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/schemas/document.py` — `DocumentRecord`, `DocumentChunk`, filters, DTOs |
| Create | `backend/app/services/document/__init__.py` |
| Create | `backend/app/services/document/service.py` |
| Create | `backend/app/services/document/exceptions.py` |
| Create | `backend/app/services/document/storage.py` — GCS + local adapter |
| Create | `backend/app/services/document/chunking.py` — hash + token estimate |
| Create | `backend/app/services/document/parsers/docling_parser.py` |
| Create | `backend/app/services/document/parsers/pymupdf_parser.py` |
| Create | `backend/app/services/document/parsers/__init__.py` — orchestrator |
| Modify | `backend/pyproject.toml` — pin `docling`, `pymupdf` |
| Create | `backend/tests/test_document_service.py` |
| Create | `backend/tests/fixtures/sample.pdf` (minimal), optional docx/epub stubs |

### Public API (service)
| Method | Notes |
|--------|-------|
| `upload(file, ...)` | GCS write, status=`uploaded`, enqueue parse |
| `parse(document_id)` | status=`processing` → parsers → chunks + `chunk_hash` |
| `get`, `list`, `update`, `delete` | CRUD + versioning |
| `list_chunks`, `list_versions` | structural reads only |
| `reparse(document_id)` | alias for parse |

### Parser tests
- PDF: Docling success path → chunks with hash
- PDF: Docling failure → PyMuPDF fallback → `parser=pymupdf`
- DOCX/EPUB: Docling only; failure → status=`failed`, zero chunks
- Re-parse: new UUIDs, same `chunk_hash` when content unchanged

### Critic checklist (Phase 2)
- [ ] `both_equal: false` — PyMuPDF never invoked for docx/epub
- [ ] Failed parse leaves **zero** chunks (transaction rollback)
- [ ] No method named `search`, `embed`, `retrieve`, `rank`
- [ ] `chunk_hash` matches spec §5.2 formula

### Promotion criteria
```yaml
document_service_unit: green
parser_boundary: green
chunk_hash: green
status_lifecycle: green
gcs_local_adapter: green
m0_m1_m2_tests: green
```

---

## Phase 3 — REST API `/upload` + `/documents`

### Objective
Thin FastAPI routes delegating exclusively to `DocumentService`. OpenAPI additive update.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/api/documents.py` |
| Modify | `backend/app/main.py` — include router |
| Modify | `contracts/openapi/openapi.yaml` |
| Create | `backend/tests/test_document_api.py` |

### Endpoints
| Method | Path |
|--------|------|
| POST | `/upload` |
| GET | `/documents` |
| GET/PATCH/DELETE | `/documents/{id}` |
| GET | `/documents/{id}/chunks` |
| GET | `/documents/{id}/versions` |
| POST | `/documents/{id}/reparse` |

### Tests
- Upload multipart → 201, status `uploaded` then async `parsed`
- List with `q=`, `status=`, `source_type=`
- PATCH optimistic lock 409
- GET chunks ordered by `chunk_index`; response includes `chunk_hash`
- API source inspection: no direct DB session in handlers
- **Forbidden route test:** no `/search`, no `/documents/search`

### Critic checklist (Phase 3)
- [ ] Handlers delegate to `DocumentService` only
- [ ] No ranked/scored chunk responses
- [ ] `q=` does not search chunk content

### Promotion criteria
```yaml
document_api: green
openapi_sync: additive
api_delegation: green
m0_m1_m2_tests: green
ruff: green
```

---

## Phase 4 — Document Administration UI

### Objective
Admin UI at `/documents` — list, upload, detail, chunk preview, versions, re-parse, delete. Mirror Memory Administration pattern.

### Files affected
| Action | Path |
|--------|------|
| Create | `frontend/lib/documentClient.ts` |
| Create | `frontend/lib/documentStore.ts` |
| Create | `frontend/app/documents/page.tsx` |
| Create | `frontend/app/documents/upload/page.tsx` |
| Create | `frontend/app/documents/[id]/page.tsx` |
| Create | `frontend/app/documents/[id]/chunks/page.tsx` |
| Create | `frontend/components/DocumentList.tsx`, `DocumentForm.tsx`, `DocumentStatusBadge.tsx`, `DocumentChunkList.tsx`, `DocumentVersionList.tsx`, `DocumentErrorBanner.tsx` |
| Create | Vitest tests mirroring memory admin coverage |

### Not included
- PDF reader, full-text search, notebook layout, summarize button, chat sidebar

### Critic checklist (Phase 4)
- [ ] No corpus search box on chunk page
- [ ] Chunk preview truncated (~200 chars)
- [ ] Status badge shows lifecycle states only (no `indexed` in M3 UI unless read-only for future)

### Promotion criteria
```yaml
document_list: green
document_upload: green
document_detail: green
chunks_preview: green
versions: green
ui_tests: green
frontend_build: green
scope_creep: false
```

---

## Phase 5 — Events + integration tests

### Objective
Wire `DocumentUploaded`, `ChunkCreated` to events table. Integration tests for full upload→parse→list path. Optional: batch `ChunkCreated`.

### Files affected
| Action | Path |
|--------|------|
| Modify | `backend/app/services/events/bus.py` |
| Modify | `backend/app/services/document/service.py` |
| Modify | `contracts/events/events.json` — additive `chunk_hash` in payload (optional) |
| Create | `backend/tests/test_document_events.py` |
| Create | `backend/tests/test_document_integration.py` |

### Tests
- Upload → event row `DocumentUploaded`
- Parse complete → `ChunkCreated` per chunk (or batch)
- Restart persistence: document + chunks survive new session
- **QA guard:** POST `/chat` with document in system — no chunk text in response (smoke)

### Promotion criteria
```yaml
events: green
integration: green
chat_unchanged: green
embeddings_zero_writes: green
```

---

## Phase 6 — Knowledge freeze + promotion

### Objective
Update `knowledge/`, create `docs/m3-promotion.md`, Critic final sign-off, merge + tag `m3-complete`.

### Files affected
| Action | Path |
|--------|------|
| Create | `docs/m3-promotion.md` |
| Modify | `knowledge/context/current-state.md`, `completed-work.md`, `next-actions.md` |
| Modify | `knowledge/architecture/documents.md` |
| Modify | `knowledge/memory/project-memory.md` |
| Modify | `knowledge/project/milestones.md`, `roadmap.md` |
| Create | `knowledge/snapshots/m3-complete.json` (optional) |

### Promotion criteria (full gate — spec §14)
```yaml
document_upload: green
parsing: green           # PDF, EPUB, DOCX each verified
versioning: green
document_service: green
memory_context_node: unchanged
graphstate: unchanged
conversation_system: unchanged
scope_creep: false
embeddings: zero_writes
documentation: complete
knowledge_updated: true
m3_tag: m3-complete
```

---

## Parallelization rules

| Allowed in parallel | Forbidden |
|---------------------|-----------|
| Phase 5 event tests while Phase 4 UI in progress **only if** Phase 3 API frozen | Two agents editing `service.py` |
| Documentation drafts after Phase 3 API frozen | Parser + API handler in same file without merge |
| Vitest component tests isolated per component | OpenAPI + service schema drift without sync |

---

## Builder packet template (per phase)

Each implementation wave should open with:

```text
SPEC: docs/superpowers/specs/2026-06-24-thesisos-m3-document-system-design.md (Frozen)
PHASE: N
BRANCH: m3-document-system
FORBIDDEN: embeddings, retrieval, /search, graph, chat injection, status=indexed
CRITIC: run checklist before PR
QA: pytest + vitest + scope_creep grep
```

### Scope creep grep (QA)

```bash
# Must return zero hits in M3 diff (excluding spec/plan/knowledge)
rg -i 'embed|vector|retriev|/search|indexed|retrieved_context' backend/app frontend/app --glob '!**/test_*'
```

---

## Risk register

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | Accidental retrieval via chunk list UI | Truncated preview; no search; Critic Phase 4 |
| R2 | Docling dependency weight / install time | Pin version; Docker layer cache; PDF fallback |
| R3 | Large PDF parse blocks event loop | BackgroundTasks + status=`processing` |
| R4 | `chunk_hash` collision | SHA-256 over doc_id+index+content; unique index per document |
| R5 | GCS unavailable in local dev | `DOCUMENT_STORAGE_BACKEND=local` adapter |
| R6 | M0 status enum drift | Migration maps parsing/error → processing/failed |

---

## References

- M2 plan pattern: `plans/m2-memory-system-plan.md`
- Frozen spec §2.1 (status), §5 (chunk_hash), §12 (parser boundary), §13 (Critic closed)
- ADR-0020, 0021, 0022
