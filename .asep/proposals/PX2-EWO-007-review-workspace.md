# Engineering WorkOrder Proposal — PX2-EWO-007

> **Status:** ⏳ **PROPOSED** — dispatch blocked until amendment ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-007-review-workspace`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §3.4, §6.6  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §6.6, §9

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-007 |
| **Sub-agent** | G |
| **Type** | **EWO** — Alignment |
| **EWO category** | **Alignment** |
| **Capability** | `px2-ewo-007-review-workspace` |
| **User capability** | **PX-2.2** Writing Flow (review path) |
| **Milestone** | PX-2 |
| **Layer** | Business |
| **Wave** | px2-parallel/wave_c |
| **Depends on** | PX2-EWO-002, PX2-EWO-003 |

---

## Objective

Activate **Review workspace** with side-by-side **ReviewCompare**, paragraph-level
hunk accept/reject, and operator-confirmed persistence — distinct from `/ai` power mode.

---

## Ownership (exclusive)

```text
frontend/components/review/ReviewCompare.tsx
frontend/components/review/ReviewMode.tsx (extend)
frontend/components/review/ReviewComparePanel.tsx (extend or supersede)
frontend/app/review/**
frontend/lib/reviewDiff.ts
```

**Forbidden:** Writer graph, AI panel, MarkdownEditor internals, `/ai` route.

---

## Scope

### In scope

1. **ReviewCompare** — equal columns original vs proposal; paragraph hunk selection
2. **Accetta parziale** — accept at paragraph granularity
3. **Accept/Reject/Edit manually** — accepted changes persist as chapter draft (operator-approved)
4. **Entry points** — Home Revisione, Writing ⌘⇧R, outline "Invia in revisione"
5. **Full-width layout** — not three-panel; ContextBar visible
6. **Revisione tab** — inline revision queue in Writing right rail (read-only list → link to /review)
7. **Loading skeleton** — side-by-side stagger per UI spec §18

### Out of scope

- Separate Reviewer/Planner agents (PX-6)
- AI-generated review without proposal queue
- `/ai` power mode changes

---

## Constraints

- IR-2: accept requires operator confirm — no silent write
- IR-1: review is workspace route, not full-screen AI
- Distinct from `/ai` — standard revision path only
- Italian operator copy (IR-5)

---

## Acceptance Criteria

- [ ] Review accept/reject changes chapter with operator confirm (AC-11)
- [ ] Side-by-side compare with paragraph-level partial accept
- [ ] Entry from Home, Writing, and outline context menu
- [ ] `/review` full-width layout with ContextBar
- [ ] Revisione tab shows pending revisions for current chapter
- [ ] Tests + `make ci` green

---

## Tests

- `ReviewCompare.test.tsx` — hunk selection, accept/reject
- `ReviewMode.test.tsx` — entry flows
- Extend existing review component tests

---

## Regression

- `make ci`
- PX-1 review shell routes still render
- `/ai` unchanged

---

## WO-TRACE

```text
PX2-EWO-002 + PX2-EWO-003 → PX2-EWO-007 → PX2-EWO-008
```
