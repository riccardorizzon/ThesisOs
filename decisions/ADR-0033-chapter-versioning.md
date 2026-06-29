# ADR-0033: Chapter Versioning as a Change Stream (M6)

- Status: **Accepted** (2026-06-29) — Architect-approved at M6.0 with the review recommendation incorporated (treat versioning as an append-only **change/event stream**, not a flat history, so diff/undo/timeline/branch/collaboration become possible without DB rework). The chapter analogue of ADR-0021 (document versioning) and ADR-0017 (memory versioning).
- Governance: Consistent with the Runtime Constitution (C5 — this is an **additive** migration, not a breaking change) and ADR-0030 (R4 — versioning lives inside `ChapterService`).
- Context: Drafting is iterative; a chapter is rewritten many times, and the user must trust history before the Critic (M9) and Citation (M7) phases build on chapter content. The M0 `chapters` table has **no** `version` column and there is **no** `chapter_versions` table. M6 needs the append-only history + optimistic-concurrency pattern from M2/M3, but the review asks for it to be a **change stream** keyed by *what kind of change* happened — not merely a snapshot log — so future capabilities are unlocked by data, not by migrations.

- Decision:

  ### 1. Model history as an append-only change stream (Rec. 3)

  `chapter_versions` is an **append-only event log** of changes to a chapter (never UPDATE/DELETE rows). Each row is a full snapshot **plus** the kind of change that produced it:

  ```text
  chapter_versions(
    id UUID pk,
    chapter_id UUID fk → chapters(id) ON DELETE CASCADE,
    version INTEGER,                       -- monotonic per chapter
    change_kind VARCHAR(16),               -- WRITE | EDIT | PROMOTE | MERGE | RESTORE
    title TEXT, status VARCHAR(16),
    content_md TEXT, summary TEXT, word_count INTEGER,
    metadata JSONB default '{}',           -- change-specific data (e.g. restored_from, merged_from)
    changed_at TIMESTAMPTZ default now(),
    UNIQUE(chapter_id, version)
  )
  ```

  - `chapters.version INTEGER NOT NULL DEFAULT 1` is added (monotonic; optimistic-lock token).
  - The migration is **additive only** (new column with default + new table); existing `chapters` rows and the M0 schema snapshot are preserved. `contracts/db/schema.sql` is regenerated.

  ### 2. `change_kind` vocabulary (frozen, extensible)

  ```text
  WRITE    — initial creation of the chapter (v1)
  EDIT     — content or metadata change
  PROMOTE  — status transition along the lifecycle (ADR-0032 §3)
  MERGE    — (reserved) combine content from another source/branch
  RESTORE  — (reserved) re-materialize a prior version as a new head
  ```

  **Emitted in M6:** `WRITE` (create) and `EDIT` (content/metadata update). `PROMOTE` is emitted when a status transition is wired (M6 may record it on `update_metadata(status=…)`); `MERGE`/`RESTORE` are reserved kinds the schema accepts but M6 does not produce. The closed set is part of the contract; adding kinds later is additive.

  ### 3. Append rules (snapshot triggers)

  | `ChapterService` call | Effect |
  |-----------------------|--------|
  | `create` | `chapters.version=1`; append `WRITE` entry |
  | `update_content` | increment `chapters.version`; append `EDIT` (content) entry; recompute `word_count` |
  | `update_metadata` (title/summary) | increment; append `EDIT` (metadata) entry |
  | `update_metadata` (status change) | increment; append `PROMOTE` entry |

  ### 4. Optimistic concurrency

  Every mutating call requires `expected_version`; mismatch → `409 write_conflict` (same contract as ADR-0021 §4 / ADR-0017).

  ### 5. What the change stream unlocks (no further DB rework)

  - **diff** — two versions' `content_md`; **undo / RESTORE** — append a `RESTORE` entry from a prior snapshot; **timeline** — read the ordered stream with `change_kind`; **branch / collaborative editing** — future kinds (`MERGE`) + `metadata` lineage. M6 ships none of these UIs, but the data model already supports them.

  ### 6. Restore deferred (read-only history in M6)

  No `restore_version` API in M6 (same posture as ADR-0021 §6 / ADR-0017). `RESTORE` is a reserved `change_kind`, not an M6 endpoint. Linear, append-only stream in M6.

- Consequences:
  - Trustworthy, queryable draft history before M7/M9 build on chapters; the user can inspect prior versions and *why* each changed.
  - Future diff/undo/timeline/branch/collaboration are additive (new `change_kind`, new endpoints) — not a schema migration.
  - One additive migration; regression suites (`make ci`) stay green; schema snapshot regenerated. `owner_type=chapter` embeddings remain out of scope (ADR-0032 §6).

- Alternatives considered:
  - **Flat snapshot history (`change_reason` only)** — rejected per review; a typed change stream (`change_kind`) future-proofs diff/undo/timeline/branch without DB rework.
  - **No versioning until later** — rejected; drafting churn is where history matters most.
  - **Event-sourced deltas (no full snapshots)** — rejected as over-engineering for M6; full snapshots + `change_kind` give the same affordances with simpler reads.
  - **Reuse `document_versions`/`memory_versions`** — rejected; different owner/columns; per-entity history mirrors the existing schema.

- References: ADR-0017, ADR-0021, ADR-0030 (R4), ADR-0032; `contracts/db/schema.sql`; `backend/app/db/models` (Alembic); `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md`.
