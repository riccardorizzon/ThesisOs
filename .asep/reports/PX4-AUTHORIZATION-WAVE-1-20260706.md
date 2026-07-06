# Architect Authorization — PX-4 Wave 1 Foundation

Program: thesisos-product-v2  
Milestone: PX-4 — Knowledge  
Wave: **Wave 1 — Foundation**  
Role: engineering  
Status: **AUTHORIZED**  
Authorized EWOs: **PX4-EWO-002**, **PX4-EWO-003**, **PX4-EWO-004**  
Pre-flight: **PASS**  
Runtime contract: `docs/product/runtime-integration-contract.md` v1.0  
Operator command: `ASEP: AUTHORIZE PX4 Wave 1 backlog`  
Timestamp: 2026-07-06

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Phase 0 complete | ✓ PX4-EWO-001 PASS @ `13d38327` |
| Integration contract | ✓ `docs/product/runtime-integration-contract.md` v1.0 |
| PX-3 Wave A foundation | ✓ read-only Knowledge Object API live |
| Program graph | ✓ `.asep/programs/thesisos-product-v2.yaml` |
| `make ci` | ✓ green on HEAD |
| Repository | ✓ clean |
| Parallel program | ✓ `.asep/programs/px4-parallel.yaml` |

---

## Authorized EWOs (parallel dispatch)

| EWO | Title | Merge order |
|-----|-------|-------------|
| PX4-EWO-002 | Domain model | 1 |
| PX4-EWO-003 | CRUD API | 2 |
| PX4-EWO-004 | Persistence | 3 |

Integration barrier: **PX4-INTEGRATION-B** after 002+003+004 PASS.

---

## Scope boundary

| Scope | Status |
|-------|--------|
| Graph / Explorer / Search (Wave 2) | NOT authorized |
| Sources / Writing / Review integration (Wave 3) | NOT authorized |
| Conformance / Promotion (Wave 4) | NOT authorized |
| MB2 runtime internals | NOT authorized |
| SoR / Constitution edits | NOT authorized |

---

## Recommended next action

Execute Wave 1 EWOs in merge order 002 → 003 → 004, then authorize PX4-INTEGRATION-B.
