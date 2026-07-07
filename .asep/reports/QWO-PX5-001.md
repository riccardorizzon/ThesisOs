# QWO-PX5-001 — PX-5 Research Qualification

> **WorkOrder:** QWO-PX5-001  
> **Type:** Milestone qualification  
> **Status:** **PASS**  
> **Date:** 2026-07-07  
> **Repository:** `main` @ `b6c04da9` (+ Wave E working tree)

---

## Objective

Verify PX-5 Research milestone end-to-end per `docs/product/specs/px5-research-experience-v1.md` §16
(AC-1…AC-10) after Wave E integration PASS.

---

## Pre-flight

| Check | Result |
|-------|--------|
| PX5-INTEGRATION-D | PASS |
| PX5-INTEGRATION-E | PASS |
| PX5-EWO-001…011 | PASS |
| `make ci` | PASS |
| System mutations during QWO | **None** |

---

## Acceptance criteria (product §16)

| # | Criterion | Evidence | Result |
|---|-----------|----------|--------|
| AC-1 | Canvas renders concept + satellite nodes | `profile=canvas` API; `ResearchCanvasViewport` kinds; EWO-008 | **PASS** |
| AC-2 | Pan/zoom + focus deep link | `ResearchCanvasViewport`; `/research/canvas?focus=`; redirect route | **PASS** |
| AC-3 | Soft/hard limits + banner/modal | `show_performance_banner`; `CanvasHardLimitModal`; EWO-011 | **PASS** |
| AC-4 | Lenses reframe without duplicate nodes | `canvasLenses.ts`; RR-2 tests | **PASS** |
| AC-5 | Selection → basket → Writing handoff | `canvasBasket.ts`; `WritingContextBar` chip; EWO-009 | **PASS** |
| AC-6 | Saved view restores camera + lens | `canvasSavedViews.ts`; `?view=` restore; hub Riprendi | **PASS** |
| AC-7 | Double-click → Explain; inspector summary only | Viewport navigate; inspector RR-6 | **PASS** |
| AC-8 | Hub links canvas + guided | `ResearchHubPage.test.tsx` | **PASS** |
| AC-9 | Canvas blocked without concepts | Hub disables card when `conceptCount=0` | **PASS** |
| AC-10 | `make ci` + PX-2/3/4 regression | `make ci` PASS; targeted suites 29/29 frontend research | **PASS** |

---

## Wave deliverable matrix

| Wave | EWOs | Integration | Result |
|------|------|-------------|--------|
| A Spec | 001 | — | PASS |
| B Hub | 002 | — | PASS |
| C Viewport | 003 | — | PASS |
| D Discovery rails | 004…007 | Integration D | PASS |
| E Satellites + polish | 008…011 | Integration E | PASS |

---

## CI gate (2026-07-07)

```text
make ci                         → PASS
  unit-frontend                 283 passed (70 files)
  unit-builder-engine           191 passed
  knowledge_graph               7/7 PASS
  px5_research_suites           29/29 PASS
```

---

## Verdict

```text
QWO-PX5-001: PASS
Recommended Next Action: AUTHORIZE PX-5 promotion (PX5-EWO-012)
```
