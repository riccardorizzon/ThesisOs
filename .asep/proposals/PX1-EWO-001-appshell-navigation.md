# Engineering WorkOrder Proposal — PX1-EWO-001

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-07-03) — report `.asep/reports/PX1-EWO-001-appshell-navigation.md`
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px1-ewo-001-appshell`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-001 |
| **Type** | **EWO** — Product Plane infrastructure |
| **EWO category** | **Infrastructure** |
| **Capability** | `px1-ewo-001-appshell` |
| **Milestone** | PX-1 Foundation |
| **Layer** | Business (Product Plane — `frontend/`) |
| **Lifecycle transition** | `approved` → `implemented` (on success) |

---

## Objective

Replace the developer-centric root layout with a researcher-facing **AppShell** and
primary sidebar navigation per ADR-0036, exposing the six workspace modules without
changing backend runtime behavior.

---

## Scope

### In scope

1. **`AppShell` component** — sidebar + main content + optional right panel slot (future AI panel).
2. **Primary navigation** — Home, Research, Writing, Sources, Knowledge, Settings (ADR-0036 INV-IA-1).
3. **Navigation config** — centralized route map in `frontend/lib/nav.ts`.
4. **Root layout migration** — `frontend/app/layout.tsx` uses AppShell instead of inline nav.
5. **Layer declaration** — Business layer on frontend changes.

### Out of scope

- Default route change (`/` → Home) — **PX1-EWO-003**
- Design system tokens — **PX1-EWO-002**
- Module stub pages and legacy redirects — **PX1-EWO-004**
- Context Engine API — **PX1-EWO-005**
- Backend changes
- Removal of legacy routes (`/chat`, `/library`, etc.) — absorbed in PX-4 routing EWO

---

## Constraints

- Product Constitution v1.0 (Frozen) + ADR-0036 sidebar invariants
- Runtime Constitution C1–C8 — no graph or contract changes
- OR-1…OR-7 regression baseline preserved
- No thesis-specific strings in AppShell chrome (ADR-0034 C4)

---

## Acceptance Criteria

- [ ] Sidebar contains exactly: Home, Research, Writing, Sources, Knowledge, Settings
- [ ] AppShell accepts optional `rightPanel` prop for future AI panel
- [ ] Active route highlighted in sidebar
- [ ] Root layout delegates to AppShell
- [ ] `npm test` and `npm run build` pass in `frontend/`

---

## Regression

- `make ci` (frontend build + tests included)
- Existing legacy routes remain reachable until PX1-EWO-004

---

## WO-TRACE

```text
EXECUTION-AUTHORIZATION (PX-1) → thesisos-product-v2.yaml → PX1-EWO-001 → AppShell
```
