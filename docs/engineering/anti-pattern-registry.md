# Architectural Anti-Pattern Registry

> **Document class:** ASEP engineering knowledge (Build Control Plane)  
> **Status:** ACTIVE  
> **Started:** 2026-07-09 (Recovery Sprint 1 Review)  
> **Scope:** Product + platform code quality — not Research Engine experimental knowledge  
> **Related:** `docs/recovery-sprint-1-report.md`, `docs/engineering/error-contract-v1.md`, `bin/check-ap001-ssr-base-url.sh`, `bin/check-ap002-error-contract.sh`

Admission criteria for registry entries: (1) ≥2 distinct issues, (2) common root cause, (3) eliminable via general rule.

---

## Registry

| ID | Nome | Confidence | Evidence | Stato | Issue correlate | Root cause (design) | Guard |
|----|------|------------|----------|-------|-----------------|---------------------|-------|
| AP-001 | SSR Base URL Misconfiguration | 0.99 | 10 | **ELIMINATED** | C1, C2, C3, C6 (SSR) | Direct `NEXT_PUBLIC_*` in clients | `ap001-guard` |
| AP-002 | Inconsistent Error Contract | 0.78 | 14 | **MITIGATED** | Home progress, Research hub, outline, ⌘K, Review | No shared policy for API failure → empty vs banner vs 500 | `ap002-guard` + Error Contract v1 |
| AP-003 | Client-Server State Duplication | 0.45 | 5 | OPEN | N1, G5, outline drift | localStorage + API dual SoR | — |
| AP-004 | Deploy URL Build-Time Coupling | 0.70 | 3 | OPEN | Beta tunnel, R5 | Build-time public URL | Deployment Sprint |
| AP-005 | Test Environment Parity Gap | 0.85 | 1 | OPEN | AP-001 missed in CI | E2E ≠ Docker SSR | — |
| AP-006 | Unhandled SSR Loader Throw | 0.55 | 3 | OPEN | C2/C3 historical | No fault isolation on optional SSR routes | — |

---

## AP-001 — SSR Base URL Misconfiguration

| Field | Detail |
|-------|--------|
| **Status** | ELIMINATED (Theme A closed 2026-07-09) |
| **Pattern** | `const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"` in `frontend/lib/*` |
| **Authorized resolver** | `frontend/lib/apiBase.ts` → `apiBaseUrl()` |
| **Why it existed** | M0 pattern copied across clients; `contextClient` / `sourcesClient` fixed later; no lint rule; dev-on-host masks bug (SSR and API both on localhost) |
| **Why tests missed it** | Vitest mocks `fetch`; E2E uses `npm run dev` on same host (see AP-005); no Docker-compose smoke in CI |
| **Modules fixed** | `knowledgeClient`, `chapterClient`, `api`, `conversationClient`, `aiActions`, `proposalClient`, `projectsClient`, `corpusClient`, `documentClient`, `memoryClient` |
| **Lessons** | (1) Split failure modes: **A1 SSR/Docker** vs **A2 Deploy/public URL**. (2) One resolver, enforced by CI. (3) Eliminate pattern class, not ticket queue. |

---

## AP-002 — Inconsistent Error Contract

| Field | Detail |
|-------|--------|
| **Status** | MITIGATED (Theme B — Error Contract Standardization, 2026-07-09) |
| **Nature** | Absence of policy — not “forbidden catch” |
| **Contract** | `docs/engineering/error-contract-v1.md` |
| **Theme B changes** | SSR Important → Degraded; Review → Error Surface; client Important → `ApiDegradedBanner` |
| **Guard** | `make ap002-guard` — no silent `return []`/`0` on SSR API loaders |
| **Remaining** | Optional surfaces (Level 3) unchanged; AP-006 (canvas/graph unhandled throw) separate |

---

## AP-003 — Client-Server State Duplication (candidate)

| Field | Detail |
|-------|--------|
| **Description** | Domain state split between localStorage and backend without SoR |
| **Symptoms** | Proposals/revisione inconsistent; outline order ≠ API; prefs only local |
| **Modules** | `sessionState.ts`, `proposalQueue.ts`, `WritingOutline.tsx`, `projectPrefs.ts`, `projectContext.ts` (duplicate key read) |
| **Probability** | Medium — intentional for offline UX in places |
| **ROI** | Medium — requires product decisions per domain |
| **Note** | Not all localStorage is wrong — distinguish **cache** vs **SoR** |

---

## AP-004 — Deploy URL Build-Time Coupling (candidate)

| Field | Detail |
|-------|--------|
| **Description** | Frontend bundle assumes reachable `NEXT_PUBLIC_API_BASE_URL` at build time |
| **Symptoms** | Cloudflare tunnel, Cloud Run prod: browser "Failed to fetch" while `/ready` OK |
| **Modules** | `docker/frontend.Dockerfile`, `bin/beta-public-open.sh`, infra CI TODOs |
| **Probability** | High in non-localhost deploys |
| **ROI** | High for beta/prod — **Deployment Recovery Sprint**, not Product Recovery |
| **Distinction** | AP-001 fixed server-side resolution; AP-004 is client-visible public URL |

---

## AP-005 — Test Environment Parity Gap (candidate)

| Field | Detail |
|-------|--------|
| **Description** | CI never runs frontend SSR inside Docker against internal service DNS |
| **Symptoms** | AP-001 shipped; `make ci` green |
| **Modules** | `tests/e2e/playwright.config.ts`, `Makefile` ci aggregate |
| **Probability** | Certain for containerized deploys |
| **ROI** | High — one smoke job prevents AP-001 class regression |
| **Suggested guard** | Optional CI job: `docker compose up` + curl `/knowledge` for "fetch failed" |

---

## Theme log

| Theme | Anti-pattern | Status | Gate |
|-------|--------------|--------|------|
| **Theme A** | AP-001 | **CLOSED** | `ap001-guard` PASS |
| **Theme B** | AP-002 | **CLOSED** | Error Contract v1 + `ap002-guard` PASS |
| Theme C (proposed) | AP-003 | Not started | TBD |
| Deployment Sprint (proposed) | AP-004 | Not started | Deploy checklist |
| Hardening (proposed) | AP-005 | Not started | Docker smoke in CI |
| Theme D (proposed) | AP-006 | Not started | Fault isolation |

---

## How to add an entry

1. Name the pattern (not the bug ID).
2. Map symptoms → issues from beta/recovery reports.
3. Rate impact + probability + architectural ROI.
4. Propose guard (lint, CI, or ADR rule) before closing theme.
5. Set status: `OPEN` → `IN_PROGRESS` → `ELIMINATED`.

---

**Maintainer:** Product Recovery Sprint / ASEP engineering  
**Next review:** After Recovery Sprint Review prioritization (ROI ranking)
