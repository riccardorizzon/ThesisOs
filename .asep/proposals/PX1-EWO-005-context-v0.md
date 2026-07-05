# Engineering WorkOrder Proposal — PX1-EWO-005

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-07-03) — report `.asep/reports/PX1-EWO-005-context-v0.md`

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-005-context-v0`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-005 |
| **Type** | EWO (Grounding) |
| **Milestone** | PX-1 Foundation |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX1-EWO-001 |
| **ADR refs** | ADR-0038, ADR-0040 |

---

## Objective

Context Engine v0: `GET /projects/{id}/context` returns ContextPacket subset
(decisions + entity + corpus_constraints + writing_rules) and ContextBar on Writing stub.

---

## Acceptance Criteria

- [ ] `GET /projects/{id}/context` returns ContextPacket schema subset
- [ ] Precedence: binding decisions + entity + corpus_constraints (ADR-0038)
- [ ] ContextBar component in Writing stub route
- [ ] Tests + build pass

---

## Out of scope

- `POST /ai/actions/{action}` — PX-2
- Concept neighborhood — PX-4+
- Full project scope scaffolding — PX1-EWO-006

---

## WO-TRACE

```text
PX1-EWO-004 → PX1-EWO-005 → PX1-EWO-006
```
