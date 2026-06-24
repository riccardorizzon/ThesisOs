# ThesisOS — M3 "Document System" Design Spec

- **Date:** 2026-06-24
- **Status:** **Frozen** — Approved (Architect 2026-06-24; Critic 2026-06-24 with conditions applied)
- **Scope:** Milestone M3 only — document ingestion foundation (upload, parse, chunk, metadata, versioning, storage, admin UI). **NOT** embeddings, retrieval, RAG, chat injection, writer agents, or citation generation.
- **Authors:** ThesisOS Architect Agent
- **Builds on:** M2 Memory System (tag `m2-complete` on `main`; frozen: `/chat`, `ConversationService`, `GraphState`, `RunContext`, `LLMClient`, `memory_context_node`)
- **New ADRs:** 0020 (document ownership), 0021 (document versioning), 0022 (document query model)

---

## 1. Goals

M3 delivers the **document ingestion foundation** that M4 Retrieval (and later M6 Writer, M7 Citations) will consume.

**M3 MUST ship:**

1. **Import formats:** PDF, EPUB, DOCX — upload, store original bytes, parse to structured text.
2. **Three domain layers:**
   - **Document** — durable identity + metadata + GCS pointer + parse status + version
   - **Chunks** — ordered structured content derived from parsing (table `chunks`; DTO `DocumentChunk`)
   - **Versions** — append-only `document_versions` history (ADR-0021)
3. **`DocumentService`** — sole writer for `documents`, `document_versions`, `chunks`; sole orchestrator of GCS uploads and parse pipeline.
4. **REST API** — realize M0 stubs: `POST /upload`, `GET /documents`, `GET /documents/{id}`; add `PATCH /documents/{id}`, `DELETE /documents/{id}`, `GET /documents/{id}/chunks`, `GET /documents/{id}/versions`, `POST /documents/{id}/reparse`.
5. **Parsing stack** — Docling (primary for PDF/DOCX/EPUB where supported); PyMuPDF fallback for PDF; explicit error surface for unsupported/corrupt files.
6. **Events** — `DocumentUploaded`, `ChunkCreated` persisted to `events` (ADR-0006).
7. **Document Administration UI** — list, upload, detail (metadata + status + chunk count), version history, re-parse trigger, delete. **Not** a reader, notebook, or search workspace.
8. **Tests** — upload, parse, chunk persistence, versioning, API delegation, GCS mock/local, M0+M1+M2 suites stay green.
9. **Knowledge update** — `knowledge/` reflects M3 scope; `docs/m3-promotion.md` at implementation time.

**Success criterion:** A user uploads a PDF/EPUB/DOCX; the original survives in GCS; metadata and chunks persist in Postgres; version history is queryable; re-parse replaces chunks atomically; admin UI manages documents; **no chunk content reaches `/chat` or embeddings**; frozen contracts unchanged.

---

## 2. Non-goals (hard boundary)

M3 explicitly **does NOT** implement:

```yaml
embeddings: false          # no writes to embeddings table
vector_search: false       # no pgvector index strategy
retrieval: false           # no ranked chunk return across corpus
rag: false                 # no context assembly for LLM
writer: false              # no summarize/draft generation
citation: false            # no CSL-JSON / sources generation
chat_injection: false      # no document/chunk content in graph or /chat
graph_extension: false     # no new LangGraph nodes in M3
semantic_search: false
hybrid_search: false
POST /search: forbidden
GET /documents/search: forbidden
status_indexed: forbidden  # reserved for M4; M3 terminal success status is parsed
status_processing: m3_only # see §6.1 lifecycle
```

### 2.1 Document status lifecycle (normative)

M3 uses a **closed set** of status values. No other strings are valid on `documents.status`.

```yaml
# M3 statuses (allowed writes in M3)
uploaded:     # row + GCS object created; parse not started
processing:   # parse job running (DocumentService.parse in flight)
parsed:       # parse succeeded; chunks persisted — M3 terminal success
failed:       # parse failed; error_message set; no partial chunks retained

# M4-only (forbidden in M3 code paths)
indexed:      # embeddings written; search-ready — RESERVED FOR M4
```

