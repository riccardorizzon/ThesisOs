# ADR-0024: Retrieval & Embedding Ownership

- Status: Accepted (frozen 2026-06-25)
- Context: M3 delivers parsed chunks and stable `chunk_hash` keys but no embeddings or ranked search. M4 must add hybrid retrieval without duplicating chunk storage, breaking the M3 DocumentService boundary, or changing frozen GraphState fields.
- Decision:
  1. **`RetrievalService` is the sole writer** for `embeddings` rows where `owner_type='chunk'` (and later `'memory'`). It reads `chunks` and `documents` via SQL joins only — never mutates chunks or re-parses.
  2. **`DocumentService` remains the sole writer** for `documents`, `chunks`, and document lifecycle. M4 may transition `documents.status` from `parsed` → `indexed` only through a narrow hook called by the embedding pipeline (same transaction boundary as embedding success).
  3. **Hybrid search** is exposed only via `POST /search` (OpenAPI M4). Admin list endpoints stay unranked (ADR-0022 precedent). No corpus search box in document admin UI.
  4. **Embedding model tagging:** every row stores `model`, `dimension`, `content_hash` (from `chunk_hash` for chunks). Default model: Vertex `text-multilingual-embedding-002` @ 768d (ADR-0002).
  5. **pgvector strategy:** one **HNSW index per `model` partition** (list partition on `embeddings.model`). Queries always filter `WHERE model = :active_model` so dimensions never mix.
  6. **Graph integration:** `retriever` LangGraph node calls `RetrievalService.search()` and writes `GraphState.retrieved_context` (existing field — no GraphState change). Retrieved text is transient wire content like M2 memory injection — not persisted as chat messages by default.
  7. **Idempotency:** re-embedding skips rows where `content_hash` unchanged; M3 re-parse with same segment hash avoids redundant Vertex calls.
- Consequences: Clear ownership lines; M3 ingestion remains stable; M4 can evolve ranking and embedding jobs without forking stores. Cost: embedding pipeline + index migrations add operational complexity; model swaps require new partition + backfill job.
- Alternatives considered:
  - DocumentService owns embeddings — rejected (mixes ingestion with retrieval concerns).
  - Single global pgvector index — rejected (model/dimension swaps become painful; M0 Q1 resolution).
  - Populate `/chat` by reading chunks directly — rejected (bypasses retrieval ranking and scope controls).
