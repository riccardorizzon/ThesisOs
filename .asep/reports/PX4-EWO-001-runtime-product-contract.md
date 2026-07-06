# PX4-EWO-001 — Product-Runtime Integration Contract

> **WorkOrder:** PX4-EWO-001  
> **Phase:** PX-4 Phase 0 — Product-Runtime Integration Contract  
> **Status:** **PASS**  
> **Authorization:** `.asep/reports/PX4-AUTHORIZATION-20260706.md`  
> **Date:** 2026-07-06

---

## Objective

Define and ratify the normative integration contract between the ThesisOS Product Plane
and the MB2 Engineering Runtime. No product features, runtime internals, SoR, or
Constitution changes.

---

## Acceptance criteria

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Runtime integration contract drafted | **PASS** | `docs/product/runtime-integration-contract.md` v1.0 |
| Event taxonomy approved | **PASS** | Contract §3 — consume/produce/forbidden lists aligned to SoR §6 |
| Projection read-only boundary approved | **PASS** | Contract §4 — INV-R-11 consumer rules |
| Supervisor observation contract approved | **PASS** | Contract §5 — WAIT/APPROVED/STOP mapping |
| Ownership matrix signed off | **PASS** | Contract §6 |
| No MB2 runtime internals modified | **PASS** | `git diff` — zero `builder_engine/` changes |
| No SoR/Constitution modifications | **PASS** | Forbidden paths untouched |
| Contract accepted | **PASS** | Sign-off block in contract §Sign-off |
| EWO report filed | **PASS** | This document |

---

## SoR mapping (evidence)

| SoR section | Deliverable | Status |
|-------------|-------------|--------|
| §6 Event model | §3 Event boundary | **PASS** |
| §9 Projection model | §4 Projection boundary | **PASS** |
| §10 Supervisor | §5 Supervisor boundary | **PASS** |
| §13 Promotion | Contract enables future §13.3 evidence path | **PASS** (contract only) |
| ADR-0042 | §1 Layer model, two-layer split | **PASS** |

---

## Deliverables

| Artifact | Path |
|----------|------|
| Normative contract | `docs/product/runtime-integration-contract.md` |
| Proposal | `.asep/proposals/PX4-EWO-001-runtime-product-contract.md` |
| Authorization receipt | `.asep/reports/PX4-AUTHORIZATION-20260706.md` |
| EWO report | `.asep/reports/PX4-EWO-001-runtime-product-contract.md` |

Interface stubs: **deferred** (optional per proposal; not required for Phase 0 PASS).

---

## Verification

| Gate | Result |
|------|--------|
| Scope isolation | No `builder_engine/`, SoR, Constitution, `backend/app/` feature, or `frontend/` feature edits |
| Contract completeness | 10 sections; versioning; compliance checklist |
| Runtime baseline pinned | `mb2-complete` @ `3957c94` |
| SoR revision pinned | `2026-07-05` |

---

## Risks (closed)

| ID | Mitigation applied |
|----|-------------------|
| R-P4-001 | Contract versioned (§9); amendments via Architect |
| R-P4-002 | Ownership matrix + PR layer gate (§6, §10) |
| R-P4-003 | Runtime tag + SoR revision pinned (§9) |
| R-P4-004 | Read-only projection rules + compliance checklist (§4, §10) |

---

## Explicitly NOT delivered

- PX-4 feature implementation (concept model, Explain, etc.)
- MB2 runtime code changes
- SoR / Constitution amendments
- MB2 re-qualification

Full PX-4 feature EWOs require **separate Architect authorization**.

---

## WO-TRACE

```text
AUTHORIZE PX-4 Phase 0
  → PX4-EWO-001 executed
  → runtime-integration-contract.md v1.0 ratified
  → Phase 0 complete — PX-4 features remain blocked
```

---

```text
Milestone Status: PASS
Repository Status: main, docs-only delta
Remaining Scope: PX-4 feature EWOs (not authorized)
Known Risks: Contract v1.0 must be cited by future integration EWOs
Recommended Next Action: AUTHORIZE PX-4 feature backlog when PX-3 gate satisfied
```
