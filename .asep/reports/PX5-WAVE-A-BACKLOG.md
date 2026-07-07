# PX-5 Wave A — Backlog Definition

> **Authority:** Architect (product architecture)  
> **Date:** 2026-07-06  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-5 Research  
> **Scope:** Wave A only — spec foundation before implementation waves

---

## Functional objective (PX-5)

Deliver the **Research spatial canvas** — interactive map of the research landscape
where nodes are concepts with live links to sources, chapters, and decisions.

**Product thesis** (`thesisos-product-ux-v1.md` §5.2):

```text
PX-4 = Knowledge  →  What does my thesis know? (Explain + bounded graph)
PX-5 = Research   →  How do I explore the landscape? (spatial canvas)
```

Wave A establishes the **normative product spec and UI foundation** before any
`/research/canvas` implementation.

**Status (2026-07-06):** Wave A complete — PX5-EWO-001 PASS.

---

## Authoritative sources (not agent-invented)

| Artifact | Role |
|----------|------|
| `docs/product/specs/px5-research-experience-v1.md` | Product spec (ratified by EWO-001) |
| `design-system/thesisos/px5-research-experience-ui-spec.md` | UI spec draft |
| `decisions/ADR-0037-knowledge-model.md` | Research domain; INV-KM-5 |
| `decisions/ADR-0036-information-architecture.md` | `/research` route |
| `docs/product/specs/px3-knowledge-experience-v2.md` | §22 exclusions; §16 guided research boundary |
| `docs/px4-promotion.md` | PX-4 delivered scope |
| `design-system/thesisos/pages/research.md` | PX-3 guided research (not canvas) |

**Deferred to later waves (not Wave A):** Canvas rendering, discovery API, Writing
handoff implementation, qualification QWO.

---

## Wave A DAG

```text
PX5-EWO-001  Research Experience Spec + UX foundation  ✓ PASS
      ↓
PX5-EWO-002  Research hub + route scaffolding  ✓ PASS
      ↓
PX5-EWO-003  Canvas viewport + node layer  (Wave C — pending authorization)
```

| EWO | Title | Parallel after |
|-----|-------|----------------|
| **PX5-EWO-001** | Research Experience Spec + UX foundation | — (first executable) |

**First executable EWO:** `PX5-EWO-001` (no dependencies).

---

## Execution model

Engineering program (not conformance). Product code only in `frontend/` and
`backend/app/` per program constraints.

```text
AUTHORIZE PX-5
      ↓
Pre-flight PASS
      ↓
PX5-EWO-001 (spec + UI spec draft)
      ↓
Architect ratification → spawn Wave B implementation backlog
```

---

## Boundary matrix (mandatory in spec)

| Capability | Owner | Route |
|------------|-------|-------|
| Guided exploration (trail + basket) | PX-3 | `/research` (existing) |
| Knowledge navigation graph | PX-3/PX-4 | `/knowledge/graph` |
| Spatial research canvas | **PX-5** | TBD in spec (likely `/research/canvas` or enhanced `/research`) |
| Concept Explain panel | PX-4 | `/knowledge/[slug]` |

---

## WO-TRACE

```text
PX-4 PROMOTED → PX-3 CONFORMANCE COMPLETE → AUTHORIZE PX-5
  → PX5-EWO-001 → (Wave B TBD after spec PASS)
```
