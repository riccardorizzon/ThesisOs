# Engineering WorkOrder Proposal — PX3-EWO-010

> **Status:** **REGISTERED — NOT AUTHORIZED** (await PX3-EWO-009 PASS)

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  classification_mode: retrospective
  classification_pass: px3-20260706-v1
  classification_registry: .asep/registry/platform-classification.yaml
  classified_on: 2026-07-06
  category: A
  hypothesis_id: n/a
  success_metric: ".asep/reports/PX3-INTEGRATION-C.md PASS"
  exit_id: n/a
  program_mode: product
```

Program: `.asep/programs/thesisos-product-v2.yaml`  
Wave: `px3-parallel/wave_c_conformance_integration`  
Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX3-EWO-010 |
| **Sub-agent** | supervisor |
| **Type** | **EWO** — Conformance Integration |
| **EWO category** | **Infrastructure** |
| **Wave objective** | Execution & Job State Observation |
| **Milestone** | PX-3 Knowledge Experience (Conformance Program) |
| **Depends on** | PX3-EWO-009 |

---

## Conformance contract

| Field | Value |
|-------|-------|
| **Primary objective (SoR)** | Conformance Integration C — §4.2 + §5 union evidence; INV-R-12 re-check |
| **Secondary objective (Product)** | Cross-surface wiring; coverage matrix update |
| **SoR sections exercised** | §4.2 Execution Graph (union) |
| **Expected invariants** | INV-R-12 |
| **Expected MB2 gates** | — |

```yaml
covers:
  sor_sections:
    - "§4.2 Execution Graph"
  invariants:
    - INV-R-12
  mb2_gates: []
  px3_exercisability: Yes
  class: A
```

---

## Ownership

```text
supervisor_only
```

---

## Integration actions

1. Merge Wave C worktrees (008 → 009)
2. Wire Explorer / Explain → Knowledge Graph navigation
3. Re-run Wave A + B regression spot-checks
4. Update `.asep/reports/MB2-CONFORMANCE-COVERAGE.md`
5. Write `.asep/reports/PX3-INTEGRATION-C.md`
6. Verify Wave C exit criteria
7. §11: document natural failures only — never inject artificial FAIL

---

## Acceptance criteria

- [ ] PX3-INTEGRATION-C.md PASS with coverage delta ≥2 Observable rows (§4.2, §5)
- [ ] INV-R-12 re-verified — no consumer computes ReadySet
- [ ] MB2-CONFORMANCE-COVERAGE.md updated
- [ ] Wave C exit criteria satisfied; no N-class in log
- [ ] `make ci` green

---

## References

- Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`
- Template: `.asep/templates/integration-review-template.md`
