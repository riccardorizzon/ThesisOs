# Document Architecture

> Sources: M3 spec (`docs/superpowers/specs/2026-06-24-thesisos-m3-document-system-design.md`), ADR-0020/0021/0022. **Status: spec draft — not implemented.**

## Design principle

Documents are **ingested sources**; chunks are **derived parse artifacts**. GCS holds originals; Postgres holds metadata and structured chunks. **No embeddings in M3.**

## Document vs Chunk

| Entity | Table | Role |
|--------|-------|------|
| **Document** | `documents` | Identity, metadata, GCS URI, parse status, version |
| **Chunk** | `chunks` (DTO: `DocumentChunk`) | Ordered text segments from parsing |

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
