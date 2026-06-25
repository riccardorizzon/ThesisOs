# M4 Retrieval System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Each phase has explicit promotion criteria — do not start the next phase until the current phase gate passes. **Critic + QA mandatory every phase.**

**Goal:** Ship chunk embedding, hybrid search, `POST /search`, `retriever` LangGraph node, and `indexed` document status — **without** writer/planner agents, GraphState schema changes, admin search UI, or chunk injection into `/chat`.

**Architecture:** `RetrievalService` sole writer for chunk embeddings; reads chunks/documents read-only; `DocumentService.mark_indexed()` hook after embed success; hybrid vector + keyword ranking; pgvector HNSW per model partition (ADR-0024).

**Tech Stack:** FastAPI, SQLAlchemy 2 async, Alembic, pgvector, LiteLLM/Vertex embeddings, LangGraph, pytest/httpx, Vitest.

**Spec:** `docs/superpowers/specs/2026-06-25-thesisos-m4-retrieval-system-design.md` (Frozen 2026-06-25)  
**ADRs:** 0024 (retrieval ownership), 0020–0022 (document boundaries preserved)

**Branch:** `m4-retrieval-system` (from `main` @ `m3-complete` / MB1 Phase 2).  
**Conventions:** TDD where practical, additive contract changes only, M0–M3 + builder_engine tests green after every phase.

**Forbidden in all phases:** GraphState new fields, `/documents` search box, chunk text in `/chat` without retrieval, DocumentService embedding writes, writer/planner nodes.

---

## Phase 1 — DB: partitions, HNSW, hybrid search columns

### Objective
Migration `0004_retrieval_system`: LIST-partition `embeddings` by `model`, HNSW per default model partition, tsvector/GIN on `chunks.content` for keyword leg, indexes for `(owner_type, owner_id, content_hash)`.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/migrations/versions/0004_retrieval_system.py` |
| Modify | `contracts/db/schema.sql` |
| Modify | `backend/tests/test_schema_snapshot.py` if needed |
| Create | `backend/tests/test_retrieval_migration.py` |

### Migration notes
- Convert or recreate `embeddings` as partitioned parent + default partition for `text-multilingual-embedding-002`
- HNSW: `USING hnsw (embedding vector_cosine_ops)` on default partition
- Add `chunks.content_tsv tsvector` generated column OR functional GIN index
- Unique partial index: `(owner_type, owner_id, model) WHERE owner_type='chunk'` for idempotency

### Tests
- Migration up/down on empty DB
- `test_schema_snapshot.py` green
- Integration (when Docker available): partition exists, index names match snapshot

### Critic checklist (Phase 1)
- [ ] No GraphState / OpenAPI breaking changes
- [ ] DocumentService tables unchanged except additive chunk search column
- [ ] `indexed` status not defaulted on existing rows

### Promotion criteria
```yaml
migration_up: green
drift_test: green
m0_m1_m2_m3_tests: green
unit_builder_engine: green
```

---

## Phase 2 — RetrievalService + LiteLLM embed

### Objective
Implement `RetrievalService` with `embed_document`, `embed_chunks`, `delete_embeddings_for_document`; wire `LiteLLMClient.embed()`; idempotent on `chunk_hash`.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/schemas/retrieval.py` — `RetrievedChunk`, search DTOs |
| Create | `backend/app/services/retrieval/__init__.py` |
| Create | `backend/app/services/retrieval/service.py` |
| Create | `backend/app/services/retrieval/exceptions.py` |
| Modify | `backend/app/llm/litellm_client.py` — implement `embed()` |
| Modify | `backend/app/services/document/service.py` — `mark_indexed()`, delete hook |
| Create | `backend/tests/test_retrieval_service.py` |
| Create | `backend/tests/test_litellm_embed.py` |

### Public API (service)
| Method | Notes |
|--------|-------|
| `embed_document(document_id)` | All chunks; skip unchanged `content_hash`; call `mark_indexed` |
| `embed_chunks(chunk_ids)` | Partial re-embed after re-parse |
| `search(query, filters, limit)` | Hybrid merge (Phase 3 may split API layer) |
| `delete_embeddings_for_document(document_id)` | Called from DocumentService.delete |

