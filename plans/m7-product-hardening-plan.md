# M7 — Product Hardening Plan (v2)

> **Phase change:** ASEP → maintenance. ThesisOS → primary delivery track.  
> **Authority:** ADR-0044 · post-audit 2026-07-07 · **review feedback incorporated**  
> **Track allocation:** Product 90% · Runtime bugfix 8% · ASEP 2% (blockers only)

**ASEP rule (binding):** *ASEP evolves only when ThesisOS requires it.*

**Goal:** gate M7 — operatore completa **solo da UI**:

```text
Import → Indice → Knowledge → Search → Chat → Writing → Review → Export
```

**Branch:** `m7-product-hardening`  
**Dashboard:** [`plans/m7-dashboard.md`](m7-dashboard.md) — aggiornare a ogni merge  
**Architecture Lock:** [`plans/m7-architecture-lock.md`](m7-architecture-lock.md)

---

## Program roadmap (post-M7)

```text
ASEP ───────────── maintenance (bugfix only)
                         │
M7 ─── Product Hardening (workflow completo, min stub)
                         │
M7.1 ─ Stub Removal (zero stub modules)     → plans/m7.1-stub-removal-plan.md
                         │
M7.2 ─ UX Polish (perf, loading, onboarding) → plans/m7.2-ux-polish-plan.md
                         │
Release Candidate → Beta
                         │
M8 ─── Product Features (Sources import, export DOCX/PDF, multi-project, …)
                         │
M9 ─── Advanced AI (tool calling, critic, async jobs)
                         │
ASEP evolve ── only if ThesisOS blocked
```

---

## Execution flow (revised)

```text
M7.0 Governance
      │
M7.0b Architecture Lock  ← API/DB/payload frozen; sign-off required
      │
Preflight (builder-engine cycle --dry-run, make ci)
      │
Wave 1a — 2 agenti PILOT (valida metodo)
      │     P-SOURCES-DB + P-KNOWLEDGE-DB
      │     merge → make ci → merge → make ci
      │
Wave 1b — 4 agenti
      │     P-CHAT-PERSIST-BE, P-REVIEW-PERSIST-BE, P-UPLOAD-UI, P-WRITING-GROUND
      │     merge → make ci (OGNI merge, non solo a fine wave)
      │
Wave 2 — domain frontend (disjoint dirs, max 5)
      │     P-SOURCES-FE, P-KNOWLEDGE-FE, P-WRITING-FE, P-REVIEW-FE, P-CHAT-FE
      │     merge → make ci per packet
      │
Wave 3 — E2E + export
      │     P-BIBTEX-DB, P-EXPORT-MIN, P-M7-E2E
      │
Wave 4 — cleanup (README, OpenAPI, legacy routes)
      │
M7 PASS (G1–G11)
```

**Non aprire 6 agenti insieme.** Pilot 2 → valida → poi 4.

---

## Packet Definition of Done (standard)

Ogni packet è **DONE** solo quando **tutti** i checkbox sono veri:

| # | Criterio | Verifica |
|---|----------|----------|
| D1 | Test verdi (comandi in `required_checks`) | CI locale |
| D2 | API documentata in `plans/m7-architecture-lock.md` se nuova/modificata | PR description |
| D3 | UI collegata al backend reale (se packet FE) | Click manuale o screenshot |
| D4 | Nessun fallback silenzioso nel dominio del packet | grep stub nel owned_files |
| D5 | Nessuno stub nel happy path del dominio | idem |
| D6 | Screenshot allegato in PR o `plans/m7-dashboard.md` | Reviewer |
| D7 | Reviewer approva | PR approved |
| D8 | `make ci` green **dopo merge** di questo packet | Merge log in dashboard |

---

## Gate M7 — Program PASS

| # | Criterio |
|---|----------|
| G1 | Upload UI → `POST /upload` |
| G2 | Indicizzazione visibile |
| G3 | Sources = DB only |
| G4 | Knowledge = DB only |
| G5 | Search da picker |
| G6 | Chat persistente |
| G7 | Writing panel grounded |
| G8 | Review accept → DB |
| G9 | BibTeX export DB |
| G10 | Zero redirect rotti |
| G11 | README ≠ M0 |