```text
uploaded ──► processing ──► parsed
                │
                └──► failed
```

| Transition | Trigger | M3 allowed |
|------------|---------|------------|
| → `uploaded` | POST /upload completes GCS write | ✅ |
| `uploaded` → `processing` | parse/reparse starts | ✅ |
| `processing` → `parsed` | parse succeeds | ✅ |
| `processing` → `failed` | parse error | ✅ |
| `parsed` → `processing` | POST /reparse | ✅ |
| `failed` → `processing` | POST /reparse | ✅ |
| → `indexed` | embedding job | ❌ M4 only |

M0 enum included `parsing` and `error` — **M3 migration renames/maps:** `parsing`→`processing`, `error`→`failed`. `indexed` remains in enum for forward compatibility but **must not be set by M3**.

| Forbidden | Deferred to |
|-----------|-------------|
| Embedding generation (`embeddings` writes) | M4 |
| Hybrid / vector retrieval, `/search`, pgvector index | M4 |
| RAG, retriever agent, `retrieved_context` in GraphState | M4 |
| `POST /summarize` | M6 |
| Writer / router / supervisor agents | M5–M6 |
| Citation agent, `/citations` | M7 |
| Full document reader UI, annotation workspace, NotebookLM-like | M14+ |
| OCR for scanned PDFs (unless Docling handles as bonus) | M3 optional stretch / M14 |
| Changes to `GraphState`, `RunContext`, `LLMClient`, `ConversationService` | Frozen |
| LangGraph checkpoint schema changes | ADR-0012 |

If it is not on the Goals list, it does not belong in M3.

---

## 3. Document vs Chunk (ownership)

> **Critical distinction:** A Document is **identity + provenance**. A Chunk is **derived parse output**.

```text
┌─────────────────────────────────────────────────────────────────┐
│  Document (documents)                                             │
│  - One row per uploaded source file                             │
│  - Owns: title, author, source_type, gcs_uri, status, version   │
│  - System of record for "what file is this?"                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ 1 : N
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Chunk (chunks) — DTO name: DocumentChunk                       │
│  - Ordered segments (chunk_index)                               │
│  - Derived on each successful parse                             │
│  - Replaceable as a set on re-parse (not individually versioned)│
│  - No independent CRUD in M3 admin (except via re-parse/delete) │
└─────────────────────────────────────────────────────────────────┘
```

| Entity | Lifecycle | M3 user actions |
|--------|-----------|-----------------|
| **Document** | Created on upload; metadata editable; deleted cascades chunks + GCS object | Upload, edit metadata, delete, re-parse |
| **Chunk** | Created by parser; **all deleted and recreated** on re-parse | View list (admin); no manual edit |

**Document ≠ Memory:** `memories.concept` / `memories.citation` remain separate until M4+ linking. M3 may store optional `metadata.document_id` on memory rows later — **not in M3 scope**.

**Document ≠ Note:** `notes` table (M0) holds user annotations anchored to documents/chapters. M3 does not create notes during ingestion.

See **ADR-0020** for normative ownership rules.

---

## 4. Storage model

```text
                    UPLOAD PATH
                         │
    User file (PDF/EPUB/DOCX)
                         │
                         ▼
              ┌──────────────────────┐
              │  Cloud Storage (GCS)  │
              │  bucket: *-documents  │
              │  key: documents/      │
              │    {document_id}/       │
              │    original/{filename}│
              └──────────┬───────────┘
                         │ gcs_uri stored on document
                         ▼
              ┌──────────────────────┐
              │  Postgres (domain)    │
              │  documents            │  ← metadata, status, version
              │  document_versions    │  ← append-only snapshots
              └──────────┬───────────┘
                         │ parse (DocumentService)
                         ▼
              ┌──────────────────────┐
              │  Postgres             │
              │  chunks               │  ← structured text segments
              └──────────────────────┘
                         │
                         ✗ NO embeddings row in M3
                         ✗ NO chunk text in GCS (M3)
```

### 4.1 GCS (original files)

