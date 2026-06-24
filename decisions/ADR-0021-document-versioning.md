# ADR-0021: Document Versioning

- Status: Accepted (2026-06-24)
- Context: Thesis sources are revised (new PDF upload, corrected metadata). M2 established append-only version history for memory; M3 needs the same pattern before M4 retrieval references stable document identities.
- Decision:
  1. **Current version** lives on `documents.version` (monotonic integer; optimistic-lock token for metadata PATCH).
  2. **History** lives in `document_versions` (append-only; never UPDATE/DELETE rows).
  3. **Snapshot triggers:** (a) successful metadata PATCH; (b) successful parse completion (records chunk_count, page_count, parser metadata).
  4. **Optimistic concurrency:** every metadata `PATCH` requires `expected_version`; mismatch → `409 write_conflict`.
  5. **Re-parse:** increments `documents.version`, appends `document_versions` row, **replaces all `chunks` for the document** in one transaction. Old chunk row UUIDs are discarded; **`chunk_hash` is stable** when content at a given `chunk_index` is unchanged (M3 spec §5.2).
  6. **Restore:** `restore_version` **deferred** — no rollback API in M3 (same as ADR-0017 for memory).
- Consequences: Audit trail before retrieval. Re-parse invalidates chunk UUIDs but preserves `chunk_hash` for unchanged segments — M4 embeddings should key on `chunk_hash`. Linear history only in M3.
- Alternatives considered: (a) Immutable chunks with chunk_versions — rejected (over-engineering for M3). (b) No versioning until M4 — rejected (Architect requirement: version before retrieval).
