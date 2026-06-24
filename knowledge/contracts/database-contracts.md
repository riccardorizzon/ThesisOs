# Database Contracts

> Sources: `contracts/db/schema.sql`, `contracts/db/langgraph-owned.md`, `backend/app/db/models.py`, `backend/migrations/`, M0 spec §7, ADR-0012. See also `architecture/database.md`.

## Canonical artifacts

- **`contracts/db/schema.sql`** — the canonical domain schema snapshot (pg_dump of
  the 14 domain tables + `CREATE EXTENSION vector`). This is the **frozen domain
  contract**.
- **`backend/app/db/models.py`** — SQLAlchemy 2.0 models; must match `schema.sql`.
- **`backend/migrations/versions/0001_initial.py`** — Alembic initial migration.
- **A schema drift test** asserts models ↔ `schema.sql` agree (renders only
  `Base.metadata`).
- **`contracts/db/langgraph-owned.md`** — ownership note for the non-domain
  `langgraph` checkpoint tables.

## Domain ownership boundary (ADR-0012)

| Schema | Owner | Governed by | Tables |
|--------|-------|-------------|--------|
| `public` | **ThesisOS** | models + Alembic + drift test | the 14 domain tables (+ `alembic_version`) |
| `langgraph` | **LangGraph** (`AsyncPostgresSaver`) | `PostgresSaver.setup()` | `checkpoints`, `checkpoint_writes`, `checkpoint_blobs`, `checkpoint_migrations` |

- The `langgraph` tables are **excluded** from Alembic, `schema.sql`, and the drift
  test by construction.
- `contracts: unchanged` in promotion gates = **`domain_contracts: unchanged`**.

## The 14 frozen domain tables

`documents`, `chunks`, `embeddings`, `sources`, `citations`, `chapters`, `notes`,
`memories`, `conversations`, `messages`, `tasks`, `events`, `agent_runs`,
`agent_steps`. Column-level detail: see `architecture/database.md` and
`backend/app/db/models.py`.

## Conventions (all domain tables)
- PK: `UUID(as_uuid=False)` default `gen_random_uuid()`.
- Timestamps: `TIMESTAMP(timezone=True)` default `now()`.
- JSON: `JSONB` (the Python attr for a `metadata` column is `metadata_`).
- Self-FKs: `chapters.parent_id`, `tasks.parent_task_id`.
- Embeddings: `Vector(768)` with per-row `model` + `dimension` tags (swap-safe).

## Change rules
- The domain schema is frozen (ADR-0001). Schema changes require: a new ADR (if it
  touches a frozen contract) + a new Alembic migration + updated `schema.sql` +
  green drift test, inside the owning milestone.
- New external-tool tables follow the ADR-0012 pattern: own schema, own setup,
  excluded from domain governance, documented in `contracts/db/`.
- No `users`/`accounts` table and no `thesisos` schema rename (single-user; M1 spec §2).
