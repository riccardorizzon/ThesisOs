# Current State

> Snapshot as of **2026-06-25**. Branch: `m3-document-system` (from `main` @ `m2-complete`).

## Where are we?

**M3 Document System — Phases 1–6 complete; tag pending. Build-time Agent OS: MB1 Phase 1 `builder_engine` shipped (`lint-graph`, `status`, `ready`).**

```text
M0 Foundations     ✅ promoted (m0-complete)
M1 Conversation    ✅ promoted (m1-complete)
M2 Memory          ✅ promoted (m2-complete)
M3 Documents       🟢 Phases 1-6 done; merge + tag pending
M4+                ⬜ not started (next: freeze M4 spec)
```

> `make ci` green: backend **77 passed / 31 skipped**, frontend **33 passed**
> (10 files). ⚠️ DB-backed document service/event/integration tests are
> skip-guarded — re-run after fixing local Docker (`make up` + `alembic upgrade head`).

## What is completed?

### M0 / M1 / M2 (promoted)
See `context/completed-work.md`. Chat seam frozen. M2 tagged `m2-complete` on `main`.

### M3 — Document System (branch `m3-document-system`)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **1 — DB** | Alembic `0003_document_system`; drift test green | ✅ |
| **2 — Service** | `DocumentService` sole writer; storage; parsers; chunk_hash | ✅ |
| **3 — API** | `/upload`, `/documents/*`; OpenAPI additive | ✅ |
| **4 — Admin UI** | `/documents` routes; client/store/components; vitest | ✅ |
| **5 — Events** | Event bus + `DocumentUploaded`/`ChunkCreated` | ✅ |
| **6 — Promotion** | `docs/m3-promotion.md` + knowledge mirror | ✅ |

**New ADRs (M3):** 0020 (ownership), 0021 (versioning), 0022 (query model).  
**Frozen spec:** `docs/superpowers/specs/2026-06-24-thesisos-m3-document-system-design.md`.

## What is NOT done (M3 remainder)?

- **DB integration validation** — Docker image store corrupted locally; skip-guarded tests not yet executed against live Postgres.
- **Real parser QA** — PDF/EPUB/DOCX with `backend[parsers]` optional deps (manual fixtures).
- **Merge + tag `m3-complete`** — see `docs/m3-promotion.md`.

## What is deployed?

- **M0/M1 shell** on `thesisos-prod`. M2/M3 stacks validated locally; not deployed to Cloud Run.

## What is validated?

| Suite | Result |
|-------|--------|
| Backend pytest | **77 passed, 31 skipped**, ruff clean |
| Frontend vitest | **33 passed** (10 files) |
| Frontend build | green (`/documents`, `/memory`, `/chat`) |
| `make ci` | **green** |
| M0/M1/M2 gates | green (historical) |

## Build-time system (BuilderOS)

- **Builder Memory** — shipped (ADR-0019).
- **MB1 Phase 0** — `Makefile`, pre-commit, GitHub Actions CI.
- **MB1 Phase 1 — Build Workflow Engine read-model (added):** `builder_engine/`
  with `lint-graph`, `status`, `ready`; 8 unit tests; `validate-state.sh` shim.
- **MB1 Phase 2+** — `schedule`/`sync`, unified state, replan (spec §10).

## What is next?

1. **Fix Docker** → run DB-backed M3 tests (`test_document_service`, `test_document_events`, `test_document_integration`).
2. **Merge + tag** — `docs/m3-promotion.md` promotion steps → `m3-complete`.
3. **M4 Retrieval** — Architect freezes M4 spec (embeddings, `/search`, pgvector) before implementation.

See `context/next-actions.md`.

## Quick status table

| Area | State |
|------|-------|
| M0–M2 | ✅ tagged on main |
| M3 spec/plan | ✅ frozen |
| M3 code | 🟢 Phases 1–6 |
| M3 tag | ⬜ pending merge |
| M4+ | ⬜ spec required |
| Validation gate | ✅ `make ci` green |
| GraphState / ConversationService | frozen, unchanged |
