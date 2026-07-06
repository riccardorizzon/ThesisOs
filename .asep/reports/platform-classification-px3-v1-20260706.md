# Platform classification — pass index

> **Schema:** `platform-contract-v1` (`.asep/templates/platform-contract-block.md`)  
> **Contract:** `docs/platform-justification.md`

This file indexes **retrospective classification passes**. Each pass is bounded;
new scope → new pass id — do not extend an existing pass silently.

---

## Pass registry

| Pass id | Date | Scope | Report |
|---------|------|-------|--------|
| `px3-20260706-v1` | 2026-07-06 | PX3-EWO-001…010 | This document § PX-3 |
| `px-exec-20260706-v1` | 2026-07-06 | PX-EXEC-EWO-001…003 | This document § PX-EXEC |

**Planned (not executed):**

| Pass id | Scope |
|---------|-------|
| `px1-multi-product-v1` | PX1-EWO-006 and related H-07 mapping |

---

## Field semantics (pass `px3-20260706-v1`)

Proposals carry:

```yaml
classification_schema: platform-contract-v1   # YAML shape — not pass version
classification_mode: retrospective
classification_pass: px3-20260706-v1          # this pass
classified_on: 2026-07-06
```

**Rule:** Metadata only — proposal body, authorization, status banners unchanged.

---

## PX-3 — pass `px3-20260706-v1`

| EWO | Status (banner, unchanged) | category | hypothesis_id | program_mode |
|-----|----------------------------|----------|---------------|--------------|
| PX3-EWO-001 | IMPLEMENTED | A | n/a | product |
| PX3-EWO-002 | IMPLEMENTED | A | n/a | product |
| PX3-EWO-003 | IMPLEMENTED | A | n/a | product |
| PX3-EWO-004 | IMPLEMENTED | A | n/a | product |
| PX3-EWO-005 | IMPLEMENTED | B | H-06 | product |
| PX3-EWO-006 | IMPLEMENTED | B | H-06 | product |
| PX3-EWO-007 | IMPLEMENTED | A | n/a | product |
| PX3-EWO-008 | AUTHORIZED | B | H-06 | product |
| PX3-EWO-009 | REGISTERED (report PASS) | B | H-06 | product |
| PX3-EWO-010 | REGISTERED (Integration C PASS) | A | n/a | product |

### Mapping rationale

| Class | EWOs | Rationale |
|-------|------|-----------|
| **A / product / n/a** | 001–004, 007, 010 | Product delivery or integration gates |
| **B / H-06** | 005, 006, 008, 009 | SoR conformance observation (Observable, not MB2-Q qualified) |

EWO-006 also cites `exit_id: X-08` (supervisor gating in product UI).

---

## PX-EXEC — pass `px-exec-20260706-v1`

| EWO | category | hypothesis_id | Notes |
|-----|----------|---------------|-------|
| PX-EXEC-EWO-001 | B | H-03 | Implemented; hypothesis not satisfied |
| PX-EXEC-EWO-002 | B | H-03 | Implemented; enables rule engine evidence |
| PX-EXEC-EWO-003 | B | H-03 | Implemented; enables dependency engine evidence |

PX-EXEC-EWO-004+ retain **native** blocks at filing (no `classification_mode`).

---

## Excluded from all passes to date

- PX-1, PX-2 proposals (except future `px1-multi-product-v1`)
- thesis-agent EWOs
- Open PX-EXEC proposals (004–009)
