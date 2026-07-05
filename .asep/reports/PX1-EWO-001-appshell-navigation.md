# PX1-EWO-001 — AppShell and Primary Navigation

**WorkOrder:** PX1-EWO-001  
**Type:** EWO (Infrastructure)  
**Milestone:** PX-1 Foundation  
**Date:** 2026-07-03  
**Verdict:** **IMPLEMENTED**

---

## Objective

Replace developer-centric root layout with researcher-facing AppShell and ADR-0036
primary sidebar navigation.

---

## Deliverables

| Artifact | Path |
|----------|------|
| AppShell component | `frontend/components/AppShell.tsx` |
| Navigation config | `frontend/lib/nav.ts` |
| Root layout | `frontend/app/layout.tsx` |
| Unit tests | `frontend/components/AppShell.test.tsx`, `frontend/lib/nav.test.ts` |
| Proposal | `.asep/proposals/PX1-EWO-001-appshell-navigation.md` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Sidebar: Home, Research, Writing, Sources, Knowledge, Settings | **PASS** |
| AppShell optional `rightPanel` slot | **PASS** |
| Active route highlighted | **PASS** |
| Root layout uses AppShell | **PASS** |
| `npm test` + `npm run build` | **PASS** (47 tests, build OK) |

---

## Layer Declaration

**Business** — Product Plane (`frontend/`). No Runtime Plane changes.

---

## Regression

- Frontend tests: 47/47 PASS
- Next.js production build: PASS
- Legacy routes (`/chat`, `/library`, etc.) unchanged — deferred to PX1-EWO-004
- Default route still redirects `/` → `/chat` — deferred to PX1-EWO-003

---

## ADR Compliance

- **ADR-0036 INV-IA-1:** Sidebar modules match spec (C2 partial — layout only; default route C1 pending EWO-003)
- **ADR-0034 C4:** No thesis-specific strings in AppShell chrome
- **ADR-0035:** No frontend → LLM bypass introduced

---

## Next Ready WorkOrders

| ID | Title | Status |
|----|-------|--------|
| PX1-EWO-002 | Design system tokens | ready (depends PX1-EWO-001 ✓) |
| PX1-EWO-004 | Product routing | ready (depends PX1-EWO-001 ✓) |
| PX1-EWO-005 | Context Engine v0 | ready (depends PX1-EWO-001 ✓) |
| PX1-EWO-006 | Project scope scaffolding | ready (depends PX1-EWO-001 ✓) |

PX1-EWO-003 blocked until PX1-EWO-002 complete.

---

## WO-TRACE

```text
EXECUTION-AUTHORIZATION (PX-1)
  → ARCHITECT-PROGRAM-REVIEW PASS
  → thesisos-product-v2.yaml (active)
  → PX1-EWO-001 proposal approved
  → AppShell implemented
  → PX1-EWO-002 next
```
