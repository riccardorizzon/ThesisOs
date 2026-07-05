# Engineering WorkOrder Proposal — PX1-EWO-010

> **Status:** APPROVED (2026-07-03) — Wave B, merge after EWO-006

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-010-navigation-experience`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-010 |
| **Sub-agent** | E |
| **Type** | EWO (Infrastructure) |
| **Milestone** | PX-1 |
| **Depends on** | PX1-EWO-006 (ProjectContext) |
| **ADR refs** | ADR-0036 |

---

## Objective

Navigation experience enhancements — breadcrumbs, project switcher stub, workspace
navigation. Minimal AppShell integration via subcomponents.

---

## Ownership (exclusive)

```text
frontend/components/navigation/**
frontend/lib/nav.ts
frontend/components/AppShell.tsx    # minimal integration diff only
```

**Forbidden:** backend, module pages, Context Engine.

---

## Scope

### In scope

- `Breadcrumbs` component (route-aware)
- `ProjectSwitcher` stub (reads ProjectContext from EWO-006)
- `WorkspaceNav` enhancements if needed
- AppShell: import navigation subcomponents (minimal diff)

### Out of scope

- Full multi-project backend (future)
- Sidebar IA redesign (frozen ADR-0036)

---

## Acceptance Criteria

- [ ] Breadcrumbs on module routes (Writing, Sources, Knowledge)
- [ ] Project switcher shows current project_id (stub)
- [ ] AppShell diff ≤ 30 lines (integration only)
- [ ] Sidebar IA unchanged (ADR-0036)
- [ ] Tests + build pass

---

## WO-TRACE

```text
PX1-EWO-006 → PX1-EWO-010
```
