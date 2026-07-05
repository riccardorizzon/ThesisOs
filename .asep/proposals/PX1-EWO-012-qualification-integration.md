# Engineering WorkOrder Proposal — PX1-EWO-012

> **Status:** APPROVED (2026-07-03) — Wave C (after 006–011)

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-012-qualification-integration`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-012 |
| **Sub-agent** | G |
| **Type** | EWO (Release) |
| **Milestone** | PX-1 |
| **Depends on** | PX1-EWO-006…011 |
| **Leads to** | QWO-PX1-001 |

---

## Objective

Qualification & integration evidence for PX-1 Foundation. E2E smoke, regression
suite, integration report. **No product feature code** — tests and evidence only.

---

## Ownership (exclusive)

```text
tests/e2e/**
frontend/playwright.config.ts         # if introduced
.asep/reports/PX1-EWO-012-*.md
.asep/certificates/PX1-EWO-012-*.yaml
```

**Forbidden:** product implementation files (backend/app, frontend/components except test utils).

---

## Scope

### In scope

- E2E smoke: Home loads, Writing shell, Sources shell, Context API health
- Integration test plan for QWO-PX1-001
- Evidence bundle: CI log, route inventory, OR baseline checklist
- QWO-PX1-001 preflight report

### Out of scope

- Feature implementation
- OR-1…OR-7 re-qualification scripts (reference existing)

---

## Acceptance Criteria

- [ ] E2E suite runs green (or documented skip with reason)
- [ ] `make ci` green on integration branch
- [ ] QWO-PX1-001 evidence package complete
- [ ] Integration report published

---

## WO-TRACE

```text
PX1-EWO-006…011 → PX1-EWO-012 → QWO-PX1-001 → PX-1 PASS
```
