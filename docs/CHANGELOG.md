# ThesisOS Product Changelog

All notable **product-track** changes (M0–M18). Platform-track (MB-series) changes
are recorded in milestone gates and ADRs unless they affect runtime behavior.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### M5 — Tool Router (in progress)

- Not started — awaiting Critic §12 sign-off on frozen M5 spec (ADR-0027).

---

## [M4 Recovery] — 2026-06-26

Product recovery sprint after dogfood revealed M4 passed CI but failed on real
thesis documents. **M4 pipeline frozen** after this release — see
`docs/m4-freeze.md`.

### Added

- **Grounding (P1):** `compose_prompt_wire()` merges memory prefix + retrieved
  sources into transient LLM wire; `sources` SSE events; `GraphState.citations`
  from retriever metadata.
- **Parser pipeline (P2):** Docker image installs `.[parsers]` + `contracts/`;
  Docling primary with `do_ocr=False` for born-digital PDFs; PyMuPDF fallback.
- **Embedding reliability (P3):** Deterministic batching under Vertex token caps;
  transient-only retries; `record_index_error()` for async indexing failures.
- **Markdown ingestion (P4):** Native `.md`/`.txt` via `MarkdownParser` sharing
  `markdown_to_chunks()` with Docling export path.
- **Dogfood:** `dogfood-m4.md`, `bin/dogfood-m4-run.sh`, `make dogfood-m4`.

### Fixed

- Retrieved chunks populated `GraphState.retrieved_context` but never reached the
  LLM prompt (answers from Gemini prior knowledge only).
- Single-request embedding exceeded Vertex limits on large documents (438 chunks).
- Background indexing failures logged but not surfaced on document records.
- Docker runtime missing parser deps and event catalog (`FileNotFoundError` on upload).
- Docling default OCR init failed in container (RapidOCR config error).

### Tests

- 53-test M4 recovery regression suite (grounding, embedding, markdown, parser,
  search, packaging, observability).

---

## [M4] — 2026-06-25 (`m4-complete`)

- Hybrid search (`POST /search`), pgvector partitions, `retriever` LangGraph node.
- Embedding pipeline, `indexed` document status, ADR-0024 ownership lines.

See `docs/m4-promotion.md` for original promotion gate.

---

## Earlier milestones

| Tag | Summary |
|-----|---------|
| `m3-complete` | Document upload, parse, chunk, events |
| `m2-complete` | Memory system, admin UI, `memory_context_node` |
| `m1-complete` | Streaming chat, LangGraph seam, Gemini SSE |
| `m0-complete` | Contracts, schema, infra shell |
