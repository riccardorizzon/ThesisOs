# Platform classification — human index

> **Authoritative source:** `.asep/registry/platform-classification.yaml`  
> **CI consumer:** `make validate-platform-classification`  
> **Contract:** `docs/platform-justification.md`

This file is a **human-readable view** of the registry. If this document and the YAML
diverge, the YAML wins.

**Runtime exclusion:** `backend/app/` and `frontend/` must **not** read this registry.

---

## Consumers

| Consumer | Entry | Role |
|----------|-------|------|
| CI | `make validate-platform-classification` | Bidirectional pass ↔ proposal invariant |
| Human reviewer | This file + proposal `platform_contract` block | Native vs retrospective vs prospective |
| Audit / agents | Registry path in `classification_registry` field | Trust boundary for metadata |
| Product runtime | **Forbidden** | Governance stays above execution |

---

## Executed passes

### `px3-20260706-v1` (retrospective · 2026-07-06)

| WorkOrder | category | hypothesis |
|-----------|----------|------------|
| PX3-EWO-001 … 004 | A | n/a |
| PX3-EWO-005, 006, 008, 009 | B | H-06 |
| PX3-EWO-007, 010 | A | n/a |

### `px-exec-20260706-v1` (retrospective · 2026-07-06)

| WorkOrder | category | hypothesis |
|-----------|----------|------------|
| PX-EXEC-EWO-001 | B | H-03 |

### `px4-20260706-v1` (prospective · 2026-07-06)

| WorkOrder | category | hypothesis |
|-----------|----------|------------|
| PX4-EWO-001 | A | n/a |

---

## Planned (not in CI scope)

| Pass id | Note |
|---------|------|
| `px1-multi-product-v1` | PX1-EWO-006 / H-07 — not executed |

---

## Invariants (enforced in CI)

1. Every `classification_pass` in a proposal exists in `registry.passes`.
2. Every workorder in a pass `scope` has a proposal with the same `classification_pass`.
3. Every scoped workorder has a proposal file on disk.
4. `retrospective` / `prospective` blocks include `classification_registry`.
