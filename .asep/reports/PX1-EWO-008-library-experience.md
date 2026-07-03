# PX1-EWO-008 — Library Experience

**WorkOrder:** PX1-EWO-008  
**Sub-agent:** C  
**Type:** EWO (Alignment)  
**Date:** 2026-07-03  
**Verdict:** **IMPLEMENTED**

---

## Objective

Library experience shell for Sources and Knowledge — EntityCard grids, filter stub,
cross-navigation between source objects and concept explorer.

---

## Deliverables

| Artifact | Path |
|----------|------|
| Stub data | `frontend/lib/libraryStub.ts` |
| Sources list | `frontend/components/library/SourcesView.tsx` |
| Source detail | `frontend/components/library/SourceDetailView.tsx` |
| Knowledge explorer | `frontend/components/library/KnowledgeView.tsx` |
| Concept detail | `frontend/components/library/KnowledgeDetailView.tsx` |
| Filter bar | `frontend/components/library/LibraryFilterBar.tsx` |
| Routes | `frontend/app/sources/page.tsx`, `sources/[sourceId]/page.tsx` |
| Routes | `frontend/app/knowledge/page.tsx`, `knowledge/[conceptId]/page.tsx` |
| Tests | `SourcesView.test.tsx`, `SourceDetailView.test.tsx`, `KnowledgeView.test.tsx`, `KnowledgeDetailView.test.tsx` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| `/sources` renders source cards (stub) | **PASS** — EntityCard grid + corpus preview data |
| `/sources/[sourceId]` detail stub | **PASS** |
| `/knowledge` concept explorer stub | **PASS** |
| `/knowledge/[conceptId]` detail stub | **PASS** |
| Filter UI placeholder (candidata / approvata / esclusa) | **PASS** — `LibraryFilterBar` |
| Cross-link Sources ↔ Knowledge | **PASS** — related concept/source links in detail views |
| Reuses design tokens + EntityCard | **PASS** |
| Tests + build | **PASS** — 4 library test files, frontend build OK, `make ci` green |

---

## Ownership compliance

Exclusive paths only. No backend, ContextBar, Writing, or AppShell edits.

---

## Merge readiness

**Yes** — Wave A merge order **#3** (after 006 → 009; independent of Writing).

---

## WO-TRACE

```text
PX1-EWO-002 → PX1-EWO-008 (Wave A parallel)
```
