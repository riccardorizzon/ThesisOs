# ADR-0018: Memory Query Model (Pre-Retrieval)

- Status: Accepted (2026-06-24)
- Context: M2 must make memory queryable without implementing M4 retrieval (embeddings, hybrid search, `/search`). A vague "search memories" requirement risks building a duplicate retrieval layer — a "poor man's retrieval" — or prematurely writing embeddings.
- Decision:
  1. **M2 query surface:** `GET /memory` with filters `kind`, `key`, `pinned`, `q`, `limit`, `offset`. **No** `GET /memory/search` or other dedicated search route.
  2. **`q` semantics:** case-insensitive substring match (`ILIKE`) over `title` and `content` in SQL — administrative list filtering only, not ranked retrieval.
  3. **Explicitly forbidden in M2:**

```yaml
semantic_search: forbidden
embeddings: forbidden          # no writes to embeddings table for memory
vector_index: forbidden        # no HNSW/IVFFlat on memories
retrieval: deferred_to_m4    # POST /search, retriever agent, retrieved_context
GET /memory/search: forbidden  # use GET /memory?q= only
```

  4. **M4 integration:** retriever reads `memories` (especially knowledge items) and optionally joins `embeddings WHERE owner_type='memory'`; it does not introduce a second memory index or shadow table.
  5. **Prompt loading** is separate from list query: `MemoryService.load_prompt_context()` fetches operational singletons by known keys (`editable`, pinned `user`/`thesis`) — not via `q`, and **never** `concept` or `citation` (masked-retriever boundary).
- Consequences: M2 delivers predictable, testable list/filter APIs without scope creep into retrieval. M4 can add semantic search without conflicting with M2 contracts. The cost is that `q` will not scale to large corpora — acceptable until M3/M4 ingestion exists.
- Alternatives considered: (a) pgvector cosine search in M2 — rejected (scope creep, Q1 index strategy deferred). (b) Postgres full-text search with tsvector — rejected for M2 (YAGNI; ILIKE sufficient for hundreds of memory rows). (c) `GET /memory/search` as alias — rejected (implies retrieval semantics; M4 owns search). (d) Client-side filter only — rejected (not API-queryable).
