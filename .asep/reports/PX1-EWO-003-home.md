# PX1-EWO-003 — Home Page

**WorkOrder:** PX1-EWO-003  
**Type:** EWO (Alignment)  
**Date:** 2026-07-03  
**Verdict:** **IMPLEMENTED**

---

## Objective

Home as default landing route (ADR-0036 INV-IA-2) with deterministic progress,
Continue, quick actions, activity feed per Spec §5.1.

---

## Deliverables

| Artifact | Path |
|----------|------|
| Home page (server) | `frontend/app/page.tsx` |
| Home view | `frontend/components/HomeView.tsx` |
| Progress formula | `frontend/lib/progress.ts` |
| Stub data | `frontend/lib/homeStub.ts` |
| Tests | `progress.test.ts`, `HomeView.test.tsx` |
| Design override | `design-system/thesisos/pages/home.md` |
| Proposal | `.asep/proposals/PX1-EWO-003-home.md` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| `/` → Home (not `/chat`) | **PASS** |
| Deterministic progress stub (ADR-0040) | **PASS** — `computeProgressPct`, unit test snapshot 57% |
| Continue deep link | **PASS** — `findContinueTarget` → `/writing/{id}` |
| Quick actions placeholders | **PASS** — Ricerca, Scrittura, Revisione, Import |
| Activity feed placeholders | **PASS** — `EntityCard` list + empty state |
| Italian operator copy | **PASS** |
| `Link` for navigation | **PASS** — EntityCard migrated to `next/link` |
| Tests + build | **PASS** — 62 tests, build OK |

---

## Design workflow applied

- ui-ux-pro-max UX domain search (progress indicators)
- `design-system/thesisos/pages/home.md` layout
- Frozen tokens from `design-system-v1.md`

---

## Notes

- Chapters loaded from API when available; falls back to `STUB_CHAPTERS`
- `/research`, `/writing`, `/ai` routes → **PX1-EWO-004** (links in place, pages pending)
- Activity feed uses stub until `activities` API (ADR-0040 INV-PS-4)

---

## Next Ready

| ID | Title |
|----|-------|
| **PX1-EWO-004** | Product routing (stub module pages + legacy redirects) |
| PX1-EWO-005 | Context Engine v0 |
| PX1-EWO-006 | Project scope scaffolding |

---

## WO-TRACE

```text
PX1-EWO-002 → PX1-EWO-003 → PX1-EWO-004
```
