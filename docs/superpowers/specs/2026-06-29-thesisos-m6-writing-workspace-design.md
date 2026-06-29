# ThesisOS — M6 "Writing Workspace" Design Spec

- **Date:** 2026-06-29
- **Status:** **Frozen** (Architect-approved 2026-06-29 at M6.0, with four design-review recommendations incorporated: writer-as-capability, `DraftResult` isolation, draft→…→published lifecycle, versioning-as-change-stream). ADR-0031/0032/0033 Accepted. M6.1 implementation authorized.
- **Scope:** Milestone M6 only — the **Writing Workspace**: a `writer` Business agent that drafts grounded prose, and a durable chapter store (`ChapterService` + `/chapters` + versioning) that persists/edits chapters. **NOT** outline tree management or `/outline` (M8), citation formatting/bibliography (M7), the critic loop (M9), or any GraphState change.
- **Builds on:** M5 Agent Runtime Platform (supervisor → planner → router → conditional execution, Event Bus, `ConversationService`; tag `m5-complete` @ `bf12c13`), M4 Retrieval (`retriever_node`, `retrieved_context`), M2 Memory (`memory_context_node`), M1 `/chat` seam. Frozen `GraphState.draft`/`citations`, `contracts/agents/writer.json`, `chapters` table (M0).
- **New ADRs:** ADR-0031 (Writer Agent & Drafting Topology), ADR-0032 (Chapter Ownership & Query Model), ADR-0033 (Chapter Versioning).
- **Authors:** ThesisOS Builder Team

---

## 1. Vision

M6 closes the produce step of the thesis pipeline:

```text
Acquire (M3) → Index (M4) → Plan & Route (M5) → WRITE (M6) → Cite (M7) / Outline (M8) / Critique (M9)
```

After M6, a user can ask the system to **draft a chapter or section**, get grounded prose (with citation markers) streamed back through the existing `/chat` seam, and **save/revise** that prose as a versioned chapter in a Writing Workspace. M6 turns `draft` and `citations` — fields that have existed (frozen, ADR-0007) but were only ever set as a convenience by `conversation_node` — into the output of a real, contract-true Writer agent, and gives chapters a durable, versioned home.

**Success criterion (one sentence):** a `/chat` turn routed to `writer` runs supervisor → planner → router → memory_context → retriever → writer, produces a coherent grounded `draft` with citation markers referencing only retrieved sources, streams via the M1 seam; and `ChapterService` + `/chapters` persist/edit chapters with append-only version history and optimistic-lock concurrency — all with **no GraphState field change** and M0–M5 suites green.

---

## 2. Objective, scope & non-goals

### 2.1 Objective

Deliver a **usable, grounded writing capability** end-to-end: (a) a Writer agent route in the runtime, and (b) a versioned chapter store with a REST workspace surface — against the already-frozen `writer.json` contract and frozen `GraphState`, governed by the Runtime Constitution and ADR-0030 layers.

### 2.2 In scope (M6 MUST ship)

| # | Deliverable |
|---|-------------|
| 1 | **`WriterCapability` + `writer` node** — `write_grounded(brief) -> DraftResult` (port, swappable impls); `make_writer_node` adapts `DraftResult` → frozen state; reads `plan, retrieved_context, messages`; writes `draft, citations`; streams; errors `empty_context`, `generation_failed` (ADR-0031, `writer.json`) |
| 2 | **Writer route wiring** — activate reserved `writer` route: `memory_context → retriever → writer → END`; route vocabulary + `route_after_router` + router selection (additive); Event Bus instrumentation of the writer node |
| 3 | **Citation discipline** — `CitationRef.source_id` restricted to sources present in `retrieved_context` (no invented ids) |
| 4 | **Chapter domain** — `ChapterService` (sole writer for `chapters`), Pydantic DTOs, `chapter_versions` table + `chapters.version` column (Alembic migration), versioning + optimistic lock (ADR-0032/0033) |
| 5 | **`/chapters` REST** — create / list / get / update content / update metadata / list versions (replaces the `501` stub); OpenAPI updated |
| 6 | **Workspace UI (minimal)** — `/workspace` route: list chapters, open editor, stream a writer turn into the editor, save → versioned chapter (thin slice; rich outline UI is M8) |
| 7 | **Qualification** — `make qualify-m6` (writer route E2E + chapter persistence E2E + error contracts + grounding/citation eval) and `dogfood-m6` (live writer turn + chapter save); benchmark `B_write` |
| 8 | **Promotion** — `docs/m6-promotion.md`, knowledge mirror, capability graph `done` + baselines, tag `m6-complete` (manual) |

### 2.3 Non-goals (hard boundary)

