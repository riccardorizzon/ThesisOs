# QWO-PX1-001-R1 — PX-1 Foundation Qualification Report

**Date:** 2026-07-03  
**WorkOrder:** QWO-PX1-001 · **Type:** QWO · **Run:** R1  
**Capability:** `qwo-px1-001` / PX-1 Foundation  
**Milestone:** PX-1  
**Verdict:** **PASS**

**Precondition:** PX1-EWO-012 PASS (`.asep/reports/PX1-EWO-012-qualification-integration.md`, certificate `PX1-EWO-012-20260703.yaml`)  
**Operator disposition:** QWO-PX1-001 AUTHORIZED — qualification only; no product mutations

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| PX1-EWO-001…012 implemented | ✅ certificates + reports on file |
| PX1-EWO-012 QC certificate | ✅ PASS |
| EWO-012 E2E preflight | ✅ `tests/e2e/evidence/qwo-px1-001-preflight.md` |
| `/health` (workspace stack) | ✅ 200 during E2E webServer |
| Postgres (docker `db`) | ✅ reachable @ `:5432` |
| System mutations during QWO | **None** (QWO discipline) |
| Repository HEAD | `94df995625e3e9a35f87322ccf35c7a0ebaa74c0` |

**Live stack note:** Qualification uses **workspace stack** (Playwright `webServer`: backend `:8001`, Next `:3001`) against shared Postgres. Stale Docker images on `:8000`/`:3000 are **not** qualification surfaces — rebuild required for operator dogfood only.

---

## 2. Acceptance checklist

| Criterion | Gate | Result |
|-----------|------|--------|
| Home default route `/` | E2E `px1-ui-smoke.spec.ts` | **PASS** — HomeView @ `/`, no `/chat` redirect |
| Sidebar IA ADR-0036 | E2E sidebar test | **PASS** — Home, Research, Writing, Sources, Knowledge + Settings |
| Context v0 API valid packet | E2E `px1-context-api.spec.ts` | **PASS** — `schema_version`, `project_context`, decisions, corpus_constraints |
| `make ci` green | Full CI gate | **PASS** — see §3 |
| OR-1…OR-7 regression on live stack | Regression suites §4 | **PASS** |

**Visual regression stubs:** 2 skipped (PX-2 deferred) — documented, non-blocking.

---

## 3. CI gate (2026-07-03)

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

Log: `tests/e2e/evidence/qwo-px1-001-r1/qwo-px1-ci-r2.log`

**Flake note:** Parallel gate execution caused transient Postgres FK errors; sequential re-run **PASS**. Qualification protocol: run gates **sequentially**.

---

## 4. OR-1…OR-7 regression (live stack)

Migration OR capabilities previously qualified (C.1-R2 … C.7-R1, D.1 E2E). PX-1 product changes must not regress runtime behavior.

| OR | Capability | Regression gate | Result |
|----|------------|-----------------|--------|
| OR-1 | Thesis structure | `make ci` unit + E2E Home/progress | **PASS** |
| OR-2 | STIGMATA framework | `test_context_api.py` (in `make ci`) + Context E2E | **PASS** |
| OR-3 | Corpus boundary | `make unit-m4-recovery` (45 tests) | **PASS** |
| OR-4 | Constraint compliance | Context API `writing_rules` + `qualify-m5` | **PASS** |
| OR-5 | Decision lifecycle | Context API binding `decisions` | **PASS** |
| OR-6 | Academic production | `make qualify-m6` (44 tests) | **PASS** |
| OR-7 | Memory runtime integrity | `make qualify-m5` (43 tests) + memory unit | **PASS** |

```text
make unit-m4-recovery  → 45 passed     (log: qwo-px1-m4-r2.log)
make qualify-m5        → 43 passed     (log: qwo-px1-m5-r3.log)
make qualify-m6        → 44 passed     (log: qwo-px1-m6-r3.log)
E2E full suite         → 7 passed, 2 skipped (log: qwo-px1-e2e.log)
```

Prior migration qualification preserved — no de-qualification policy applied (integration PASS).

---

## 5. E2E product smoke

```text
cd tests/e2e && npm run test

  ✓ Context API — writing + home surfaces
  ✓ Home loads
  ✓ Sidebar ADR-0036
  ✓ Writing workspace shell
  ✓ Sources shell
  ✓ /workspace → /writing redirect
  - 2 visual baselines deferred PX-2
```

---

## 6. Capability Coverage

| Dimension | Value |
|-----------|-------|
| Ground Truth Coverage | unchanged (QWO discipline) |
| Runtime Coverage | regression suites green on workspace stack |
| Qualification Coverage | **PASS** |
| Evidence Coverage | certificate + report + `tests/e2e/evidence/qwo-px1-001-r1/` |

---

## 7. Lifecycle transition

| Verdict | Capability | Milestone | Unblocks |
|---------|------------|-----------|----------|
| **PASS** | `qwo-px1-001` → **qualified** | **PX-1 Foundation COMPLETE** | PX-2 authorization gate |

**Completion criteria:** `thesisos-product-v2.yaml` — `PX-1: QWO-PX1-001 PASS` ✅

---

## 8. Known risks (non-blocking)

| Risk | Mitigation |
|------|------------|
| Docker `:8000`/`:3000` stale vs workspace | `make up --build` before operator dogfood |
| Parallel pytest FK flakes | Run qualification gates sequentially |
| OR-6 PASS\* (W-06 numeric cites) | Platform limitation unchanged from migration |

---

## 9. Recommended next action — PX-2 authorization

PX-1 Foundation is **qualified**. PX-2 remains **EXCLUDED** per `docs/product/EXECUTION-AUTHORIZATION.md` until Gate 3 amendment.

```text
1. Supervisor records PX-1 PASS in program state
2. Architect issues Execution Authorization amendment for PX-2 Writing
3. Activate PX-2 EWOs only after amendment ratified
```

Do **not** begin PX-2 implementation without explicit authorization amendment.

---

## WO-TRACE

```text
PX1-EWO-001…012 → QWO-PX1-001-R1 PASS → PX-1 COMPLETE → PX-2 authorization (pending)
```
