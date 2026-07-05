# META-1 — Capability Model Gate (pre C.4)

> **Status:** ✅ **APPROVED** (operator 2026-06-30) — baseline locked  
> **Blocks:** ~~C.4 proposal~~ → **C.4 proposal published** (awaiting approval)  
> **Artifact:** `docs/asep-capability-model.md`

---

## Purpose

Formalize four ASEP framework evolutions **before** OR-4, so C.4 qualifies
**Constraint Compliance** on **Normative** knowledge — not a repeat of OR-3 patterns.

---

## Deliverables

| # | Evolution | Priority | Location |
|---|-----------|----------|----------|
| 1 | C.3 → Knowledge Utilization sub-capabilities (retroactive) | High | `docs/asep-capability-model.md` §2 |
| 2 | Normative vs Scientific knowledge domains | High | `docs/asep-capability-model.md` §1 |
| 3 | Traceability Coverage (5th dimension) | Medium | `docs/engineering-program.md` + capability model §3 |
| 4 | Normative FAIL taxonomy | Medium | `docs/engineering-program.md` FAIL tree |

---

## OR-3 qualification validation

Operator confirmed: `or-3-corpus` → **`qualified`** is architecturally valid.

```text
approved → QWO → EWO-4/4A → re-QWO → qualified
```

No WO-TRACE violation. Sub-capability mapping documents *what* was qualified:

| Sub-cap | Status |
|---------|--------|
| C.3.1 Retrieval | ✅ EWO-4A |
| C.3.2 Grounding | ✅ EWO-4 |
| C.3.3 Reasoning | ✅ C.3-R4 |
| C.3.4 Attribution | ⚠️ partial (opere supporto) |

---

## Next WorkOrder

**C.4 proposal** must declare:

- `knowledge_domain: normative`
- `capability_class: constraint-compliance`
- `qwo_sensitivity: deterministic`
- Sub-capabilities C.4.1–C.4.4 per Qualification Contract
- FAIL class: **Normative** (primary)

No C.4 QWO until proposal approved.
