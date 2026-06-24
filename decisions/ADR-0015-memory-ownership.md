# ADR-0015: Memory Ownership Model

- Status: Accepted (2026-06-24)
- Context: M2 introduces six memory kinds in a single `memories` table. Without explicit ownership rules, singleton kinds (user profile, thesis scope, editable page) could be duplicated; agent-driven writes (M5+) could conflict with user edits; and LangGraph checkpoints could be mistaken for memory storage — duplicating M1's lessons about `messages` vs checkpoint truth.
- Decision:
  1. **`memories` + `memory_versions` are the sole system of record** for long-term memory. LangGraph checkpoints must not be treated as authoritative for memory content.
  2. **Two categories under one table (M2):** *operational memory* (`user`, `thesis`, `decision`, `editable`) vs *knowledge items* (`concept`, `citation`). Same table in M2 (`temporary_unified_model: true`); `concept` and `citation` are documented `future_extraction_candidates` for dedicated tables or `sources`/`notes` relations in M3–M6.
  3. **Singleton kinds** (`user`, `thesis`, `editable`) each have exactly one canonical row, identified by fixed keys (`user`, `thesis`, `editable`) and enforced by partial unique indexes.
  4. **Multi kinds** (`concept`, `citation`, `decision`) allow unbounded rows; `(kind, key)` is unique when `key` is non-null.
  5. **Write authority in M2:** REST `/memory` (source=`user`) is the only active write path. `MemoryService.apply_ops` exists for future agent use but is not invoked during the chat loop until M5+.
  6. **Read authority:** REST reads all kinds; `memory_context_node` reads **operational kinds only** (editable + pinned user/thesis — not concept/citation); future M4 retriever reads knowledge items via embeddings — never from checkpoints or a parallel cache.
- Consequences: Clear boundaries prevent duplication with checkpoints and retrieval. Singleton enforcement avoids ambiguous "which editable page is canonical?" bugs. The cost is migration complexity (partial unique indexes) and explicit upsert logic for singleton kinds in `MemoryService`.
- Alternatives considered: (a) Separate tables per kind — rejected (ADR-0003 single-table discriminator). (b) Storing editable memory only in GraphState — rejected (not persistent across threads, violates domain-truth pattern). (c) Soft multi-instance editable pages — rejected (prompt injection requires one canonical page in M2).