| Property | Value |
|----------|-------|
| Bucket | `{project_id}-thesisos-documents` (Terraform `storage.tf`) |
| Object layout | `documents/{document_id}/original/{sanitized_original_filename}` |
| Access | Backend service account `roles/storage.objectAdmin` |
| Local dev | MinIO or filesystem adapter with same key layout (env `DOCUMENT_STORAGE_BACKEND=gcs\|local`) |

Original bytes are **immutable** after upload. Re-parse reads the same GCS object. Replace file → new upload (new document_id) in M3.

### 4.2 Database (metadata)

M0 `documents` table extended additively:

| Column | Change | Notes |
|--------|--------|-------|
| `version` | **ADD** INTEGER NOT NULL DEFAULT 1 | Optimistic lock (ADR-0021) |
| `parser` | **ADD** VARCHAR(32) NULL | e.g. `docling`, `pymupdf` |
| `parsed_at` | **ADD** TIMESTAMPTZ NULL | Last successful parse |
| `chunk_count` | **ADD** INTEGER NULL | Denormalized for list UI |
| `error_message` | **ADD** TEXT NULL | Last parse failure |

Existing M0 columns retained: `title`, `author`, `source_type`, `original_filename`, `gcs_uri`, `status`, `page_count`, `language`, `metadata`.

### 4.3 Chunks (structured content)

M0 `chunks` table extended additively:

| Column | Change | Notes |
|--------|--------|-------|
| `chunk_hash` | **ADD** VARCHAR(64) NOT NULL | Stable content identity for M4 (§5.2) |

Existing M0 columns retained: `document_id`, `chunk_index`, `content`, `token_count`, `page_from`, `page_to`, `section_path`, `metadata`, `created_at`.

No rename to `document_chunks` (avoid breaking M0 contract); domain DTO is `DocumentChunk`.

Unique index: `(document_id, chunk_index)` and `(document_id, chunk_hash)` — hash unique per document at a given parse generation.

### 4.4 document_versions (new table)

```sql
document_versions (
  id              UUID PK,
  document_id     UUID FK → documents ON DELETE CASCADE,
  version         INTEGER NOT NULL,
  title           TEXT NOT NULL,
  author          TEXT,
  source_type     VARCHAR(16) NOT NULL,
  page_count      INTEGER,
  chunk_count     INTEGER,
  parser          VARCHAR(32),
  metadata        JSONB NOT NULL DEFAULT '{}',
  changed_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  change_reason   VARCHAR(16) NOT NULL  -- 'metadata' | 'parse'
)
```

Append-only. Unique `(document_id, version)`.

---

## 5. Chunk contract

Normative DTO — **defined now for M4**, implemented in M3 without embeddings:

```python
class DocumentChunk(BaseModel):
    """Domain chunk — maps to table `chunks`. No embedding fields in M3."""

    id: str                          # UUID; NOT stable across re-parse
    document_id: str                 # FK — parent document
    chunk_index: int                 # 0-based order within document
    chunk_hash: str                  # SHA-256 hex; stable across re-parse if content unchanged (§5.2)
    content: str                     # Plain/markdown text segment
    page_from: int | None = None     # Source page start (PDF/EPUB)
    page_to: int | None = None       # Source page end
    section_path: str | None = None  # e.g. "Chapter 2 > Methods"
    token_count: int | None = None   # Estimated tokens (chars/4 or tiktoken)
    metadata: dict = Field(default_factory=dict)  # parser hints, heading level
    created_at: datetime
```

### 5.1 Chunking rules (M3)

| Rule | Value |
|------|-------|
| Strategy | Structure-aware (headings, pages) via Docling; fallback fixed-size window with overlap if structure unavailable |
| Target size | ~512–1024 tokens per chunk (config constant) |
| Overlap | 64 tokens when sliding window used |
| Ordering | `chunk_index` monotonic 0..N-1 within document |
| Empty content | Skip; do not insert zero-length chunks |

### 5.2 Chunk identity and M4

```yaml
chunk_uuid_stable_across_reparse: false
chunk_hash_stable_across_reparse: true   # when content + index unchanged
```

**`chunk_hash` algorithm (normative):**

```text
normalized = content.strip().replace("\r\n", "\n")
chunk_hash = sha256(f"{document_id}:{chunk_index}:{normalized}").hexdigest()
```

