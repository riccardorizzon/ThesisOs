# ThesisOS — M4 "Retrieval System" Design Spec

- **Date:** 2026-06-25
- **Status:** Frozen (Architect 2026-06-25) — **no M4 implementation until this spec + ADR-0024 are merged and Critic sign-off recorded.**
- **Scope:** Milestone M4 only — chunk embedding, hybrid search, `POST /search`, `retriever` graph node, `indexed` status. **NOT** writer, planner/router, multi-agent, citation generation, or Mem0.
- **Authors:** ThesisOS Builder Team
- **Builds on:** M3 Document System (tag `m3-complete`), M2 Memory, M1 Conversation seam; frozen `GraphState.retrieved_context`, `contracts/agents/retriever.json`, M0 `embeddings` table + pgvector
- **New ADR:** ADR-0024 Retrieval & Embedding Ownership

---

## 1. Vision

M4 closes the Knowledge OS loop between **ingestion (M3)** and **reasoning (M5+)**:

```text
Acquire (M3) → Organize (M3 chunks) → Index (M4) → Retrieve on demand (M4) → Use in agents (M5+)
```

The user can ask questions grounded in their uploaded corpus. Answers cite ranked chunks, not raw admin lists. Chat still does not bypass retrieval — chunks enter the LLM only through `retrieved_context` after hybrid search.

**Success criterion:** After uploading and parsing documents (M3), the user runs an embedding job (or automatic pipeline); documents reach `indexed`; `POST /search` returns ranked chunks; the `retriever` node populates `GraphState.retrieved_context` for downstream agents; **no change to GraphState field list**; M0–M3 suites stay green.

---

## 2. Scope & non-goals

### 2.1 In scope (M4 MUST ship)

| # | Deliverable |
|---|-------------|
| 1 | **`RetrievalService`** — sole writer for chunk embeddings; hybrid search API |
| 2 | **Embedding pipeline** — Vertex multilingual embeddings via `LiteLLMClient.embed()` |
| 3 | **pgvector indexes** — HNSW per `model` partition (ADR-0024) |
| 4 | **`POST /search`** — hybrid vector + keyword over chunks |
| 5 | **`retriever` LangGraph node** — reads route/messages; writes `retrieved_context` |
| 6 | **Document status `indexed`** — after successful embed for all chunks of a document |
| 7 | **Events** — optional `ChunkIndexed` additive to catalog (or reuse batch in logs only — default: no new event unless needed) |
| 8 | **Tests** — embedding idempotency, search ranking, empty corpus, `embed_failed`, drift |
| 9 | **Knowledge + promotion** — `docs/m4-promotion.md`, knowledge mirror |

### 2.2 Non-goals (hard boundary)

| Forbidden | Deferred to |
|-----------|-------------|
| Writer / draft generation | M6 |
| Planner / router / supervisor | M5 |
| `/summarize`, document graph agent | M3+ jobs / M5 |
| Memory embedding + search in chat wire (operational memory stays M2 path) | M4 optional phase / M15 |
| Mem0 auto-extraction | M15–M16 |
| Cross-corpus export without query | Never |
| GraphState schema changes | Frozen ADR-0007 |
| Re-parsing or chunk mutation in retrieval | DocumentService only |
| Search UI in `/documents` admin | Forbidden (ADR-0022) |

```yaml
writer: false
multi_agent: false
graphstate_new_fields: false
document_admin_search_box: false
chunk_direct_to_chat: false
```

---

## 3. Architecture

### 3.1 Component model

```text
┌─────────────────────────────────────────────────────────────────┐
│                         THESISOS RUNTIME (M4)                    │
│                                                                  │
│  POST /search ──► RetrievalService.search()                      │
│                         │                                        │
│                         ├── reads chunks + embeddings (SQL)      │
│                         ├── calls LiteLLMClient.embed() (query)  │
│                         └── returns ranked RetrievedChunk DTOs   │
│                                                                  │
│  Embedding job / pipeline ──► RetrievalService.embed_document()  │
│                         │                                        │
│                         ├── reads chunks (chunk_hash)            │
│                         ├── writes embeddings (owner_type=chunk) │
│                         └── DocumentService.mark_indexed() hook  │
│                                                                  │
│  LangGraph: retriever_node ──► RetrievalService.search()         │
│                         └── GraphState.retrieved_context         │
└─────────────────────────────────────────────────────────────────┘

DocumentService (M3)          RetrievalService (M4)
  sole writer: documents        sole writer: embeddings (chunk)
  sole writer: chunks           reader: chunks, documents
  parse / upload                hybrid search / embed pipeline
```

