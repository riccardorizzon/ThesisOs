# Engineering WorkOrder Proposal — PX1-EWO-008

> **Status:** APPROVED (2026-07-03) — Wave A (parallel with 006, 009)

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-008-library-experience`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-008 |
| **Sub-agent** | C |
| **Type** | EWO (Alignment) |
| **Milestone** | PX-1 (Sources/Knowledge UX shell) |
| **Depends on** | PX1-EWO-002 (design system) |
| **ADR refs** | ADR-0036, ADR-0037 |

---

## Objective

Library experience shell for Sources and Knowledge modules — cards, filters stub,
navigation between source objects and concept explorer.

---

## Ownership (exclusive)

```text
frontend/app/sources/**
frontend/app/knowledge/**
frontend/components/library/**
frontend/lib/libraryStub.ts
```

**Forbidden:** Context Engine, backend, Writing, Navigation core.

---

## Scope

### In scope

- Sources list view with EntityCard grid
- Source detail stub (`/sources/[sourceId]`)
- Knowledge explorer stub with concept cards
- Filter bar placeholder (status: candidata / approvata / esclusa)
- Cross-link Sources ↔ Knowledge navigation

### Out of scope

- Full source ingestion (PX-3)
- Concept graph (PX-4)
- Backend API changes

---

## Acceptance Criteria

- [ ] `/sources` renders source cards (stub or API)
- [ ] `/knowledge` renders concept explorer stub
- [ ] Filter UI placeholder present
- [ ] Reuses design tokens + EntityCard
- [ ] Tests + build pass

---

## WO-TRACE

```text
PX1-EWO-002 → PX1-EWO-008 (Wave A parallel)
```