M4 embeddings, citations, and retrieval caches **should key on `chunk_hash`**, not `chunks.id`. Re-parse generates new UUIDs but preserves hashes for unchanged segments — avoiding unnecessary re-embedding.

`ChunkCreated` event payload may include `chunk_hash` (additive events.json update in implementation).

---

## 6. Versioning strategy

See **ADR-0021**. Summary:

1. **`documents.version`** — fast read + optimistic lock for metadata PATCH.
2. **`document_versions`** — append-only history.
3. **Metadata PATCH** — requires `expected_version`; mismatch → `409 write_conflict`.
4. **Parse completion** — bump version, append version row with `change_reason=parse`, set `chunk_count`, `page_count`, `parsed_at`.
5. **Re-parse** — delete all chunks for `document_id`, insert new set, single transaction.
6. **Restore** — deferred (`restore_version: false` in M3).

---

## 7. DocumentService (single writer)

Mirror **MemoryService** pattern (ADR-0015, M2 spec §4).

```text
POST /upload          ──┐
REST /documents/*     ──┼──► DocumentService ──► documents
POST .../reparse      ──┤         │              document_versions
                        │         ├──► GCS adapter (original bytes)
                        │         └──► Parser pipeline → chunks
Graph (M5+)           ──┘              (future; not wired in M3)
```

### 7.1 Public methods (sketch)

| Method | Responsibility |
|--------|----------------|
| `upload(file, metadata?)` | Create document row, upload GCS, emit `DocumentUploaded`, enqueue/trigger parse |
| `get(id)` / `list(filters)` | Read metadata |
| `update(id, patch, expected_version)` | Metadata PATCH + version snapshot |
| `delete(id)` | Delete chunks, document_versions, document, GCS object |
| `parse(document_id)` | Load from GCS, run parser, replace chunks, update status |
| `reparse(document_id)` | Public alias for `parse` after user action |
| `list_chunks(document_id)` | Ordered chunks — structural read only |
| `list_versions(document_id)` | Version history |

**No method** named `search`, `retrieve`, `embed`, or `rank`.

### 7.2 Parse pipeline

Uses status lifecycle from §2.1.

```text
status: uploaded → processing → parsed | failed

1. SET status=processing
2. Download bytes from gcs_uri
3. Parse via Parser Boundary (§12) — primary Docling; PDF fallback PyMuPDF only
4. Extract: title (if missing), author, page_count, language (best-effort)
5. Chunk structured text → DocumentChunk[] with chunk_hash computed per §5.2
6. TX: DELETE chunks WHERE document_id; INSERT new chunks;
        UPDATE documents SET status=parsed, version++, chunk_count, ...
        INSERT document_versions (change_reason=parse)
   ON ERROR: SET status=failed, error_message=...; ensure zero chunks remain
7. Emit ChunkCreated per chunk (or batch event — see §8)
```

Parse runs **asynchronously** after upload returns (FastAPI `BackgroundTasks` or jobs stub — must not block `/upload` for large PDFs). Upload response: `{ document_id, status: "uploaded" }` then background transitions to `processing`.

---

## 8. Events

Per `contracts/events/events.json`:

```json
{ "name": "DocumentUploaded", "payload": { "document_id": "uuid" } }
{ "name": "ChunkCreated", "payload": { "chunk_id": "uuid", "document_id": "uuid" } }
```

M3 may batch `ChunkCreated` into a single event with `chunk_ids[]` if event volume is high — requires additive events.json update and ADR note. Default: one event per chunk (simplest, matches catalog).

---

## 9. REST API

Additive realization of M0 OpenAPI stubs. Handlers **delegate to DocumentService only**.

| Method | Path | M3 behavior |
|--------|------|-------------|
| POST | `/upload` | Multipart file + optional title/author; returns document_id, status=uploaded (→ processing async) |
| GET | `/documents` | List; filter `source_type`, `status`; `q=` ILIKE on title/filename only (ADR-0022) |
| GET | `/documents/{id}` | Metadata + chunk_count; no ranked chunks |
| PATCH | `/documents/{id}` | Metadata only; `expected_version` required |
| DELETE | `/documents/{id}` | Cascade delete |
| GET | `/documents/{id}/chunks` | All chunks, ordered by chunk_index — **unranked, document-scoped** |
| GET | `/documents/{id}/versions` | Version history |
| POST | `/documents/{id}/reparse` | Trigger parse again from GCS original |

