# UX Alignment Review — Governance Gate

> **Status:** FROZEN 2026-07-04  
> **Product spec:** `docs/product/specs/px3-knowledge-experience-v2.md`  
> **UI spec:** `design-system/thesisos/px3-knowledge-experience-ui-spec.md`  
> **Result:** PASS — all checklist items satisfied

---

## Pipeline (mandatory)

```text
Product Specification          ← milestone, capability, ownership (Product owns)
        │
        ▼
UX Alignment Review          ← this gate
        │
        ▼
UI Specification             ← layout, components, interaction (UX owns)
        │
        ▼
Engineering EWOs             ← after PX predecessor qualified + authorization
```

---

## UX may

- Improve flows, component hierarchy, spacing, typography, motion
- Propose interaction patterns and visual hierarchy
- Elevate recurring ideas to **product patterns** (`design-system/thesisos/product-patterns.md`)
- Suggest copy (Italian operator / English nav per IR-5)

## UX may not

- Redefine **milestones** (PX-n scope)
- Split or merge **capabilities** (PX-n.m IDs)
- Change **module ownership** or route responsibilities frozen in ADR-0036
- Alter **roadmap sequencing** (e.g. move graph canvas into an earlier milestone)
- Amend Product Constitution, ADRs, or META-1

If UX discovers a product gap → **stop** and file feedback to Product; do not encode the change in UI spec.

---

## Alignment checklist (per milestone)

| # | Check | Pass criterion |
|---|-------|----------------|
| 1 | Spec citation | UI spec header links canonical `docs/product/specs/px*-*.md` |
| 2 | Capability map | Every PX-n.m capability has ≥1 UI section; no orphan UI scope |
| 3 | Milestone boundary | No UI section tagged with wrong PX-n; deferred items in Exclusions |
| 4 | IA frozen | Sidebar + routes match ADR-0036 + product spec §IA |
| 5 | PX predecessor | UI spec states "builds on PX-(n-1) frozen"; no retroactive PX-(n-1) changes |
| 6 | Interaction rules | Product IR/KR rules preserved in UI spec |
| 7 | Qualification trace | UI sections map to QWO acceptance criteria where published |

---

## Review record template

```text
Milestone:     PX-3 Knowledge Experience
Product spec:  docs/product/specs/px3-knowledge-experience-v2.md
UI spec:       design-system/thesisos/px3-knowledge-experience-ui-spec.md
Reviewer:      UX & Design System Lead
Date:          YYYY-MM-DD
Result:        ALIGNED | BLOCKED
Notes:         (capability mismatches, if any)
```

---

## WO-TRACE

```text
Product Architect spec → UX Alignment Review → UI Specification → (later) Engineering
```
