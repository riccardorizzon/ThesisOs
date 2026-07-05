# PX1-EWO-004 — Product Routing

**WorkOrder:** PX1-EWO-004  
**Date:** 2026-07-03  
**Verdict:** **IMPLEMENTED**

---

## Deliverables

| Artifact | Path |
|----------|------|
| Route registry | `frontend/lib/routes.ts` |
| Next config redirects | `frontend/next.config.ts` |
| Module stub | `frontend/components/ModuleStub.tsx` |
| AI power mode | `frontend/app/ai/page.tsx`, `components/AiChatView.tsx` |
| Stub modules | `app/research`, `writing`, `sources`, `knowledge` (+ dynamic) |
| Chat legacy | `app/chat/page.tsx` → redirect `/ai` |
| Tests | `frontend/lib/routes.test.ts` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Stub pages Research, Writing, Sources, Knowledge | **PASS** |
| Dynamic segments `[conceptId]`, `[chapterId]`, `[sourceId]` | **PASS** |
| `/chat` → `/ai` | **PASS** (page redirect + next.config) |
| Legacy redirects documented | **PASS** — `LEGACY_REDIRECTS` in `routes.ts` |
| Tests + build | **PASS** — 66 tests, 18 routes |

---

## Legacy redirects (ADR-0036)

| Source | Destination |
|--------|-------------|
| `/chat` | `/ai` |
| `/library` | `/sources` |
| `/workspace` | `/writing` |
| `/outline` | `/writing` |
| `/memory` | `/knowledge` |

**Deferred PX-3:** `/documents/*` → `/sources/*` (document UI still active under `/documents`)

---

## Next Ready

| ID | Title |
|----|-------|
| **PX1-EWO-005** | Context Engine v0 |
| PX1-EWO-006 | Project scope scaffolding |
| QWO-PX1-001 | PX-1 qualification |

---

## WO-TRACE

```text
PX1-EWO-003 → PX1-EWO-004 → PX1-EWO-005 (ContextBar on Writing stub)
```
