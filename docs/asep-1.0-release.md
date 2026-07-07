# ASEP Core 1.0 — Release & Maintenance Freeze

> **Status:** COMPLETE (maintenance)  
> **Date:** 2026-07-07  
> **Authority:** ADR-0043  
> **Tag (operator):** `asep-core-1.0` — apply when ready; not automatic with this document

---

## What this means

ASEP Core 1.0 is **not** “perfect platform architecture.”

It means:

> **Governance is sufficient to stop building the framework and start using it for product work.**

From this point, **ThesisOS product delivery is the primary progress metric.**
ASEP changes require a **documented product block** or **break/fix** — not improvement
for its own sake.

---

## ASEP Core 1.0 — IN SCOPE (frozen as maintained)

| Capability | Evidence |
|------------|----------|
| CI validation pipeline | `make ci`, `.github/workflows/ci.yml` |
| Isolation & drift gates | `make isolation`, `test_schema_snapshot.py`, pre-commit |
| Engineering discipline | ADRs, PR layer checklist, Constitution C7 |
| Qualification workflow | QWO/STOP, `.asep/pipeline/qualification.md`, thesis-agent track |
| Platform justification contract | `docs/platform-justification.md` |
| Platform contract on EWOs | `.asep/templates/platform-contract-block.md` |
| Classification registry | `.asep/registry/platform-classification.yaml` |
| Registry CI consumer | `make validate-platform-classification` |
| Human classification index | `.asep/reports/platform-classification-index.md` |
| Program / authorization model | `.asep/programs/`, `authorize.md`, ASEP skill |
| MB2 Era I sidecar (maintained) | `builder_engine/` closed STATE; tests in CI |

These are **maintained**, not expanded, unless the change policy below applies.

---

## OUT OF SCOPE for ASEP Core 1.0 (explicit)

| Track | Status | Policy |
|-------|--------|--------|
| **PX-EXEC** (Rule Engine, Dependency Engine, Scheduler, plugins, …) | **R&D — frozen** | No new EWO without promotion criteria (below) |
| New `.asep/reports/` per routine EWO | Discouraged | Use PR description + tests; reports for FAIL/promotion/ADR only |
| `platform-contract-v2` | Not started | Only if v1 schema breaks validation |
| Product runtime reading governance registry | **Forbidden** | See registry `consumers` |
| Speculative platform docs | Frozen | `docs/platform/*` meta-model — no new docs without consumer |

---

## Change policy (post 1.0)

An ASEP Core change is allowed **only if one of**:

1. **Break/fix** — CI red, isolation violation, registry drift, security
2. **Product block** — reproducible; product milestone blocked; minimal fix only
   (all three from `next-actions.md` operating mode)
3. **Architect exception** — written in ADR amendment or `# ARCHITECT AUTHORIZATION`

Everything else → **defer** or route to **PX-EXEC R&D** (if promotion criteria met).

**Default question:**

> Does this modification break the ASEP 1.0 freeze? If not, don’t do it.

---

## PX-EXEC — R&D status (not Core)

PX-EXEC remains a **separate R&D track**. It is **not** part of ASEP Core 1.0.

### Promotion to Core (any one sufficient)

| # | Criterion | Evidence required |
|---|-----------|-------------------|
| P1 | **Two active Engineering Programs** using the same wave/QWO pattern | Second program completes ≥1 wave with QWO PASS |
| P2 | **Demonstrated merge pain** without Runtime | ≥1 documented incident; manual orchestration failed |
| P3 | **Parallel wave cadence** | ≥2 builder waves in 30 days with audit trail |

Until promotion: **no PX-EXEC EWO-002+ implementation** without Architect act citing
a satisfied criterion.

### Stop / remain frozen (any one sufficient)

| ID | Condition | Source |
|----|-----------|--------|
| X-04 | No second program by 2026-12-31 | `platform-justification.md` §3 |
| X-06 | MB2-Q1 not authorized by 2026-01-05 | §3 |
| X-02 | `<5` engineering bus events in 90 days while PX-EXEC “active” | §3 |

---

## Operator checklist — close ASEP 1.0

- [x] Release document (this file)
- [x] ADR-0043 accepted
- [ ] Git tag: `git tag -a asep-core-1.0 -m "ASEP Core 1.0 — governance maintenance freeze"`
- [ ] Announce in `knowledge/context/next-actions.md` — product-first cycle starts
- [ ] **Dogfood ThesisOS** — record real bottlenecks (only valid input for unfreezing PX-EXEC)

---

## What happens next

```text
ASEP Core 1.0 COMPLETE
        ↓
Maintenance mode (break/fix + product blocks only)
        ↓
ThesisOS dogfood + product milestones
        ↓
Data (pain or absence of pain)
        ↓
Decide: promote PX-EXEC | simplify | archive
```

The framework stops being the project center. The thesis product becomes the center.

---

## References

- `docs/platform-justification.md`
- `decisions/ADR-0043-asep-core-1.0-maintenance-freeze.md`
- `.asep/registry/platform-classification.yaml`
- `knowledge/context/next-actions.md`
