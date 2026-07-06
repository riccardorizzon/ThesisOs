# Conformance EWO Template — PX-3+ (MB2 SoR)

> Use for **Runtime Conformance Program** Work Orders (PX-3+).  
> Product specs define *what* to build; this block defines *what SoR surface the EWO validates*.

> **Platform contract (required):** `.asep/templates/platform-contract-block.md`  
> Conformance EWOs are typically **Category B** (Observable) unless extending §1 Validated surfaces.

---

## Platform contract

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: B
  hypothesis_id: H-06
  success_metric: "<SoR section promoted Observable → evidenced in report>"
  exit_id: n/a
  program_mode: product
```

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-NNN |
| **Wave objective** | `<Projection Conformance \| Supervisor Conformance \| …>` |
| **Type** | EWO |
| **Milestone** | PX-3 Knowledge Experience (Conformance Program) |

---

## Conformance contract (mandatory)

| Field | Value |
|-------|-------|
| **Primary objective (SoR)** | `<e.g. Projection Conformance §9>` |
| **Secondary objective (Product)** | `<e.g. Explain Page shell>` |
| **Product objective** | `<user-visible deliverable — may be secondary>` |
| **SoR sections exercised** | `<§9, §10, …>` |
| **Expected invariants** | `<INV-R-11, …>` |
| **Expected MB2 gates** | `<MB2-Q5, …>` |

```yaml
covers:
  sor_sections:
    - "§9 Projection"
  invariants:
    - INV-R-11
  mb2_gates:
    - MB2-Q5
  px3_exercisability: Yes   # Yes | Observable | No (Runtime) | No (Qualification)
  class: A                    # A=Yes B=Observable C=No*
```

### `covers:` cap (Architect rule)

**At most three elements total** across `sor_sections`, `invariants`, and `mb2_gates`
(typically one per list). An EWO covering many § sections is oversized — split it.

**Rule:** Wave B+ EWOs MUST declare `covers`. Coverage matrix updates as  
`Coverage += union(EWO.covers)` after each wave.

---

## Primary vs secondary objective (example)

```text
PX3-EWO-005

Primary objective (SoR)
  Projection Conformance (§9) — read-only observability artifact

Secondary objective (Product)
  Explain Page regions A–B (loading + ready states)
```

Use **Conformance** or **Validation** — not **Exercise**. PX-3 verifies SoR contract
alignment; it does not exercise the Runtime.

---

## PX-3 exercisability (Architect ratified)

| PX-3 exercisability | Class | Primary EWO allowed? |
|---------------------|-------|----------------------|
| **Yes** | A | Yes |
| **Observable** | B | Secondary only |
| **No (Runtime)** | C | No |
| **No (Qualification)** | C | No |

Do **not** authorize EWOs whose primary `covers` are class **C** or No (Runtime/Qualification).

§11 Failure: **optional** covers entry only when failure occurs naturally — not forced.

---

## Wave selection rule

Each wave must answer:

> **Which new part of the SoR becomes verifiable because of this wave?**

---

## Acceptance (conformance-aware)

- [ ] All `covers.invariants` evidenced in report (pass or logged deviation)
- [ ] Projection artifact attached if §9 in `covers`
- [ ] Conformance Log updated for any I/S/A/N
- [ ] `make ci` green; PX-2 regression preserved
- [ ] Product acceptance criteria (secondary objective)

---

## References

- Architect decision: `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-FRAMEWORK.md`
- Coverage matrix: `.asep/reports/MB2-CONFORMANCE-COVERAGE.md`
- Wave B framework: `.asep/reports/PX3-WAVE-B-DESIGN-FRAMEWORK.md`
- Wave B backlog: `.asep/reports/PX3-WAVE-B-BACKLOG.md`
- SoR: `docs/superpowers/specs/mb2-engineering-runtime-spec.md`