### 3.2 Service boundaries (normative)

| Table / concern | Owner | M4 access |
|-----------------|-------|-----------|
| `documents`, `chunks` | DocumentService | RetrievalService **read-only** |
| `embeddings` (`owner_type=chunk`) | RetrievalService | exclusive write |
| `documents.status` → `indexed` | DocumentService | updated via **`mark_indexed(document_id)`** called from RetrievalService after embed success |
| `GraphState.retrieved_context` | retriever node | set each retrieval turn |

---

## 4. Interfaces

### 4.1 REST — `POST /search`

Realizes OpenAPI stub (`x-milestone: M4`).

**Request (additive schema):**

```json
{
  "query": "string (required, min 1)",
  "limit": 10,
  "document_ids": ["uuid"] ,
  "source_types": ["pdf"],
  "hybrid_alpha": 0.5
}
```

- `document_ids` optional — scope search to subset (thesis chapter sources)
- Default: search all **indexed** documents
- **Forbidden:** returning chunks without scores; unbounded corpus dump

**Response:**

```json
{
  "results": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "chunk_hash": "sha256…",
      "score": 0.87,
      "content": "…",
      "document_title": "…",
      "page_from": 1,
      "page_to": 2
    }
  ],
  "query_embedding_model": "text-multilingual-embedding-002"
}
```

**Errors:** `400` empty query · `422` embed_failed · `200` with `results:[]` for no_results (not 404)

### 4.2 RetrievalService (Python)

| Method | Responsibility |
|--------|----------------|
| `embed_document(document_id, *, session?)` | Embed all chunks; idempotent on `chunk_hash`; call `mark_indexed` |
| `embed_chunks(chunk_ids, *, session?)` | Partial re-embed after re-parse |
| `search(query, filters, *, limit=10)` | Hybrid search → list of `RetrievedChunk` + metadata |
| `delete_embeddings_for_document(document_id)` | Cascade on document delete (called from DocumentService delete hook or event consumer — **design: synchronous hook from DocumentService.delete**) |

### 4.3 LangGraph — `retriever` node

Per `contracts/agents/retriever.json`:

- **Reads:** `messages` (last user text as query), `route`
- **Writes:** `retrieved_context: list[RetrievedChunk]` (chunk_id, score, content)
- **Errors:** `embed_failed`, `no_results` → append to `errors`, empty context

M4 graph topology (minimal):

```text
START → memory_context_node → retriever_node → conversation_node → END
```

`conversation_node` unchanged; it may optionally prepend retrieved context to wire (same transient pattern as memory — **not** persisted as user messages).

### 4.4 LiteLLMClient

Implement `embed(texts: list[str]) -> list[list[float]]` (currently `NotImplementedError`). Model from settings; must tag rows with `model` + `dimension`.

---

## 5. Data flow

### 5.1 Indexing pipeline

```text
Document status=parsed (M3)
        │
        ▼
RetrievalService.embed_document(id)
        │
        ├── FOR EACH chunk:
        │     IF embedding exists AND content_hash=chunk_hash → SKIP
        │     ELSE call Vertex embed → INSERT embeddings
        │
        ▼
DocumentService.mark_indexed(id)   # status=indexed, version++
        │
        ▼
(Optional) emit metric / log; no GraphState change
```

Trigger: **async job** post-parse (preferred) OR explicit `POST /documents/{id}/index` (admin). M4 spec default: **background job after parse completes** + manual re-index on reparse.

### 5.2 Search path

```text
POST /search { query }
        │
        ▼
embed query (Vertex)
        │
        ▼
SQL: vector score (pgvector, model partition)
   + keyword score (tsvector / ILIKE on chunk.content — hybrid)
        │
        ▼
weighted merge (hybrid_alpha)
        │
        ▼
return top-k RetrievedChunk
```

### 5.3 Re-parse interaction (M3 contract)

- M3 re-parse replaces chunk UUIDs; **`chunk_hash` stable** for unchanged text
- M4: delete orphan embeddings by old chunk_id; re-embed new rows; skip unchanged hashes

---

## 6. State machines

### 6.1 Document lifecycle (M3 + M4)

```text
uploaded → processing → parsed ──(M4 embed OK)──► indexed
              │              │
              └──── failed ◄─┘
```

- `indexed` **forbidden in M3**; M4 only
- Failed embed: remain `parsed`, set `error_message` on document or job record

### 6.2 Embedding row lifecycle

```text
(none) → pending → embedded
           │
           └── failed (retry / dead-letter in job table — M4 uses jobs stub or in-process)
```

---

