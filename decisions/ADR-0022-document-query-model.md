# ADR-0022: Document Query Model (M3)

- Status: Proposed (2026-06-24) — pending M3 spec freeze
- Context: M2 ADR-0018 forbade masked retrieval in memory. M3 introduces chunks — the highest-risk milestone for accidental RAG. List/filter semantics must be frozen before implementation.
- Decision:
  1. **Admin list query:** `GET /documents?q=` — ILIKE substring on `title` and `original_filename` only. No full-text on chunk `content`. No ranking score.
  2. **Structural reads:** `GET /documents/{id}`, `GET /documents/{id}/chunks`, `GET /documents/{id}/versions` — keyed by document id; chunks ordered by `chunk_index` ascending.
  3. **Forbidden in M3:**
     - `GET /documents/search`, `POST /search`, hybrid/vector endpoints
     - Query parameters: `semantic`, `embedding`, `similarity`, `top_k`, `rerank`
     - Any API that accepts natural-language questions and returns ranked chunks
     - Writes to `embeddings` table
     - Population of `GraphState.retrieved_context`
  4. **Chunk content in API responses:** Allowed for admin detail/debug (`GET .../chunks`) — this is **not retrieval** because it is document-scoped, unranked, and not injected into chat. **Forbidden:** injecting chunk lists into `/chat` or graph nodes in M3.
  5. **Status `indexed`:** Reserved for M4. M3 terminal success status is **`parsed`** only.
- Consequences: M3 admin UI can show chunk preview per document without becoming a reader/RAG surface. M4 adds search without changing M3 query contracts.
- Alternatives considered: (a) Hiding chunk content until M4 — rejected (admin needs parse verification). (b) Full-text search on chunks in M3 — rejected (that is retrieval; deferred M4).
