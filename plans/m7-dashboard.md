# M7 Dashboard

> Aggiornare **a ogni merge** di packet. Legenda: 🔴 blocked · 🟡 in progress · 🟢 done · ⚪ not started

**Branch:** `main`  
**Architecture Lock:** ☑ PASS (date: 2026-07-07)  
**M7 Gate:** ☑ PASS (date: 2026-07-08)  
**M7.2 Gate:** ☑ PASS (date: 2026-07-08)  
**RC Gate:** ☑ PASS — `v2.0.0-rc.2` @ `5039df77` (date: 2026-07-08)  
**Beta:** 🟢 OPEN — Day 0 validator PASS (cohort onboarding)

---

## Program roadmap

```text
ASEP ── maintenance ──┐
                        ├──► M7 ──► M7.1 ──► M7.2 ──► RC ──► Beta ──► GA / M8
ThesisOS ── primary ────┘    (done)  (done)  (done)  (done)  ▲ HERE   (future)
```

**ASEP rule:** evolves only when ThesisOS requires it (ADR-0044).

---

## Phase status

| Phase | Status | Notes |
|-------|--------|-------|
| M7.0 Governance | 🟢 | ADR-0044 + plan v2 |
| M7.0b Architecture Lock | 🟢 | L1–L7 signed 2026-07-07 |
| Preflight | 🟢 | builder-engine cycle dry-run |
| Wave 1a Pilot (2 agents) | 🟢 | P-SOURCES-DB + P-KNOWLEDGE-DB merged, CI pass |
| Wave 1b (4 agents) | 🟢 | all 4 packets merged, CI pass |
| Wave 2 (domain FE) | 🟢 | all 5 packets merged, CI pass |
| Wave 3 (E2E + export) | 🟢 | dogfood-m7 + Playwright pass |
| Wave 4 (cleanup) | 🟢 | README, OpenAPI, legacy redirects |
| **M7 PASS** | 🟢 | G1–G11 ☑ |
| **M7.1 Stub Removal** | 🟢 | gate 0 stub refs, `make ci` |
| **M7.2 UX Polish** | 🟢 | skeletons, lazy routes, coach marks, Playwright CI |
| **Release Candidate** | 🟢 | `v2.0.0-rc.2` tagged, staging deploy, beta-validator Day 0 |
| **Beta validation** | 🟢 | cohort open — 7-day window, triage tracker active |

---

## Wave 1a — Pilot (max 2 agents)

| Packet | Status | Branch | Merged | CI post-merge | Reviewer |
|--------|--------|--------|--------|---------------|----------|
| P-SOURCES-DB | 🟢 | feat/p-sources-db | 2026-07-07 | ☑ pass | |
| P-KNOWLEDGE-DB | 🟢 | feat/p-knowledge-db | 2026-07-07 | ☑ pass | |

---

## Wave 1b — Remaining backend + upload

| Packet | Status | Branch | Merged | CI post-merge | Reviewer |
|--------|--------|--------|--------|---------------|----------|
| P-CHAT-PERSIST-BE | 🟢 | feat/p-chat-persist-be | 2026-07-07 | ☑ pass | |
| P-REVIEW-PERSIST-BE | 🟢 | feat/p-review-persist-be | 2026-07-07 | ☑ pass | |
| P-UPLOAD-UI | 🟢 | feat/p-upload-ui | 2026-07-07 | ☑ pass | |
| P-WRITING-GROUND | 🟢 | feat/p-writing-ground | 2026-07-07 | ☑ pass | |

---

## Wave 2 — Domain frontend (max 5 parallel, disjoint dirs)

| Packet | Domain | Status | Branch | Merged | CI post-merge | Reviewer |
|--------|--------|--------|--------|--------|---------------|----------|
| P-SOURCES-FE | Sources | 🟢 | feat/p-sources-fe | 2026-07-07 | ☑ pass | |
| P-KNOWLEDGE-FE | Knowledge | 🟢 | feat/p-knowledge-fe | 2026-07-07 | ☑ pass | |
| P-WRITING-FE | Writing | 🟢 | feat/p-writing-fe | 2026-07-07 | ☑ pass | |
| P-REVIEW-FE | Review | 🟢 | feat/p-review-fe | 2026-07-07 | ☑ pass | |
| P-CHAT-FE | Chat | 🟢 | feat/p-chat-fe | 2026-07-07 | ☑ pass | |

---

## Wave 3 — Export + E2E

| Packet | Status | Branch | Merged | CI post-merge | Reviewer |
|--------|--------|--------|--------|---------------|----------|
| P-BIBTEX-DB | 🟢 | m7-product-hardening | 2026-07-07 | ☑ pass | |
| P-EXPORT-MIN | 🟢 | m7-product-hardening | 2026-07-07 | ☑ pass | |
| P-M7-E2E | 🟢 | m7-product-hardening | 2026-07-07 | ☑ pass | |

