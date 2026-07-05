# Engineering WorkOrder Proposal — PX2-EWO-005

> **Status:** ⏳ **PROPOSED** — dispatch blocked until amendment ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-005-decision-cards`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §3.5, §6.2  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §6.2

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-005 |
| **Sub-agent** | E |
| **Type** | **EWO** — Alignment |
| **EWO category** | **Alignment** |
| **Capability** | `px2-ewo-005-decision-cards` |
| **User capability** | **PX-2.4** Decision Visibility |
| **Milestone** | PX-2 |
| **Layer** | Business |
| **Wave** | px2-parallel/wave_a |
| **Depends on** | PX2-EWO-001 |

---

## Objective

Surface **DecisionCard** components in Context Inspector with binding/open status,
influenced chapters, and **ContextBar amber warning** when selection conflicts with
a binding decision — frozen decisions read-only with explanation (OR-5).

---

## Ownership (exclusive)

```text
frontend/components/decisions/DecisionCard.tsx
frontend/components/context/ContextInspector.tsx (decision section only — merge after EWO-001)
frontend/components/context/DecisionBadge.tsx (extend)
frontend/lib/decisionClient.ts
```

**Forbidden:** Settings/admin surfaces, backend Decisions.md mutation, graph redesign,
MarkdownEditor, AI panel internals.

---

## Scope

### In scope

1. **DecisionCard** — DEC-ID, Vincolante/Aperta badge, summary, influenced chapters
2. **Inspector decision section** — accordion in Contesto tab
3. **ContextBar amber state** — full-bar warning when binding decision affects selection
4. **Frozen decision guard** — edit blocked; "Decisione vincolante — non modificabile"
5. **"Chiedi al revisore"** action hook → AI panel (integration point for EWO-003)
6. **Human-readable copy** — no OR protocol names in primary UI

### Out of scope

- Decision creation/editing (Settings / OR-5 admin)
- Raw Decisions.md exposure
- New backend decision storage

---

## Constraints

- OR-5: frozen decisions immutable in product UI
- IR-3: binding decisions in Context Packet (already EWO-001)
- Decision IDs visible but secondary (spec §22)
- Italian operator copy (IR-5)

---

## Acceptance Criteria

- [ ] Decision card readable with ID, status, summary, influenced chapters (AC-8)
- [ ] Frozen/binding decision edit attempt blocked with explanation
- [ ] ContextBar amber state when binding decision affects active selection
- [ ] Decision section in Context Inspector accordion
- [ ] "Chiedi al revisore" dispatches to AI with decision in packet
- [ ] Tests + `make ci` green

---

## Tests

- `DecisionCard.test.tsx` — status badges, read-only frozen state
- ContextBar warning state integration test

---

## Regression

- `make ci`
- OR-5 decision lifecycle unchanged
- PX-1 DecisionBadge still renders on ContextBar

---

## WO-TRACE

```text
PX2-EWO-001 → PX2-EWO-005
```
