# ADR-0017: Memory Versioning Strategy

- Status: Accepted (2026-06-24)
- Context: Thesis memory must be editable and trustworthy — users need to see what changed and agents (M5+) must not silently overwrite user edits. The M0 schema includes a `version` integer on `memories` but no history table or concurrency protocol.
- Decision:
  1. **Current state** on `memories` row: `version` monotonically increases on every successful write; serves as the optimistic-lock token.
  2. **History** in append-only `memory_versions` table: one snapshot row per committed version (including v1 on create). Snapshots store `title`, `content`, `metadata`, `source`, `changed_at`.
  3. **Optimistic concurrency:** `PATCH /memory/{id}` requires `expected_version`; mismatch returns HTTP `409` with `code: write_conflict` (aligned with `contracts/agents/memory.json`).
  4. **Linear history only** in M2 — no branching, merge, or CRDT semantics.
  5. **Delete:** hard delete on `memories`; version rows cascade away. Audit for deleted records is limited to `events` (`MemoryUpdated`) — acceptable for M2 single-user scope.
- Consequences: Users and tests can verify versioning and conflict detection. Storage grows with edits (acceptable for single-user thesis scale). M5+ agent writes must respect the same lock protocol via `MemoryService`.
- Alternatives considered: (a) Version only in JSONB metadata — rejected (no queryable history). (b) Full event-sourcing without current-state row — rejected (over-engineered for M2). (c) Pessimistic row locks for all reads — rejected ( unnecessary for single-user ).
