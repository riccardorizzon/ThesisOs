# Execution Authorization Amendment — PX-2 Research Workspace Experience

> **Gate 3 Amendment** — Proposed 2026-07-04  
> **Amends:** `docs/product/EXECUTION-AUTHORIZATION.md` (PX-1 authorization, 2026-07-01)  
> **Status:** **RATIFIED** — 2026-07-04

---

## Status

| Field | Value |
|-------|-------|
| **Constitution** | Product Constitution v1.0 (Frozen — unchanged) |
| **META-1** | **FROZEN** — `docs/asep-capability-model.md` |
| **META-2** | **NOT OPEN** — architectural backlog only |
| **PX-1 Foundation** | **COMPLETE / QUALIFIED** — frozen at QWO-PX1-001-R1 |
| **PX-2** | **AUTHORIZED** — ratified 2026-07-04 |

---

## Framework policy

### META-1 — frozen

The capability model baseline (`docs/asep-capability-model.md`, META-1) is **frozen**.
No framework evolution without a future META gate and explicit architect decision.

### META-2 — not opened

The following items remain in **architectural backlog** (not framework changes):

| Item | Rationale for deferral |
|------|------------------------|
| Infrastructure Reliability Issue (IRI) | Single observed episode (QWO-PX1-001-R1); generalize after PX-2/PX-3 patterns |
| Qualification Environment taxonomy | Record ad hoc in QWO reports until pattern consolidates |

```text
META-1 FROZEN → PX-2…PX-3 execution → META-2 (only if patterns consolidate)
```

Framework and product must not co-evolve on every improvement observation.

---

## PX-1 — frozen

PX-1 Foundation is **complete and qualified**. This amendment does not reopen PX-1 scope.

| Artifact | Role |
|----------|------|
| QWO-PX1-001-R1 | Qualification record — immutable |
| `.asep/reports/PX1-COMPLETE.md` | Program disposition |
| PX1-EWO-001…012 | Implemented — no retroactive changes |

**Constraint:** PX-2 work must not regress OR-1…OR-7 or PX-1 qualification surfaces.

---

## PX-2 — objective

### Name (architectural)

```text
PX-2
Research Workspace Experience
```

**Not** "Writing Workspace Experience."

Writing is one activity within the workspace. The user enters to read corpus, explore
sources, compare chapters, decide, annotate, review, and write. The milestone name must
reflect the **workspace**, not a single activity.

### Purpose

PX-2 is the first milestone where the operator **works** in the product — not only
navigates foundation shells. Capabilities are **user-perceived**, not UI components.

---

## PX-2 capabilities (user-perceived)

Each sub-capability is a qualification target, not a screen or component.

| ID | Capability | User-perceived outcome |
|----|------------|------------------------|
| **PX-2.1** | Context Awareness | Operator sees binding decisions, corpus constraints, and active scope while working |
| **PX-2.2** | Writing Flow | Operator drafts and revises chapter text in a focused writing flow |
| **PX-2.3** | Source Interaction | Operator reads, cites, and connects corpus sources to the active chapter |
| **PX-2.4** | Decision Visibility | Operator sees how project decisions affect current work without admin surfaces |
| **PX-2.5** | Session Continuity | Operator resumes work across sessions with preserved context and progress |

```text
PX-2 Research Workspace Experience
├── PX-2.1 Context Awareness
├── PX-2.2 Writing Flow
├── PX-2.3 Source Interaction
├── PX-2.4 Decision Visibility
└── PX-2.5 Session Continuity
```

**Note:** PX-1 delivered layout shells (Writing three-panel, Sources list, ContextBar view).
PX-2 **activates** these surfaces with real runtime behavior — capability by capability.

---

## Authorized scope (upon ratification)

| Milestone | Status after ratification |
|-----------|----------------------------|
| PX-1 Foundation | **FROZEN** (qualified) |
| **PX-2 Research Workspace Experience** | **AUTHORIZED** |
| PX-3 Sources | EXCLUDED |
| PX-4 Knowledge | EXCLUDED |
| PX-5 Research | EXCLUDED |
| PX-6 Polish | EXCLUDED |

### PX-2 authorized deliverables (capability-driven)

Engineering WorkOrders (EWO) will be derived per sub-capability after program draft review.
Expected domains (non-binding until EWO proposals):

- **PX-2.1** — Context Engine integration in workspace surfaces; live ContextPacket assembly
- **PX-2.2** — Chapter editor, save flow, writer route integration (M6 seam)
- **PX-2.3** — Source reader, citation hooks, corpus retrieval in workspace
- **PX-2.4** — Decision/dec constraint surfacing in workspace (not settings admin)
- **PX-2.5** — Continue/resume, session state, progress persistence

**Constraints (unchanged):**

- Product Constitution v1.0 + Runtime Constitution C1–C8
- OR-1…OR-7 regression on qualification
- ADR amendment only via constitution governance (P8)
- META-1 frozen — no new ASEP categories without META gate

---

## Qualification (PX-2)

PX-2 completes through **QWO-PX2-001** (to be proposed after EWO backlog defined).

Minimum acceptance (draft — refined in QWO proposal):

- Each PX-2.1…PX-2.5 capability demonstrable on live stack
- `make ci` green
- OR-1…OR-7 regression green
- No PX-1 qualification regression

Qualification environment: declare in QWO report § Pre-flight (ad hoc until META-2, if ever opened).

---

## Engineering program activation (not automatic)

```text
Ratify this amendment
        ↓
Draft PX-2 EWO backlog in thesisos-product-v2.yaml (or px2 program slice)
        ↓
Architect Program Review (PX-2 scope)
        ↓
PX-2 EWO dispatch
        ↓
QWO-PX2-001
```

EWO dispatch is **not authorized** until this amendment is **ratified** and program draft reviewed.

---

## Roadmap (architect)

```text
META-1 FROZEN
    ↓
Execution Authorization Amendment (this document)
    ↓
PX-2 Research Workspace Experience
    ↓
PX-2 Qualification (QWO-PX2-001)
    ↓
PX-3 …
    ↓
META-2 (only if consolidated patterns emerge)
```

---

## Sign-off

```text
Product Constitution:     v1.0 (Frozen)
META-1:                   FROZEN
META-2:                   NOT OPEN
PX-1:                     COMPLETE / QUALIFIED (frozen)
Proposed scope:           PX-2 Research Workspace Experience
Excluded:                 PX-3, PX-4, PX-5, PX-6

Architect:                ratified (operator directive 2026-07-04)
Date:                     2026-07-04 (ratified)
Prior authorization:      docs/product/EXECUTION-AUTHORIZATION.md (2026-07-01)
```

---

## WO-TRACE

```text
Gate 3 (PX-1) → QWO-PX1-001-R1 PASS → PX-1 COMPLETE
    → Gate 3 Amendment (PX-2) → PX-2 EWOs → QWO-PX2-001 → PX-3 …
```