Script: `make dogfood-m7` (Wave 3).

---

## Work Order Index

| ID | Sub-wave | Layer | Effort | Dipende da |
|----|----------|-------|--------|------------|
| M7.0 | 0 | Gov | S | baseline |
| M7.0b | 0 | Arch | S | M7.0 |
| **P-SOURCES-DB** | **1a** | BE | M | M7.0b |
| **P-KNOWLEDGE-DB** | **1a** | BE | M | M7.0b |
| P-CHAT-PERSIST-BE | 1b | BE | M | M7.0b, 1a merged |
| P-REVIEW-PERSIST-BE | 1b | BE | S | M7.0b, 1a merged |
| P-UPLOAD-UI | 1b | FE | S | M7.0b |
| P-WRITING-GROUND | 1b | BE | M | M7.0b |
| P-SOURCES-FE | 2 | FE | M | P-SOURCES-DB |
| P-KNOWLEDGE-FE | 2 | FE | M | P-KNOWLEDGE-DB |
| P-WRITING-FE | 2 | FE | M | P-UPLOAD-UI, P-WRITING-GROUND |
| P-REVIEW-FE | 2 | FE | M | P-REVIEW-PERSIST-BE |
| P-CHAT-FE | 2 | FE | M | P-CHAT-PERSIST-BE |
| P-BIBTEX-DB | 3 | BE | S | P-SOURCES-DB |
| P-EXPORT-MIN | 3 | BE+FE | M | Wave 2 |
| P-M7-E2E | 3 | QA | M | Wave 2 |
| P-LEGACY-ROUTES | 4 | FE | S | M7 PASS |
| P-DEAD-SCHEMA | 4 | BE | M | Wave 3 |
| P-DOCS-SYNC | 4 | Docs | S | Wave 3 |

**Rimosso:** `P-STUB-POLICY-FE` (troppo trasversale) → stub removal per dominio in Wave 2 FE + M7.1 completo.

---

## M7.0 — Governance (sequenziale)

- ADR-0044 Accepted
- This plan v2
- Dashboard initialized

```bash
git checkout -b m7-product-hardening
make ci   # MUST be green
```

---

## M7.0b — Architecture Lock (sequenziale, prima di qualsiasi agente)

**Objective:** congelare contratti in [`m7-architecture-lock.md`](m7-architecture-lock.md).

**Tasks:**
1. Architect review endpoint list + payload shapes
2. Sign checklist L1–L7
3. Mark Architecture Lock PASS in dashboard

**PASS:** nessun builder Wave 1 parte senza Lock PASS.

---

## Wave 1a — Pilot (2 agenti max)

### P-SOURCES-DB

**owned_files:** `backend/migrations/versions/0007_*`, `backend/app/services/sources/`, `backend/app/graph/corpus_query.py`, `backend/tests/test_sources_*.py`

**DoD focus:** D1, D2, D4 (no CORPUS_PICKER in list path)

```bash
cd backend && pytest tests/test_sources_api.py tests/test_sources_db.py -q && cd .. && make drift
```

---

### P-KNOWLEDGE-DB

**owned_files:** `backend/app/services/knowledge/service.py`, `catalog.py`, `knowledge_search.py`, `backend/tests/test_knowledge_*.py`

**DoD focus:** D1, D2, D4 (no CONCEPT_CATALOG in happy path)

```bash
cd backend && pytest tests/test_knowledge_api.py tests/test_knowledge_crud.py -q
```

### Wave 1a merge protocol

```bash
# Agent 1 finishes → PR → merge → IMMEDIATELY:
make ci
# Update plans/m7-dashboard.md (status 🟢, merge log)

# Agent 2 finishes → PR → merge → IMMEDIATELY:
make ci

# Only if both green → proceed to Wave 1b
```

---

## Wave 1b — 4 agenti (dopo pilot green)

