# Architect Decision — PX-3 Wave B Framework Ratification

> **Date:** 2026-07-05  
> **Authority:** Architect  
> **Receipt:** Ratifies MB2 Conformance Coverage taxonomy with refinements; authorizes Wave B backlog **drafting only**

---

## Decision

```text
Ratifico la tassonomia A/B/C come modello di classificazione della MB2
Conformance Coverage.

Wave B resta Design Only per l'implementazione.

Backlog Wave B autorizzato alla progettazione.

Implementation: NOT AUTHORIZED.
```

---

## Refinement 1 — PX-3 exercisability column

**Parziale** is replaced by **Observable**.

| PX-3 exercisability | Meaning |
|---------------------|---------|
| **Yes** | Can be fully demonstrated in PX-3 |
| **Observable** | PX-3 can observe effects; cannot prove the Runtime contract |
| **No (Runtime)** | Requires Reference Implementation |
| **No (Qualification)** | Requires MB2-Q gates |

Mapping to class A/B/C (retained for wave gating):

| Class | PX-3 exercisability |
|-------|---------------------|
| **A** | Yes |
| **B** | Observable |
| **C** | No (Runtime) or No (Qualification) |

---

## Refinement 2 — Conformance, not Exercise

Wave themes use **Conformance** or **Validation** — not **Exercise**.

PX-3 does not exercise the Runtime. It verifies that product behavior aligns with
the contract defined in the SoR.

---

## Wave B objectives (approved)

| Tier | SoR target |
|------|------------|
| **Primary** | §9 Projection Conformance |
| **Secondary** | §10 Supervisor interaction |
| **Optional** | §11 Failure semantics — only when encountered naturally; not forced |

Failure and Recovery must not be primary Wave B objectives.

---

## EWO constraint — `covers:` cap

Each EWO `covers:` block: **at most three elements total** — typically one each in
`sor_sections`, `invariants`, `mb2_gates`. More than three indicates an oversized EWO.

---

## Wave selection rule

Each wave must answer:

> **Which new part of the SoR becomes verifiable because of this wave?**

Not: *Which features does it add?*

---

## Authorization state after this decision

| Gate | Status |
|------|--------|
| Taxonomy A/B/C | **RATIFIED** (with Yes/Observable refinement) |
| Wave B framework | **RATIFIED** |
| Wave B backlog draft | **AUTHORIZED** |
| Wave B implementation | **NOT AUTHORIZED** — pending backlog review + explicit `AUTHORIZE` |

---

## WO-TRACE

```text
Wave A Conformance Review PASS
  → Coverage taxonomy draft
  → Architect Decision (this doc) — RATIFIED
  → PX3-WAVE-B-BACKLOG.md draft
  → Backlog review → AUTHORIZE PX-3 Wave B dispatch (future)
```

---

## References

- Coverage matrix: `.asep/reports/MB2-CONFORMANCE-COVERAGE.md`
- Wave B framework: `.asep/reports/PX3-WAVE-B-DESIGN-FRAMEWORK.md`
- Wave B backlog (draft): `.asep/reports/PX3-WAVE-B-BACKLOG.md`
- EWO template: `.asep/templates/conformance-ewo-template.md`
