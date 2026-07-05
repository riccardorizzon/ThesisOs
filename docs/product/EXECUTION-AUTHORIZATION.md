# Execution Authorization — Product v2 Engineering

> **Gate 3** — Issued 2026-07-01. Scoped authorization only.

---

## Status

| Field | Value |
|-------|-------|
| **Constitution** | Product Constitution v1.0 (Frozen) |
| **Authorization** | **ISSUED** |
| **Engineering program** | `thesisos-product-v2.draft.yaml` → review → activate |

---

## Authorized scope

| Milestone | Status |
|-----------|--------|
| **PX-1 Foundation** | **AUTHORIZED** |
| PX-2 Writing | EXCLUDED |
| PX-3 Sources | EXCLUDED |
| PX-4 Knowledge | EXCLUDED |
| PX-5 Research | EXCLUDED |
| PX-6 Polish | EXCLUDED |

---

## PX-1 authorized deliverables

- AppShell + sidebar (ADR-0036)
- Default route Home (ADR-0036 INV-IA-2)
- Design system tokens + core components
- Home: progress, continue, quick actions, activity feed (ADR-0040)
- Routing per Spec §4
- Context Engine v0 (ADR-0038 minimal packet)
- `project_id` scaffolding (ADR-0040 INV-PS-5)

**Constraints:** Frozen Product Constitution + Runtime Constitution C1–C8; OR-1…OR-7 regression.

---

## Engineering program activation (not automatic)

```text
Generate thesisos-product-v2.draft.yaml
        ↓
Architect Program Review PASS
        ↓
Activate thesisos-product-v2.yaml
        ↓
PX-1 EWO execution
```

Draft generation is **authorized**. Active program requires **Architect Program Review** (`docs/product/ARCHITECT-PROGRAM-REVIEW.md`).

---

## Sign-off

```text
Product Constitution: v1.0 (Frozen)
Authorized Scope:   PX-1 Foundation
Excluded Scope:     PX-2, PX-3, PX-4, PX-5, PX-6

Architect: approved (Gate 3)
Date:     2026-07-01
```

---

## Amendments

| Amendment | Milestone | Status |
|-----------|-----------|--------|
| [EXECUTION-AUTHORIZATION-PX2-AMENDMENT.md](EXECUTION-AUTHORIZATION-PX2-AMENDMENT.md) | PX-2 Research Workspace Experience | **PROPOSED** (2026-07-04) |

---

## WO-TRACE

```text
Frozen Constitution → EXECUTION-AUTHORIZATION (PX-1) → v2.draft.yaml → review → v2.yaml → code
```
