# M6 — Writing Workspace — Promotion

**Branch:** `m6-writing-workspace` (from `m5-complete` @ `bf12c13`) ·
**Promotion baseline:** `2bd6ba6` (M6.5) → this doc is M6.6.
**Spec:** `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md` (Frozen).
**ADRs:** 0031 (Writer Capability & Drafting Topology), 0032 (Chapter Ownership/Lifecycle/Query), 0033 (Chapter Versioning as a Change Stream).

## Summary

M6 adds the **Writing Workspace** on top of the promoted M5 runtime: a `writer`
capability that drafts grounded thesis prose, and a durable, versioned chapter
store. The reserved ADR-0027 `writer` route is activated
(`memory_context → retriever → writer → END`); the writer is a swappable
`WriterCapability.write_grounded(brief) -> DraftResult` port whose pure result is
isolated from persistence; `ChapterService` is the sole writer for chapters with an
append-only change stream and optimistic locking; and `/chapters` + a minimal
`/workspace` UI expose the save/edit flow — all **without changing `GraphState`**
(ADR-0007) or the M1 `/chat` seam.

## Capability map (frozen baselines)

| Capability | Milestone | Commit |
|------------|-----------|--------|
| Spec + ADR-0031/0032/0033 frozen | M6.0 | `cfebe01` |
| Writer capability + DraftResult + node (unwired) | M6.1 | `b8e3b20` |
| Writer route wiring + instrumentation | M6.2 | `5ad34bf` |
| Chapter store (ChapterService + change stream + migration 0005) | M6.3 | `0387929` |
| Chapters REST API + Workspace UI | M6.4 | `648d563` (+ `19afb7f` review fix) |
| Writing Qualification (integration + eval + dogfood) | M6.5 | `2bd6ba6` |

## Promotion gates

Deterministic gates (run in this environment):

```yaml
writer_capability: green        # test_writer_node.py (write_grounded → DraftResult, swappable)
writer_isolation: green         # test_writer_node.py (no db/runtime/services/langgraph imports)
writer_node: green              # test_writer_node.py (DraftResult → draft/citations only)
writer_route: green             # test_m6_writer_route.py (memory_context → retriever → writer → END)
existing_routes_unchanged: green# test_m6_writer_route.py + test_m5_graph_topology.py
citation_discipline: green      # test_writer_node.py + test_m6_writing_eval.py (citations ⊆ retrieved)
chapter_service: green          # test_chapter_service.py (sole writer; CRUD + versions)
chapter_lifecycle: green        # test_chapter_service.py (draft/review wired; approved/published reserved)
change_stream: green            # test_chapter_service.py (WRITE/EDIT/PROMOTE; change_kind closed set)
optimistic_lock: green          # test_chapter_service.py + test_chapters_api.py (expected_version → 409)
chapters_api: green             # test_chapters_api.py (/chapters CRUD + versions; /outline not wired)
writing_integration: green      # test_m6_writing_integration.py (route + degraded + persist E2E)
writing_eval: green             # test_m6_writing_eval.py (routing accuracy 1.0 + citation presence)
migration_additive: green       # make drift (schema.sql regenerated; M0 chapters preserved)
graphstate: unchanged           # asserted: model_fields unchanged; run_context absent
retriever_memory_unchanged: green # make unit-m4-recovery (43)
conversation_seam: green        # make qualify-m5 (43); /chat SSE unchanged
scope_creep: false              # make scope (only intentional pre-existing stubs)
m0_m1_m2_m3_m4_m5_tests: green  # make ci (backend 300 passed/1 skipped, frontend 40, builder_engine 65)
adrs: accepted                  # ADR-0031/0032/0033
documentation: complete         # this doc + runtime-contract §5 writer example
knowledge_updated: true         # roadmap, agents/README, writer-agent, graph.md, graphstate
```

Live stack gates (`make up` + Vertex ADC) — recorded 2026-06-29 via `make dogfood-m6`
(backend rebuilt with M6 code; migration 0005 applied):

```yaml
dogfood_writer: green           # writer turn streamed a grounded draft (6620 chars)
dogfood_chapter_save: green     # POST /chapters → PATCH content → versions [WRITE, EDIT]
benchmarks_recorded: true       # B_write = 63.6s (evidence: /tmp/dogfood-m6-evidence.jsonl)
m6_tag: green                   # `m6-complete` @ 79fb52a (qualified); `m6-main` @ 79fb52a (integrated on main)
```

**Benchmark notes:** `B_write` is a full writer turn (3 orchestration LLM calls +
retrieval + a 6620-char chapter draft). Single-sample smoke, not a statistical
benchmark — sufficient for the promotion gate; latency optimization is deferred
(ADR-0027 / M11 consequence).

## Tags (applied 2026-06-29)

| Tag | SHA | Meaning |
|-----|-----|---------|
| `m6-complete` | `79fb52a` | Qualified baseline on `m6-writing-workspace` (**immutable**) |
| `m6-main` | `79fb52a` | Integrated baseline on `main` (fast-forward merge) |

Both tags point to the same commit after FF merge; semantic distinction is preserved.
Post-tag bugs → a new tag (`m6.0.1`), never move `m6-complete` (same policy as `m5-complete`).

## What M6 explicitly did NOT do

Outline tree management / `/outline` / the `ChapterCreated` product event (M8),
citation formatting + `/citations` + `/bibliography` + writes to `sources`/`citations`
(M7), the Critic loop (M9), retrieval/embeddings over chapter content, auto-persist
of the draft from the graph (RunContext target — deferred), and any `GraphState`
schema change. The writer route is qualified deterministically (routing + citation
discipline); live drafting quality is a dogfood/benchmark concern.
