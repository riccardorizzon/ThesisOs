# M4 Recovery Sprint — Final Report

> **Date:** 2026-06-26  
> **Status:** CLOSED  
> **Evidence:** `dogfood-m4.md`, `docs/CHANGELOG.md`, `docs/m4-freeze.md`  
> **Commits:** `054331a` … `b39fcbb` (11 recovery commits on `main`)

---

## 1. Initial objectives

The M4 Recovery Sprint was authorized after **dogfood on real thesis documents**
revealed that M4 passed CI but failed in production-like usage:

| Goal | Intent |
|------|--------|
| **Reliability** | Real documents upload, parse, embed, and index completely |
| **Grounding** | Chat answers drawn from uploaded corpus, not Gemini prior knowledge |
| **Observability** | Indexing failures visible to the user |
| **Minimal scope** | Product-first; no ASEP/M5 work; no GraphState schema changes |

---

## 2. Problems found during dogfood (pre-recovery)

| # | Symptom | Root cause |
|---|---------|------------|
| 1 | Chat answers generic; ignore thesis content | `conversation_node` never read `retrieved_context` |
| 2 | Large markdown thesis fails to index | All chunks embedded in one Vertex request → token limit |
| 3 | Upload succeeds but document unsearchable | Async embed failures logged only; status stays `parsed` |
| 4 | PDF parse always PyMuPDF in Docker | Missing `.[parsers]` + contracts; Docling OCR init crash |
| 5 | No native `.md` ingestion | M3 formats only; thesis corpus already in markdown |

---

## 3. Changes implemented (P1–P5)

### P1 — Grounding (`054331a`, `4840a3f`, `dbc2921`)

- `prompt_wire.compose_prompt_wire()` — memory + grounding in one transient system block
- SSE `sources` events; `GraphState.citations` propagation
- Tests: `test_grounding.py` (5), including persistence guard

### P2 — Parser Pipeline (`b11640f`, `8f957b0`, `7b777f1`)

- Docker: `.[parsers]`, native libs, `COPY contracts/`
- Docling: `do_ocr=False` for born-digital PDFs
- Tests: `test_packaging.py`, parser boundary unchanged

### P3 — Embedding Reliability (`cad84b9`, `12e039b`)

- `plan_embedding_batches()` — 14k token / 250 chunk caps
- `_embed_with_retry()` — transient retries only
- `record_index_error()` + async handler split
- Tests: `test_embedding_batching.py` (8), `test_retrieval_service.py` (+3), `test_index_observability.py` (2)

### P4 — Markdown (`b3a7968`, `10cac5d`)

- `MarkdownParser` + shared `markdown_to_chunks()`
- `VALID_SOURCE_TYPES` extended: `markdown`, `text`
- Tests: `test_markdown_ingestion.py` (5)

### P5 — Dogfood (`b39fcbb` + closure docs)

- `dogfood-m4.md`, hardened `bin/dogfood-m4-run.sh`
- `make dogfood-m4`, `make unit-m4-recovery`

---

## 4. Final validation results

| Check | Result |
|-------|--------|
| M4 recovery unit suite | **53/53 passed** |
| Dogfood workflow | **PASS** — upload → index → search → memory → chat → follow-up |
| *The Craftsman full markdown* (438 chunks) | `indexed`, 14 embed batches, search + grounded chat |
| Persistence | Assistant messages exclude raw `Sources:` blocks |
| Failure simulation | `parsed` + `index_failed:` message; zero partial embeddings |

---

## 5. Residual risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Chunk >14k est. tokens | Low | Document in backlog R4-M2; rare for current chunking |
| Legacy `parsed` documents | Low | Backlog R4-M1; manual re-index |
| No UI for `sources` SSE | Medium | Backlog R4-UX1; M6 workspace |
| Docling cold start / Docker build time | Low | Operational; backlog R4-OP1/2 |
| M5 graph rewire regression | Medium | Run `make dogfood-m4` after M5 changes |

---

## 6. Recommendations for M5 (Tool Router)

1. **Extend, don't rewrite** — add supervisor/planner/router *before* retriever; keep M4 nodes frozen per `docs/m4-freeze.md`.
2. **Route-aware grounding** — when `route=grounded_chat`, existing retriever path is sufficient (M5 spec §277); verify with dogfood after graph rewire.
3. **Dogfood as gate** — no M5 promotion without `make unit-m4-recovery` + `make dogfood-m4` green.
4. **Defer UX debt** — `sources` panel is not M5-blocking unless router work touches chat UI; schedule with M6 workspace.
5. **Critic §12 first** — unblock M5 spec sign-off before implementation; maintain product-first discipline.

---

## 7. M4 closure checklist

| Item | Status |
|------|--------|
| Working tree clean (M4 closure commits) | ✅ |
| Architecture + changelog updated | ✅ `docs/architecture.md`, `docs/CHANGELOG.md` |
| Residual backlog registered | ✅ `next-actions.md` § M4 Recovery |
| `bin/dogfood-m4-run.sh` reusable | ✅ exit codes + assertions + `make dogfood-m4` |
| M4 pipeline frozen | ✅ `docs/m4-freeze.md` |

**M4 Recovery Sprint: CLOSED. Authorized to resume product track with M5.**