---

## Wave 4 — Cleanup

| Packet | Status | Branch | Merged | CI post-merge | Reviewer |
|--------|--------|--------|--------|---------------|----------|
| P-LEGACY-ROUTES | 🟢 | m7-product-hardening | 2026-07-08 | ☑ pass | |
| P-DOCS-SYNC | 🟢 | m7-product-hardening | 2026-07-08 | ☑ pass | |

---

## Gate checklist (M7 PASS)

| # | Criterion | Status |
|---|-----------|--------|
| G1 | Upload UI works | ☑ |
| G2 | Index status visible | ☑ |
| G3 | Sources = DB only | ☑ |
| G4 | Knowledge = DB only | ☑ |
| G5 | Search from picker | ☑ |
| G6 | Chat persists | ☑ |
| G7 | Writing panel grounded | ☑ |
| G8 | Review accept → DB | ☑ |
| G9 | BibTeX export | ☑ |
| G10 | No broken redirects | ☑ |
| G11 | README updated | ☑ |

---

## Gate checklist (M7.2 → RC)

| # | Criterion | Status |
|---|-----------|--------|
| G1 | ApiErrorBanner + retry on module errors | ☑ |
| G2 | Empty states with actionable CTAs | ☑ |
| G3 | Loading skeletons + lazy heavy routes | ☑ |
| G4 | Coach marks extended (5 steps) | ☑ |
| G5 | Breadcrumb edge cases (/ai, /review, upload) | ☑ |
| G6 | Playwright `m7-product-flow` in CI | ☑ |
| G7 | `docs/user/getting-started.md` | ☑ |

---

## Gate checklist (RC → Beta)

| # | Criterion | Status |
|---|-----------|--------|
| G1 | `make ci` green on RC commit | ☑ |
| G2 | Staging deploy (docker compose) | ☑ |
| G3 | Beta validator Day 0 (`make beta-validator-rc`) | ☑ |
| G4 | RC bundle + approval certificate | ☑ |
| G5 | Onboarding guide updated | ☑ |
| G6 | Human cohort (5–10) | 🟡 open |
| G7 | 7-day stability + triage | 🟡 in progress |

---

## Blockers

| Date | Packet | Blocker | Resolution |
|------|--------|---------|------------|
| | | | |

---

## Merge log (CI per merge — required)

| Date | Packet | Commit | `make ci` | Notes |
|------|--------|--------|-----------|-------|
| 2026-07-07 | P-SOURCES-DB | b595530e | ☑ pass | migration 0007 + DB-backed sources API |
| 2026-07-07 | P-KNOWLEDGE-DB | 8617019a | ☑ pass | DB-only knowledge list/search |
| 2026-07-07 | P-CHAT-PERSIST-BE | 4a675200 | ☑ pass | conversations API + chat persist |
| 2026-07-07 | P-REVIEW-PERSIST-BE | 5eea046e | ☑ pass | proposals API + migration 0008 |
| 2026-07-07 | P-UPLOAD-UI | 6b3e4718 | ☑ pass | /sources/upload + Home CTA |
| 2026-07-07 | P-WRITING-GROUND | f82ce777 | ☑ pass | retrieval context in writing actions |
| 2026-07-07 | P-SOURCES-FE | 4c745777 | ☑ pass | sources UI wired to API |
| 2026-07-07 | P-KNOWLEDGE-FE | 6c7317e6 | ☑ pass | knowledge explorer API-only |
| 2026-07-07 | P-WRITING-FE | 8909a7ae | ☑ pass | grounded writing UI + index banner |
| 2026-07-07 | P-REVIEW-FE | f76e8375 | ☑ pass | review wired to proposals API |
| 2026-07-07 | P-CHAT-FE | 25f84b93 | ☑ pass | persistent chat threads from API |
| 2026-07-07 | Wave 3 | 36ef13f8 | ☑ pass | P-BIBTEX-DB + P-EXPORT-MIN + P-M7-E2E |
| 2026-07-08 | Wave 4 | 93403046 | ☑ pass | README + OpenAPI M7 + legacy redirects |
| 2026-07-08 | M7.1 | 71fa72fb | ☑ pass | stub removal — API-only runtime |
| 2026-07-08 | M7.2 | 2dda483f | ☑ pass | UX polish — RC gate |
| 2026-07-08 | RC | 5039df77 | ☑ pass | v2.0.0-rc.2 tagged, beta Day 0 PASS |

---

*Last updated: 2026-07-08 (RC v2.0.0-rc.2 — Beta open)*
