# Engineering WorkOrder Proposal — PX1-EWO-007

> **Status:** APPROVED (2026-07-03) — Wave B, merge after EWO-009

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-007-writing-workspace`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-007 |
| **Sub-agent** | B |
| **Type** | EWO (Alignment) |
| **Milestone** | PX-1 (layout shell; full editor PX-2) |
| **Depends on** | PX1-EWO-009 (ContextBar path) |
| **ADR refs** | ADR-0036, ADR-0038, ADR-0039 |

---

## Objective

Writing workspace **layout shell** — three-panel structure per Spec §5.3.
Editor functionality deferred to PX-2; this EWO delivers structure + placeholders.

---

## Ownership (exclusive)

```text
frontend/app/writing/**
frontend/components/writing/**
```

**Forbidden:** backend, `components/context/**`, API schemas.

---

## Scope

### In scope

- Three-panel layout: outline | editor | AI actions
- ContextBar placement (import from `@/components/context`)
- Outline tree stub (chapters from API or stub)
- Editor area placeholder (Markdown shell)
- AI panel slot (action buttons stub)
- Responsive collapse behavior

### Out of scope

- Full Markdown editor (PX-2)
- AI action execution (PX-2)
- Backend changes

---

## Acceptance Criteria

- [ ] `/writing` and `/writing/[chapterId]` render three-panel shell
- [ ] ContextBar visible above or within workspace chrome
- [ ] Outline shows chapter list stub
- [ ] No backend modifications
- [ ] Tests + build pass

---

## WO-TRACE

```text
PX1-EWO-009 → PX1-EWO-007
```
