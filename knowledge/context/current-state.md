# Current State

> Snapshot as of **2026-06-25**. Branch: `m3-document-system` (from `main` @ `m2-complete`).

## Where are we?

**M2 promoted. M3 — spec frozen; Phase 1 (DB) implemented in the working tree (uncommitted); Phase 2 next. Build-time: Builder Memory shipped; MB1 Workflow Engine designed + Phase 0 dev foundation added.**

```text
M0 Foundations     ✅ promoted (m0-complete)
M1 Conversation    ✅ promoted (m1-complete)
M2 Memory          ✅ promoted (m2-complete)
M3 Documents       🟡 spec frozen + plan; Phase 1 DB done (uncommitted), Phase 2+ pending
M4+                ⬜ not started
```

> ⚠️ The working tree holds a large body of **uncommitted** work spanning 4
> concerns (builder_memory · M3 Phase 1 DB · MB1 docs · vision). Last commit:
> `4fe9906`. See *What is next?* for the commit plan.

## What is completed?

### M0 / M1 (promoted)
See `context/completed-work.md`. Chat seam frozen: `POST /chat` → `ConversationService` → LangGraph (`conversation_node`) → LiteLLM → SSE. ADR-0001..0014.

### M2 — Phases 1–4 (on `m2-memory-system`, not yet tagged)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **1 — DB** | Alembic `0002_memory_system`: `memories.title`, `memory_versions`, singleton indexes; drift test green | ✅ |
| **2 — Service** | `MemoryService` (sole writer), `WriteConflictError`, `load_prompt_context()` → `PromptContext`, versioning | ✅ |
| **3 — API** | Thin `/memory` CRUD + versions; OpenAPI updated (additive); error mapping 409/404/400 | ✅ |
| **4 — Admin UI** | Memory Administration UI: list/detail/create/edit/delete/versions; `memoryClient` + `useMemoryStore`; Vitest 15/15 | ✅ |
| **5 — Knowledge** | Freeze + `docs/m2-promotion.md` + Health Report v2 | ✅ |
| **6 — Graph** | `memory_context_node`; `START → memory_context_node → conversation_node → END` | ✅ |

**New ADRs (M2):** 0015 (ownership), 0017 (versioning), 0018 (query model).  
**Frozen spec:** `docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md`.

## What is NOT done (M2 remainder)?

- **`MemoryUpdated` events** — event bus still stub; optional M2 close-out (not gate-blocking for graph).
- **M2 promotion gate** — see `docs/m2-promotion.md` (`memory_events` optional; merge + tag pending).
- **Merge + tag `m2-complete`** — after QA/Critic sign-off on promotion doc.

## What is deployed?

- **M0/M1 shell** on `thesisos-prod` (Cloud Run + Cloud SQL). Domain migration on prod may still be `0001_initial` until M2 deploy.
- **M2 memory stack** validated locally via docker compose + Postgres; not deployed to Cloud Run.

## What is validated?

| Suite | Result |
|-------|--------|
| Backend pytest | **46 passed, 14 skipped**, ruff clean (`app`) |
| Backend memory (docker DB) | 8 service + 11 API integration tests green |
| Frontend vitest | **15 passed** |
| Frontend build | green (`/memory`, `/memory/new`, `/memory/[id]`) |
| M0/M1 gates | green (historical) |
| `make ci` (MB1 Phase 0) | **green** — ruff lint, tsc, backend 46/14-skip, frontend 15, drift, isolation |

## Build-time system (BuilderOS)

The Cursor-agent build system is now partly hardened (ADR-0023; MB1 spec):

- **Builder Memory** — `builder_memory/` sidecar shipped (BM25 index, episodic,
  snapshots); ADR-0019. Build-time only, never a runtime dependency.
- **MB1 Build Workflow Engine** — direction frozen:
  `decisions/ADR-0023-build-workflow-engine.md` +
  `docs/superpowers/specs/2026-06-25-thesisos-mb1-workflow-engine-design.md`.
- **MB1 Phase 0 — deterministic validation pipeline (added):** root `Makefile`
  (`make check` / `make ci`), `.pre-commit-config.yaml` (local/offline),
  `.github/workflows/ci.yml` (additive test gate; Cloud Build stays deploy-only).
  `format` is staged for adoption (`make format-fix`), not yet in the gate.

## What is next?

1. **Commit the working tree** — 4 logical commits: builder-memory · M3 Phase 1 DB
   · MB1 (ADR-0023 + spec) · vision (Knowledge-OS reframing).
2. **M3 Phase 2** — document parsing / ingestion per the frozen spec + plan
   (Phase 1 DB already in tree; gate evidence: `docs/m3-phase1-gate.md`).
3. **Validate every change** with `make check` (local / pre-commit) and `make ci`.
4. **Still forbidden until their milestones:** embeddings/retrieval/graph `/search`
   (M4), writer (M6).

See `context/next-actions.md`.

## Quick status table

| Area | State |
|------|-------|
| M0 | ✅ tagged |
| M1 | ✅ tagged on main |
| M2 DB/Service/API/UI | ✅ Phases 1–4 |
| M2 graph injection | ✅ Phase 6 |
| M2 tag | ✅ `m2-complete` on `main` |
| M3 spec | ✅ frozen (Critic approved 2026-06-24) |
| M3 plan | ✅ `plans/m3-document-system-plan.md` |
| M3 code | 🟡 Phase 1 (DB) done (uncommitted); Phase 2+ pending |
| M3+ | ⬜ not started |
| Builder Memory | ✅ shipped (ADR-0019, build-time) |
| MB1 engine | 🟡 ADR-0023 + spec frozen; Phase 0 validation pipeline added |
| Validation gate | ✅ `make ci` green (lint/tsc/tests/drift/isolation) |
| GraphState / RunContext / LLMClient / ConversationService | frozen, unchanged |
| Tests | backend 46/14 skip; frontend 15 |
