# ADR-0047: Multi-Thesis Workspace — Thesis Manager and project_id partitioning

**Status:** Accepted
**Date:** 2026-07-23
**Plane:** Product
**Related:** ADR-0040 (INV-PS-5), ADR-0045 (INV-COMP-6), ADR-0034 (INV-PV-4),
ADR-0014 (RunContext), PX-6.3 (`docs/product/specs/px6-polish-experience-v1.md` §7),
RC limitation L-01, `plans/multi-thesis-workspace/`

## Context

ADR-0040 ratified INV-PS-5 («`project_id` scopes all product state») but the
implementation stopped at chapters, sources, concepts and proposals. Documents,
memories, conversations, embeddings/retrieval, events, tasks and agent runs are a
single shared pool; the project registry is in-memory and loses created projects on
restart (RC limitation L-01: «isolation is registry-scoped, not DB-partitioned»).
The owner needs multiple independent theses with an active-thesis switcher, while
the current thesis (`thesis-agent`) must keep working unchanged.

## Decision

One ThesisOS, N thesis workspaces. The **Thesis Manager** completes INV-PS-5:

1. **`projects` table** becomes the durable registry SoR (`id`, `display_name`,
   `kind` owned|demo, `status` active|archived, `settings` JSONB). Seed rows:
   `thesis-agent` (owned — the current thesis, unchanged id) and `demo-thesis`
   (demo). `ProjectRegistryService` reads/writes this table and self-heals the two
   seed rows if missing. API: `GET/POST /projects` unchanged, plus
   `PATCH /projects/{id}` (rename).
2. **Identifier scheme.** The default thesis keeps the id `thesis-agent`
   (semantics: Default Thesis; renaming the literal would be a high-risk,
   zero-value data migration). New theses get sequential ids `thesis-002`,
   `thesis-003`, … with a user-chosen `display_name`.
3. **Partition columns.** `project_id VARCHAR(64) NOT NULL` (backfilled to
   `thesis-agent`, indexed) is added to the root aggregates `documents`,
   `memories`, `conversations`, `notes`, `tasks`, `agent_runs`, `events`.
   Child tables inherit scope via FK (chunks/embeddings via document, messages via
   conversation, versions via parent). No hard FK to `projects` in v1 (legacy
   literals exist); the resolver validates against the registry.
4. **Scope resolution.** A single resolver (`explicit param → default
   thesis-agent`) replaces scattered literals. All new API params are **optional**
   with default `thesis-agent`: requests that do not pass a project behave exactly
   as today (backwards compatibility invariant).
5. **Retrieval isolation.** Hybrid search, chat RAG and the writing panel filter by
   `documents.project_id`. Uploads register document + source under the active
   project.
6. **Companion.** The file-SoR flow (`knowledge/thesis-agent/`) remains exclusive
   to `thesis-agent` (ADR-0041 blueprint tenant). Other theses run DB-only
   companion behaviour (generic resume packet, scoped memory/workspace context).
7. **Events.** `project_id` is added as an **additive** field to the runtime event
   envelope and product outbox rows (C5-compatible; no consumer break).
8. **Frontend.** One scope-injection helper feeds every API client from the active
   project (localStorage + SSR cookie); browser persistence keys become
   project-namespaced (`thesisos:{project_id}:…`) with a one-time legacy-key
   migration into the `thesis-agent` namespace; the chat route follows the active
   thesis instead of being pinned to `thesis-agent`.

## Invariants

- **INV-MTW-1:** Any request without an explicit project resolves to
  `thesis-agent` and behaves as before this ADR.
- **INV-MTW-2:** Every product-state read/write path is filtered by `project_id`;
  a thesis can never read or write another thesis's documents, memory, chapters,
  bibliography, embeddings, conversations or configuration.
- **INV-MTW-3:** Created theses survive backend restarts (registry is DB-backed).
- **INV-MTW-4:** Schema migrations for partitioning are additive and reversible;
  backfill attributes existing rows to `thesis-agent`.
- **INV-MTW-5:** Event payload changes are additive only.

## Compliance

- `backend/tests/test_project_registry.py` — DB registry, sequential ids, restart
  survival, rename.
- `backend/tests/test_multi_thesis_isolation.py` — cross-thesis isolation per
  domain (documents, memory, retrieval, conversations, chapters).
- Existing suites (`make ci`) — INV-MTW-1 regression guard.
