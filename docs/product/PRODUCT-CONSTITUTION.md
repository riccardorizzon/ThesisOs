# Product Constitution — Manifest

> **Source of Truth** for Product Plane governance. This file is an **index**;
> authoritative text lives in linked artifacts. Do not duplicate ADR bodies here.

---

## Metadata

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Lifecycle** | **Frozen** |
| **Program** | PA-0 — **COMPLETE** |
| **Ratified** | 2026-07-01 |
| **Frozen** | 2026-07-01 |
| **Supersedes** | — |
| **Compliance** | Ratified per `.asep/reports/PA-0-constitution-compliance.md` |

---

## Compatibility

| Field | Value |
|-------|-------|
| **Runtime Constitution** | v1 (`docs/runtime-constitution.md`) |
| **Minimum runtime release** | `thesisos-v1.0-operational` |
| **Maximum runtime release** | `thesisos-v1.x` (until superseded) |
| **Qualification baseline** | OR-1…OR-7, E.1 — regression required for PX-n |

---

## Index (bundle)

| Part | Artifact | Status |
|------|----------|--------|
| Meta governance | `docs/CONSTITUTION-GOVERNANCE.md` | FROZEN |
| Charter | `docs/product/CONSTITUTION-PROGRAM-charter.md` | FROZEN |
| Vision | `docs/product/VISION.md` | APPROVED |
| RFC | `docs/product/rfc/RFC-001-research-os.md` | ACCEPTED |
| Specification | `docs/product/specs/thesisos-product-ux-v1.md` | FROZEN |
| ADR-0034 Product Vision | `decisions/ADR-0034-product-vision.md` | Accepted |
| ADR-0035 Product Architecture | `decisions/ADR-0035-product-architecture.md` | Accepted |
| ADR-0036 Information Architecture | `decisions/ADR-0036-information-architecture.md` | Accepted |
| ADR-0037 Knowledge Model | `decisions/ADR-0037-knowledge-model.md` | Accepted |
| ADR-0038 Context Engine | `decisions/ADR-0038-context-engine.md` | Accepted |
| ADR-0039 AI Interaction Model | `decisions/ADR-0039-ai-interaction-model.md` | Accepted |
| ADR-0040 Product State | `decisions/ADR-0040-product-state.md` | Accepted |
| ADR-0041 Blueprint Runtime Sync | `decisions/ADR-0041-blueprint-runtime-sync.md` | Accepted |
| Architecture freeze | `docs/product/ARCHITECTURE-FREEZE.md` | ISSUED |
| Architecture Review | `docs/product/ARCHITECTURE-REVIEW.md` | PASS (Gate 1) |
| Ratification | `docs/product/RATIFICATION.md` | ISSUED |
| ASEP compliance | `.asep/reports/PA-0-constitution-compliance.md` | READY → ratified |
| Execution Authorization | `docs/product/EXECUTION-AUTHORIZATION.md` | ISSUED (PX-1) |
| Engineering program (draft) | `.asep/programs/thesisos-product-v2.draft.yaml` | DRAFT |
| Program review | `docs/product/ARCHITECT-PROGRAM-REVIEW.md` | PENDING |

---

## Lifecycle transitions

```text
Draft  →  Ratified  →  Frozen  →  Superseded  →  Archived
   ↑          Gate 2 (ASEP READY FOR RATIFICATION + RATIFICATION.md signed)
```

Amendment policy: `docs/CONSTITUTION-GOVERNANCE.md` P8.

---

## Invariants (summary)

Full invariants live in ADR-0034…0041 after acceptance. Headlines:

- ThesisOS Product is a **Research Operating System** — not a chatbot (ADR-0034).
- Four layers: Workspace → Knowledge Engine → AI Engine → Runtime (ADR-0035).
- Knowledge-centric, not document-centric (ADR-0037).
- AI lateral, never central UI (ADR-0039).
- Context Engine assembles context; operator does not build prompts (ADR-0038).

---

## Execution (blocked)

Engineering program `thesisos-product-v2` requires:

1. This manifest **Frozen**
2. `docs/product/EXECUTION-AUTHORIZATION.md` — **ISSUED**

PX-1…PX-6 remain blocked until both.
