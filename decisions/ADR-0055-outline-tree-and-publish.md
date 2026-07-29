# ADR-0055: Outline Tree Management & Publish (M8)

- Status: **Proposed** (2026-07-29) — not Accepted; freeze at M8.0 before implementation.
- Governance: Extends ADR-0032 (chapter ownership/lifecycle) and ADR-0033 (versioning); consistent with ADR-0006 (events outbox), ADR-0007 (no GraphState change), Constitution C1/C3.
- Context: M6 allowed `parent_id`/`order_index` on create but forbade tree ops, `/outline`, and `ChapterCreated`. The self-referencing `chapters` table is already the outline. M8 must freeze mutation semantics, event emission, and the `published` lifecycle wire without opening chapter RAG or critic scope.

- Decision:

  ### 1. Outline is a projection of `chapters`, not a separate store

  No `outlines` table. `GET/PUT /outline` read/write the same rows as `/chapters`, shaped as a tree. `ChapterService` remains the **sole writer**.

  ### 2. Tree invariants

  - Siblings: same `parent_id` (or all roots), ordered by ascending `order_index` (dense or gapped — service normalizes on write).
  - No cycles; move/reparent validates ancestry.
  - Max depth **4** unless Architect revises at freeze.
  - Deleting a node with children: **reject** by default (`409 children_exist`) or explicit `cascade=true` flag — default reject for Wave 1 safety.

  ### 3. Mutation API

  - **LOCKED:** ops-batch `PUT /outline` only (create/move/update/delete). Full-tree replace is out of M8.
  - Each mutating op that changes durable fields appends a `chapter_versions` entry per ADR-0033. **Recommendation (locked for Proposed):** structural move/reparent/reorder uses existing **`EDIT`** (metadata/structure change); status changes use **`PROMOTE`**. Do **not** add a new `MOVE` kind in M8 — avoids amending ADR-0033's closed set (`WRITE|EDIT|PROMOTE|MERGE|RESTORE`). Optional `metadata.move = {from_parent,to_parent,order_index}` on the version row for audit.
  - Concurrent edits: require `expected_version` on update/move of existing ids → `409` on mismatch (same as M6 content).

  ### 4. `ChapterCreated` emission

  - Emit product event `ChapterCreated` with `{ chapter_id }` when a chapter row is **inserted**, from every create path (`POST /chapters`, outline `create` op).
  - Delivery via existing outbox/Event Bus pattern (ADR-0006 / runtime bus). M6 silent creates become emitting creates in M8 (behavioral add).

  ### 5. Publish transition

  - Lifecycle remains `draft | review | approved | published` (ADR-0032).
  - M8 authorizes **explicit** `status=published` via `update_metadata` / outline `update` op.
  - M8 does **not** auto-transition to `approved` (reserved for M9 Critic gate).
  - Publishing does not by itself export files; export remains existing export surfaces.

  ### 6. Read model

  - Outline payloads are **structure-only** (no `content_md`) to keep list/tree fast and avoid accidental RAG misuse.

- Consequences: One tree, one service, clear publish wire, observable creates. Cost: careful migration of any clients assuming silent creates; frontend must handle events optionally.

- Alternatives considered:
  - **Separate outline document (JSON blob)** — rejected; dual source of truth vs `chapters`.
  - **Full-tree PUT only** — rejected as default (clobber risk); may offer later as admin.
  - **Auto-publish on export** — rejected; explicit status keeps user control.
  - **Graph node emits ChapterCreated** — rejected; domain service/outbox only.

- References: M8 design spec `docs/superpowers/specs/2026-07-29-thesisos-m8-outline-design.md`; ADR-0032, ADR-0033, ADR-0006; `contracts/events/events.json`.
