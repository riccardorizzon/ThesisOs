# PX5-EWO-003 — Canvas viewport + node layer

> **WorkOrder:** PX5-EWO-003  
> **Wave:** C — Canvas viewport  
> **Status:** **PASS**  
> **Authorization:** `.asep/reports/PX5-AUTHORIZATION-WAVE-C-20260707.md`  
> **Date:** 2026-07-07  
> **Layer:** Business (Product Plane)

---

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Canvas layout | `frontend/lib/canvasLayout.ts` | **PASS** |
| Dev fallback graph | `frontend/lib/researchCanvasStub.ts` | **PASS** |
| Canvas viewport | `frontend/components/research/canvas/ResearchCanvasViewport.tsx` | **PASS** |
| Canvas page shell | `frontend/components/research/ResearchCanvasPage.tsx` | **PASS** |
| Canvas route | `frontend/app/research/canvas/page.tsx` | **PASS** |
| Unit tests | `ResearchCanvasViewport.test.tsx` | **PASS** |
| Wave C backlog | `.asep/reports/PX5-WAVE-C-BACKLOG.md` | **PASS** |
| Proposal | `.asep/proposals/PX5-EWO-003-canvas-viewport-node-layer.md` | **PASS** |

**Removed:** `ResearchCanvasStub.tsx` (replaced by viewport)

---

## Acceptance criteria

| Criterion | Result | Evidence |
|-----------|--------|----------|
| `/research/canvas` pan/zoom viewport (not dashed stub) | **PASS** | `ResearchCanvasViewport` — wheel zoom 25–400%, drag pan |
| Concept nodes 48px / 64px core + lifecycle badge | **PASS** | SVG circles + `KnowledgeLifecycleBadge` |
| Typed edges (supports/contradicts/extends/related) | **PASS** | `EDGE_STROKE` + dashed contradicts |
| `?focus={slug}` centers viewport | **PASS** | Focus effect + `getKnowledgeGraph({ depth: 2 })` |
| Performance banner at soft limit | **PASS** | `ResearchCanvasPage` banner when `limits.show_performance_banner` |
| Viewport culling | **PASS** | `visibleWorldBounds` + `isNodeVisible` |
| `make ci` green | **PASS** | 252 frontend tests + full gate |

---

## Boundary verification

| Surface | Route | Status |
|---------|-------|--------|
| Spatial canvas | `/research/canvas` | Viewport + concept node layer |
| Lens rail | — | **Deferred** (future wave) |
| Inspector rail | — | **Deferred** |
| Serendipity strip | — | **Deferred** |
| Saved views | `?view=` | Acknowledged only — no persistence |
| Satellite nodes | — | **Deferred** Wave D+ |

---

## Regression

| Check | Result |
|-------|--------|
| Frontend unit tests | PASS (252) |
| `make ci` | PASS |

---

## WO-TRACE

```text
AUTHORIZE PX-5 Wave C → PX5-EWO-003 PASS (this report)
  → Lens / inspector / serendipity (future wave)
```

---

```text
Milestone Status: PASS
Repository Status: main — working tree dirty (Wave C product + governance)
Remaining Scope: PX-5 Wave D+ (lens rail, inspector, serendipity, saved views)
Known Risks: Stub fallback graph when API offline; no satellite node kinds yet
Recommended Next Action: Spawn Wave D backlog → AUTHORIZE when ready
```
