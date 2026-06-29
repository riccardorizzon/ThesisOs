# ADR-0032: Chapter Ownership, Lifecycle & Query Model (M6 Writing Workspace)

- Status: **Accepted** (2026-06-29) — Architect-approved at M6.0 with the review recommendation incorporated (explicit Draft → … → Published lifecycle that grows without API changes). Combines for chapters what ADR-0020 (ownership) and ADR-0022 (query model) did for documents.
- Governance: Consistent with the Runtime Constitution (C1, C3) and ADR-0030 (R4 — `ChapterService` is a Business domain service). Same sole-writer pattern as ADR-0015 (memory) and ADR-0020 (documents).
- Context: M0 created the `chapters` table (self-referencing tree) but no write path. M6 introduces the Writing Workspace: the writer capability produces an ephemeral `DraftResult` (ADR-0031), and the user persists/edits durable chapters. Without explicit ownership, chapters could be written from API handlers or graph nodes, and a future RAG path could start ranking chapter prose. Ownership, the **chapter lifecycle**, read authority, and the no-retrieval rule must be frozen before implementation. Outline/tree management and the `ChapterCreated` product event are **M8**.

- Decision:

  ### 1. `chapters` (+ `chapter_versions`, ADR-0033) are the sole system of record for thesis prose

  Distinct from documents (ingested sources, ADR-0020) and memories (ADR-0015).

  ### 2. Write authority — `ChapterService` is the only writer

  `ChapterService` (`backend/app/services/chapter/`, Business) is the **only** module that INSERT/UPDATE/DELETEs `chapters`/`chapter_versions`. API handlers, graph nodes, and agents call `ChapterService` only. The writer **graph node never writes chapters** (ADR-0031 §6): it yields a `DraftResult`; persistence is an explicit `ChapterService` call from the REST layer.

  ### 3. Draft vs Published Chapter — one row, an extensible lifecycle (Rec. 2)

  A chapter is a single row whose **status** moves along a lifecycle. Draft and Published are the **same entity** in different states — the API does not change as the lifecycle grows.

  ```text
  draft ──► review ──► approved ──► published
   (write)   (M6 manual) (M9 critic gate) (M8 publish)
  ```

  - **Lifecycle vocabulary (frozen, extensible):** `draft | review | approved | published`.
  - **Wired in M6:** `draft` (created/edited prose) and `review` (user-set "ready to be checked"). `approved` and `published` are **reserved, accepted values** the schema and API already understand but M6 does **not** auto-transition — `approved` is gated by the Critic (M9), `published` by outline/publish (M8). Transitions are explicit (`update_metadata(status=…)`); no automatic promotion in M6.
  - Rationale: the workflow (`draft → review → approved → published`, and later collaborative states) extends **without changing API or schema** — exactly the review's intent.

  ### 4. M6 public service surface (minimal)

  | Method | Purpose |
  |--------|---------|
  | `create(title, *, parent_id=None, order_index, status="draft", content_md=None)` | insert chapter/section; v1 change-stream entry (ADR-0033) |
  | `get(chapter_id)` | single chapter (includes `content_md`) |
  | `list(*, parent_id=None, q=None)` | structural list, ordered by `order_index` (NOT ranked) |
  | `update_content(chapter_id, content_md, *, expected_version)` | set body; recompute `word_count`; append change entry |
  | `update_metadata(chapter_id, *, title=None, summary=None, status=None, expected_version)` | metadata/status transition; append change entry |
  | `list_versions(chapter_id)` | append-only change stream (read-only, ADR-0033) |

  `parent_id`/`order_index` are accepted on create (a chapter may be a **section** of another) but M6 ships **no tree-management ops** (reorder/move/re-parent/bulk outline edits) — M8.

  ### 5. Read authority & query model (M6)

  - `GET /chapters` — structural list (optional `parent_id`), ordered by `order_index`; optional `q` = ILIKE substring on `title` only (admin filter, **not** semantic search; ADR-0018/0022).
  - `GET /chapters/{id}`, `GET /chapters/{id}/versions` — keyed by id; versions ordered by `version`.

  ### 6. Forbidden in M6 (hard boundary)

  - Writing `chapters`/`chapter_versions` from API handlers or graph nodes directly (only `ChapterService`).
  - Any retrieval/RAG over chapter content: no `/chapters/search`, no `owner_type=chapter` embeddings, no `top_k`/`similarity`/`rerank`, no injection of chapter prose into `/chat` as ranked context.
  - Outline tree ops, `/outline`, emitting the `ChapterCreated` product event (M8).
  - Writes to `sources`/`citations` tables (M7) — M6 keeps `CitationRef` in `DraftResult`/`GraphState`/stream only.
  - Auto status promotion (`approved`/`published` are manual/reserved in M6, see §3).

  ### 7. Allowed (not retrieval)

  Returning `content_md` in `GET /chapters/{id}` is allowed (the workspace editor surface — document-scoped, unranked, not injected into chat), exactly the ADR-0022 reasoning.

- Consequences:
  - One disciplined write boundary; M8 outline management, the `ChapterCreated` event, and later lifecycle states extend `ChapterService` without reopening the contract or the API.
  - M6 cannot become a chapter-RAG surface; chapter retrieval, if ever wanted, gets its own ADR + `owner_type=chapter` embeddings.
  - The writer node stays pure; the only chapter writer is a Business service called from REST.

- Alternatives considered:
  - **Two-state `draft|final` only** — rejected per review; the explicit `draft→review→approved→published` lifecycle lets review/approval/publish (M8/M9) and collaboration land without API churn.
  - **Separate `drafts` and `chapters` tables** — rejected; Draft vs Published is a *state* of one row, not two entities; avoids dual write paths and migrations.
  - **Writer graph node persists chapters** — rejected; violates R1/R3/R8 and forces a chapter target into frozen GraphState.
  - **Direct API → DB writes** — rejected (ADR-0015/0020 sole-writer service).
  - **Separate `sections` table** — rejected; `chapters.parent_id` already models sections.
  - **Embed chapters for retrieval in M6** — rejected; scope creep behind its own future ADR.

- References: ADR-0006, ADR-0015, ADR-0018, ADR-0020, ADR-0022, ADR-0024, ADR-0030 (R4), ADR-0031, ADR-0033; `contracts/db/schema.sql`; `contracts/openapi/openapi.yaml` (`/chapters` M6, `/outline` M8); `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md`.
