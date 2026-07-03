# PX1-EWO-011 — Review Experience

**WorkOrder:** PX1-EWO-011  
**Sub-agent:** F  
**Type:** EWO (Alignment)  
**Milestone:** PX-1 (Review shell)  
**Date:** 2026-07-03  
**Depends on:** PX1-EWO-004 (routing)  
**Verdict:** **IMPLEMENTED**

---

## Objective

Review experience shell — revision workflow placeholder, compare/acceptance UI
stubs. Distinct from `/ai` power mode (ADR-0036, ADR-0039).

---

## Deliverables

| Artifact | Path |
|----------|------|
| Review route | `frontend/app/review/page.tsx` |
| Review mode shell | `frontend/components/review/ReviewMode.tsx` |
| Document selector stub | `frontend/components/review/ReviewDocumentSelector.tsx` |
| Compare placeholder | `frontend/components/review/ReviewComparePanel.tsx` |
| Accept/reject stubs | `frontend/components/review/ReviewActionBar.tsx` |
| Workflow steps | `frontend/components/review/ReviewWorkflowSteps.tsx` |
| Stub data | `frontend/components/review/reviewStub.ts` |
| Route registry | `frontend/lib/routes.ts` (`/review` entry) |
| Unit tests | `ReviewMode.test.tsx`, `ReviewDocumentSelector.test.tsx`, `ReviewComparePanel.test.tsx`, `ReviewActionBar.test.tsx`, `ReviewWorkflowSteps.test.tsx` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| `/review` renders review mode shell | **PASS** |
| Workflow steps visible (select → compare → accept stub) | **PASS** |
| No backend changes | **PASS** |
| Frontend tests + build | **PASS** (87 tests, 24 files; build OK) |

---

## Implementation Notes

- `ReviewMode` state machine: select chapter → compare (diff placeholder) → accept/reject stubs.
- `ReviewWorkflowSteps` shows current step in the revision pipeline.
- `/review` added to `PRODUCT_ROUTES` with module `review`, milestone PX-1.
- Home quick action "Revisione" → `/review` link deferred to **Supervisor merge** (one-line `HomeView.tsx` change per proposal).

---

## Layer Declaration

**Business** — Product Plane (`frontend/app/review/**`, `frontend/components/review/**`, `routes.ts` entry only).

---

## Regression / CI Evidence

| Gate | Result |
|------|--------|
| `make lint` | **PASS** |
| `make typecheck` | **PASS** |
| `make unit-frontend` | **PASS** (87 tests) |
| `npm run build` (frontend) | **PASS** |
| `make ci` (full) | **FAIL** — backend unit pre-existing on branch (not introduced by EWO-011) |

---

## Ownership compliance

Exclusive paths only. No backend, Writing editor, Context Engine, or HomeView edits.

---

## Merge readiness

**Yes** — Wave B merge order **#3** (after 007 → 010).

| Blocker | Owner |
|---------|-------|
| HomeView "Revisione" href still `/ai` | Supervisor one-line update at merge |
| Full `make ci` backend failures | Pre-existing — verify on integrated main |

---

## WO-TRACE

```text
PX1-EWO-004 → PX1-EWO-011 (Wave B) → PX1-EWO-012 → QWO-PX1-001
```
