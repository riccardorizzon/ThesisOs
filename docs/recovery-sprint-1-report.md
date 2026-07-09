# Recovery Sprint 1 — Product Recovery Report

> **Mode:** Product-only — no platform, language, or architecture work  
> **Started:** 2026-07-09  
> **Frozen:** Research Language v1, Metric Language v1, Research Engine, Builder Engine, ASEP Core (ADR-0050)  
> **Rule:** One fix at a time — independent, reversible, verified

---

## Operating constraints

- No new features, milestones, or architectural changes
- Smallest correct diff per fix
- Verify regressions after each fix (`make unit-frontend` minimum)

---

## Bug backlog (from beta reports V1–V4)

| ID | Issue | Priority |
|----|-------|----------|
| C1 | Knowledge fetch failed | 🔴 |
| C2 | Canvas SSR crash | 🔴 |
| C3 | Graph SSR crash | 🔴 |
| C4 | AI Chat fetch failed | 🔴 |
| C5 | No chapter creation UI | 🔴 |
| C6 | Writing fetch failed | 🔴 |
| C7 | New project crash | 🔴 |
| G1–G8, M1–M5 | UX / polish | 🟡–🟢 |

> **Rule:** One fix at a time — independent, reversible, verified  
> **Anti-pattern registry:** AP-001 — SSR Base URL Misconfiguration

---

## Anti-pattern registry (Recovery Sprint)

| ID | Anti-pattern | Gate |
|----|--------------|------|
| **AP-001** | Direct `NEXT_PUBLIC_API_BASE_URL` / `localhost:8000` in HTTP clients instead of `apiBaseUrl()` | `make ap001-guard` — see `docs/engineering/anti-pattern-registry.md` |

Issue mapping: C1, C2, C3, C6 (SSR), Home progress silent fail → **AP-001**.  
Deploy/tunnel failures with wrong public URL → **A2** (separate root cause, not AP-001).

---

## Recovery Theme A — Anti-Pattern Elimination

**Status:** ✅ **CLOSED** (2026-07-09)

**Goal:** Eliminate AP-001 from all frontend HTTP clients — not per-bug fixes.

### Files modified (URL resolver only)

| File | Change |
|------|--------|
| `frontend/lib/knowledgeClient.ts` | Fix #1 — `apiBaseUrl()` |
| `frontend/lib/chapterClient.ts` | `apiBaseUrl()` |
| `frontend/lib/api.ts` | `apiBaseUrl()` |
| `frontend/lib/conversationClient.ts` | `apiBaseUrl()` |
| `frontend/lib/aiActions.ts` | `apiBaseUrl()` |
| `frontend/lib/proposalClient.ts` | `apiBaseUrl()` |
| `frontend/lib/projectsClient.ts` | `apiBaseUrl()` |
| `frontend/lib/corpusClient.ts` | `searchRemote` → `apiBaseUrl()` |
| `frontend/lib/documentClient.ts` | `apiBaseUrl()` |
| `frontend/lib/memoryClient.ts` | `apiBaseUrl()` |

Already conformant: `contextClient.ts`, `sourcesClient.ts`, `apiBase.ts`.

### Protection (permanent)

| Artifact | Role |
|----------|------|
| `bin/check-ap001-ssr-base-url.sh` | Repository scan |
| `make ap001-guard` | Local + CI target |
| Wired into `make check` and `make ci` | Regression prevention |

### Theme A gate

- [x] Pattern eliminated from all `frontend/lib/*Client*.ts` + `api.ts`
- [x] `make ap001-guard` — **PASS** (0 occurrences outside `apiBase.ts`)
- [x] `make unit-frontend` — 306/306 PASS
- [x] Docker smoke — `/knowledge` no "fetch failed"

### Exceptions (motivated — outside client code)

| Location | Why allowed |
|----------|-------------|
| `frontend/lib/apiBase.ts` | **Authorized resolver** |
| `docker-compose.yml`, `docker/frontend.Dockerfile` | Deploy env injection (A2) |
| `tests/e2e/playwright.config.ts` | E2E env setup |
| Docs / knowledge / `.env.example` | Documentation only |

---

## Fix log

### Fix #1 — C1 (first manifestation of AP-001)

| Field | Detail |
|-------|--------|
| **Bug** | C1 — `/knowledge` shows "fetch failed" while backend is healthy |
| **Root cause** | `knowledgeClient.ts` hardcoded `NEXT_PUBLIC_API_BASE_URL` (`http://localhost:8000`). SSR inside the frontend Docker container cannot reach backend on `localhost` — must use `INTERNAL_API_BASE_URL` (`http://backend:8000`) via `apiBaseUrl()` (already used by `contextClient`, `sourcesClient`). |
| **Evidence** | `curl http://127.0.0.1:3000/knowledge` → HTML contains "fetch failed". From frontend container: `fetch('http://localhost:8000/health')` → ERR; `fetch('http://backend:8000/health')` → OK. |
| **Change** | `frontend/lib/knowledgeClient.ts` — replace module-level `BASE` with `apiBaseUrl()` on all fetch URLs |
| **Tests** | `frontend/lib/knowledgeClient.test.ts` — asserts internal base URL used |
| **Reversible** | Revert single file |
| **Also unblocks** | C2 (canvas), C3 (graph) — same client, same SSR path |
| **Status** | ✅ **VERIFIED** — Docker rebuild; concepts render on `/knowledge` |

---

## Verification checklist (Fix #1)

- [x] `make unit-frontend` — 306/306 PASS
- [x] Docker rebuild: `docker compose up --build -d frontend`
- [x] `/knowledge` — "Aura", "Abbigliamento" visible; no "fetch failed"
- [x] `/knowledge/graph` — HTTP 200
- [x] `/research/canvas` — HTTP 200 (graph payload in SSR)

---

## Next theme (prioritized by architectural ROI)

| Theme | Anti-pattern | Status |
|-------|--------------|--------|
| **Theme B** | AP-002 Error Contract | ✅ CLOSED |
| AP-006 | Unhandled SSR throw (canvas/graph) | ⬜ OPEN |
| AP-005 | Test parity (Docker smoke) | ⬜ deferred |
| AP-004 | Deploy URL | ⬜ Deployment Sprint |
| AP-003 | State duplication | ⬜ OPEN |
| UX | C5, G2–G8 | ⬜ product backlog |

---

## Recovery Theme B — Error Contract Standardization

**Status:** ✅ **CLOSED** (2026-07-09)

| Phase | Deliverable |
|-------|-------------|
| B1 | `docs/engineering/error-contract-v1.md` |
| B2 | SSR: `app/page.tsx`, `app/research/page.tsx`, `app/review/page.tsx` |
| B3 | `WritingWorkspace`, `CommandPalette`, `ProjectSwitcher` + `ApiDegradedBanner` |
| Guard | `make ap002-guard` in `check` + `ci` |

**Verification:** `ap002-guard` PASS · `unit-frontend` 306/306 PASS

---

**Sprint status:** Theme A + Theme B **CLOSED**  
**Registry:** `docs/engineering/anti-pattern-registry.md` · **Contract:** `docs/engineering/error-contract-v1.md`
