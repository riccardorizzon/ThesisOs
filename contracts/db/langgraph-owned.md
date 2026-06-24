# LangGraph-Owned Infrastructure Tables (ADR-0012)

These tables are external infrastructure artifacts, **not** part of the ThesisOS domain contract.

- Ownership: LangGraph `AsyncPostgresSaver` (`langgraph-checkpoint-postgres`)
- Schema: `langgraph` (falls back to `public` only if the pinned version cannot target a schema)
- Creation: `PostgresSaver.setup()` at application startup
- NOT managed by Alembic. Excluded from `contracts/db/schema.sql`.
- Excluded from the drift test by construction (the test renders only `Base.metadata`).

Tables: `checkpoints`, `checkpoint_writes`, `checkpoint_blobs` (+ any future checkpointer tables).