| Packet | owned_files (disjoint) |
|--------|------------------------|
| P-CHAT-PERSIST-BE | `backend/app/api/conversations.py`, `services/conversation/`, `tests/test_conversations_api.py` |
| P-REVIEW-PERSIST-BE | `backend/app/api/proposals.py`, `services/proposal/`, `tests/test_proposals_api.py` |
| P-UPLOAD-UI | `frontend/app/sources/upload/`, `HomeView.tsx`, `routes.ts` |
| P-WRITING-GROUND | `backend/app/api/writing_actions.py`, `tests/test_writing_actions_api.py` |

**Merge rule:** one packet at a time → `make ci` → dashboard update.

---

## Wave 2 — Domain frontend (disjoint directories)

Ogni packet possiede **un solo dominio UI**. Nessun file condiviso tra packet nella stessa wave.

| Packet | Directory ownership | Stub removal in-scope |
|--------|---------------------|----------------------|
| **P-SOURCES-FE** | `frontend/app/sources/`, `components/sources/`, `lib/sourcesClient.ts` | `stubSources`, `libraryStub` usage in sources |
| **P-KNOWLEDGE-FE** | `frontend/app/knowledge/`, `components/knowledge/`, `lib/knowledgeClient.ts` | `stubConcepts` |
| **P-WRITING-FE** | `frontend/app/writing/`, `components/writing/`, `lib/aiActions.ts`, `lib/contextLoad.ts` | mock aiActions, CONTEXT_STUB in writing path |
| **P-REVIEW-FE** | `frontend/app/review/`, `components/review/`, `lib/proposalClient.ts` | in-memory queue → API |
| **P-CHAT-FE** | `frontend/app/ai/`, `components/AiChatView.tsx`, `ConversationList.tsx`, `lib/conversationClient.ts` | static conversation list |

**Nota Home:** `frontend/app/page.tsx` — aggiornare solo in P-UPLOAD-UI (Wave 1b) per CTA import; activity feed stub → M7.2.

---

## Wave 3 — Close the loop

- **P-BIBTEX-DB** — export from DB
- **P-EXPORT-MIN** — chapter `.md` download
- **P-M7-E2E** — Playwright full flow + `make dogfood-m7`

---

## Wave 4 — Cleanup (post M7 PASS or non-blocking)

- Legacy routes, dead schema, README, OpenAPI sync

---

## Command reference — ordine operativo

### 0. Setup (once)

```bash
cd "/home/ricky/agent thesis"
git checkout main && git pull
git checkout -b m7-product-hardening
cp .env.example .env   # GOOGLE_CLOUD_PROJECT, etc.
make install && make ensure-test-db && make ci
```

### 1. M7.0 + M7.0b (sequenziale, no agents)

```bash
# Commit governance artifacts
git add decisions/ADR-0044-product-phase.md plans/m7-*.md
git commit -m "M7.0: product phase governance + architecture lock draft"

# Review & sign plans/m7-architecture-lock.md
# Mark PASS in plans/m7-dashboard.md
git add plans/m7-architecture-lock.md plans/m7-dashboard.md
git commit -m "M7.0b: architecture lock PASS"
```

### 2. Preflight

```bash
builder-engine lint-graph --repo-root .
builder-engine observe --repo-root .
builder-engine policy --repo-root .
builder-engine cycle --dry-run --repo-root .
make up && make status
```

### 3. Wave 1a — 2 worktrees, 2 agenti

```bash
git worktree add .worktrees/p-sources-db -b feat/p-sources-db
git worktree add .worktrees/p-knowledge-db -b feat/p-knowledge-db
# Dispatch 2 agents with prompts below
# Merge feat/p-sources-db → m7-product-hardening
make ci && git push   # update dashboard
# Merge feat/p-knowledge-db → m7-product-hardening
make ci && git push   # update dashboard
# STOP if either CI fails — fix before Wave 1b
```

### 4. Wave 1b — 4 worktrees, 4 agenti (sequenzial merge + CI each)

```bash
git worktree add .worktrees/p-chat-persist-be -b feat/p-chat-persist-be
git worktree add .worktrees/p-review-persist-be -b feat/p-review-persist-be
git worktree add .worktrees/p-upload-ui -b feat/p-upload-ui
git worktree add .worktrees/p-writing-ground -b feat/p-writing-ground
# Merge one at a time: merge → make ci → dashboard → next
```

