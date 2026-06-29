# Capability Inventory

> **Navigation index** for Product Plane capabilities as of baseline **`m6-main`**
> (`79fb52a`, 2026-06-29). Machine-readable detail lives in
> `.asep/capabilities/runtime-platform.yaml` (Runtime Platform + M6 nodes).
>
> **Status legend:** `stable` = promoted & qualified · `planned` = spec/contract
> exists, not implemented · `future` = roadmap only

---

## Product capabilities (user-visible)

| Capability | Status | First milestone | Primary artifacts |
|------------|--------|-----------------|-------------------|
| chat | stable | M1 | `POST /chat`, `ConversationService`, SSE |
| memory | stable | M2 | `MemoryService`, `memory_context_node`, `/memory` |
| ingest | stable | M3 | `DocumentService`, `/upload`, `/documents` |
| retrieve | stable | M4 | `RetrievalService`, `retriever_node`, `/search` |
| orchestrate | stable | M5 | supervisor → planner → router, `TaskService` |
| route | stable | M5 | `route_after_router`, conditional graph dispatch |
| observe | stable | M5 | Runtime Event Bus, `agent_steps`, instrumentation |
| write | stable | M6 | `WriterCapability`, writer route, `DraftResult` |
| chapter-store | stable | M6 | `ChapterService`, `/chapters`, Workspace UI |
| ground | planned | M7 | Grounding Engine (provenance, evidence, bibliography) |
| cite-format | planned | M7 | CSL-JSON → APA/MLA/Chicago (subset of Grounding Engine) |
| outline | planned | M8 | `/outline`, chapter tree, `ChapterCreated` event |
| critique | planned | M9 | `critic` agent, `CritiqueCompleted` event |
| qa | planned | M10 | QA phase over the agent loop |

---

## Runtime Platform capabilities (M5)

| Capability | Status | Phase | Baseline commit |
|------------|--------|-------|-----------------|
| event-contract | stable | M5.4A | `0339643` |
| event-bus | stable | M5.4B | `520d3bb` |
| observability | stable | M5.4C | `630d647` |
| lifecycle-instrumentation | stable | M5.4C | `630d647` |
| qualification (M5) | stable | M5.5 | `82c3dd3` |
| promotion (M5) | stable | M5.6 | tag `m5-complete` @ `bf12c13` |

**Live benchmarks (smoke, 2026-06-29):** B_lat = 9.89s · B_ground = 6.54s

---

## Writing Workspace capabilities (M6)

| Capability | Status | Phase | Baseline commit |
|------------|--------|-------|-----------------|
| writer-agent | stable | M6.1 | `b8e3b20` |
| writer-route | stable | M6.2 | `5ad34bf` |
| chapter-store | stable | M6.3 | `0387929` |
| chapter-api | stable | M6.4 | `648d563` |
| writing-qualification | stable | M6.5 | `2bd6ba6` |
| writing-promotion | stable | M6.6 | tag `m6-complete` / `m6-main` @ `79fb52a` |

**Live benchmark (smoke, 2026-06-29):** B_write = 63.6s

---

## Graph routes (orchestration dispatch)

| Route | Status | Path after router | Milestone |
|-------|--------|-------------------|-----------|
| conversation | stable | → `conversation_node` → END | M5 |
| grounded_chat | stable | → `retriever_node` → `conversation_node` → END | M5 |
| writer | stable | → `retriever_node` → `writer_node` → END | M6 |
| critic | planned | TBD | M9 |
| citation | planned | TBD | M7 |

Route vocabulary is additive (ADR-0027). Existing routes must remain byte-for-byte
unchanged when new routes ship (Constitution C6).

---

## Promotion tags

| Tag | SHA | Meaning |
|-----|-----|---------|
| `m4-complete` | (M4 baseline) | Retrieval qualified |
| `m5-complete` | `bf12c13` | Runtime Platform qualified (branch) |
| `m6-complete` | `79fb52a` | Writing Workspace qualified (branch; **immutable**) |
| `m6-main` | `79fb52a` | Writing Workspace integrated on `main` |

Qualified and integrated baselines may share a SHA after fast-forward merge; the
tags preserve semantic distinction.

---

## Engineering Runtime (separate boundary)

| Capability | Status | Location |
|------------|--------|----------|
| builder-engine | stable | `builder_engine/` — must **not** import `backend.app` |

See ADR-0023, ADR-0026 for ASEP Engineering Runtime vs Product Plane separation.
