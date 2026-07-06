# Engineering WorkOrder Proposal — PX3-EWO-003

> **Status:** ✅ **IMPLEMENTED** — Integration A PASS
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Wave: `px3-parallel/wave_a_core` (parallel with EWO-002)  
> Spec: `docs/product/specs/px3-knowledge-experience-v2.md` §8  
> UI: `design-system/thesisos/px3-knowledge-experience-ui-spec.md` §5.1

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  classification_mode: retrospective
  classification_pass: px3-20260706-v1
  classified_on: 2026-07-06
  category: A
  hypothesis_id: n/a
  success_metric: "Acceptance criteria in this proposal; Integration A PASS"
  exit_id: n/a
  program_mode: product
```

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-003 |
| **Sub-agent** | C |
| **Type** | **EWO** — Alignment |
| **EWO category** | **Alignment** |
| **Capability** | `px3-ewo-003-knowledge-explorer` |
| **User capability** | **PX-3.2** Knowledge Explorer |
| **Milestone** | PX-3 Knowledge Experience |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX3-EWO-001 |

---

## Objective

Activate **`/knowledge`** as the Knowledge Explorer: browse concept Knowledge Objects
with filters, concept cards, and navigation stubs — not the full Explain Page (§9).

---

## Ownership (exclusive)

```text
frontend/components/knowledge/explorer/**
frontend/app/knowledge/page.tsx
frontend/components/library/KnowledgeView.tsx   (replace stub wiring)
```

**Forbidden:** `components/sources/**`, Explain Page (`/knowledge/[slug]` full §9),
graph view, author index, annotation/citation modules.

---

## Scope

### In scope

1. **Explorer layout** — outline + main grid per UI spec §5.1
2. **Concept cards** — lifecycle badges, link counts, confidence (spec §8.1)
3. **Filters** — knowledge state, core flag, confidence (§8.2); hide Deprecated default
4. **Data wiring** — Knowledge API from EWO-001 (concepts list)
5. **Navigation stubs** — Apri → concept route placeholder; Grafo → disabled/deferred chip
6. **Empty states** — no concepts, filter no-match

### Out of scope

- Explain Page regions A–G (§9 — later wave)
- Knowledge Graph `/knowledge/graph` (§10)
- Author pages
- Semantic search hub (⌘K extension — later)
- AI overlay on Explain Page

---

## Constraints

- Replace `LIBRARY_CONCEPTS` stub with API-backed data
- ADR-0036 — `/knowledge` route already exists; enrich, no new top-level nav
- PX-2 Writing/Context surfaces unchanged

---

## Acceptance Criteria

- [ ] `/knowledge` shows concept cards with lifecycle + confidence badges
- [ ] Filters match spec §8.2 options (minimum: stato, core, confidenza)
- [ ] Deprecated hidden by default; candidate toggle works
- [ ] Cards link to concept route (stub page acceptable — full Explain later)
- [ ] `make ci` green; no PX-2 regression

---

## WO-TRACE

```text
PX3-EWO-001 → PX3-EWO-002 ∥ PX3-EWO-003 → PX3-EWO-004
```