### 5. Wave 2 — domain FE (5 worktrees, merge + CI each)

```bash
git worktree add .worktrees/p-sources-fe -b feat/p-sources-fe
git worktree add .worktrees/p-knowledge-fe -b feat/p-knowledge-fe
git worktree add .worktrees/p-writing-fe -b feat/p-writing-fe
git worktree add .worktrees/p-review-fe -b feat/p-review-fe
git worktree add .worktrees/p-chat-fe -b feat/p-chat-fe
```

### 6. Wave 3 — gate

```bash
make ci && make qualify-m5 && make qualify-m6 && make unit-m4-recovery
make dogfood-m7
git tag m7-product-hardening -m "M7 gate PASS"
```

### 7. M7.1 → M7.2 → M8

```bash
# Only after tag:
# Follow plans/m7.1-stub-removal-plan.md
# Then plans/m7.2-ux-polish-plan.md
# Then plan M8
```

---

## Agent prompts — Wave 1a (pilot)

### P-SOURCES-DB
```text
Implement M7 packet P-SOURCES-DB per plans/m7-product-hardening-plan.md v2.
Architecture Lock: plans/m7-architecture-lock.md — do not change contracts.
Wire SourcesService to DB; migration 0007; no CORPUS_PICKER in list path.
DoD: all D1–D8 in plan. Screenshot: GET /projects/thesis-agent/sources JSON.
Checks: pytest tests/test_sources_api.py tests/test_sources_db.py -q && make drift
Do not touch frontend/.
```

### P-KNOWLEDGE-DB
```text
Implement M7 packet P-KNOWLEDGE-DB per plans/m7-product-hardening-plan.md v2.
Architecture Lock: plans/m7-architecture-lock.md — do not change contracts.
DB-only knowledge list/search; no CONCEPT_CATALOG happy path.
DoD: all D1–D8. Screenshot: empty DB returns [].
Checks: pytest tests/test_knowledge_api.py tests/test_knowledge_crud.py -q
Do not touch frontend/.
```

---

## Agent prompts — Wave 1b

### P-CHAT-PERSIST-BE
```text
Implement P-CHAT-PERSIST-BE per plans/m7-architecture-lock.md API spec.
Conversations CRUD + persist on POST /chat. DoD D1–D8.
Checks: pytest tests/test_conversations_api.py && make qualify-m5
```

### P-REVIEW-PERSIST-BE
```text
Implement P-REVIEW-PERSIST-BE per architecture lock. Proposals API; accept → ChapterService.
Checks: pytest tests/test_proposals_api.py -q
```

### P-UPLOAD-UI
```text
Implement P-UPLOAD-UI: /sources/upload page, Home CTA, no 404 on redirect.
Owned: frontend/app/sources/upload/, HomeView.tsx, routes.ts only.
Checks: cd frontend && npx tsc && npm run test -- --run HomeView
Screenshot: upload page loaded.
```

### P-WRITING-GROUND
```text
Implement P-WRITING-GROUND: replace retrieved_context=[] with RetrievalService.search().
Checks: pytest tests/test_writing_actions_api.py && make qualify-m6
```

---

## Track C — ASEP during M7

| Trigger | Action |
|---------|--------|
| Product blocked on async jobs | Product `jobs/` only |
| OpenAPI blocks test | P-DOCS-SYNC in Wave 4 |
| Anything else | **Defer** — log in dashboard blockers |

---

## Risk register (updated)

| Risk | Mitigation |
|------|------------|
| Pilot reveals bad architecture lock | Only 2 agents at risk; fix lock before 1b |
| Cross-domain FE conflicts | Disjoint dir ownership per Wave 2 table |
| CI only at wave end | **Mandatory CI per merge** + dashboard merge log |
| Stub policy too broad | Per-domain in Wave 2; M7.1 for complete removal |

---

*Plan version: 2.0 — 2026-07-07 (review feedback)*
