# Architect Authorization — PX-5 Research (Wave C)

Program: thesisos-product-v2  
Milestone: PX-5 — Research  
Role: engineering  
Status: **AUTHORIZED**  
Authorized EWO: **PX5-EWO-003**  
Pre-flight: **PASS**  
Operator command: `ASEP: AUTHORIZE PX-5 Wave C` / `ASEP: AUTHORIZE PX5-EWO-003`  
Timestamp: 2026-07-07

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Program graph | ✓ `.asep/programs/thesisos-product-v2.yaml` |
| PX-5 authorized | ✓ Wave A + B complete |
| PX5-EWO-002 (Wave B) | ✓ PASS |
| Wave C backlog | ✓ `.asep/reports/PX5-WAVE-C-BACKLOG.md` |
| Proposal PX5-EWO-003 | ✓ `.asep/proposals/PX5-EWO-003-canvas-viewport-node-layer.md` |
| Product spec | ✓ `docs/product/specs/px5-research-experience-v1.md` §5 |
| UI spec | ✓ `design-system/thesisos/px5-research-experience-ui-spec.md` §4–§5 |
| `make ci` | ✓ green @ `aa11de2a` |
| Repository | ✓ clean on `main` |
| First executable EWO | ✓ PX5-EWO-003 |

---

## Scope boundary

Wave C entry — **canvas viewport + concept node layer** only. Does **not** authorize:

- Lens rail, inspector rail, serendipity strip
- Saved views persistence or discovery API
- Satellite node kinds (source/author/decision/chapter)
- MB2 runtime / SoR / Constitution modifications
- PX-6 Polish

---

## Authorized EWO

| Field | Value |
|-------|-------|
| **Id** | PX5-EWO-003 |
| **Title** | Canvas viewport + node layer |
| **Category** | Infrastructure |
| **Layer** | Business (Product Plane) |
| **Proposal** | `.asep/proposals/PX5-EWO-003-canvas-viewport-node-layer.md` |
| **Depends on** | PX5-EWO-002 PASS |

### Deliverables (in scope)

- Pan/zoom infinite canvas viewport (25–400% zoom)
- Concept node layer (circle 48px / 64px core)
- Typed concept↔concept edges
- Focus entry via `?focus={slug}`
- Performance banner at soft limit
- Viewport culling

---

## WO-TRACE

```text
PX5-EWO-002 PASS (Wave B)
  → AUTHORIZE PX-5 Wave C → PX5-EWO-003 (authorized)
  → Lens / inspector / serendipity (future wave)
```

---

## Recommended next action

Execute **PX5-EWO-003** — implement canvas viewport + node layer.
