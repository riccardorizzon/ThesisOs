# Architect Authorization — PX-5 Research (Wave D)

Program: thesisos-product-v2  
Milestone: PX-5 — Research  
Role: engineering  
Status: **AUTHORIZED**  
Pre-flight: **PASS**  
Operator command: `ASEP: AUTHORIZE PX-5 Wave D` / `ASEP: AUTHORIZE PX5-EWO-004` / `ASEP: AUTHORIZE PX5-EWO-005` / `ASEP: AUTHORIZE PX5-EWO-006`  
Timestamp: 2026-07-07

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Program graph | ✓ `.asep/programs/thesisos-product-v2.yaml` |
| PX-5 authorized | ✓ Wave A + B + C complete |
| PX5-EWO-003 (Wave C) | ✓ PASS @ `e76a2d7b` |
| Wave D backlog | ✓ `.asep/reports/PX5-WAVE-D-BACKLOG.md` |
| Product spec | ✓ `docs/product/specs/px5-research-experience-v1.md` §5.4, §6, §7 |
| UI spec | ✓ `design-system/thesisos/px5-research-experience-ui-spec.md` §4–§8 |
| Proposals | ✓ PX5-EWO-004, 005, 006 filed |
| `make ci` | ✓ green @ `e76a2d7b` |
| Repository | ✓ dirty governance sync (waived by explicit AUTHORIZE) |
| PX-4 promoted | ✓ `px4-complete` |
| First executable EWO | ✓ PX5-EWO-004 |

---

## Authorized EWOs

| EWO | Title | Dispatch |
|-----|-------|----------|
| **PX5-EWO-004** | Canvas shell + selection model | **Execute now** (first executable) |
| **PX5-EWO-005** | Inspector rail | **Authorized** — parallel after EWO-004 PASS |
| **PX5-EWO-006** | Discovery lenses + lens rail | **Authorized** — parallel after EWO-004 PASS |
| PX5-EWO-007 | Serendipity strip + integration | **Not authorized** — blocked on 005 + 006 |

**Parallel dispatch:** EWO-005 and EWO-006 may run concurrently in isolated worktrees after
EWO-004 PASS. Merge barrier before EWO-007.

---

## Scope boundary

Wave D entry — **discovery rails shell** (lens · inspector · selection · serendipity
deferred to EWO-007). Does **not** authorize:

- PX5-EWO-007 (serendipity + integration) — separate authorization after 005/006 PASS
- Basket drawer + Writing handoff (Wave E)
- Saved views persistence (Wave E)
- Satellite node kinds (Wave E)
- MB2 runtime / SoR / Constitution modifications
- PX-6 Polish

---

## Authorized EWO details

### PX5-EWO-004 — Canvas shell + selection model

| Field | Value |
|-------|-------|
| **Category** | Infrastructure |
| **Layer** | Business (Product Plane) |
| **Proposal** | `.asep/proposals/PX5-EWO-004-canvas-shell-selection.md` |
| **Depends on** | PX5-EWO-003 PASS |

Three-region canvas shell, multi-select, responsive breakpoints per Wave D backlog.

### PX5-EWO-005 — Inspector rail

| Field | Value |
|-------|-------|
| **Category** | Alignment |
| **Layer** | Business (Product Plane) |
| **Proposal** | `.asep/proposals/PX5-EWO-005-inspector-rail.md` |
| **Depends on** | PX5-EWO-004 PASS |

Inspector rail (Dettaglio / Collegamenti / Azioni) per UI spec §6.

### PX5-EWO-006 — Discovery lenses + lens rail

| Field | Value |
|-------|-------|
| **Category** | Alignment |
| **Layer** | Business (Product Plane) |
| **Proposal** | `.asep/proposals/PX5-EWO-006-discovery-lenses.md` |
| **Depends on** | PX5-EWO-004 PASS |

Six discovery lenses + filter popover per product §6.

---

## WO-TRACE

```text
PX5-EWO-003 PASS (Wave C)
  → AUTHORIZE PX-5 Wave D → PX5-EWO-004 (execute now)
  → PX5-EWO-005 + PX5-EWO-006 (parallel after 004 PASS)
  → PX5-EWO-007 (future authorization)
```

---

## Recommended next action

Execute **PX5-EWO-004** immediately. Dispatch **PX5-EWO-005** and **PX5-EWO-006** in
parallel once EWO-004 reports PASS.
