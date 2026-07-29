# Product Track M7–M9 — Proposed package closure

**Date:** 2026-07-29  
**Decision:** Close design stragglers; leave **only** Product Track M7→M8→M9 open as the next product line.  
**Does not authorize implementation** (ADR-0001) until Architect Accept on each milestone.

---

## Closed (this session)

| Item | Disposition |
|------|-------------|
| M7/M8/M9 design ambiguity (outline PUT shape, critique receipt, bibliography OpenAPI) | **LOCKED** in Proposed specs/ADRs |
| ADR number collision with ADR-0049 Writing Action Loop | Renumbered to **ADR-0053…0056** |
| Demo presentability | Remains **closed** (prior receipt) |
| GA / human cohort | Remains **deferred** (no authorize) |
| Product Hardening “M7” (ADR-0044 / rc.2) | **Shipped** — not reopened; naming kept distinct |

## Open (product-best next line)

1. **NEXT:** Architect Accept → M7 Grounding Engine Wave 1 (Citations)  
   - Spec + ADR-0053/0054 + `docs/m7-grounding-promotion.md`  
   - Tag target: `m7-grounding-complete`
2. **Queued:** M8 Outline (ADR-0055) → M9 Critic (ADR-0056)
3. **Still deferred:** GA package, M10+

## Artifact index

| M | Spec | ADRs | Gate |
|---|------|------|------|
| M7 | `docs/superpowers/specs/2026-07-29-thesisos-m7-grounding-engine-design.md` | 0053, 0054 | `docs/m7-grounding-promotion.md` |
| M8 | `docs/superpowers/specs/2026-07-29-thesisos-m8-outline-design.md` | 0055 | `docs/m8-outline-promotion.md` |
| M9 | `docs/superpowers/specs/2026-07-29-thesisos-m9-critic-design.md` | 0056 | `docs/m9-critic-promotion.md` |

## Program pointer

`.asep/programs/thesisos-product-v2.yaml`: `next_milestone` → M7 Grounding Wave 1 (Proposed).  
`milestone_authorized: none` until an Architect authorize act.

## Operator next command (when ready)

```text
AUTHORIZE M7 GROUNDING
```

(or equivalent Architect Accept on the M7 Grounding spec + ADR-0053/0054)
