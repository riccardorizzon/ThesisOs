# PX1-EWO-012 — Qualification & Integration

**WorkOrder:** PX1-EWO-012  
**Sub-agent:** G  
**Type:** EWO (Release)  
**Date:** 2026-07-03  
**Verdict:** **IMPLEMENTED**

---

## Objective

Qualification and integration evidence for PX-1 Foundation: E2E smoke (Home, Writing,
Sources, Context API), QWO-PX1-001 preflight bundle, `make ci` green. No product
feature code modified.

---

## Preconditions

| Precondition | State |
|--------------|-------|
| PX1-EWO-006…011 merged | **PASS** — Wave A + B @ `89c0824` |
| Wave B `make ci` | **PASS** — `.asep/reports/PX1-WAVE-B-handoff.md` |

---

## Deliverables

| Artifact | Path |
|----------|------|
| E2E UI smoke | `tests/e2e/px1-ui-smoke.spec.ts` |
| E2E Context API | `tests/e2e/px1-context-api.spec.ts` |
| Visual regression stubs | `tests/e2e/px1-visual-regression.stub.spec.ts` |
| Playwright config | `tests/e2e/playwright.config.ts` |
| E2E runner package | `tests/e2e/package.json` |
| Route inventory | `tests/e2e/evidence/route-inventory.json` |
| OR baseline checklist | `tests/e2e/evidence/or-baseline-checklist.md` |
| QWO preflight bundle | `tests/e2e/evidence/qwo-px1-001-preflight.md` |
| CI log | `tests/e2e/evidence/ci-log-20260703.txt` |
| QC certificate | `.asep/certificates/PX1-EWO-012-20260703.yaml` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| E2E suite runs green (or documented skip) | **PASS** — 7 passed, 2 skipped (PX-2 visual baselines) |
| `make ci` green | **PASS** — see CI evidence |
| QWO-PX1-001 evidence package complete | **PASS** — `tests/e2e/evidence/qwo-px1-001-preflight.md` |
| Integration report published | **PASS** — this document |

---

## E2E smoke results (2026-07-03)

Isolated stack via Playwright `webServer` (ports **8001** backend, **3001** frontend) —
avoids stale Docker images on `:8000`/`:3000`.

```text
cd tests/e2e && npm install && npm run test

  ✓ GET /projects/thesis-agent/context returns valid ContextPacket
  ✓ Context API home surface matches schema
  ✓ Home loads as default route
  ✓ sidebar IA matches ADR-0036
  ✓ Writing workspace shell renders
  ✓ Sources shell renders with library cards
  ✓ legacy /workspace redirects to Writing
  - Home screenshot baseline — deferred to PX-2 (documented skip)
  - Writing three-panel screenshot — deferred to PX-2 (documented skip)

  7 passed, 2 skipped (33s)
```

**Coverage:**

| Surface | Assertion |
|---------|-----------|
| Home `/` | HomeView heading + progress copy |
| Sidebar | ADR-0036 labels (Home…Knowledge + Settings) |
| Writing `/writing` | `writing-workspace`, editor placeholder, ContextBar |
| Sources `/sources` | heading + stub EntityCard (Albers) |
| Legacy `/workspace` | redirect → `/writing` |
| Context API | `schema_version`, `project_context`, decisions, corpus_constraints |

---

## CI gate (2026-07-03)

```text
make ci → PASS

  lint                          PASS
  typecheck                     PASS
  unit (backend)                327 passed, 1 skipped
  unit-frontend                 132 passed (36 files)
  unit-builder-engine           65 passed
  drift                         PASS
  scope / isolation             PASS
```

Full log: `tests/e2e/evidence/ci-log-20260703.txt`

---

## Ownership compliance

| Allowed | Status |
|---------|--------|
| `tests/e2e/**` | **COMPLIANT** |
| `.asep/reports/PX1-EWO-012-*` | **COMPLIANT** |
| `.asep/certificates/PX1-EWO-012-*` | **COMPLIANT** |
| Product feature code | **NOT TOUCHED** |

**Note:** Playwright config lives under `tests/e2e/` (deps co-located) rather than
`frontend/playwright.config.ts` to keep `@playwright/test` out of frontend `tsc` gate.

---

## QWO-PX1-001 readiness

| Gate | EWO-012 | QWO scope |
|------|---------|-----------|
| Home default route | E2E PASS | Re-verify on production stack |
| Sidebar IA (ADR-0036) | E2E PASS | Re-verify |
| Context v0 API | E2E PASS (workspace backend) | Live stack with `make up` rebuild |
| `make ci` | PASS | Required at QWO |
| OR-1…OR-7 regression | Checklist references migration PASS | QWO executes on live agent |

**Disposition:** **READY FOR QWO-PX1-001 AUTHORIZATION**

Supervisor should authorize QWO-PX1-001-R1 after merge of EWO-012 artifacts.

---

## Merge readiness

**Yes** — tests + evidence only; `make ci` green; no product code conflicts.

**Operator note:** Run `npx playwright install-deps chromium` once on fresh VMs before E2E.
Rebuild Docker (`make up --build`) before QWO live-stack OR regression.

---

## WO-TRACE

```text
PX1-EWO-006…011 → PX1-EWO-012 → QWO-PX1-001 → PX-1 PASS
```
