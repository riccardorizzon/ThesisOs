# PX-6 Wave A — Backlog Definition

> **Authority:** ASEP design session (extract from `PX6-BACKLOG.md`)  
> **Date:** 2026-07-07  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-6 Polish  
> **Scope:** Wave A only — spec foundation before implementation waves

---

## Functional objective (Wave A)

Establish the **normative PX-6 Polish** product specification and UI spec draft
before any validator, export, or multi-project implementation.

**Master backlog:** `.asep/reports/PX6-BACKLOG.md`

**Product thesis:**

```text
PX-6 = Polish → Is the thesis workflow production-ready?
```

Wave A answers: *what* PX-6 delivers, *what* remains deferred, and *how* W-06
mitigation differs from OR-6 re-qualification.

---

## Authoritative sources

| Artifact | Role |
|----------|------|
| `docs/product/specs/thesisos-product-ux-v1.md` | §10 PX-6 deliverables |
| `docs/KNOWN_LIMITATIONS.md` | W-06 — mitigation architecture input |
| `docs/product/specs/px2-research-workspace-experience-v2.md` | §26 W-06 UX |
| `docs/product/specs/px3-knowledge-experience-v2.md` | Bibliography + flags |
| `docs/product/specs/px5-research-experience-v1.md` | §15 exclusions |
| `design-system/thesisos/MASTER.md` | Typography phase |
| `docs/px5-promotion.md` | Deferred scope handoff |

**Deferred to Waves B–F (not Wave A):** All implementation — validator, export,
multi-project, outline reorder, settings, fonts, performance.

---

## Wave A DAG

```text
PX-5 PROMOTED (px5-complete)
      ↓
PX6-EWO-001  Polish Experience Spec + UX foundation  ← first executable
      ↓
(Architect ratification → spawn Wave B validator backlog)
```

| EWO | Title | Parallel after |
|-----|-------|----------------|
| **PX6-EWO-001** | Polish Experience Spec + UX foundation | — (first executable) |

**First executable EWO:** `PX6-EWO-001`

---

## PX6-EWO-001 — deliverables

| Artifact | Path |
|----------|------|
| Product spec | `docs/product/specs/px6-polish-experience-v1.md` |
| UI spec draft | `design-system/thesisos/px6-polish-experience-ui-spec.md` |
| PASS report | `.asep/reports/PX6-EWO-001-polish-experience-spec.md` |

### Spec must include

1. **Capability map** PX-6.1…PX-6.7 (from master backlog)
2. **W-06 mitigation architecture** — product validation layer; not OR-6 re-proof
3. **Boundary matrix** — vs PX-2…PX-5 (mandatory table)
4. **Export formats** — BibTeX minimum; RIS optional; print scope
5. **Multi-project model** — project list, switch semantics, isolation rules
6. **Settings sections** — replace M0 stub scope
7. **Typography** — Crimson Pro + Atkinson Hyperlegible adoption criteria
8. **QWO-PX6-001 draft** — AC-1…AC-11 acceptance table
9. **Exclusions** — collaboration, separate agents, MB2, model replacement

### Acceptance (EWO-001)

- [ ] Product spec ratified with all § above
- [ ] UI spec defines validator, export dialog, project switcher, settings layout
- [ ] Boundary table: no scope bleed from PX-5 canvas or PX-4 Explain
- [ ] W-06 section cites KNOWN_LIMITATIONS partial mitigation path
- [ ] No implementation code in this EWO (spec-only)
- [ ] Proposal `.asep/proposals/PX6-EWO-001-polish-experience-spec.md` filed

---

## Execution model

```text
AUTHORIZE PX-6 (milestone) ✓
      ↓
DESIGN PX-6 backlog ✓
      ↓
ASEP: develop PX6-EWO-001
      ↓
Architect ratification → AUTHORIZE PX-6 Wave B
```

Engineering program. Product docs + design-system only — no `backend/app` or
`frontend/` code in Wave A.

---

## Boundary matrix (preview — full table in spec)

| Surface | PX-5 delivered | PX-6 adds |
|---------|----------------|-----------|
| Writing | Cite flow, W-06 stub message | Live validator + reorder |
| Sources | Bibliografia view-only | Export + validator badges |
| AppShell | Disabled project switcher | Active multi-project |
| Settings | M0 stub | Project prefs + export defaults |
| Research canvas | Complete | Perf audit only (no feature expansion) |

---

## WO-TRACE

```text
AUTHORIZE PX-6 → DESIGN PX6-BACKLOG → PX6-EWO-001 (Wave A)
  → (Wave B validator — after spec PASS)
```
