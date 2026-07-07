# PX5 Integration D — Wave D Discovery Rails

> **Verdict:** **PASS**  
> **Date:** 2026-07-07

| EWO | Title | Status |
|-----|-------|--------|
| PX5-EWO-004 | Canvas shell + selection model | IMPLEMENTED |
| PX5-EWO-005 | Inspector rail | IMPLEMENTED |
| PX5-EWO-006 | Discovery lenses + lens rail | IMPLEMENTED |
| PX5-EWO-007 | Serendipity strip + integration | IMPLEMENTED |

## Shell integration

| Surface | Status |
|---------|--------|
| Three-region shell (lens \| canvas \| inspector) | PASS |
| Header bar (lens dropdown, filters, stubs) | PASS |
| Lens rail — six lenses L-all…L-unread | PASS |
| Inspector rail — Dettaglio/Collegamenti/Azioni | PASS |
| Serendipity strip — ≤5 deterministic cards | PASS |
| Action bar — selection count + disabled handoff | PASS |
| Desktop required <1024px (RR-8) | PASS |

## Cross-module regression

| Check | Result |
|-------|--------|
| PX-2 qualification preserved | PASS |
| PX-3 Sources/Knowledge routes | PASS |
| PX-4 concept graph API | PASS |
| `make ci` | PASS |

## Wave D exit criteria

1. PX5-EWO-004…007 each report PASS — **PASS**
2. PX5-INTEGRATION-D verdict PASS — **PASS** (this document)
3. Lenses operable (L-all, L-gap, L-controversy minimum) — **PASS**
4. Inspector populated for selection — **PASS**
5. Serendipity strip deterministic (RR-7) — **PASS**
6. `make ci` green — **PASS**

## Deferred (Wave E)

- Basket persistence + Writing handoff
- Saved views camera restore
- Minimap / cluster / hard-limit modal
- Full L-author / L-unread API wiring
