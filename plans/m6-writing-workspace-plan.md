# M6 Writing Workspace — Implementation Plan (Work Orders)

> **For agentic workers:** run each work order via the ASEP skill (`ASEP: implementa M6.x …`). Each WO has explicit PASS criteria — **do not start the next WO until the current gate is green.** ASEP cadence per WO: Observe → Analyze → Strategy → Execute → Verify → Commit → Report. Critic review every WO.

**Goal:** deliver a grounded **Writer agent** route and a versioned **chapter store** (Writing Workspace) on top of the frozen M5 Runtime Platform — **without** GraphState changes, outline management (M8), citation formatting (M7), or the critic loop (M9).

**Spec:** `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md` (Proposed → freeze before M6.1)
**ADRs:** 0031 (writer agent & topology), 0032 (chapter ownership/query), 0033 (chapter versioning) — **Proposed**; accept at M6.0.
**Baseline:** branch off `m5-complete` @ `bf12c13` (working tree clean, `make ci` + `make qualify-m5` + `make unit-m4-recovery` green).
**Branch:** `m6-writing-workspace`.
**Layer discipline (ADR-0030 §4):** every PR declares `Layer: Business | Runtime | Infrastructure`; review order Constitution → Layer → Contracts → Events → Feature → Performance → Code (C7).

**Forbidden in all WOs:** new/changed `GraphState` fields; `/outline` or chapter tree ops; `ChapterCreated` event emission; writes to `sources`/`citations` tables; chapter retrieval/embeddings; chapter writes from graph nodes or API handlers (only `ChapterService`); Engineering Runtime imports of `backend.app`.

**Regression gate (every WO):** `make ci` + `make unit-m4-recovery` + `make qualify-m5` green; `GraphState.model_fields` unchanged.