### Tests
- Idempotency: second embed skips Vertex when hash unchanged
- Re-parse: orphan embeddings removed; stable hash skipped
- `embed_failed` surfaces 422; document stays `parsed`
- M3 test `test_embeddings_zero_writes_after_ingestion` still passes pre-index

### Critic checklist (Phase 2)
- [ ] DocumentService remains sole chunk writer
- [ ] No `/search` route yet (service-only)
- [ ] Embedding rows tagged with model + dimension

### Promotion criteria
```yaml
retrieval_service_unit: green
embed_idempotency: green
mark_indexed_hook: green
m0_m1_m2_m3_tests: green
```

---

## Phase 3 — REST `POST /search` + index trigger

### Objective
Thin FastAPI routes; OpenAPI additive schemas; optional `POST /documents/{id}/index` admin trigger.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/api/search.py` |
| Modify | `backend/app/api/documents.py` — index trigger (optional) |
| Modify | `contracts/openapi/openapi.yaml` — `/search` request/response |
| Create | `backend/tests/test_search_api.py` |

### Tests
- Empty query → 400
- No corpus → 200 + `results: []`
- Ranked results include score, chunk_id, document metadata
- Scoped `document_ids` filter works

### Critic checklist (Phase 3)
- [ ] No admin list endpoint ranking changes
- [ ] No search UI in frontend `/documents`

### Promotion criteria
```yaml
search_api: green
openapi_drift: green
m0_m1_m2_m3_tests: green
```

---

## Phase 4 — LangGraph `retriever_node`

### Objective
Insert `retriever_node` between `memory_context_node` and `conversation_node`; populate `retrieved_context` per `contracts/agents/retriever.json`.

### Files affected
| Action | Path |
|--------|------|
| Create | `backend/app/graph/nodes/retriever.py` |
| Modify | `backend/app/graph/build.py` — topology update |
| Create | `backend/tests/test_retriever_node.py` |
| Modify | `backend/tests/test_conversation_graph.py` |

### Tests
- Last user message used as query
- `no_results` → empty context + error entry
- `embed_failed` → error entry; conversation continues
- GraphState field list unchanged

### Promotion criteria
```yaml
retriever_node: green
graph_topology: green
m0_m1_m2_m3_tests: green
```

---

## Phase 5 — Embed job wiring post-parse

### Objective
Background embed after parse completes; re-index on reparse; jobs stub interface (ADR-0009 pattern).

### Files affected
| Action | Path |
|--------|------|
| Modify | `backend/app/services/document/service.py` — enqueue embed after parse |
| Modify | `backend/app/services/jobs/queue.py` or in-process BackgroundTasks |
| Create | `backend/tests/test_embed_pipeline.py` |

### Tests
- Parse → embed job scheduled (mock Vertex)
- Failed embed leaves `parsed`
- Successful embed → `indexed`

### Promotion criteria
```yaml
embed_pipeline: green
indexed_status: green
m0_m1_m2_m3_tests: green
```

---

## Phase 6 — Promotion gate + tag

### Objective
`docs/m4-promotion.md`, knowledge mirror, builder CheckRunner stages `embed` + `search-smoke`, tag `m4-complete`.

### Files affected
| Action | Path |
|--------|------|
| Create | `docs/m4-promotion.md` |
| Modify | `builder_engine/checks.py` — register M4 stages (post-implementation only) |
| Modify | knowledge mirror per ADR-0010 pattern |

### Promotion criteria
```yaml
embedding_pipeline: green
idempotency: green
search_api: green
retriever_node: green
indexed_status: green
graphstate: unchanged
document_service: unchanged
scope_creep: false
m0_m1_m2_m3_tests: green
documentation: complete
knowledge_updated: true
m4_tag: m4-complete
```

---

## Wave / builder integration

After Phase 2+, optional `plans/builder/STATE.yaml` epic `m4-retrieval-system` with packets mirroring phases. Use `builder-engine schedule` / `sync` for implementer packets with `checks: ["unit", "drift"]`.

**CheckRunner M4 stages** (`embed`, `search-smoke`) register only in Phase 6 — not before service exists (M4 spec §11).

---

## References

- `decisions/ADR-0024-retrieval-ownership.md`
- `contracts/agents/retriever.json`
- Tag `m3-complete`
- `docs/mb1-phase2-gate.md` — engine runtime ready for M4 validation stages
