# Milestones — detail & status

> Sources: M0 spec (`docs/superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md`), M1 spec (`docs/superpowers/specs/2026-06-24-thesisos-m1-conversation-system-design.md`), plans under `docs/superpowers/plans/`, gates `docs/m0-promotion.md` / `docs/m1-promotion.md`, `plans/builder/STATE.yaml`.

**M0–M6** are promoted with frozen specs. **M7–M9** have **Proposed** design
specs + ADRs + promotion templates (2026-07-29) — Architect freeze required before
implementation. **M10–M18** remain roadmap-only.

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

## M2 — Memory ✅ (`m2-complete` on `main`)

Promoted. See `context/completed-work.md`.

---

## M3 — Document System ✅ (`m3-complete` on `main`)

Promoted 2026-06-25. See `docs/m3-promotion.md`, `context/completed-work.md`.

---

## M4 — Retrieval ✅ (`m4-complete` on `main`)

Promoted 2026-06-25. See `docs/m4-promotion.md`, `context/completed-work.md`.

**Frozen spec:** `docs/superpowers/specs/2026-06-25-thesisos-m4-retrieval-system-design.md`  
**ADR:** 0024 (retrieval ownership)

| Phase | Status | Deliverable |
|-------|--------|-------------|
| Spec + plan | ✅ | Frozen spec, ADR-0024, implementation plan |
| Implementation | ✅ | RetrievalService, `/search`, retriever node, embed pipeline |
| Promotion | ✅ | `m4-complete` tag |

---

## M5 — Tool Router / Orchestration ✅

Promoted — see `docs/m5-promotion.md`, tag `m5-complete`.

## M6 — Writing Workspace ✅

Promoted — see `docs/m6-promotion.md`, tags `m6-complete` / `m6-main`.

## M7 — Grounding Engine 🟡 (Proposed)

**Not frozen.** Distinct from ADR-0044 Product Hardening.

| Artifact | Path |
|----------|------|
| Design spec | `docs/superpowers/specs/2026-07-29-thesisos-m7-grounding-engine-design.md` |
| ADR-0053 | `decisions/ADR-0053-citation-capability-topology.md` |
| ADR-0054 | `decisions/ADR-0054-bibliography-styles.md` |
| Promotion gate | `docs/m7-grounding-promotion.md` |

Wave 1 = Citations (resolve + styles + `citation` route). Evidence/confidence = M7.x. Requires Architect Accept before implementation.

## M8 — Outline 🟡 (Proposed)

| Artifact | Path |
|----------|------|
| Design spec | `docs/superpowers/specs/2026-07-29-thesisos-m8-outline-design.md` |
| ADR-0055 | `decisions/ADR-0055-outline-tree-and-publish.md` |
| Promotion gate | `docs/m8-outline-promotion.md` |

## M9 — Critic 🟡 (Proposed)

| Artifact | Path |
|----------|------|
| Design spec | `docs/superpowers/specs/2026-07-29-thesisos-m9-critic-design.md` |
| ADR-0056 | `decisions/ADR-0056-critic-loop-and-approval-gate.md` |
| Promotion gate | `docs/m9-critic-promotion.md` |

## M10–M18

Still roadmap-only — require Architect-frozen specs before implementation (ADR-0001). M6/M7 Proposed specs are the template for scope discipline.
