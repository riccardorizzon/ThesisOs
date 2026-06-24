# Milestones — detail & status

> Sources: M0 spec (`docs/superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md`), M1 spec (`docs/superpowers/specs/2026-06-24-thesisos-m1-conversation-system-design.md`), plans under `docs/superpowers/plans/`, gates `docs/m0-promotion.md` / `docs/m1-promotion.md`, `plans/builder/STATE.yaml`.

Only **M0**, **M1**, and **M2** have frozen, detailed specs in the repository. M3+
are defined by contracts and roadmap; specs required before implementation.

---

## M0 — Foundations ✅ (tag `m0-complete`)

**Goal:** stand up architecture, contracts, schema, and GCP infra so M1–M18 add
slices against frozen contracts. **No product feature code.**

**Delivered:**
- `docs/architecture.md` (human mirror of the frozen spec).
- Contracts: `contracts/openapi/openapi.yaml`, 9 agent I/O contracts, event
  catalog, `contracts/db/schema.sql`.
- ADR-0001 … ADR-0010 (frozen).
- Backend skeleton: `/health`, `/ready`, `/metrics`, `/jobs` (501 stub), LLM
  interface (`NotConfiguredLLM`), service stubs, telemetry, 14 domain DB models +
  Alembic `0001_initial`.
- Frontend skeleton: App Router with 6 placeholder routes, api client, zustand store.
- `docker-compose.yml` (pgvector + backend + frontend), Terraform for GCP, Cloud
  Build CI.

**Gate (all green — `docs/m0-promotion.md`):** architecture approved, contracts
frozen, ADRs complete, `terraform_apply` success, `docker_compose` green,
`cloud_run` deployed, `health` green, `db_migrations` green, zero feature debt.

**Verified live on `thesisos-prod`:** 2 Cloud Run services READY (private/auth
invoker), Cloud SQL `thesisos-pg` (POSTGRES_16) RUNNABLE, 15 public tables (14
domain + `alembic_version`), pgvector 0.8.1, `embeddings.embedding = vector(768)`,
`alembic_version = 0001_initial`. Backend tests 8/8, ruff clean.

---

## M1 — Conversation System ✅ (`m1-complete` on `main`)

Promoted. See `context/completed-work.md`. Optional: prod Cloud Run deploy smoke.

---

## M2 — Memory 🟡 (branch `m2-memory-system`)

**Frozen spec:** `docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md`

| Phase | Status | Deliverable |
|-------|--------|-------------|
| 1 DB | ✅ | `0002_memory_system`, `memory_versions`, indexes |
| 2 Service | ✅ | `MemoryService`, `PromptContext`, ADR-0015/0017/0018 |
| 3 API | ✅ | Thin `/memory` CRUD + versions |
| 4 Admin UI | ✅ | Memory Administration at `/memory` |
| 5 Knowledge | ✅ | knowledge/ + `docs/m2-promotion.md` |
| 6 Graph | ⬜ | `memory_context_node`, transient injection |

**Gate:** `docs/m2-promotion.md` — Phases 1–4 green; Phase 6 + tag pending.

**Deferred within M2 close-out:** `MemoryUpdated` events, conversation titling (Q10), restore_version.

**Explicitly not M2:** embeddings, retrieval, RAG, writer, multi-agent runtime.

---

## M3–M18

M3+ require Architect-frozen specs before implementation (ADR-0001). M2 spec is the template for scope discipline.
