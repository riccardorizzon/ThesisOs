# Platform contract block — EWO proposals

> **Binding:** `docs/platform-justification.md` §5–§6  
> **Include in:** every EWO proposal (`.asep/proposals/*.md`) and internal Work Orders  
> **Authorize gate:** `.asep/resolvers/authorize.md` pre-flight

Copy the YAML block below into the proposal **immediately after the title/status
banner**. Authorization **STOP**s if B or C is missing `hypothesis_id`,
`success_metric`, or `exit_id`.

---

## Required YAML

```yaml
platform_contract:
  category: A | B | C
  hypothesis_id: H-0N | n/a
  success_metric: "<measurable statement>"
  exit_id: X-0N | n/a
  program_mode: core | product | rd
```

| Field | Required when | Values |
|-------|---------------|--------|
| `category` | Always | **A** Validated · **B** Experimental · **C** Research |
| `hypothesis_id` | B, C | `H-01`…`H-07` from platform-justification §2; `n/a` only for Category A |
| `success_metric` | B, C | Falsifiable; cite proposal acceptance or §2 metric |
| `exit_id` | B, C | `X-01`…`X-08` from platform-justification §3 |
| `program_mode` | Always | **core** ASEP maintenance · **product** delivery · **rd** PX-EXEC / authorized R&D |

---

## Classification guide

### Category A — Validated

- Extends a capability listed in platform-justification §1, **or**
- Pure product delivery with **no** platform path touch (default for PX-1…PX-3 product EWOs).

```yaml
platform_contract:
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
