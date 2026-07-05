# Constitution Governance

> **FROZEN** — Meta layer governing the relationship between Runtime and Product
> Constitutions. Amendment requires Architect decision + documented rationale.
> Does not live inside Product ADRs or Runtime Constitution articles.

---

## Scope

This document defines **precedence**, **boundaries**, and **change policy** between:

| Constitution | Governs | Authoritative artifact |
|--------------|---------|------------------------|
| **Runtime** | Engine — layers, events, contracts, graph topology | `docs/runtime-constitution.md` (C1–C8) |
| **Product** | UX — modules, knowledge model, AI interaction, product state | `docs/product/PRODUCT-CONSTITUTION.md` (manifest) |

Neither constitution replaces ASEP. ASEP validates compliance; this document resolves conflicts.

---

## Principles

### P1 — Runtime governs the engine

Runtime Constitution invariants (C1–C8) bind all Product Plane work. Product features
must not violate layer boundaries, public contracts, or qualified runtime behavior
unless a **Runtime ADR** authorizes the change.

### P2 — Product governs the product

Product Constitution binds UX, information architecture, knowledge-centric model,
Context Engine semantics, and AI interaction patterns. Runtime must not prescribe
navigation, layout, or product module structure.

### P3 — Precedence on direct conflict

When Product Constitution and Runtime Constitution **directly conflict**, **Runtime
Constitution prevails**. Product must adapt (new Product Constitution version or
Product ADR amendment), not silently override runtime invariants.

### P4 — Product Plane contract compliance

Product Plane code (`frontend/`, product-facing `backend/app/` APIs and graph nodes)
**must not** break frozen runtime contracts (`GraphState`, `/chat` external shape,
canonical events) without a Runtime ADR + version bump per `docs/runtime-contract.md`.

### P5 — Runtime Plane UX neutrality

Runtime Plane **must not** impose product UX decisions (default routes, sidebar
structure, module naming). Product Constitution owns operator-facing experience.

### P6 — Cross-plane changes

Changes touching **both** planes require **dual approval**:

1. **Architect** — Product Constitution impact acknowledged
2. **Runtime ADR** — engine change authorized

Document in both Product and Runtime change records.

### P7 — Qualification baseline

Product Constitution v1.0 assumes **ThesisOS v1.0 Operational** qualification
(OR-1…OR-7, E.1) as regression baseline. Product execution programs (PX-n) must
not regress qualified runtime capabilities unless explicitly superseded by a new
runtime release baseline.

### P8 — Constitution change policy

A **new Product Constitution version** (e.g. v1.0 → v1.1) may be opened **only**
when at least one of the following holds:

| Trigger | Example |
|---------|---------|
| **Product Vision change** | Research OS repositioning |
| **Product invariant change** | ADR-defined rule amended |
| **New architectural domain** | Collaboration plane, multi-tenant workspace |
| **Runtime incompatibility** | Product requires runtime contract break |
| **Explicit Architect decision** | Documented in ratification rationale |

In **all other cases**, change the **Engineering Program** (scope, milestones,
EWO backlog) — **not** the Product Constitution.

Minor UX iteration, bug fixes, and PX milestone adjustments do **not** require a
new Constitution version.

---

## Product Constitution lifecycle

```text
Draft  →  Ratified  →  Frozen  →  Superseded  →  Archived
```

| State | Meaning |
|-------|---------|
| **Draft** | PA-0 / Governance Program in progress; not binding |
| **Ratified** | ASEP Validate Constitution PASS + Architect ratification |
| **Frozen** | Architecture freeze marker; no in-place edits |
| **Superseded** | New version ratified; old version read-only |
| **Archived** | Historical; not referenced by active programs |

Supersession **replaces** a version. Do not edit a Frozen constitution in place.

---

## Compatibility (Product ↔ Runtime)

Each Product Constitution manifest declares runtime compatibility:

```yaml
compatibility:
  runtime_constitution: "v1"
  minimum_runtime_release: thesisos-v1.0-operational
  maximum_runtime_release: thesisos-v1.x   # until superseded
```

Future Product Constitution v2.0 may require Runtime Constitution v2.0 — both fields
must be updated together under P6 dual approval.

---

## Governance programs (ASEP)

| `program_type` | Purpose | Work orders | Code mutation |
|----------------|---------|-------------|---------------|
| **governance** | Constitution, policy, standards | EWO (docs only) | `false` |
| **engineering** | Product implementation (PX-n) | EWO | `true` (scoped) |
| **qualification** | Evidence, gates | QWO | `false` |

No new Work Order types. Program constraints define behavior.

---

## Gates (summary)

```text
Gate 1  Architecture Review PASS           (Architect — four questions)
Gate 2  ASEP READY FOR RATIFICATION        (Architect signs RATIFICATION.md → Frozen)
Gate 3  Execution Authorization            (Architect — scoped e.g. PX-1 only)
```

Gate 3 is incremental per milestone — not all PX authorized at once.

### Engineering program activation

```text
Execution Authorization (PX-n)
        ↓
thesisos-product-v2.draft.yaml
        ↓
Architect Program Review PASS
        ↓
thesisos-product-v2.yaml (active)
        ↓
EWO execution
```

Planning is **not** automatic. Draft ≠ active program.

See `docs/product/CONSTITUTION-PROGRAM-charter.md` for full pipeline.

---

## WO-TRACE

```text
Product UX vision → Constitution Governance (this doc) → PA-0 Governance Program
→ Product Constitution v1.0 → Execution Authorization → thesisos-product-v2 → PX-n
```
