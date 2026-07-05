# QWO-PX1-001 Preflight — Evidence Bundle

**Prepared by:** PX1-EWO-012 (Sub-agent G)  
**Date:** 2026-07-03  
**Status:** **READY FOR QWO AUTHORIZATION**

---

## Preconditions

| Precondition | State |
|--------------|-------|
| PX1-EWO-001…005 | Implemented + certificates |
| PX1-EWO-006…011 | Merged (Wave A + B) |
| PX1-EWO-012 | This bundle |

---

## Acceptance mapping (from `thesisos-product-v2.yaml`)

| QWO criterion | EWO-012 evidence |
|---------------|------------------|
| Home default route verified | `tests/e2e/px1-ui-smoke.spec.ts` — Home loads @ `/` |
| Sidebar IA matches ADR-0036 | Same file — PRIMARY_NAV labels |
| Context v0 API valid packet | `tests/e2e/px1-context-api.spec.ts` |
| make ci green | `.asep/reports/PX1-EWO-012-qualification-integration.md` CI log |
| OR-1…OR-7 regression | `or-baseline-checklist.md` + existing migration PASS |

---

## Artifacts

| Artifact | Path |
|----------|------|
| E2E UI smoke | `tests/e2e/px1-ui-smoke.spec.ts` |
| E2E Context API | `tests/e2e/px1-context-api.spec.ts` |
| Visual regression stubs | `tests/e2e/px1-visual-regression.stub.spec.ts` |
| Route inventory | `tests/e2e/evidence/route-inventory.json` |
| OR baseline | `tests/e2e/evidence/or-baseline-checklist.md` |
| Playwright config | `tests/e2e/playwright.config.ts` |
| Integration report | `.asep/reports/PX1-EWO-012-qualification-integration.md` |
| QC certificate | `.asep/certificates/PX1-EWO-012-20260703.yaml` |

---

## Run commands

```bash
# Unit + lint gate
make ci

# Full E2E (starts workspace backend :8001 + Next dev :3001)
cd tests/e2e && npm install && npx playwright install chromium
# First run on fresh VM: npx playwright install-deps chromium
cd tests/e2e && npm run test

# UI-only / API-only
cd tests/e2e && npm run test:ui
cd tests/e2e && npm run test:api

# Live Docker stack (QWO): rebuild before qualification
make up --build
PLAYWRIGHT_SKIP_WEBSERVER=1 PLAYWRIGHT_BASE_URL=http://localhost:3000 \
  E2E_API_BASE_URL=http://localhost:8000 cd tests/e2e && npm run test
```

**Latest run (2026-07-03):** 7 passed, 2 skipped (visual stubs).

---

## Recommended QWO next step

1. Supervisor authorizes **QWO-PX1-001-R1**
2. Execute on integrated stack (`make up` + full E2E suite)
3. PASS → `PX-1` milestone complete per program completion criteria
