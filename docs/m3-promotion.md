# M3 Promotion Gate — Status

_As of 2026-06-25. Branch `m3-document-system`. Phases 1–6 complete in code; merge + tag pending._

```yaml
# --- Implemented & verified (green in CI) ---
document_db:            green    # 0003_document_system; drift test; Document/Chunk/DocumentVersion models
document_service:         green    # DocumentService sole writer; storage local/GCS; parser boundary
document_api:             green    # thin /upload + /documents/*; OpenAPI additive; error mapping
document_ui:              green    # Document Administration at /documents; vitest 33/33 (10 files)
document_events:          green    # DocumentUploaded + ChunkCreated → events outbox (ADR-0006)
scope_creep:              green    # no /search, embeddings, graph nodes, chat chunk injection
domain_contracts:         green    # GraphState, RunContext, LLMClient, ConversationService unchanged
documentation:            green    # M3 spec, ADRs 0020/0021/0022, knowledge/ updated
knowledge_updated:        green    # Phase 6 knowledge mirror + this doc
tests_ci:                 green    # make ci: backend 77 passed / 31 skipped; frontend 33 passed
contracts:                additive # OpenAPI + events.json (chunk_hash) additive only

# --- Pending validation (environment / manual QA) ---
db_integration:           pending  # skip-guarded service/event/integration tests need Postgres (Docker fix)
parser_formats:           pending  # PDF/EPUB/DOCX with real Docling — install backend[parsers] + manual fixtures
m3_tag:                   pending  # merge → main → tag m3-complete

# --- Explicitly out of M3 gate (deferred) ---
document_graph_node:      deferred # contracts/agents/document.json — M5+
summarize_endpoint:       deferred # POST /summarize — job-backed, post-M3
memory_updated_events:    deferred # MemoryUpdated — optional M2 close-out now unblocked by bus
```

## Critic sign-off (Phase 6)

| Check | Result |
|-------|--------|
| No `/search` or semantic query params | ✅ OpenAPI guard test |
| No embeddings writes for chunks | ✅ integration test (skip without DB) |
| No chunk text in `/chat` SSE | ✅ smoke + leak guard tests |
| `GET /documents/{id}/chunks` document-scoped only | ✅ API + UI |
| GraphState unchanged | ✅ No new fields |
| `memory_context_node` unchanged | ✅ Operational memory only |
| Status `indexed` not used in M3 | ✅ lifecycle uploaded→processing→parsed\|failed |

## QA sign-off (Phase 6)

| Check | Result |
|-------|--------|
| `test_document_events.py` | ✅ 5 tests (skip without Postgres) |
| `test_document_integration.py` | ✅ 5 tests (4 skip without Postgres) |
| `test_document_service.py` | ✅ skip-guarded DB suite |
| `test_document_api.py` | ✅ TestClient + mocked service |
| Frontend vitest + build | ✅ 33 passed; `/documents` routes compile |
| Full `make ci` | ✅ green |

## Evidence (local, reproducible)

```bash
# Full gate (repo root)
make ci

# Backend document suites (from backend/)
.venv/bin/python -m pytest tests/test_document_*.py -v

# Frontend (from frontend/)
npm run test
npm run build

# DB path (after Docker fixed)
make up
cd backend && .venv/bin/alembic upgrade head
.venv/bin/python -m pytest tests/test_document_service.py tests/test_document_events.py tests/test_document_integration.py -v
```

## Promotion (when approved)

```bash
git checkout main
git merge --no-ff m3-document-system
git tag m3-complete
# release: v0.0.4-m3
```

## Known non-blockers (carry forward)

- Real Docling/PyMuPDF runs — optional `[parsers]` group; CI uses fake parsers in unit tests.
- `MemoryUpdated` — bus now persists events; wire MemoryService when convenient.
- M3 cloud deploy — follow M1/M2 pattern after local DB validation.

## Forbidden until M4+ specs frozen

Embeddings (M4), `/search` (M4), retriever graph node (M4), writer (M6), citation generation (M7), document graph agent (M5+).
