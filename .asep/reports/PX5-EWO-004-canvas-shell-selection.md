# PX5-EWO-004 — Canvas shell + selection model

> **WorkOrder:** PX5-EWO-004  
> **Wave:** D — Discovery rails (shell)  
> **Status:** **PASS**  
> **Authorization:** `.asep/reports/PX5-AUTHORIZATION-WAVE-D-20260707.md`  
> **Date:** 2026-07-07  
> **Layer:** Business (Product Plane)

---

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Canvas shell | `frontend/components/research/canvas/ResearchCanvasShell.tsx` | **PASS** |
| Selection helpers | `frontend/lib/canvasSelection.ts` | **PASS** |
| Transform type | `frontend/lib/canvasTransform.ts` | **PASS** |
| Viewport (controlled) | `frontend/components/research/canvas/ResearchCanvasViewport.tsx` | **PASS** |
| Page wrapper | `frontend/components/research/ResearchCanvasPage.tsx` | **PASS** |
| Shell tests | `ResearchCanvasShell.test.tsx` | **PASS** |
| Selection tests | `canvasSelection.test.ts` | **PASS** |
| Viewport tests (updated) | `ResearchCanvasViewport.test.tsx` | **PASS** |

---

## Acceptance criteria

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Three-region shell (240px lens \| canvas \| 320px inspector) | **PASS** | `ResearchCanvasShell` — `canvas-three-region-shell` |
| Multi-select ⌘+click toggle | **PASS** | `applyNodeSelection` + viewport meta click test |
| Shift+drag marquee | **PASS** | `slugsInMarquee` + marquee overlay |
| Esc clears selection | **PASS** | Shell keydown handler + test |
| Node click does not trigger pan | **PASS** | `onPointerDown` stopPropagation on nodes |
| `<1024px` desktop-required (RR-8) | **PASS** | `canvas-desktop-required` |
| Header bar controls (lens/filters/basket disabled) | **PASS** | Stub controls in header |
| Action bar selection count + disabled handoff | **PASS** | `canvas-action-bar` |
| `make ci` green | **PASS** | Full gate |

---

## Boundary verification

| Surface | Status |
|---------|--------|
| Inspector rail content | **Deferred** → PX5-EWO-005 (slot only) |
| Lens rail filters | **Deferred** → PX5-EWO-006 (slot + disabled dropdown) |
| Serendipity strip | **Deferred** → PX5-EWO-007 |
| Basket / Writing handoff | **Deferred** → Wave E |

---

## Regression

| Check | Result |
|-------|--------|
| Frontend unit tests | PASS |
| `make ci` | PASS |

---

## WO-TRACE

```text
AUTHORIZE PX-5 Wave D → PX5-EWO-004 PASS (this report)
  → Dispatch PX5-EWO-005 + PX5-EWO-006 in parallel
```

---

```text
Milestone Status: PASS
Repository Status: main — ready for feat commit
Remaining Scope: PX5-EWO-005, PX5-EWO-006 (authorized, parallel)
Known Risks: Side rails hidden below xl breakpoint; full responsive drawer in later EWO
Recommended Next Action: Execute PX5-EWO-005 + PX5-EWO-006
```
