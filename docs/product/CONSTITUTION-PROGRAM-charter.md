# PA-0 — Product Constitution Program Charter

> **FROZEN** — Process architecture for ThesisOS Product v2. Do not extend gates,
> Work Order types, or meta layers without amending `docs/CONSTITUTION-GOVERNANCE.md`.

---

## Status

| Field | Value |
|-------|-------|
| **Milestone** | PA-0 |
| **Program** | `thesisos-product-governance` |
| **`program_type`** | `governance` |
| **Program status** | `READY_FOR_EXECUTION` (after Gate 1 PASS) |
| **Code mutation** | `false` |

---

## Objective

Transform Product Vision into a **ratified, frozen Product Constitution** — not
implementation. Engineering starts only after **Execution Authorization**.

---

## Pipeline (frozen)

```text
IDEA
  ↓
VISION
  ↓
RFC
  ↓
PRODUCT SPECIFICATION
  ↓
ARCHITECTURE REVIEW              Gate 1 — Architect
  ↓
PA-0  (thesisos-product-governance)
  ↓
PRODUCT CONSTITUTION v1.0          Gate 2 — Ratification (ASEP Validate + Architect)
  ↓
EXECUTION AUTHORIZATION          Gate 3 — Architect
  ↓
ENGINEERING PROGRAM              thesisos-product-v2
  ↓
PX-1 Foundation … PX-6 Polish
  ↓
QUALIFICATION (QWO)
  ↓
RELEASE v2.0
```

---

## Gates

### Gate 1 — Architecture Review

Four questions only (see `ARCHITECTURE-REVIEW.md`). Not a page audit.

| | |
|-|-|
| **Owner** | Architect |
| **Artifact** | `docs/product/ARCHITECTURE-REVIEW.md` |
| **Required status** | `PASS` |
| **Status** | **PASS** (2026-07-01) |

### Gate 2 — Ratification

| | |
|-|-|
| **ASEP objective** | `Validate Constitution` → verdict **READY FOR RATIFICATION** |
| **Owner (ratify)** | Architect — `RATIFICATION.md` signature |
| **ASEP artifact** | `.asep/reports/PA-0-constitution-compliance.md` |
| **On ratify** | PRODUCT-CONSTITUTION Frozen; ADR Accepted; ARCHITECTURE-FREEZE ISSUED |
| **Blocks** | Execution Authorization |

PA-0 **COMPLETE** at Gate 2 ratification. Does **not** activate `thesisos-product-v2.yaml`.

Engineering program flow:

```text
EXECUTION-AUTHORIZATION → thesisos-product-v2.draft.yaml → ARCHITECT-PROGRAM-REVIEW → v2.yaml active
```

### Gate 3 — Execution Authorization

| | |
|-|-|
| **Owner** | Architect only |
| **Artifact** | `docs/product/EXECUTION-AUTHORIZATION.md` |
| **Effect** | Authorizes **scoped** engineering — e.g. PX-1 only; PX-2+ remain planned but excluded until re-authorized |
| **Blocks** | Product code EWOs outside authorized scope |

Ratification ≠ permission to code. Execution Authorization is **incremental per milestone**, not all-or-nothing.

---

## PA-0 acceptance criteria

PA-0 is **COMPLETE** (Gate 2) when:

| # | Artifact | Required state |
|---|----------|----------------|
| 1 | Architecture Review | PASS |
| 2 | Product Vision | APPROVED — `docs/product/VISION.md` |
| 3 | RFC-001 | ACCEPTED — `docs/product/rfc/RFC-001-research-os.md` |
| 4 | Product Specification | FROZEN — `docs/product/specs/thesisos-product-ux-v1.md` |
| 5 | ADR-0034 … ADR-0041 | ACCEPTED — `decisions/ADR-0034-*.md` … `0041` |
| 6 | Architecture Freeze marker | ISSUED — `docs/product/ARCHITECTURE-FREEZE.md` |
| 7 | ASEP compliance | PASS — `.asep/reports/PA-0-constitution-compliance.md` |
| 8 | Product Constitution manifest | Ratified → Frozen — `docs/product/PRODUCT-CONSTITUTION.md` |
| 9 | Ratification record | ISSUED — `docs/product/RATIFICATION.md` |

**Not included:** Engineering program YAML, PX EWOs, product code.

---

## Product Constitution ADR set

| ADR | Title |
|-----|-------|
| ADR-0034 | Product Vision |
| ADR-0035 | Product Architecture (4 layers) |
| ADR-0036 | Information Architecture |
| ADR-0037 | Knowledge Model |
| ADR-0038 | Context Engine |
| ADR-0039 | AI Interaction Model |
| ADR-0040 | Product State |
| ADR-0041 | Blueprint ↔ Runtime Sync |

---

## Execution milestones (blocked until Gate 3)

| Milestone | Scope | Depends on |
|-----------|-------|------------|
| PX-1 | Foundation — AppShell, Home, nav, design system, Context v0 | Gate 3 |
| PX-2 | Writing — outline, editor, AI panel | PX-1 |
| PX-3 | Sources — import, metadata, citations | PX-2 |
| PX-4 | Knowledge — concept, Explain this thesis | PX-3 |
| PX-5 | Research — graph, discovery | PX-4 |
| PX-6 | Polish — citation validator, perf, multi-project | PX-5 |

---

## Roles

| Role | PA-0 | PX-n |
|------|------|------|
| **Architect** | Writes Vision/RFC/Spec/ADR drafts; Architecture Review; Ratification; Execution Authorization | Scope, priorities, program authorization |
| **ASEP** | Validate Constitution (compliance only) | EWO/QWO compliance vs Product + Runtime Constitutions |
| **Engineering** | No code | Implements EWO |

---

## Program constraints

```yaml
code_mutation: false
allowed_paths:
  - docs/product/**
  - docs/CONSTITUTION-GOVERNANCE.md
  - decisions/ADR-0034-*.md
  - decisions/ADR-0035-*.md
  - decisions/ADR-0036-*.md
  - decisions/ADR-0037-*.md
  - decisions/ADR-0038-*.md
  - decisions/ADR-0039-*.md
  - decisions/ADR-0040-*.md
  - decisions/ADR-0041-*.md
  - .asep/programs/thesisos-product-governance.yaml
  - .asep/reports/PA-0-*.md
forbidden_outputs:
  - .asep/programs/thesisos-product-v2.yaml   # Gate 3 only
  - frontend/**
  - backend/app/**
```

Work orders remain **EWO** (`ewo_category: Constitution` or `Release` for compliance report).

---

## References

| Document | Role |
|----------|------|
| `docs/CONSTITUTION-GOVERNANCE.md` | Meta precedence P1–P8 |
| `docs/runtime-constitution.md` | Runtime invariants |
| `docs/engineering-program.md` | ASEP program model |
| `.asep/programs/thesisos-product-governance.yaml` | PA-0 program instance |