| Forbidden in M6 | Deferred to |
|-----------------|-------------|
| Outline tree management, re-parent/reorder/move, `/outline` | M8 |
| `ChapterCreated` product event emission (events outbox) | M8 |
| Citation formatting (CSL-JSON → APA7/MLA/Chicago), `/citations`, `/bibliography`, writes to `sources`/`citations` tables | M7 |
| Critic / critique loop / hallucination gating | M9 |
| Retrieval/RAG over chapter content; `owner_type=chapter` embeddings | later (own ADR) |
| New / changed `GraphState` fields | Frozen (ADR-0007) |
| Auto-persist draft → chapter from the graph (RunContext target + persist hook) | possible later enhancement |
| Engineering Runtime / Build Control Plane changes | Platform Track (MB*) |

```yaml
outline_management: false
chapter_created_event: false
citation_formatting: false
critic_loop: false
chapter_retrieval: false
graphstate_new_fields: false
graph_chapter_autopersist: false
platform_track_changes: false
```

---

## 3. Architecture

### 3.1 Layer placement (ADR-0030 §2)

| Component | Layer | New/Reused |
|-----------|-------|-----------|
| `schemas/draft.py` (`WriterBrief`, `DraftResult`) | **Business** | new |
| `graph/writer.py` (`WriterCapability` port + `LLMWriter` impl + `make_writer_node` adapter) | **Business** | new |
| `graph/orchestration/` writer prompt-wire + route constants/coerce | **Business** | extend (additive) |
| `services/chapter/` (`ChapterService`, DTOs, exceptions) | **Business** | new |
| `graph/conversation.py` `build_graph` — wire writer route + instrument writer node | **Runtime** | extend (additive) |
| `graph/routing.py` — `route_after_router` writer edge key | **Runtime** | extend (additive) |
| `api/chapters.py` — `/chapters` router | **Runtime/HTTP boundary** | new |
| `db/models` + Alembic migration (`chapters.version`, `chapter_versions`) | **Infrastructure** | new (additive) |
| `frontend/app/workspace/` | frontend | extend placeholder |

**No new Runtime Platform abstractions.** M6 is a Product Plane feature built *on* the frozen Runtime Platform; it reuses the Event Bus, lifecycle, and contracts unchanged.

### 3.2 Component decisions (Phase 4 evaluation)

The brief asked whether to introduce each of the following. Decision + rationale:

| Candidate | Decision | Rationale |
|-----------|----------|-----------|
| **Writer Agent** | **YES — as a `WriterCapability` (port), not a special node** | Headline of M6. The route depends on the capability `write_grounded(brief) -> DraftResult`; `writer-agent` is today's implementation, swappable for `writer-v2/fast/reasoning/local` at the composition root with no topology change (ADR-0031 §2; Rec. 1). |
| **Draft Engine** | **NO separate component; the writer returns a pure `DraftResult`** | "Drafting" = `WriterCapability.write_grounded()` returning `DraftResult{draft, citations, metadata, reasoning?, metrics}`. A separate layer decides save/show/discard/compare — the writer is fully isolated from `ChapterService`/REST/DB (ADR-0031 §3; Rec. 4). No standalone "engine" object. |
| **Workspace Service** | **YES — as `ChapterService`** | The domain sole-writer for `chapters` (ADR-0032), mirroring `DocumentService`/`MemoryService`. "Workspace" = the backend service + the `/workspace` frontend. |
| **Chapter Model** | **YES — reuse existing table** | `chapters` exists (M0); M6 adds SQLAlchemy usage + Pydantic `ChapterRecord` + the version column. |
| **Section Model** | **NO separate table** | Sections = `chapters` with `parent_id` (self-referencing tree, M0). M6 allows `parent_id` on create; tree ops are M8. |
| **Versioning** | **YES — new ADR + migration** | `chapter_versions` + `chapters.version` (ADR-0033), mirroring `document_versions`. Drafting is iterative; history is essential. |
| **Draft persistence** | **YES — via `ChapterService`, decoupled from graph** | Writer emits ephemeral `draft`; the `/chapters` REST path persists. Keeps GraphState frozen + writer pure (ADR-0031 §5). |
| **Outline integration** | **Minimal/read-only** | Writer reads `plan` (M5 brief). Full outline tree + `/outline` + `ChapterCreated` event = M8. Documented seam, not implemented. |
| **Memory integration** | **Reuse M2** | Writer route runs through `memory_context_node` like every route; no new memory writes. |
| **Retrieval integration** | **YES — writer route is grounded** | `retriever_node` runs before `writer_node`; writer reads `retrieved_context` and cites it. |

### 3.2.1 Writer capability & `DraftResult` (Rec. 1 + Rec. 4)

