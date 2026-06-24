# Database Architecture

> Sources: `backend/app/db/models.py`, M0 spec §7, `contracts/db/schema.sql`, `contracts/db/langgraph-owned.md`, `docs/m0-promotion.md` (verified prod schema), ADR-0003/0007/0012.

Postgres + pgvector is the **single source of truth** (M0 spec §7). Local dev uses
`pgvector/pgvector:pg16`; prod uses Cloud SQL Postgres 16 (`db-f1-micro`). pgvector
extension verified at **0.8.1** in prod.

## Two schemas (ADR-0012)

- **`public`** — the **ThesisOS domain**, owned by ThesisOS, governed by SQLAlchemy
  models + Alembic + the schema drift test. **14 domain tables** (+ `alembic_version`).
- **`langgraph`** — **external infrastructure**, owned by `AsyncPostgresSaver`,
  created by `PostgresSaver.setup()` at startup, **excluded** from Alembic and the
  drift test. Tables: `checkpoints`, `checkpoint_writes`, `checkpoint_blobs`,
  `checkpoint_migrations`.

The promotion phrase `contracts: unchanged` means **`domain_contracts: unchanged`**,
not `all_database_objects` (ADR-0012).

## Domain tables (14)

> All PKs are `UUID` (`gen_random_uuid()`), timestamps `TIMESTAMP(timezone=True)`
> default `now()`. `metadata` column is mapped as `metadata_` in Python.

| Table | Purpose & key columns | Milestone in use |
|-------|-----------------------|------------------|
| `documents` | uploaded sources; `title, author, source_type[pdf\|epub\|docx], original_filename, gcs_uri, status[uploaded\|parsing\|parsed\|indexed\|error], page_count, language, metadata` | M3 |
| `chunks` | ordered text segments; `document_id→documents, chunk_index, content, token_count, page_from, page_to, section_path` — **no embedding column** | M3 |
| `embeddings` | **model-agnostic** vectors; `owner_type[chunk\|note\|memory\|chapter], owner_id, model, dimension, embedding vector(768), content_hash` | M4 |
| `sources` | CSL-JSON bibliographic sources; `document_id?, type, csl_json, title, authors, year, doi, url` | M7 |
| `citations` | per-chapter refs; `source_id→sources, chapter_id?→chapters, locator, prefix, suffix` | M7 |
| `chapters` | self-FK tree; `parent_id?→chapters, order_index, title, status[planned\|drafting\|draft\|revised\|final], content_md, summary, word_count` | M6/M8 |
| `notes` | `document_id?, chapter_id?, kind[note\|highlight], content, anchor` | M6+ |
| `memories` | 6-kind editable memory; `kind[user\|thesis\|concept\|citation\|decision\|editable], key?, content, pinned, source[user\|system\|agent], version, metadata` | M2 |
| `conversations` | `title?` | **M1** |
| `messages` | chat history; `conversation_id→conversations, role, content, tool_calls` | **M1** |
| `tasks` | AgentOS work loop; self-FK `parent_task_id?, title, description, status[pending\|in_progress\|blocked\|done\|cancelled], owner_agent, priority, payload` | M5+ |
| `events` | persisted outbox; `type, payload, source, correlation_id, occurred_at` | M2+ |
| `agent_runs` | run tracing; `conversation_id?, graph, trigger, input, output, status, error, started_at, finished_at` | **M1** |
| `agent_steps` | step tracing; `agent_run_id→agent_runs, agent, phase[observe\|hypothesis\|plan\|implement\|test\|critic\|qa\|revise\|promote], input, output, status` | M5+ |

> Note: `agent_steps.phase` enumerates the **AgentOS loop phases** — the development
> methodology is encoded in the data model. See `development/workflow.md`.

## Key design decisions

- **Model/dimension-tagged embeddings (ADR-0002, spec §7/§19).** Embeddings live in
  a dedicated polymorphic table tagging `model` + `dimension` per row, so the
  provider can be swapped without a painful migration. `EMBEDDING_DIM = 768` is the
  active model's dim (`text-multilingual-embedding-002`).
- **No vector index yet.** HNSW/IVFFlat needs a fixed dimension; strategy
  (partition by `model`) is deferred to **M2/M4** when retrieval is built
  (spec §19). See `context/open-questions.md`.
- **Messages = system of record for chat (ADR-0007, M1 spec §5).** The LangGraph
  checkpoint holds *derived* working state, rebuildable from `messages`.
- **Token accounting on `agent_runs`, not `messages`** (M1 spec §5, ADR-0014) — so
  future per-agent accounting attaches without touching domain rows.

## Migrations & drift
- Alembic `0001_initial`: `CREATE EXTENSION IF NOT EXISTS vector` + all 14 tables.
  No HNSW index (deferred). The backend container runs `alembic upgrade head` at boot.
- A **schema drift test** (`tests/test_schema_snapshot.py`) renders only
  `Base.metadata` and guards models ↔ `contracts/db/schema.sql`; `langgraph.*`
  tables are invisible to it by construction.
