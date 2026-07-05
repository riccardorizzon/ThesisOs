# Engineering WorkOrder Proposal — PX3-EWO-007

> **Status:** ✅ **IMPLEMENTED** — `.asep/reports/PX3-INTEGRATION-B.md` PASS

Program: `.asep/programs/thesisos-product-v2.yaml`  
Wave: `px3-parallel/wave_b_conformance_integration`  
Type: Conformance Integration EWO (supervisor-owned)

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-007 |
| **Sub-agent** | Supervisor |
| **Type** | **EWO** — Conformance Integration |
| **EWO category** | **Infrastructure** |
| **Wave objective** | Projection Conformance (Wave B) |
| **Capability** | `px3-ewo-007-conformance-integration-b` |
| **Milestone** | PX-3 Knowledge Experience (Conformance Program) |
| **Depends on** | PX3-EWO-006 |

---

## Conformance contract

| Field | Value |
|-------|-------|
| **Primary objective (SoR)** | Conformance Integration B — merge Wave B evidence; verify SoR contract continuity |
| **Secondary objective (Product)** | Explorer ↔ Explain wiring; regression |
| **Product objective** | Integrated Wave B tree |
| **SoR sections exercised** | §9 Projection (union) |
| **Expected invariants** | INV-R-12 |
| **Expected MB2 gates** | — |

```yaml
covers:
  sor_sections:
    - "§9 Projection"
  invariants:
    - INV-R-12
  mb2_gates: []
  px3_exercisability: Yes
  class: A
```

---

## Objective

**Conformance Integration B** — not generic integration. Merge Wave B branches, verify
product still respects SoR contract, update coverage matrix, and produce integration
evidence with explicit **coverage delta** vs Wave A baseline.

---

## Scope

### In scope

1. **Merge** — integrate PX3-EWO-005 + PX3-EWO-006 deliverables
2. **Regression** — `make ci`; PX-2 cite + ContextBar spot-check
3. **Coverage update** — `Coverage += union(EWO.covers)` in `MB2-CONFORMANCE-COVERAGE.md`
4. **Report** — `.asep/reports/PX3-INTEGRATION-B.md` with PASS/FAIL and coverage delta
5. **Wave B exit criteria** — verify all four PASS conditions (see backlog)

### Out of scope

- New product features beyond wiring
- Wave C planning
- QWO / milestone qualification

---

## Wave B exit criteria (integration verifies)

- [ ] PX3-EWO-005, 006, 007 each PASS
- [ ] This integration PASS
- [ ] Conformance Log: no N-class from Wave B
- [ ] Coverage matrix: ≥1 new Yes or Observable row vs Wave A

---

## Acceptance criteria

- [ ] Integrated tree; `make ci` green
- [ ] Explorer ↔ Explain navigation works
- [ ] PX3-INTEGRATION-B.md written with PASS/FAIL + coverage delta
- [ ] MB2-CONFORMANCE-COVERAGE.md updated from union(EWO.covers)
- [ ] No open N-class blockers

---

## References

- Backlog: `.asep/reports/PX3-WAVE-B-BACKLOG.md`
- Wave A integration pattern: `.asep/reports/PX3-INTEGRATION-A.md`