## 7. Storage & indexing

### 7.1 Embeddings table (M0 — unchanged shape)

Uses existing columns: `owner_type`, `owner_id`, `model`, `dimension`, `embedding vector(768)`, `content_hash`.

**Chunk rows:** `owner_type='chunk'`, `owner_id=chunks.id`, `content_hash=chunks.chunk_hash`.

### 7.2 pgvector (Q1 resolution)

- **Partition** `embeddings` by LIST (`model`)
- **HNSW** index per partition (`vector_cosine_ops`)
- Queries **must** include `WHERE model = :active_model`
- Migration: `0004_retrieval_system` — partition setup + indexes; drift test update

### 7.3 Hybrid ranking

```text
score = alpha * vector_score + (1 - alpha) * keyword_score
```

Default `alpha=0.5`; configurable per request. Keyword leg: PostgreSQL `ts_rank` on `chunks.content` or fallback ILIKE for MVP.

---

## 8. Acceptance criteria (promotion gate preview)

```yaml
embedding_pipeline: green      # parsed doc → embeddings rows
idempotency: green             # same chunk_hash → no duplicate embed call
search_api: green              # POST /search ranked results
retriever_node: green          # populates retrieved_context
indexed_status: green          # documents reach indexed
graphstate: unchanged          # field list frozen
document_service: unchanged    # sole chunk writer
scope_creep: false             # no writer/planner/search UI
m0_m1_m2_m3_tests: green
documentation: complete
knowledge_updated: true
m4_tag: m4-complete
```

---

## 9. Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Vertex embed outage | `embed_failed` | Surface 422; document stays `parsed`; retry job |
| Dimension mismatch | migration guard | Partition per model; reject mixed queries |
| Empty corpus | `no_results` | 200 + empty list |
| Stale chunk after re-parse | orphan embeddings | Delete by document_id on reparse hook |
| Accidental chat injection | QA test | Assert chunk text not in `/chat` without retrieval |
| Scope creep: admin search box | UI review | Reject PR |

---

## 10. Migration strategy

| Phase | Deliverable |
|-------|-------------|
| **1 — DB** | `0004_retrieval_system`: partitions, HNSW, optional tsvector on chunks |
| **2 — Service** | `RetrievalService`, `LiteLLMClient.embed`, idempotent embed |
| **3 — API** | `POST /search`, optional index trigger |
| **4 — Graph** | `retriever_node`, extend `build_graph` |
| **5 — Jobs** | Wire embed after parse (BackgroundTasks → jobs stub interface) |
| **6 — Promotion** | Gate doc, tag `m4-complete` |

**Order:** Spec freeze (this doc) → implementation phases → **MB1 Phase 2** (engine runtime) may proceed after this freeze.

---

## 11. Relationship to Builder Engine (MB1)

Per ADR-0025, MB1 Phase 2 `schedule`/`sync` must not hard-code M4 retrieval semantics before this spec is frozen. M4 embedding validation stages (`embed`, `search-smoke`) register in CheckRunner **after** M4 implementation, not before.

---

## 12. Open questions (resolved in this spec)

| ID | Question | Resolution |
|----|----------|------------|
| Q-R1 | pgvector index strategy | Partition by `model`; HNSW per partition (ADR-0024) |
| Q-R2 | Who writes embeddings | RetrievalService |
| Q-R3 | Graph topology in M4 | Insert `retriever_node` before `conversation_node` |
| Q-R4 | Memory embeddings | Out of M4 core; chunk-only |
| Q-R5 | New GraphState fields | None — use `retrieved_context` |
| Q-R6 | Admin search UI | Forbidden |

---

## 13. Freeze record

- [x] M3 handoff contract (§10 M3 spec) honored
- [x] ADR-0024 accepted
- [x] GraphState frozen
- [x] Critic conditions: no admin search; no direct chunk→chat; DocumentService boundary preserved

- [x] Critic sign-off: 2026-06-25 — DocumentService boundary preserved; no GraphState fields; no admin search UI; chunk→chat only via `retrieved_context` (QA checklist §8)
- [x] Planner plan: `plans/m4-retrieval-system-plan.md` (2026-06-25)

**Implementation authorized:** Critic sign-off + Planner plan delivered.

---

## 14. References

- ADR-0002 Vertex Runtime · ADR-0006 Events · ADR-0007 GraphState · ADR-0020–0022 Document
- ADR-0024 Retrieval Ownership
- `docs/superpowers/specs/2026-06-24-thesisos-m3-document-system-design.md` §10
- `contracts/agents/retriever.json`
- Tag `m3-complete`
