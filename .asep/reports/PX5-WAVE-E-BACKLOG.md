# PX-5 Wave E — Backlog Definition

> **Authority:** Architect (Integration E authorization)  
> **Date:** 2026-07-07  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-5 Research  
> **Scope:** Wave E — satellites, basket, saved views, canvas polish

---

## Functional objective

Complete PX-5 product capabilities deferred from Wave D — satellite node layer,
session basket with Writing handoff, saved views persistence, and canvas performance
affordances (minimap, cluster, hard-limit modal).

**Product source:** `docs/product/specs/px5-research-experience-v1.md` §4–§9, §16  
**UI source:** `design-system/thesisos/px5-research-experience-ui-spec.md` §5–§9

**Capabilities addressed:**

| ID | Capability | Wave E coverage |
|----|------------|-----------------|
| **PX-5.1** | Spatial Canvas | Satellite nodes (source, author, decision, chapter) |
| **PX-5.4** | Canvas Selection | Basket drawer + Porta in Scrittura |
| **PX-5.5** | Saved Views | Camera + lens + filter persistence |
| *(polish)* | Performance UX | Minimap, cluster collapse, hard-limit modal |

**Status (2026-07-07):** Wave E **authorized** — `.asep/reports/PX5-AUTHORIZATION-INTEGRATION-E-20260707.md`

**Prerequisite:** PX5-INTEGRATION-D **PASS**

---

## Wave E DAG

```text
PX5-EWO-001…007  Waves A–D                    ✓ PASS
PX5-INTEGRATION-D                             ✓ PASS
      ↓
PX5-EWO-008  Satellite node layer            ← Wave E (first executable)
      ↓
      ├──────────────────┬──────────────────┐
      ▼                  ▼                  │
PX5-EWO-009          PX5-EWO-010            │  (parallel after 008)
Basket + handoff     Saved views            │
      └──────────────────┴──────────────────┘
                         ↓
PX5-EWO-011  Minimap + cluster + hard-limit modal
      ↓
PX5-INTEGRATION-E  Wave E merge review
      ↓
QWO-PX5-001  Milestone qualification
```

| EWO | Title | Parallel after | Status |
|-----|-------|----------------|--------|
| **PX5-EWO-008** | Satellite node layer | PX5-INTEGRATION-D | **authorized** |
| **PX5-EWO-009** | Basket + Writing handoff | PX5-EWO-008 | **authorized** |
| **PX5-EWO-010** | Saved views persistence | PX5-EWO-008 | **authorized** |
| **PX5-EWO-011** | Minimap + cluster + hard-limit | PX5-EWO-009, PX5-EWO-010 | proposed |
| PX5-INTEGRATION-E | Wave E merge review | PX5-EWO-011 | pending |
| QWO-PX5-001 | Milestone qualification | PX5-INTEGRATION-E | pending |

**First executable EWO:** `PX5-EWO-008`

**Parallel dispatch:** EWO-009 and EWO-010 may run concurrently after EWO-008 PASS.

---

## Wave E exit criteria (PASS)

Wave E is **PASS** only when **all** of:

1. **PX5-EWO-008**, **009**, **010**, **011** each report PASS  
2. **PX5-INTEGRATION-E** verdict PASS  
3. AC-1 concept + satellite nodes from PX-4 API  
4. AC-5 basket → Porta in Scrittura imports Context  
5. AC-6 saved view restore on hub **Riprendi mappa**  
6. `make ci` green; no PX-2/PX-3/PX-4 regression  

---

## Candidate EWOs

### PX5-EWO-008 — Satellite node layer

| Field | Value |
|-------|-------|
| **Category** | Infrastructure |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX5-INTEGRATION-D PASS |

**Objective:** Extend knowledge graph API with `profile=canvas` to return concept +
linked satellite nodes per product §4.1; render distinct shapes in viewport.

**Deliverables:**

- Backend: `kind` on graph nodes; canvas limits 80/150/300; satellite enrichment
- Frontend: `canvasLayout` satellite positioning; viewport shapes per kind
- Canvas route: `profile=canvas`, `max_nodes=80`
- Unit tests (backend graph + frontend layout/viewport)
- `.asep/reports/PX5-EWO-008-satellite-node-layer.md`

**Acceptance:**

- [ ] `/knowledge/graph?profile=canvas&depth=2` returns concept + source satellites minimum
- [ ] Author/decision/chapter satellites from catalog stubs when linked
- [ ] Viewport renders distinct shapes per `kind`; concept double-click → Explain preserved
- [ ] PX-3 navigation graph unchanged (`profile` default)
- [ ] `make ci` green

---

### PX5-EWO-009 — Basket + Writing handoff

**Objective:** Session-scoped canvas basket (product §8) + Porta in Scrittura Context import.

**Depends on:** PX5-EWO-008

---

### PX5-EWO-010 — Saved views persistence

**Objective:** Persist camera, lens, filters (product §9); hub **Riprendi mappa**.

**Depends on:** PX5-EWO-008

---

### PX5-EWO-011 — Minimap + cluster + hard-limit modal

**Objective:** Product §5.2–§5.3 performance UX.

**Depends on:** PX5-EWO-009, PX5-EWO-010

---

## WO-TRACE

```text
PX5-INTEGRATION-D PASS
  → AUTHORIZE Integration E (this wave)
  → PX5-EWO-008…011 → PX5-INTEGRATION-E → QWO-PX5-001
```