**Frozen milestones (baseline tracking — filled at each WO's commit):**

| Sub | Capability node | Commit | Scope |
|-----|-----------------|--------|-------|
| M6.0 | (governance) | `cfebe01` | spec + ADR-0031/0032/0033 frozen |
| M6.1 | `writer-agent` | `b8e3b20` | writer capability + DraftResult + node (pure, unwired) |
| M6.2 | `writer-route` | `5ad34bf` | activate `writer` route + instrumentation |
| M6.3 | `chapter-store` | `0387929` | `ChapterService` + `chapter_versions` change stream + migration 0005 |
| M6.4 | `chapter-api` | _pending_ | `/chapters` REST + minimal `/workspace` |
| M6.5 | `writing-qualification` | _pending_ | `qualify-m6` + `dogfood-m6` + `B_write` |
| M6.6 | `writing-promotion` | _pending_ | promotion doc + freeze + tag `m6-complete` |

Frozen scopes **do not reopen** except demonstrable bugs (Constitution C6).

---

## Minimal implementation path (WO order & dependency DAG)

```text
M6.0 (ADRs/spec freeze)
   └─► M6.1 Writer node ─────────┐
            └─► M6.2 Writer route ─┤        (usable: grounded drafting via /chat)
   ┌─────────────────────────────┘
   └─► M6.3 Chapter domain ──► M6.4 Chapters REST + Workspace UI
                                     └─► M6.5 Qualification ──► M6.6 Promotion
```

Rationale: the **smallest user-visible slice** is the writer route (M6.1→M6.2): no schema change, no REST, GraphState already has `draft`/`citations`. Persistence (M6.3→M6.4) is the second increment. M6.1/M6.2 and M6.3 both depend only on the M5 baseline and could run in parallel; the serial order below is the lowest-risk path.

| WO | Capability node | Depends on | Effort |
|----|-----------------|-----------|--------|
| M6.0 | (governance) | baseline | S |
| M6.1 | `writer-agent` | M6.0 | M |
| M6.2 | `writer-route` | M6.1 | M |
| M6.3 | `chapter-store` | M6.0 | M |
| M6.4 | `chapter-api` | M6.3 | M |
| M6.5 | `writing-qualification` | M6.2, M6.4 | M |
| M6.6 | `writing-promotion` | M6.5 | S |

Effort: S ≈ ≤0.5 day · M ≈ 0.5–1.5 day (single-builder, TDD).

---

## WO M6.0 — Freeze spec + ADRs (governance gate)

- **Objective:** accept the M6 spec and ADR-0031/0032/0033; record Critic sign-off. No product code.
- **Context:** ADRs are `Proposed`; ASEP `develop` cannot start until requires-ADRs are `Accepted` (capability resolver §5).
- **Files:** `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md` (Draft→Frozen), `decisions/ADR-0031/0032/0033` (Proposed→Accepted), `.asep/governance/manifest.yaml` (repoint `plan:` → this file), `.asep/capabilities/runtime-platform.yaml` (M6 nodes already added; flip blockers as ADRs accept).
- **Components:** governance only.
- **Dependencies:** baseline gates green.
- **Tests required:** none (doc gate). Verify `make ci` still green (docs-only).
- **PASS:** spec Frozen; ADRs Accepted; manifest points to M6 plan; capability graph consistent.
- **Rollback:** revert ADR status to Proposed; restore manifest pointer to `plans/m5-tool-router-plan.md`.

---

## WO M6.1 — Writer capability + node (Business, not wired)

- **Objective:** implement the `WriterCapability` port (`write_grounded(brief) -> DraftResult`), a default `LLMWriter` implementation, and a thin `make_writer_node(writer)` adapter honoring `contracts/agents/writer.json`; **not** wired to the graph.
- **Context:** ADR-0031 §2/§3/§5/§7 — writer is a swappable capability returning a **pure `DraftResult`**, isolated from `ChapterService`/REST/DB/Event Bus; the node only adapts `DraftResult` → frozen state. Mirrors `make_retriever_node` for graph packaging.
- **Files:**
  - create `backend/app/schemas/draft.py` — `WriterBrief`, `DraftResult` (Pydantic; `DraftResult{draft, citations, metadata, reasoning?, metrics}`);
  - create `backend/app/graph/writer.py` — `WriterCapability` Protocol, `LLMWriter` (injected `LLMClient`, streams `astream`), `make_writer_node(writer)` adapter;
  - create `backend/app/graph/orchestration/writer_prompt.py` — compose the writer wire from `plan` + `retrieved_context` + `messages`;
  - create `backend/tests/test_writer_node.py`.
- **Components:** `WriterCapability` port; `LLMWriter` impl; `DraftResult`/`WriterBrief`; node adapter; writer prompt-wire helper.
- **Dependencies:** M6.0; frozen `GraphState`, `writer.json`.
- **Tests required:**
  - capability happy path (fake LLM) → `DraftResult.draft` set, `citations ⊆ retrieved_context` sources, `metrics` populated;
  - adapter maps `DraftResult` → `{messages(+assistant), draft, citations, errors}` only (writer.json); `metadata`/`reasoning`/`metrics` NOT in the state partial;
  - `empty_context` → error appended, best-effort draft, no citations;
  - `generation_failed` (LLM raises) → error appended, no draft, no crash;
  - citation discipline: invented `source_id` dropped;
  - **isolation/purity:** `graph/writer.py` + `schemas/draft.py` import no `app.db`, `app.runtime`, `app.services.chapter`, telemetry (R1/R3/R8/C3);
  - swappability: a second fake `WriterCapability` drops into `make_writer_node` unchanged.
- **PASS:**
  ```yaml
  writer_capability_unit: green
  draft_result_mapping: green   # DraftResult → writer.json state only
  writer_isolation: green       # no db/runtime/chapter-service/telemetry imports
  writer_swappable: green       # port accepts an alternate impl
  graphstate: unchanged
  make_ci: green
  unit_m4_recovery: green
  qualify_m5: green
  ```
- **Rollback:** delete `schemas/draft.py`, `graph/writer.py`, `orchestration/writer_prompt.py`, test; no wiring touched → graph unaffected.

---

## WO M6.2 — Writer route wiring + instrumentation (Runtime)

- **Objective:** activate the reserved `writer` route: `memory_context → retriever → writer → END`; instrument the writer node on the Event Bus. Existing routes byte-for-byte unchanged.
- **Context:** ADR-0031 §1/§3/§7; only `build_graph`/`routing.py`/route constants change; reuses `retriever_node` unchanged (C6).
- **Files:** modify `backend/app/graph/orchestration/constants.py` (`WRITER_ROUTE`); modify `backend/app/graph/orchestration/coerce.py` (recognize `writer` + drafting heuristic); modify `backend/app/graph/routing.py` (`route_after_router` writer edge key); modify `backend/app/graph/conversation.py` (`build_graph`: add `writer_node`, conditional edge, retriever→writer edge, instrument writer phase `implement`); modify `contracts/agents/router.json` (route enum, additive) if enumerated; create `backend/tests/test_m6_writer_route.py`; modify `backend/tests/test_routing.py`, `test_m5_graph_topology.py` (additive cases).
- **Components:** route vocabulary; conditional dispatch; Event Bus wrapper for writer.
- **Dependencies:** M6.1.
- **Tests required:**
  - `route=writer` → retriever invoked then writer; conversation_node NOT invoked;
  - `route=conversation`/`grounded_chat` unchanged (regression);
  - writer node emits `NodeStarted`/`NodeCompleted` (and `NodeFailed` on error) via the bus; zero-subscriber still valid;
  - E2E InMemorySaver + fake LLM: writer route fills `draft`/`citations`;
  - `GraphState` field list unchanged.
- **PASS:**
  ```yaml
  writer_route: green
  conditional_routing: green
  existing_routes_unchanged: green   # conversation + grounded_chat
  writer_events: green               # NodeStarted/Completed/Failed
  graphstate: unchanged
  make_ci: green
  unit_m4_recovery: green
  qualify_m5: green
  ```
- **Rollback:** revert `build_graph`/`routing.py`/constants/coerce edits; writer node remains shipped but unwired (M6.1 state).

---

## WO M6.3 — Chapter domain (model + migration + ChapterService)

- **Objective:** durable, versioned chapter store; `ChapterService` is the **sole writer** for `chapters`/`chapter_versions` (ADR-0032/0033). No graph, no REST.
- **Context:** mirrors `DocumentService` + `document_versions`; additive Alembic migration; optimistic lock.
- **Files:** Alembic migration (add `chapters.version`, create `chapter_versions` as an append-only change stream with `change_kind`); modify `backend/app/db/models` (Chapter version col, ChapterVersion model); create `backend/app/services/chapter/{__init__,service,exceptions}.py`; create `backend/app/schemas/chapter.py` (`ChapterRecord`, `ChapterVersionRecord`); regenerate `contracts/db/schema.sql`; create `backend/tests/test_chapter_service.py`.
- **Components:** `ChapterService` (create/get/list/update_content/update_metadata/list_versions); lifecycle `draft→review→approved→published` (ADR-0032 §3, M6 wires draft/review); change stream `change_kind ∈ {WRITE,EDIT,PROMOTE,MERGE,RESTORE}` (ADR-0033, M6 emits WRITE/EDIT/PROMOTE); `word_count` recompute.
- **Dependencies:** M6.0.
- **Tests required:**
  - create → `chapters.version=1` + `WRITE` change-stream entry;
  - update_content/metadata → version increments + `EDIT` entry; `word_count` recomputed;
  - status transition → `PROMOTE` entry; `approved`/`published` accepted but never auto-set;
  - optimistic lock: stale `expected_version` → `409 write_conflict`;
  - list ordered by `order_index`; `q` ILIKE on title only (no chunk/content search);
  - sole-writer: service is the only writer (no direct session writes elsewhere — scope scan);
  - migration up/down clean; schema snapshot matches; M0 chapters preserved.
- **PASS:**
  ```yaml
  chapter_service_unit: green
  chapter_lifecycle: green         # draft/review wired; approved/published reserved
  change_stream: green             # WRITE/EDIT/PROMOTE entries; change_kind closed set
  optimistic_lock: green
  migration_additive: green        # m0 chapters preserved; schema.sql regenerated
  make_ci: green
  unit_m4_recovery: green
  qualify_m5: green
  ```
- **Rollback:** downgrade migration (drop `chapter_versions`, drop `chapters.version`); remove `services/chapter/`, `schemas/chapter.py`, tests; restore `schema.sql`.

---

## WO M6.4 — Chapters REST API + minimal Workspace UI

- **Objective:** expose `ChapterService` via `/chapters` (replace `501` stub) and a thin `/workspace` UI that streams a writer turn into an editor and saves a versioned chapter.
- **Context:** REST is the persistence surface that connects the ephemeral writer draft (M6.2) to durable chapters (M6.3) — ADR-0031 §5, ADR-0032 §4.
- **Files:** create `backend/app/api/chapters.py` (router); register in app; modify `contracts/openapi/openapi.yaml` (`/chapters`, `/chapters/{id}`, `/chapters/{id}/versions` + `Chapter*` schemas); create `backend/tests/test_chapters_api.py`; frontend: `frontend/app/workspace/*` (list + editor + "draft with AI" calling `/chat` writer route + save → `PATCH /chapters/{id}`); api client + types.
- **Components:** chapters HTTP router; OpenAPI; minimal workspace UI.
- **Dependencies:** M6.3 (and M6.2 for the live "draft with AI" action).
- **Tests required:**
  - POST/GET/PATCH/versions happy paths; 404 unknown; 409 stale version; 422 invalid status;
  - `/outline` still `501`;
  - SSE writer turn unchanged externally (reuse `test_chat_endpoint` shape);
  - frontend: smoke (list renders, save round-trips) per existing frontend test conventions.
- **PASS:**
  ```yaml
  chapters_api: green
  openapi_valid: green
  outline_still_stub: green
  conversation_seam: green
  make_ci: green
  unit_m4_recovery: green
  qualify_m5: green
  ```
- **Rollback:** restore `/chapters` `501` stub + remove router/UI/tests; `ChapterService` (M6.3) remains usable internally.

---

## WO M6.5 — Writing qualification

- **Objective:** qualify the writing capability end-to-end (route + persistence + errors + grounding/citation eval + live dogfood + `B_write`).
- **Context:** mirrors M5.5; deterministic eval (no live LLM) + live dogfood on the running stack.
- **Files:** create `backend/tests/test_m6_writing_integration.py`; create `backend/tests/fixtures/m6_writing_eval.json` (drafting prompts + expected route + citation-presence assertions); create `backend/tests/test_m6_writing_eval.py`; create `bin/dogfood-m6-writing-run.sh`; modify `Makefile` (`qualify-m6`, `dogfood-m6`).
- **Components:** integration suite; eval harness; dogfood script; benchmark capture.
- **Dependencies:** M6.2 + M6.4.
- **Tests required (gates):**
  - writer route E2E via HTTP (fake LLM): draft streamed, citations ⊆ retrieved;
  - chapter persist E2E: writer draft → `PATCH /chapters` → versioned row → re-read;
  - error contracts: `empty_context`/`generation_failed` still yield a finalized turn;
  - eval: drafting prompts route to `writer`; citation-presence on grounded drafts;
  - live `dogfood-m6`: real writer turn (Vertex) produces grounded draft + saves chapter; record `B_write`.
- **PASS:**
  ```yaml
  writing_integration: green
  writing_eval: green
  error_contracts: green
  dogfood_writer: green
  dogfood_chapter_save: green
  benchmarks_recorded: true        # B_write
  make_ci: green
  unit_m4_recovery: green
  qualify_m5: green
  ```
- **Rollback:** remove qualification suites/fixtures/script + Makefile targets; capability stays at M6.4.

---

## WO M6.6 — Promotion

- **Objective:** freeze M6, publish promotion doc, mirror knowledge, set capability nodes `done` + baselines, tag `m6-complete` (manual, after live gates + explicit approval).
- **Context:** mirrors M5.6 promotion stage (`.asep/pipeline/promotion.md`).
- **Files:** create `docs/m6-promotion.md` (promotion-criteria yaml green); modify `docs/runtime-contract.md` §5 (worked "add the writer agent" example; event names additive only — no freeze breakage); modify `knowledge/project/roadmap.md` (M6 ✅), `knowledge/agents/README.md` + `knowledge/agents/writer-agent.md` (implemented), `knowledge/architecture/graph.md` (writer route), `knowledge/contracts/graphstate.md` (writer ownership notes); modify `.asep/capabilities/runtime-platform.yaml` (M6 nodes → `done` + baselines); write `plans/handoffs/HANDOFF_*_m6-*.md`.
- **Components:** promotion doc; knowledge mirror; capability baselines; tag.
- **Dependencies:** M6.5 all green.
- **Tests required:** all promotion gates from the spec §4 (re-run, evidence-backed); no test weakened.
- **PASS:**
  ```yaml
  documentation: complete
  knowledge_updated: true
  capability_graph: done_with_baselines
  all_promotion_gates: green
  m6_tag: m6-complete              # only on explicit go-ahead
  ```
- **Rollback:** `m6-complete` is immutable; post-tag bugs → new tag (`m6.0.1`), never move `m6-complete` (per M5 user preference).

---

## Promotion criteria, gates & benchmarks (Phase 6 summary)

- **Intermediate gates:** each WO's PASS yaml above; `make ci` + `make unit-m4-recovery` + `make qualify-m5` green after every WO (no half-wired graph).
- **Final gate:** spec §4 promotion yaml (deterministic) + live `dogfood-m6` (`dogfood_writer`, `dogfood_chapter_save`, `B_write`).
- **Benchmarks:** `B_write` = end-to-end writer turn latency (orchestration + retrieval + generation), single-sample smoke (statistical benchmark deferred to M11, per ADR-0027 latency consequence).
- **Automated tests:** writer node unit + purity; routing/topology; chapter service + versioning + optimistic lock; chapters API; writing integration + eval; full regression (M0–M5).
- **Manual tests:** live `/workspace` drafting session (ask to draft a chapter, verify grounded prose + citation markers, save, reload, view version history); 409 conflict by concurrent edit.

## References

- `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md`
- `decisions/ADR-0031-writer-agent-drafting-topology.md`, `ADR-0032-chapter-ownership-query-model.md`, `ADR-0033-chapter-versioning.md`
- `docs/runtime-contract.md` §5 · `decisions/ADR-0030-...` · `decisions/ADR-0027-...`
- `contracts/agents/writer.json` · `contracts/db/schema.sql` · `contracts/openapi/openapi.yaml`
- Format reference: `plans/m5-tool-router-plan.md`
