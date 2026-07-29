# ThesisOS — M8 "Outline" Design Spec

- **Date:** 2026-07-29
- **Status:** **Proposed** — Architect freeze required before implementation (ADR-0001).
- **Scope:** Milestone **M8 Outline** — thesis outline / chapter-tree management over the existing self-referencing `chapters` table: `GET`/`PUT /outline`, reorder/re-parent/move, emit `ChapterCreated`, wire `published` lifecycle transition, and an outline UI route. **NOT** citation/grounding (M7), critic loop (M9), or chapter RAG.
- **Builds on:** M6 `ChapterService` + `/chapters` + versioning (ADR-0032/0033), `order_index` / `parent_id` columns (M0), reserved OpenAPI `/outline`, event `ChapterCreated` (M8) in `contracts/events/events.json`.
- **New ADR (Proposed):** ADR-0055 (Outline Tree & Publish).
- **Authors:** ThesisOS Builder Team

---

## 1. Vision

M8 turns the flat/partial chapter list into a **managed thesis skeleton**:

```text
… → WRITE (M6) → CITE (M7) → OUTLINE (M8) → Critique (M9)
```

Users can view and edit the full tree (chapters + sections), reorder and re-parent nodes, create nodes that emit `ChapterCreated`, and mark structure `published` when ready — without changing GraphState or retrieval semantics.

**Success criterion (one sentence):** `GET/PUT /outline` round-trips a consistent tree over `chapters` (`parent_id` + `order_index`), tree mutations go only through `ChapterService` extensions, creating a node emits `ChapterCreated` via the product outbox, `status=published` is a valid explicit transition, and the frontend `/outline` route supports tree edit/reorder — M6 chapter content APIs remain green.

---

## 2. Objective, scope & non-goals

### 2.1 In scope (M8 MUST ship)

| # | Deliverable |
|---|-------------|
| 1 | **Outline DTO + `GET /outline`** — nested tree for a `project_id` (structural, ordered by `order_index`) |
| 2 | **`PUT /outline`** — replace/patch tree: reorder, re-parent, create missing nodes, optional title/status updates (semantics in ADR-0055) |
| 3 | **`ChapterService` tree ops** — `reorder`, `move`/`reparent`, bulk apply outline; sole writer preserved |
| 4 | **`ChapterCreated` event** — emit on create paths (REST `/chapters` and outline create) via ADR-0006 outbox |
| 5 | **Lifecycle** — allow explicit transition to `published` (ADR-0032 reserved); no auto-publish from graph |
| 6 | **Frontend `/outline`** — tree view, drag/reorder or move controls, status display/edit |
| 7 | **Qualification + promotion** — `docs/m8-outline-promotion.md`, tag `m8-complete` |

### 2.2 Non-goals

| Forbidden in M8 | Deferred to |
|-----------------|-------------|
| Citation resolve / style engine | M7 Grounding |
| Critic / `approved` auto-gate / revise loop | M9 |
| GraphState changes | Frozen |
| Semantic search over chapters / embeddings `owner_type=chapter` | future ADR |
| Multi-user collaborative OT/CRDT outline | later |
| Changing M6 content versioning model | ADR-0033 stays |

```yaml
citation_route: false
critic_loop: false
chapter_rag: false
graphstate_change: false
```

---

## 3. Architecture

### 3.1 Data model (unchanged tables)

- Tree = `chapters.parent_id` + `chapters.order_index` (siblings share parent; order_index unique enough per parent — enforce in service).
- Sections are chapters with non-null `parent_id` (M6 decision — no `sections` table).

### 3.2 Outline representation

```text
OutlineNode:
  id: uuid
  title: str
  status: draft|review|approved|published
  order_index: int
  parent_id: uuid | null
  children: OutlineNode[]
```

`GET /outline?project_id=` returns root forest. Content body (`content_md`) **omitted** from outline payload (structure-only; editor stays on `/chapters` / workspace).

### 3.3 `PUT /outline` semantics (**LOCKED**)

- Request shape: **ops batch only** (full-tree replace is out of M8 — clobber risk).

```text
ops: [
  { op: create, temp_id?, title, parent_id?, order_index, status? },
  { op: move, id, parent_id, order_index },
  { op: update, id, title?, status? },
  { op: delete, id }   # reject if children exist unless cascade=true (ADR-0055)
]
```

- Optimistic concurrency: per-node `expected_version` on move/update/delete of existing ids → `409` on mismatch.
- Cycles forbidden; service rejects moves that would cycle.
- Max depth **4** (constant in `ChapterService`).

### 3.4 Events

- On successful create (any path that inserts a chapter): enqueue `ChapterCreated { chapter_id }` (and `project_id` on envelope if ADR-0047 applies).
- M6 create paths that currently omit the event **gain** emission in M8 (documented breaking behavioral add — additive event, not API break).

### 3.5 Lifecycle

Per ADR-0032:

```text
draft → review → approved → published
```

- M8 wires **user/API** transition into `published` (structure “ready for export/freeze”).
- M8 does **not** auto-set `approved` (M9 Critic).
- Invalid transitions → `409` / `422` with stable codes.

---

## 4. Internal milestones

| Sub | Name | Output |
|-----|------|--------|
| **M8.0** | Spec + ADR-0055 Accepted | freeze + Critic sign-off |
| **M8.1** | ChapterService tree ops | unit tests: reorder/move/cycle reject |
| **M8.2** | `/outline` GET+PUT + OpenAPI | API tests |
| **M8.3** | `ChapterCreated` outbox | event contract tests |
| **M8.4** | Frontend outline route | component + e2e smoke |
| **M8.5** | Qualification + promotion | tag `m8-complete` |

---

## 5. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| PUT full-tree clobber | Prefer ops batch + per-node versions |
| Cycle / orphan trees | Service invariants + tests |
| Event spam on bulk import | Batch create still one event per row; document; no aggregate event in M8 |
| UI drag-and-drop complexity | MVP: move up/down + indent/outdent if DnD slips |
| Collision with WritingOutline components | Extend existing writing outline UI; don't fork two trees |

---

## 6. Critic checklist (pre-implementation)

- [ ] Sole writer remains `ChapterService`
- [ ] No GraphState change
- [ ] `ChapterCreated` payload matches `events.json`
- [ ] `published` transition explicit only
- [ ] No citation/critic scope
- [ ] OpenAPI `/outline` updated (GET + PUT)

---

## 7. References

- ADR-0032, ADR-0033, Proposed ADR-0055
- `contracts/openapi/openapi.yaml` (`/outline`)
- `contracts/events/events.json` (`ChapterCreated`)
- `docs/m8-outline-promotion.md`
- M6 Writing Workspace design spec
