# PX Design Workflow — Product Experience EWOs

> Binds **ASEP governance** + **ui-ux-pro-max** + **impeccable** + frozen Product Constitution.  
> Use for PX1-EWO-003 onward (Home, Routing, Writing, Sources, …).

---

## When to use

Every **Product Plane EWO** that touches `frontend/`:

| EWO | ui-ux-pro-max focus |
|-----|---------------------|
| PX1-EWO-003 Home | `pages/home.md`, dashboard pattern, quick actions |
| PX1-EWO-004 Routing | `--stack nextjs`, redirects, IA |
| PX-2 Research Workspace | three-panel layout, editor UX (frozen at qualification) |
| **PX-3 Knowledge Experience** | Explorer, Explain Page, graph, enriched Sources — `px3-knowledge-experience-ui-spec.md` |
| PX-5 Research canvas | deferred — Product spec defines scope |
| PX-6 Polish | citation validator, export, multi-project |

---

## Pipeline (mandatory order)

```text
1. ASEP              Proposal + scope from thesisos-product-v2.yaml
2. Product Spec      Canonical px*-*.md (milestone ownership)
3. UX Alignment      docs/product/UX-ALIGNMENT-REVIEW.md checklist
4. ui-ux-pro-max     Design intelligence (CLI below)
5. Constitution      Merge with design-system-v1.md tokens (tokens WIN)
6. UI Specification  design-system/thesisos/px*-*.md
7. impeccable        context.mjs → reference/product.md → craft/audit
8. Implement         Code + tests (after predecessor PX qualified)
9. Checklist         MASTER.md + product-patterns.md
10. ASEP             Report + QC certificate
```

---

## Step 2 — ui-ux-pro-max commands

From repo root (`python3` required):

```bash
# A. Design system for the module (read output; adapt colors to frozen tokens)
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py \
  "<product type + module keywords>" \
  --design-system -p "ThesisOS" --format markdown

# B. Persist page override (optional, for complex pages)
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py \
  "<query>" --design-system --persist -p "ThesisOS" --page "<page>"

# C. UX / accessibility supplement
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py \
  "accessibility focus animation" --domain ux

# D. Next.js implementation rules
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py \
  "<topic>" --stack nextjs
```

**Skill file:** `.cursor/skills/ui-ux-pro-max/SKILL.md`  
**Source:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

---

## Step 3 — Precedence rules

| Source | Wins on |
|--------|---------|
| `docs/product/PRODUCT-CONSTITUTION.md` | Architecture, invariants |
| `docs/product/specs/px*-*.md` | Milestone scope, capabilities, routes |
| `docs/product/design-system-v1.md` | Color, spacing tokens |
| `docs/product/specs/thesisos-product-ux-v1.md` | Baseline IA (superseded per-milestone by px*-*.md) |
| `design-system/thesisos/px*-ui-spec.md` | Implementation UI (after UX Alignment) |
| `design-system/thesisos/product-patterns.md` | Cross-milestone patterns |
| `design-system/thesisos/pages/*.md` | Page layout deviations |
| ui-ux-pro-max output | Typography ideas, UX checklist, anti-patterns |

**Never** apply uupm-generated hex colors if they conflict with `frontend/styles/tokens.css`.

---

## Step 4 — impeccable

```bash
node .cursor/skills/impeccable/scripts/context.mjs --target frontend/app
```

Then read `reference/product.md` (app UI register). Run audit before closing EWO if visual change is significant.

---

## Hierarchical retrieval (pages)

When building page `X`:

1. Read `design-system/thesisos/pages/X.md` if exists  
2. Else `design-system/thesisos/MASTER.md`  
3. Always enforce `docs/product/design-system-v1.md` tokens  

---

## Skill stack summary

| Skill | Role |
|-------|------|
| **asep** | Governance, EWO, evidence |
| **ui-ux-pro-max** | Design intelligence, 99 UX rules, stack hints |
| **impeccable** | Craft, contrast, browser QA |
| **frontend-design** | Optional; use if impeccable insufficient |

---

## WO-TRACE

```text
PX handoff → PX-DESIGN-WORKFLOW → ui-ux-pro-max CLI → frozen tokens → EWO implement
```