```text
WriterCapability:  async write_grounded(brief: WriterBrief) -> DraftResult

WriterBrief:   { plan, retrieved_context, messages }      # pure input from frozen state
DraftResult:   { draft: str,
                 citations: list[CitationRef],            # ⊆ retrieved sources
                 metadata: dict,                          # model id, route — non-state
                 reasoning: str | None,                   # optional (Critic/debug)
                 metrics: dict }                          # tokens, durations, counts
```

- The **capability is the abstraction**; `writer-agent` is one implementation. Variants register at the composition root — no topology/route/contract change (C8; R1/R2).
- The capability is **isolated**: it never imports `ChapterService`, REST, DB, or the Event Bus. It returns a `DraftResult`; a different layer decides **save / show / discard / compare**.
- `make_writer_node(writer)` is a thin **adapter**: `DraftResult` → `{messages(+assistant), draft, citations, errors}` (exactly `writer.json`). `metadata`/`reasoning`/`metrics` ride the stream / Event Bus, **never** GraphState (frozen).

### 3.3 Graph topology (ADR-0031)

```text
START → supervisor → planner → router → memory_context → [route_after_router]
        conversation:  → conversation_node → END                       (M5, unchanged)
        grounded_chat: → retriever_node → conversation_node → END        (M5, unchanged)
        writer:        → retriever_node → writer_node → END              (M6, NEW)
```

The `grounded_chat` and `writer` routes share `retriever_node` (reused, unchanged). The writer node and the conversation node both stream tokens through the existing custom stream; the writer additionally emits validated `citations`.

### 3.4 GraphState usage (no schema change)

| Field | Writer behavior |
|-------|-----------------|
| `plan` | **read** — the writing brief (from M5 planner) |
| `retrieved_context` | **read** — grounding sources for prose + citations |
| `messages` | **read** — user instruction + history; **write** assistant draft message (set semantics, like `conversation_node`) |
| `draft` | **write (set)** — the generated prose |
| `citations` | **write (set)** — `CitationRef`s restricted to retrieved sources |
| `errors` | **append** — `empty_context` / `generation_failed` |

Asserted in tests: `GraphState.model_fields` unchanged; `run_context` not in `GraphState`.

### 3.5 Chapter domain & persistence

- `ChapterService` (Business, sole writer — ADR-0032 §2/§4) with the minimal surface in ADR-0032 §4.
- **Lifecycle (Rec. 2, ADR-0032 §3):** one row, status along `draft → review → approved → published` (frozen, extensible). M6 wires `draft` + `review` (manual); `approved` (M9 Critic) / `published` (M8) are reserved values, no auto-promotion.
- **Versioning as a change stream (Rec. 3, ADR-0033):** `chapter_versions` is append-only with `change_kind ∈ {WRITE, EDIT, PROMOTE, MERGE, RESTORE}` (M6 emits WRITE/EDIT, and PROMOTE on status change); enables future diff/undo/timeline/branch with no DB rework.
- Optimistic lock: `update_*` requires `expected_version` → `409 write_conflict`. `word_count` recomputed on content writes.
- **No** chapter writes from graph nodes or API handlers directly.

### 3.6 REST API (`/chapters`)

| Method | Path | Notes |
|--------|------|-------|
| POST | `/chapters` | create (optional `parent_id`, `order_index`) → 201 `Chapter` |
| GET | `/chapters` | list (optional `parent_id`, `q` ILIKE on title) ordered by `order_index` |
| GET | `/chapters/{id}` | single chapter (includes `content_md`) |
| PATCH | `/chapters/{id}` | update content and/or metadata; requires `expected_version`; 409 on conflict |
| GET | `/chapters/{id}/versions` | append-only history |

OpenAPI: replace the `/chapters` `501` stub; add `/chapters/{id}` and `/chapters/{id}/versions`; add `Chapter`, `ChapterCreate`, `ChapterUpdate`, `ChapterVersion` schemas. `/outline` stays `501` (M8).

### 3.7 Two event systems (do not conflate)

- **Runtime Event Bus** (canonical `NodeStarted/NodeCompleted/...`, ADR-0030): the writer node is wrapped by `build_graph` and emits these automatically — no Business telemetry (R8).
- **Product event catalog** (`contracts/events/events.json`, ADR-0006 outbox): `ChapterCreated` is tagged **M8**; M6 does **not** emit it. `ChapterService` persists chapters silently in M6.

---

## 4. Success criteria (M6 promotion gate)

