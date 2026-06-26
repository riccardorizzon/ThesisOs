# Dogfood M4 — Recovery Sprint Evidence

> **Date:** 2026-06-26  
> **Environment:** local Docker (`docker compose`), backend `:8000`, Vertex embeddings via ADC  
> **Scope:** End-to-end validation after M4 recovery (P1–P4). Not a promotion gate — product dogfood record.

## Sprint context

M4 passed CI but failed on real thesis documents. Recovery sprint addressed:

| Phase | Issue | Fix |
|-------|-------|-----|
| P1 Grounding | `retrieved_context` never reached LLM prompt | `compose_prompt_wire()` |
| P2 Parser | Docker missing deps; Docling OCR init failed | `.[parsers]`, `do_ocr=False`, contracts COPY |
| P3 Embedding | Single Vertex request exceeded token cap; async failures silent | Batched embed + `record_index_error` |
| P4 Markdown | No native `.md`/`.txt` ingestion | `MarkdownParser` + shared `markdown_to_chunks` |

## Regression suite (pre-dogfood)

```bash
# 53 tests — M4 recovery scope (2026-06-26)
pytest tests/test_grounding.py \
       tests/test_embedding_batching.py \
       tests/test_retrieval_service.py \
       tests/test_index_observability.py \
       tests/test_markdown_ingestion.py \
       tests/test_document_parsers.py \
       tests/test_document_service.py \
       tests/test_retriever_node.py \
       tests/test_search_api.py \
       tests/test_packaging.py
# Result: 53 passed
```

Re-run dogfood: `bin/dogfood-m4-run.sh`

---

## Workflow exercised

```text
upload → parse → embed/index → search → grounded chat → memory → follow-up chat
```

### Primary corpus

| Document | ID | Chunks | Parser | Status |
|----------|----|--------|--------|--------|
| **The Craftsman full markdown** | `c31abf2c-a069-4919-b7fb-5eeb6cbebc19` | 438 | markdown | indexed |
| Dogfood M4 Sennett excerpt | `8246a26d-f148-4594-9f13-8e2edb968e19` | 1 | markdown | indexed |

---

## Step-by-step evidence

### 1. Upload

```http
POST /upload  (dogfood_m4.md)
→ 201, source_type=markdown, status=uploaded
```

### 2. Index (background parse + embed)

Poll `GET /documents/{id}`:

```json
{
  "status": "indexed",
  "parser": "markdown",
  "chunk_count": 1,
  "error_message": null
}
```

Time to indexed: ~2 s (1-chunk document).

**Large document (438 chunks):** re-index validated in P3 — 14 embedding batches, all 438 vectors written, `status=indexed`.

### 3. Retrieve

```http
POST /search
{"query":"What is craftsmanship according to Sennett?","limit":5,"document_ids":["8246a26d-..."]}
```

Top hit for dogfood document:

```text
"Richard Sennett argues that craftsmanship is **the desire to do a job well for its own sake**."
document_title: "Dogfood M4 Sennett excerpt"
score: 0.43
```

### 4. Grounded chat

```http
POST /chat
{"message":"According to my uploaded Dogfood M4 document, how does Sennett define craftsmanship?"}
```

SSE events observed:

| Event | Evidence |
|-------|----------|
| `sources` | 10 chunks with `chunk_id`, `document_title`, `score` |
| `token` | Grounded answer citing `[5]` (dogfood doc) |
| `done` | `conversation_id` returned |

Sample assistant text:

```text
According to your "Dogfood M4 Sennett excerpt" document, Richard Sennett argues that
craftsmanship is "the desire to do a job well for its own sake" [5].
```

**Persistence check:** stored assistant messages do **not** contain `Sources:` blocks or raw chunk text (`Sources: False` in DB inspection).

### 5. Memory

```http
POST /memory
{"kind":"thesis","content":"This thesis discusses Richard Sennett's book The Craftsman...","pinned":true}
→ 201, key=thesis, pinned=true
```

Memory context is injected via `memory_context_node` (transient wire prefix); not persisted as user messages.

### 6. Follow-up chat

```http
POST /chat
{"conversation_id":"6505d8dd-...","message":"Why does Sennett think that motivation matters for skilled work?"}
```

Follow-up returned grounded answer with citations `[2, 3, 4, 7]`, drawing from indexed corpus (including *The Craftsman full markdown* chunks). Conversation history preserved across turns.

---

## Issues found / residual limits

| Item | Severity | Notes |
|------|----------|-------|
| Docling cold start ~26 s | Low | Operational; first PDF parse loads torch weights |
| Docker rebuild ~7–12 min | Low | Docling ML deps; not a runtime defect |
| Search `document_ids` filter | — | Use top-level `document_ids` in `SearchRequest`, not nested `filters` |
| Single chunk >14k est. tokens | Low | May still fail Vertex; needs chunk split (future) |
| UI does not display `sources` SSE | Medium | Backend emits events; frontend not wired (M6+ scope) |
| Legacy docs stuck at `parsed` | Low | Pre-P3 failures; re-upload or manual `/documents/{id}/index` |

---

## Commits (M4 recovery)

```text
054331a fix(m4): wire retrieved_context into LLM prompt via prompt_wire composer
4840a3f feat(m4): emit sources SSE events for grounded chat turns
dbc2921 feat(m4): propagate citation metadata from retrieved context to GraphState
b11640f fix(m4): package parser deps and contracts in backend Docker image
8f957b0 fix(m4): disable Docling OCR so primary PDF parsing works in Docker
7b777f1 test(m4): resolve Dockerfile path in packaging tests from any cwd
cad84b9 fix(m4): batch document embeddings under Vertex token limits
12e039b fix(m4): surface background indexing failures on the document record
b3a7968 feat(m4): add native markdown and plain-text document ingestion
10cac5d test(m4): add markdown ingestion regression tests and update format guards
```

---

## Verdict

**M4 recovery sprint: PASS for product dogfood.**

Thesis-scale markdown (438 chunks) indexes, retrieves, and grounds chat answers on document content — not only Gemini prior knowledge. The full upload→chat workflow is usable on real Sennett corpus.

**Next:** M5 Tool Router (per roadmap) — only after explicit product decision; recovery sprint complete.
