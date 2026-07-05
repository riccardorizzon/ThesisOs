# Engineering WorkOrder Proposal — PX1-EWO-002

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-07-03) — report `.asep/reports/PX1-EWO-002-design-system.md`

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-002-design-system`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-002 |
| **Type** | EWO (Infrastructure) |
| **Milestone** | PX-1 Foundation |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX1-EWO-001 |

---

## Objective

Establish design system v1 — semantic tokens (color, typography, spacing) and core
component stubs (`ProgressRing`, `EntityCard`) for Home and module surfaces.

---

## Scope

### In scope

1. Token documentation — `docs/product/design-system-v1.md`
2. CSS token layer — `frontend/styles/tokens.css`
3. Tailwind extension mapping tokens
4. `ProgressRing` — deterministic progress display (ADR-0040 Home ring)
5. `EntityCard` — reusable entity summary stub (sources, chapters, concepts)
6. Refactor `AppShell` to consume semantic tokens

### Out of scope

- Home page assembly — PX1-EWO-003
- shadcn component library install
- Custom web fonts (system stack v1)
- Dark mode theme

---

## Acceptance Criteria

- [ ] Design tokens documented (color, type, spacing)
- [ ] Core components: AppShell (tokenized), ProgressRing, EntityCard stub
- [ ] Unit tests for ProgressRing and EntityCard
- [ ] `npm test` + `npm run build` pass

---

## WO-TRACE

```text
PX1-EWO-001 → PX1-EWO-002 → PX1-EWO-003 (Home)
```