```yaml
writer_capability: green         # write_grounded(brief) -> DraftResult; swappable impl behind port
writer_isolation: green          # writer returns DraftResult; no ChapterService/REST/db/runtime imports
writer_node: green               # adapter maps DraftResult → draft/citations; errors
writer_route: green              # memory_context → retriever → writer → END wired; conditional dispatch
citation_discipline: green       # citations ⊆ retrieved sources (no invented source_id)
chapter_service: green           # sole writer; create/get/list/update/versions
chapter_lifecycle: green         # draft→review wired; approved/published reserved (no auto-promote)
chapter_versioning: green        # append-only change stream (change_kind) + 409 optimistic lock
change_stream: green             # WRITE/EDIT/PROMOTE recorded; MERGE/RESTORE reserved
chapters_api: green              # /chapters CRUD + versions replaces 501 stub
graphstate: unchanged            # model_fields identical; run_context absent
existing_routes_unchanged: green # conversation/grounded_chat byte-for-byte
retriever_memory_unchanged: green# make unit-m4-recovery + qualify-m5
m0_m1_m2_m3_m4_m5_tests: green   # make ci
constitution_layers: green       # C1–C8 + R1–R8 (writer pure; persistence via service; no Business telemetry)
adrs: accepted                   # ADR-0031/0032/0033
dogfood_writer: green            # live writer turn → grounded draft + citations
dogfood_chapter_save: green      # persist + version + re-read
benchmarks_recorded: true        # B_write
documentation: complete          # m6-promotion.md + runtime-contract §5 example
knowledge_updated: true          # roadmap, agents/README, writer-agent, graph.md
m6_tag: m6-complete              # manual, after live gates + approval
```

---

## 5. Internal milestones

| Sub | Name | Output |
|-----|------|--------|
| **M6.0** | Spec + ADRs frozen | this spec + ADR-0031/0032/0033 accepted, Critic sign-off |
| **M6.1** | Writer node | `make_writer_node` (pure, fake-LLM tested); not wired |
| **M6.2** | Writer route wiring | activate `writer` route + instrumentation; topology + integration tests |
| **M6.3** | Chapter domain | model + `chapter_versions` migration + `ChapterService` + versioning |
| **M6.4** | Chapters REST + Workspace UI | `/chapters` API + minimal `/workspace` |
| **M6.5** | Qualification | `qualify-m6` + `dogfood-m6` + `B_write` |
| **M6.6** | Promotion | docs, freeze, knowledge mirror, tag |

(See `plans/m6-writing-workspace-plan.md` for full work orders.)

---

## 6. Dependencies, assumptions, risks

### 6.1 Dependencies

M5 runtime (build_graph, router/routing, Event Bus, ConversationService) · M4 RetrievalService/`retriever_node` · M2 `memory_context_node` · LLM seam (Vertex) · `chapters` table (M0) · ADR-0027 reserved `writer` route · ADR-0031/0032/0033 accepted.

### 6.2 Assumptions

- M5 is the frozen baseline; all M5 gates PASS (`m5-complete` @ `bf12c13`).
- `writer.json` is authoritative and stays frozen.
- `GraphState` needs **no** change (`draft`/`citations` already exist) — no ADR-0007 amendment.
- The frontend `/workspace` placeholder (M0) is the home for the workspace UI; rich UI may stay thin in M6.

### 6.3 Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| **Latency** — writer turn = 3 orchestration calls + retrieval + long generation (`B_write` high) | token streaming; single-sample smoke acceptable for the gate; optimization deferred to M11 |
| **Hallucinated citations** | restrict `source_id` to retrieved sources (ADR-0031 §4); full hallucination gating is the Critic (M9) |
| **Scope creep into outline (M8)** | hard non-goals: no `/outline`, no tree ops, no `ChapterCreated` event |
| **Schema change touching M0-frozen `chapters`** | additive-only migration (column default + new table); regenerate `schema.sql`; `make ci` green; ADR-0033 |
| **Regressing M4/M5 routes (C6)** | writer is a *new* route; existing routes untouched; `unit-m4-recovery` + `qualify-m5` green |
| **Premature citation persistence (M7)** | M6 keeps `CitationRef` in-stream/GraphState only; no `sources`/`citations` writes |
| **Checkpoint carry-forward of stale `draft`** | writer overwrites `draft` (set semantics) each turn |

---

## 7. References

- `docs/runtime-constitution.md` (C1–C8) · `decisions/ADR-0030-agent-runtime-layer-boundaries.md` (R1–R8) · `docs/runtime-contract.md` §5 (adding a Business agent)
- `decisions/ADR-0027-multi-agent-graph-topology.md` (reserved routes) · `decisions/ADR-0031/0032/0033`
- `contracts/agents/writer.json` · `contracts/db/schema.sql` (`chapters`) · `contracts/openapi/openapi.yaml` (`/chapters`)
- `knowledge/agents/writer-agent.md` · `knowledge/contracts/graphstate.md`
- `plans/m6-writing-workspace-plan.md` (implementation plan + work orders)
- Format reference: `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`
