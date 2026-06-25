# M3 Phase 1 — Gate Report (DB)

_As of 2026-06-24. Branch `m3-document-system`. Scope: schema & domain models only._

## Phase 1 deliverables

| Deliverable | Path | Status |
|-------------|------|--------|
| Alembic migration | `backend/migrations/versions/0003_document_system.py` | ✅ |
| SQLAlchemy models | `backend/app/db/models.py` — `Document` extended, `DocumentVersion`, `Chunk.chunk_hash` | ✅ |
| Schema contract | `contracts/db/schema.sql` regenerated (16 domain tables) | ✅ |
| Model tests | `backend/tests/test_document_models.py` (7 tests) | ✅ |
| Import registry | `backend/tests/test_models_import.py` — `document_versions` | ✅ |

## Migration summary (`0003_document_system`)

**documents** (additive columns):
- `version` INTEGER NOT NULL DEFAULT 1
- `parser` VARCHAR(32)
- `parsed_at` TIMESTAMPTZ
- `chunk_count` INTEGER
- `error_message` TEXT

**Status alignment:** `parsing`→`processing`, `error`→`failed`

**document_versions** (new):
- Append-only history with `change_reason` (`metadata` \| `parse`)
- FK `document_id` → `documents` ON DELETE CASCADE
- Unique `(document_id, version)`

**chunks** (additive):
- `chunk_hash` VARCHAR(64) NOT NULL (backfill via SHA-256 per spec §5.2 for existing rows)
- Unique `(document_id, chunk_index)`
- Unique `(document_id, chunk_hash)`

**Indexes:** `idx_documents_status`, `idx_documents_updated_at`, `idx_document_versions_document_id`

## Promotion gate

```yaml
migration_up:     green_code    # 0003_document_system.py; pgcrypto backfill for existing chunks
drift_test:       green         # test_schema_snapshot_matches_models
m0_m1_m2_tests:   green         # 46 passed, 14 skipped
document_models:  green         # 7/7
ruff:             green
scope_creep:      green         # see Critic report
docker_apply:     pending       # rebuild backend + alembic upgrade head (env I/O error at gate time)
```

## Explicitly NOT in Phase 1 (deferred)

- DocumentService, parsers, GCS adapter
- REST `/upload`, `/documents` API
- Frontend Document Administration UI
- Events wiring
- Embeddings writes

## Next phase (blocked until Architect approval)

**Phase 2:** DocumentService + storage + parsers (Docling primary, PyMuPDF PDF fallback)
