# Engineering WorkOrder Proposal — PX3-EWO-002

> **Status:** ✅ **IMPLEMENTED** — Integration A PASS
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Wave: `px3-parallel/wave_a_core` (parallel with EWO-003)  
> Spec: `docs/product/specs/px3-knowledge-experience-v2.md` §12  
> UI: `design-system/thesisos/px3-knowledge-experience-ui-spec.md` §5.4

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-002 |
| **Sub-agent** | B |
| **Type** | **EWO** — Alignment |
| **EWO category** | **Alignment** |
| **Capability** | `px3-ewo-002-sources-module-enrichment` |
| **User capability** | **PX-3.1** (partial), **PX-3.5** (list-level relationships) |
| **Milestone** | PX-3 Knowledge Experience |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX3-EWO-001 |

---

## Objective

Upgrade the **Sources module** from PX-2 corpus browser to PX-3 enriched list:
filter rail, knowledge-object cards, relationship chips, and unified search entry —
without full reader/annotation work (later waves).

---

## Ownership (exclusive)

```text
frontend/components/sources/**
frontend/app/sources/**
backend/app/api/sources.py
backend/app/services/sources/**
frontend/lib/corpusClient.ts          (extend list/query only)
```

**Forbidden:** `components/knowledge/explorer/**`, reader annotation toolbar,
import modal, PDF parse, `components/writing/**`.

---

## Scope

### In scope

1. **Sources list** — card grid using Knowledge Object envelope from EWO-001
2. **Filter rail** — lifecycle, confidence, chapter link filters per UI spec §5.4
3. **Relationship chips** — concept links on source cards (PX-3.5 list level)
4. **Search bar** — corpus search with grouped results stub (PX-3.1 entry point)
5. **Empty / loading states** — Italian copy per design system
6. **Esclusa badge** — preserve PX-2 exclusion semantics (IR-4)

### Out of scope

- Source reader enrichment (§5.5 — later wave)
- Annotation persistence (PX-3.7)
- Full semantic ranking across entity types (Explorer/search hub — later)
- Source import / drag-drop import modal
- Citation builder

---

## Constraints

- Extend PX-2 `SourcesView` / reader — do not break cite flow (PX2-EWO-004)
- ADR-0036 routes unchanged (`/sources`, `/sources/[sourceId]`)
- Conformance program — SoR read-only

---

## Acceptance Criteria

- [ ] `/sources` renders enriched list with filter rail per UI spec §5.4
- [ ] Source cards use Knowledge Object envelope components from EWO-001
- [ ] Lifecycle and confidence badges visible on cards
- [ ] Search returns corpus results; excluded sources omitted from default (AC-13 pattern)
- [ ] PX-2 cite-from-chapter flow still works
- [ ] `make ci` green

---

## WO-TRACE

```text
PX3-EWO-001 → PX3-EWO-002 ∥ PX3-EWO-003 → PX3-EWO-004
```