**Not exposed in M3:** `/search`, `/summarize`, `/documents/search`, semantic query params.

Error codes: `document_not_found`→404, `write_conflict`→409, `parse_failed`→422, `unsupported_format`→400.

---

## 10. Future retrieval integration (M4 contract)

M3 deliberately stops at **ingestion + structural storage** so M4 can layer retrieval without rework:

| Concern | M3 (this milestone) | M4 (retrieval) |
|---------|---------------------|----------------|
| Chunk storage | `chunks` table, full content | Read same table |
| Query | `GET /documents/{id}/chunks` only | `POST /search` hybrid vector + keyword |
| Embeddings | None | `embeddings(owner_type=chunk, owner_id=...)` |
| GraphState | Unchanged | `retrieved_context` populated by retriever node |
| Status | `parsed` | `indexed` after embedding job |
| Chat | No document content | Retrieved chunks appended separately from memory |

**M4 integration rule:** Retriever reads chunks produced by M3; must not re-parse or fork a parallel chunk store. Document CRUD remains exclusively via `DocumentService`.

---

## 11. Document Administration UI

**Not a reader. Not a notebook.** Admin tooling only — mirror Memory Administration UI pattern.

| Screen | Behavior |
|--------|----------|
| **List** (`/documents`) | Table: title, type, status, chunk_count, updated_at; filter by status/type; `q=` on title |
| **Upload** (`/documents/upload`) | Drag-drop or file picker; PDF/EPUB/DOCX; shows parsing spinner |
| **Detail** (`/documents/[id]`) | Metadata edit (PATCH with version); parse status/error; chunk count; link to chunk list |
| **Chunks** (`/documents/[id]/chunks`) | Paginated table: index, page_from/to, section_path, content preview (~200 chars) — **verification only, not search** |
| **Versions** | Read-only list from `/documents/{id}/versions` |
| **Actions** | Re-parse, Delete |

No in-browser PDF renderer, no full-text highlight search, no chat sidebar, no AI summarize button.

---

## 12. Parser boundary (normative)

**There is one authoritative parser and one subordinate fallback. They are not equal.**

```yaml
primary_parser:
  name: docling
  formats: [pdf, docx, epub]
  authority: normative
  responsibilities:
    - structure detection (headings, sections)
    - metadata extraction (title, author where available)
    - chunk boundary selection
    - page mapping where supported

fallback_parser:
  name: pymupdf
  formats: [pdf]
  authority: subordinate
  invoked_when:
    - source_type is pdf AND docling raises ParseError
    - OR source_type is pdf AND docling returns zero extractable text
  responsibilities:
    - plain text extraction only
    - fixed-size chunking with overlap (§5.1 sliding window)
  forbidden_for: [docx, epub]   # no fallback; failure → status=failed

both_equal: false
```

| Format | Path | `documents.parser` value |
|--------|------|--------------------------|
| PDF | Docling → (on failure) PyMuPDF | `docling` or `pymupdf` |
| DOCX | Docling only | `docling` |
| EPUB | Docling only | `docling` |

Parser module layout (implementation): `app/services/document/parsers/docling_parser.py`, `pymupdf_parser.py`; orchestrated only from `DocumentService.parse()` — never from API handlers.

Dependencies added in M3 implementation phase only (`docling`, `pymupdf`). Pin versions in `pyproject.toml`.

---

## 13. Critic review (gate — closed)

> **Question:** Could this design accidentally become retrieval?

### Verdict: **NO** — approved (Critic 2026-06-24).

Conditions applied before freeze:
1. Parser boundary explicit (§12) — Docling primary, PyMuPDF PDF-only fallback; `both_equal: false`.
2. `chunk_hash` on `DocumentChunk` (§5) — stable M4 reference key.
3. Status lifecycle closed set (§2.1) — `indexed` reserved for M4.

**Retrieval accident guardrails (must remain in implementation):**

