# PX-5 Wave C — Backlog Definition

> **Authority:** Architect  
> **Date:** 2026-07-07  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-5 Research  
> **Scope:** Wave C — canvas viewport + node layer

---

## Functional objective

Deliver the **spatial canvas viewport** — pan/zoom map with concept nodes and typed
edges — replacing the Wave B route stub.

**Product source:** `docs/product/specs/px5-research-experience-v1.md` §5  
**UI source:** `design-system/thesisos/px5-research-experience-ui-spec.md` §4–§5

---

## Wave C DAG

```text
PX5-EWO-001  Research Experience Spec        ✓ PASS
      ↓
PX5-EWO-002  Research hub + route scaffolding ✓ PASS
      ↓
PX5-EWO-003  Canvas viewport + node layer   ← Wave C (authorized)
      ↓
(future)     Lens rail · inspector · serendipity · saved views
```

| EWO | Title | Status |
|-----|-------|--------|
| **PX5-EWO-003** | Canvas viewport + node layer | **PASS** |

**First executable EWO:** `PX5-EWO-003`

---

## Explicit exclusions (Wave C)

- Discovery lenses (product §6)
- Inspector rail (UI spec §6)
- Serendipity strip (product §7)
- Saved views persistence (PX-5.5)
- Satellite nodes (source/author/decision/chapter)
- Basket and Writing handoff

---

## WO-TRACE

```text
PX5-EWO-002 PASS → AUTHORIZE PX-5 Wave C → PX5-EWO-003
```
