# PX5-EWO-002 — Research hub + route scaffolding

> **WorkOrder:** PX5-EWO-002  
> **Wave:** B — Route scaffolding  
> **Status:** **PASS**  
> **Authorization:** `.asep/reports/PX5-AUTHORIZATION-20260707.md`  
> **Date:** 2026-07-07  
> **Layer:** Business (Product Plane)

---

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Research hub component | `frontend/components/research/ResearchHubPage.tsx` | **PASS** |
| Canvas stub | `frontend/components/research/ResearchCanvasStub.tsx` | **PASS** |
| Guided stub | `frontend/components/research/ResearchGuidedStub.tsx` | **PASS** |
| Hub route | `frontend/app/research/page.tsx` | **PASS** |
| Canvas route | `frontend/app/research/canvas/page.tsx` | **PASS** |
| Guided route | `frontend/app/research/guided/page.tsx` | **PASS** |
| Concept focus redirect | `frontend/app/research/[conceptId]/page.tsx` | **PASS** |
| Route registry | `frontend/lib/routes.ts` | **PASS** |
| Unit tests | `ResearchHubPage.test.tsx`, `routes.test.ts` | **PASS** |

---

## Acceptance criteria

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `/research` hub with canvas + guided links | **PASS** | `ResearchHubPage` — UI spec §3 |
| `/research/canvas` route stub wired | **PASS** | `ResearchCanvasStub` accepts `focus` + `view` |
| `/research/[conceptId]` redirect to canvas focus | **PASS** | `redirect(/research/canvas?focus=…)` |
| `ModuleStub` replaced | **PASS** | No `ModuleStub` on research routes |
| `make ci` green | **PASS** | See regression below |

---

## Boundary verification

| Surface | Route | Status |
|---------|-------|--------|
| Research hub | `/research` | Hub with mode cards |
| Spatial canvas | `/research/canvas` | Stub — viewport deferred Wave C |
| Guided trail | `/research/guided` | PX-3.10 placeholder |
| Concept focus | `/research/[conceptId]` | Redirect only |

---

## Regression

| Check | Result |
|-------|--------|
| Frontend unit tests | PASS |
| `make ci` | PASS |

---

## WO-TRACE

```text
PX-3 gate SATISFIED → AUTHORIZE PX-5 Wave B
  → PX5-EWO-002 PASS (this report)
  → Spawn Wave C (canvas viewport + node layer)
```

---

```text
Milestone Status: PASS
Repository Status: main @ d5206a0f (working tree — governance + product)
Remaining Scope: PX5-EWO-003+ canvas viewport
Known Risks: Canvas stub only — no spatial rendering yet
Recommended Next Action: Spawn Wave C backlog → AUTHORIZE PX-5 Wave C
```