```yaml
embeddings: forbidden
vector_columns: forbidden      # no new vector cols on chunks/documents in M3
retrieval_routes: forbidden
graph_integration: forbidden
chat_integration: forbidden
status_indexed: forbidden      # M4 only
```

| Risk vector | Mitigation in spec | Accidental retrieval if violated? |
|-------------|-------------------|-----------------------------------|
| `GET /documents/{id}/chunks` | Document-scoped, unranked, admin-only purpose | Would become retrieval if exposed to chat or ranked by relevance |
| `GET /documents?q=` | ILIKE on title/filename only — same as M2 memory list | Would become retrieval if extended to chunk `content` |
| Chunk preview in UI | Truncated preview for parse verification | Would become retrieval if UI adds corpus search box |
| Large chunk count | Pagination on chunk list | Low risk |
| `POST /summarize` M0 stub | Explicitly non-goal | **Yes** — must not implement |
| Embeddings table exists (M0) | No writes in M3 | **Yes** — if M3 populates embeddings |
| `GraphState.retrieved_context` | No graph changes | **Yes** — if M3 adds retriever node |
| Status `indexed` | Forbidden in M3 (§2.1) | **Yes** — implies search-ready index |

### Critic sign-off

```yaml
critic: approved
date: 2026-06-24
risk: low
implementation: forbidden_until_planner_gate
```

Implementation PR must still satisfy conditions 1–4 below. QA verifies guardrails on every phase.

1. Implementation PR must not add `/search`, embedding jobs, or graph nodes.
2. QA must assert no chunk content in `/chat` responses or `memory_context_node` wire.
3. OpenAPI review must reject any endpoint returning ranked/scored chunks.
4. `GET /documents/{id}/chunks` must require `document_id` path param — no bulk export across corpus without id list.

**If any condition fails during implementation → stop and revise spec or code.**

---

## 14. Promotion gate (preview)

M3 complete only when all true:

```yaml
document_upload: green       # POST /upload → GCS + documents row
parsing: green               # PDF/EPUB/DOCX → chunks for each format
versioning: green            # document_versions + optimistic lock
persistence: green           # survives restart
document_service: green      # sole writer enforced (no API direct DB)
api_tests: green
m0_m1_m2_tests: green
graphstate: unchanged
conversation_system: unchanged
scope_creep: false           # §2 non-goals
embeddings: zero_writes      # assert COUNT(embeddings WHERE owner_type=chunk)=0 or unchanged
documentation: complete
knowledge_updated: true
frontend: admin_green          # list, upload, detail, chunks preview, versions
events: green                # DocumentUploaded, ChunkCreated
```

---

## 15. Implementation sequencing (Planner)

**Spec frozen 2026-06-24.** See `plans/m3-document-system-plan.md`.

---

## 16. Open questions (resolved in this spec)

| ID | Question | Resolution |
|----|----------|------------|
| Q-D1 | Table name `chunks` vs `document_chunks` | Keep M0 `chunks`; DTO `DocumentChunk` |
| Q-D2 | Sync vs async parse | Async after upload returns |
| Q-D3 | Chunk UUID stability | Not stable; use `chunk_hash` for M4 keys |
| Q-D6 | Parser authority | Docling primary; PyMuPDF PDF fallback only (§12) |
| Q-D7 | Status values | §2.1 lifecycle; `indexed` M4-only |
| Q-D4 | OCR for scanned PDF | Out of M3 core; Docling may partially help |
| Q-D5 | Local dev without GCS | `DOCUMENT_STORAGE_BACKEND=local` adapter |

---

## 17. References

- ADR-0001 Contract-First
- ADR-0006 Event Driven
- ADR-0007 State Contract (GraphState frozen)
- ADR-0012 External Infrastructure Schemas
- ADR-0015 Memory Ownership (service pattern precedent)
- ADR-0018 Memory Query Model (list vs retrieval precedent)
- ADR-0020 Document Ownership (new)
- ADR-0021 Document Versioning (new)
- ADR-0022 Document Query Model (new)
- `contracts/agents/document.json`
- `contracts/events/events.json`
- `contracts/db/schema.sql` (M0 documents + chunks)
- `docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md`
- Tag `m2-complete`
