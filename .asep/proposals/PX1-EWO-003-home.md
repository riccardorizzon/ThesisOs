# Engineering WorkOrder Proposal — PX1-EWO-003

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-07-03) — report `.asep/reports/PX1-EWO-003-home.md`

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-003-home`  
Design: `design-system/thesisos/pages/home.md`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-003 |
| **Type** | EWO (Alignment) |
| **Milestone** | PX-1 Foundation |
| **Depends on** | PX1-EWO-001, PX1-EWO-002 |

---

## Objective

Implement Home as default landing route per ADR-0036 INV-IA-2 with progress,
Continue, quick actions, and activity feed placeholders per Spec §5.1.

---

## Acceptance Criteria

- [ ] `/` renders Home — not redirect to `/chat`
- [ ] Progress via deterministic formula stub (ADR-0040 INV-PS-1)
- [ ] Continue deep link + quick actions + activity feed placeholders
- [ ] Italian operator copy; `Link` for navigation
- [ ] Tests + build pass

---

## WO-TRACE

```text
PX1-EWO-002 → PX1-EWO-003 → design-system/thesisos/pages/home.md
```
