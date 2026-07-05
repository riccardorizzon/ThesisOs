# Engineering WorkOrder Proposal — PX1-EWO-004

> **Status:** ✅ **APPROVED + IMPLEMENTED** (2026-07-03) — report `.asep/reports/PX1-EWO-004-routing.md`

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-004-routing`

---

## Objective

Product routes per Spec §4 stub pages; legacy `/chat` → `/ai` and ADR-0036 disposition redirects.

---

## Acceptance Criteria

- [ ] Stub pages: Research, Writing, Sources, Knowledge (+ dynamic segments)
- [ ] `/ai` power mode (chat UI relocated from `/chat`)
- [ ] Legacy redirects configured and documented
- [ ] Tests + build pass

---

## Out of scope

- Full `/documents/*` → `/sources/*` migration (PX-3)
- ContextBar on Writing (PX1-EWO-005)
