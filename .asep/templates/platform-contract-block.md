# Platform contract block — EWO proposals

> **Binding:** `docs/platform-justification.md` §5–§6  
> **Include in:** every EWO proposal (`.asep/proposals/*.md`) and internal Work Orders  
> **Authorize gate:** `.asep/resolvers/authorize.md` pre-flight

Copy the YAML block below into the proposal **immediately after the title/status
banner**. Authorization **STOP**s if B or C is missing `hypothesis_id`,
`success_metric`, or `exit_id`.

---

## Required YAML (native — at filing time)

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A | B | C
  hypothesis_id: H-0N | n/a
  success_metric: "<measurable statement>"
  exit_id: X-0N | n/a
  program_mode: core | product | rd
```

| Field | Required when | Values |
|-------|---------------|--------|
| `classification_schema` | Always (from 2026-07-06) | `platform-contract-v1` — shape of this YAML block |
| `category` | Always | **A** Validated · **B** Experimental · **C** Research |
| `hypothesis_id` | B, C | `H-01`…`H-07` from platform-justification §2; `n/a` only for Category A |
| `success_metric` | B, C | Falsifiable; cite proposal acceptance or §2 metric |
| `exit_id` | B, C | `X-01`…`X-08` from platform-justification §3 |
| `program_mode` | Always | **core** ASEP maintenance · **product** delivery · **rd** PX-EXEC / authorized R&D |

**Native filings** omit `classification_mode`, `classification_pass`, and `classified_on`.

---

## Versioning (three distinct concepts)

| Concept | Field | Example | Meaning |
|---------|-------|---------|---------|
| **Schema** | `classification_schema` | `platform-contract-v1` | YAML field set and semantics — evolves when the contract model changes |
| **Mode** | `classification_mode` | `retrospective` | How the block was added: `retrospective` vs native at filing |
| **Pass** | `classification_pass` | `px3-20260706-v1` | A bounded backfill operation — scope + date; **not** the schema version |
| **Pass date** | `classified_on` | `2026-07-06` | When the pass ran (not original EWO authorization date) |
| **Registry** | `classification_registry` | `.asep/registry/platform-classification.yaml` | Authoritative pass index — required for retrospective/prospective |

**Consumers:** CI (`make validate-platform-classification`), human index, agents — **not** product runtime.

Future passes use new `classification_pass` ids (e.g. `px1-multi-product-v1`) while
reusing or bumping `classification_schema` only when the YAML shape changes.

---

## Retrospective classification (closed proposals)

When adding `platform_contract` **after** original authorization — metadata only;
**do not** edit proposal body, outcomes, or authorization text.

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  classification_mode: retrospective
  classification_pass: <program>-<YYYYMMDD>-vN
  classification_registry: .asep/registry/platform-classification.yaml
  classified_on: 2026-07-06
  category: A | B | C
  hypothesis_id: H-0N | n/a
  success_metric: "<measurable or report reference>"
  exit_id: X-0N | n/a
  program_mode: core | product | rd
```

| Rule | |
|------|--|
| Pure product EWO | `category: A`, `hypothesis_id: n/a` — do not force H-* |
| Conformance / Observable SoR | `category: B`, link H-06 when mapping is obvious |
| Platform R&D (PX-EXEC) | `category: C` or **B** if implemented but hypothesis open |
| Open / PROPOSED proposals | Native block — no `classification_mode` / `classification_pass` |

**Pass index:** `.asep/reports/platform-classification-*` documents scope per pass.

---

## Classification guide

### Category A — Validated

- Extends a capability listed in platform-justification §1, **or**
- Pure product delivery with **no** platform path touch (default for PX-1…PX-3 product EWOs).

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  hypothesis_id: n/a
  success_metric: "Acceptance criteria §… in this proposal"
  exit_id: n/a
  program_mode: product
```

### Category B — Experimental

- Implemented but hypothesis not yet satisfied (e.g. PX-EXEC-EWO-001).

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: B
  hypothesis_id: H-03
  success_metric: "≥20 engineering cycles logged in 90 days with program_id"
  exit_id: X-02
  program_mode: rd
```

### Category C — Research

- PX-EXEC default; spec-only or not yet implemented.

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: C
  hypothesis_id: H-01
  success_metric: "≥3 policy rules evaluated in builder-engine cycle; zero manual policy overrides for 5 consecutive cycles"
  exit_id: X-01
  program_mode: rd
```

---

## Scope check (before filing)

1. Touches `builder_engine/` or `.asep/programs/px-exec.yaml` → minimum **B** or **C**, `program_mode: rd`.
2. Touches `backend/app/` / `frontend/` only → default **A**, `program_mode: product`.
3. Violates platform-justification §4 → reclassify as product work or reject.

---

## References

- Hypotheses: `docs/platform-justification.md` §2  
- Exit criteria: `docs/platform-justification.md` §3  
- Decision protocol: `docs/platform-justification.md` §6  
- Pass index: `.asep/reports/platform-classification-index.md` (human view of registry)
