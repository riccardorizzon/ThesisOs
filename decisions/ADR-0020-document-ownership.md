# ADR-0020: Document Ownership Model

- Status: Accepted (2026-06-24)
- Context: M0 defines `documents` and `chunks` tables but no write path. M3 introduces ingestion. Without explicit ownership, original files could be orphaned in GCS, chunks could be written from API handlers or graph nodes directly, and M4 retrieval could fork a parallel document store.
- Decision:
  1. **`documents` + `document_versions` + `chunks` are the sole system of record** for ingested thesis sources. GCS holds **original bytes only**; Postgres holds metadata and structured chunks.
  2. **Document ≠ Chunk:** A `Document` is the durable identity of a source file (metadata, GCS pointer, parse status, version). A `Chunk` is a **derived, replaceable artifact** of parsing — owned by exactly one document, ordered by `chunk_index`, with no independent lifecycle in M3.
  3. **Write authority:** `DocumentService` is the **only** module that INSERT/UPDATE/DELETE on `documents`, `document_versions`, and `chunks`. API handlers, graph nodes, and future agents call `DocumentService` only — never SQLAlchemy sessions on these tables directly.
  4. **GCS authority:** `DocumentService` (or a dedicated storage adapter called exclusively from it) is the only writer to the `documents` bucket. Object keys are deterministic: `documents/{document_id}/original/{filename}`.
  5. **Read authority in M3:** REST `/documents` reads metadata; `GET /documents/{id}/chunks` lists chunks **by document_id only** (structural, not ranked). No cross-document query, no semantic search, no embedding reads.
  6. **Embeddings table:** **No writes** in M3. `owner_type=chunk` embeddings are M4 only.
- Consequences: M4 retriever consumes chunks produced here without re-parsing. Re-parse replaces all chunks for a document atomically under service control. The cost is a strict service boundary and parse orchestration complexity.
- Alternatives considered: (a) Storing chunk text in GCS — rejected (M4 needs SQL-addressable chunks for hybrid retrieval). (b) Chunk-level versioning table — rejected for M3 (document-level version + full chunk replace on re-parse is sufficient). (c) Direct API DB access — rejected (same pattern as ADR-0015 MemoryService).
