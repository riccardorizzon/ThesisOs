# Engineering WorkOrder Proposal — PX1-EWO-009

> **Status:** APPROVED (2026-07-03) — Wave A (parallel with 006, 008)

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-009-context-visualization`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-009 |
| **Sub-agent** | D |
| **Type** | EWO (Alignment) |
| **Milestone** | PX-1 |
| **Depends on** | PX1-EWO-005 (ContextPacket consumer) |
| **ADR refs** | ADR-0038 |

---

## Objective

Context visualization components — **view layer only**. Migrate ContextBar to
`components/context/`, add constraint chips and decision badges.

---

## Ownership (exclusive)

```text
frontend/components/context/**
```

**Allowed import-path updates:** `frontend/app/writing/**` (import lines only).

**Forbidden:** backend, Context Engine assembly, Writing layout structure.

---

## Scope

### In scope

- Migrate `ContextBar` → `components/context/ContextBar.tsx`
- `ConstraintChip` — corpus exclusion indicators (CORPUS-02/03)
- `DecisionBadge` — binding decision count/summary
- `ContextSummary` — composable bar (fonti · concetti · decisioni · citazioni)
- Update Writing page imports

### Out of scope

- Context assembly logic (backend)
- Writing three-panel layout (EWO-007)

---

## Invariants

- **INV:** ContextBar displays packet state only — never as source of truth
- **INV:** No API or schema changes

---

## Acceptance Criteria

- [ ] ContextBar lives under `components/context/`
- [ ] Constraint chips render corpus_constraints from packet
- [ ] Decision badges reflect binding decisions count
- [ ] Writing routes import from new path
- [ ] Tests migrated + pass

---

## WO-TRACE

```text
PX1-EWO-005 → PX1-EWO-009 → PX1-EWO-007
```
