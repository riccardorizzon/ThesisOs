# Document Architecture

> Sources: M3 spec (Frozen 2026-06-24), ADR-0020/0021/0022. **Status: spec frozen — implementation not started.**

## Design principle

Documents are **ingested sources**; chunks are **derived parse artifacts**. GCS holds originals; Postgres holds metadata and structured chunks. **`chunk_hash`** provides stable M4 reference. **No embeddings in M3.**

## Document vs Chunk

| Entity | Table | Role |
|--------|-------|------|
| **Document** | `documents` | Identity, metadata, GCS URI, status, version |
| **Chunk** | `chunks` (DTO: `DocumentChunk`) | Ordered text segments; `chunk_hash` stable across re-parse |

## Status lifecycle (M3)

```text
uploaded → processing → parsed | failed
indexed  → M4 only (forbidden in M3)
```

## Parser boundary

```yaml
primary_parser: docling      # pdf, docx, epub
fallback_parser: pymupdf     # pdf only
both_equal: false
```

## Storage

```text
GCS (*-thesisos-documents)  →  original bytes
Postgres documents          →  metadata + version
Postgres document_versions  →  append-only history
Postgres chunks             →  structured content
```

## Write path

```text
REST /upload, /documents/*  ──► DocumentService ──► documents, chunks, GCS
                                         ▲
                                   sole writer (ADR-0020)
```

## Query model (M3 — not retrieval)

- `GET /documents?q=` — ILIKE on title/filename only (ADR-0022)
- `GET /documents/{id}/chunks` — structural list by document_id, unranked
- **Forbidden:** `/search`, embeddings, RAG, chat injection

## M4 handoff

M4 reads `chunks` + writes `embeddings(owner_type=chunk)`. M3 sets status `parsed`; M4 sets `indexed`.

## UI

Document Administration UI at `/documents` — not a reader or notebook.
