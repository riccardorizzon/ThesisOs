# Architect Authorization — PX-4 Phase 0

Program: thesisos-product-v2  
Milestone: PX-4 — Knowledge  
Phase: **Phase 0 — Product-Runtime Integration Contract**  
Role: engineering  
Status: **AUTHORIZED**  
Authorized EWO: **PX4-EWO-001**  
Pre-flight: **PASS**  
SoR revision: 2026-07-05  
Runtime baseline: `mb2-complete` @ `3957c94`  
Operator command: `ASEP: AUTHORIZE PX-4 Phase 0 — product-runtime integration contract`  
Timestamp: 2026-07-06

---

## Scope boundary

This authorization covers **Phase 0 only** — the normative product-runtime integration
contract. It does **not** authorize PX-4 feature implementation, MB2 runtime internals
changes, SoR/Constitution edits, or MB2 re-qualification.

Full PX-4 feature EWOs remain blocked until Phase 0 contract is ratified (PASS report).

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Program graph | ✓ `.asep/programs/thesisos-product-v2.yaml` |
| Proposal filed | ✓ `.asep/proposals/PX4-EWO-001-runtime-product-contract.md` |
| Platform contract block | ✓ Category A, `program_mode: product` |
| PX-2 frozen | ✓ 2026-07-05 |
| PX-3 in progress | ✓ active — waived for Phase 0 contract-only scope |
| MB2 promoted | ✓ `.asep/certificates/MB2-PROMOTION-20260706.yaml` @ `3957c94` |
| SoR frozen | ✓ `.asep/certificates/MB2-SOR-20260705.yaml` revision 2026-07-05 |
| Product Constitution | ✓ frozen |
| Runtime Constitution | ✓ frozen |
| `make ci` | ✓ green @ `fff66845` |
| Live stack `/health` | ✓ 200 |
| Repository | ✓ clean (untracked proposal only) |
| First executable EWO | ✓ PX4-EWO-001 (no EWO deps; MB2 + SoR prereqs satisfied) |

---

## Authorized EWO

| Field | Value |
|-------|-------|
| **Id** | PX4-EWO-001 |
| **Title** | Product-Runtime Integration Contract |
| **Category** | Alignment |
| **Layer** | Business + Runtime boundary |
| **Proposal** | `.asep/proposals/PX4-EWO-001-runtime-product-contract.md` |

### Deliverables (in scope)

- `docs/product/runtime-integration-contract.md` (normative)
- `.asep/reports/PX4-EWO-001-runtime-product-contract.md` (PASS report)
- Interface stubs (optional, contract-only)

### Forbidden paths (enforced)

```text
builder_engine/events.py
builder_engine/scheduler.py
builder_engine/rules.py
builder_engine/job_queue.py
builder_engine/dependency.py
builder_engine/plugin_registry.py
docs/superpowers/specs/mb2-engineering-runtime-spec.md
docs/runtime-constitution.md
```

---

## Explicitly NOT authorized

| Scope | Status |
|-------|--------|
| PX-4 feature EWOs (concept model, Explain, etc.) | **NOT authorized** |
| PX-5 / PX-6 | **NOT authorized** |
| MB2 runtime internals | **NOT authorized** |
| SoR / Constitution modifications | **NOT authorized** |
| MB2 re-qualification | **NOT authorized** |
| Phase 2 plugin development | **NOT authorized** |

---

## WO-TRACE

```text
MB2 promoted @ mb2-complete (3957c94)
  → AUTHORIZE PX-4 Phase 0
  → PX4-EWO-001 runtime-product contract (authorized)
  → Contract ratified (pending execution)
  → PX-4 feature EWOs (future — requires separate authorization)
```

---

## Recommended next action

Execute **PX4-EWO-001**: draft `docs/product/runtime-integration-contract.md` from
proposal §Product-runtime contract, file PASS report, obtain Architect ratification of
event taxonomy, projection read-only boundary, and Supervisor observation contract.
