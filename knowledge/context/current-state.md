# Current State

> Snapshot as of **2026-06-24** (M2 Phase 6 complete). Branch: `m2-memory-system` (from `main` @ `m1-complete`). Sources: code, tests, `docs/m2-promotion.md`, gates M0/M1, M2 spec.

## Where are we?

**M2 Memory System — Phases 1–6 complete; promotion gate pending.**

M0 and M1 are **promoted and tagged** on `main` (`m0-complete`, `m1-complete`). Active development is on branch `m2-memory-system` for the memory foundation.

```text
M0 Foundations     ✅ promoted (m0-complete)
M1 Conversation    ✅ promoted (m1-complete)
M2 Memory          🟡 Phases 1–6 done; promotion + tag pending
M3+                ⬜ not started
```

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
| Backend pytest | **39 passed, 14 skipped**, ruff clean (changed files) |
| Backend memory (docker DB) | 8 service + 11 API integration tests green |
| Frontend vitest | **15 passed** |
| Frontend build | green (`/memory`, `/memory/new`, `/memory/[id]`) |
| M0/M1 gates | green (historical) |

## What is next?

1. **M2 promotion** — flip remaining gate items in `docs/m2-promotion.md` → merge `m2-memory-system` → `main` → tag `m2-complete`.
2. **M3 Document System** — Architect frozen spec first (Docling, chunks, storage; no embeddings/retrieval).

See `context/next-actions.md`.

## Quick status table

| Area | State |
|------|-------|
| M0 | ✅ tagged |
| M1 | ✅ tagged on main |
| M2 DB/Service/API/UI | ✅ Phases 1–4 |
| M2 graph injection | ✅ Phase 6 |
| M2 tag | ⬜ pending promotion |
| M3+ | ⬜ not started |
| GraphState / RunContext / LLMClient / ConversationService | frozen, unchanged |
| Tests | backend 39/14 skip; frontend 15 |
