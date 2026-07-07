# Design System Master — ThesisOS (UI UX Pro Max + Product Constitution)

> **Precedence (binding):**
>
> 1. **Frozen tokens** — `docs/product/design-system-v1.md` + `frontend/styles/tokens.css`  
>    (Product Constitution v1.0; do not override without ADR)
> 2. **Product spec** — `docs/product/specs/thesisos-product-ux-v1.md` (IA, modules)
> 3. **This file** — UX patterns, typography guidance, checklists (ui-ux-pro-max intelligence)
> 4. **Page overrides** — `design-system/thesisos/pages/[page].md`

Generated from [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) on 2026-07-03,  
**adapted** for ThesisOS Research OS (not a marketing landing page).

---

## Product type

**Research Operating System** — knowledge workspace, academic writing, sources/concepts/decisions.  
Operator locale: Italian. Nav labels: English (ADR-0036).

---

## Color (frozen — use CSS tokens)

| Role | Token | Value |
|------|-------|-------|
| Background | `--color-bg` | `#fafaf9` |
| Surface | `--color-surface` | `#ffffff` |
| Ink | `--color-ink` | `#1c1917` |
| Muted | `--color-ink-muted` | `#57534e` |
| Accent | `--color-accent` | `#1e4d6b` |

Do **not** adopt uupm-generated palettes (teal/gold/black) — they conflict with PX1-EWO-002.

---

## Typography (PX-1 v1 → PX-6 polish)

| Phase | Choice |
|-------|--------|
| **PX-1…PX-3** | System UI stack (`--font-sans`) — ship without font CDN |
| **PX-6** | Crimson Pro (headings) + Atkinson Hyperlegible (body) — **ACTIVE** |

Mood: academic, readable, low cognitive friction. Max body line ~70ch.

---

## Style

**Soft workspace minimalism** — not Exaggerated Minimalism (fashion/editorial).  
Calm surfaces, clear hierarchy, one accent. AI panel secondary to content.

### Anti-patterns (Research OS)

- Chat-as-home, OR jargon in UI
- AI purple/pink gradients, emoji icons
- LLM-estimated progress (use deterministic formula — ADR-0040)
- Layout-shifting hover scales on dense lists
- Poor navigation / hiding Sources or Writing behind chat

---

## Pre-delivery checklist (ui-ux-pro-max)

- [ ] No emojis as icons — Lucide SVG
- [ ] `cursor-pointer` on clickable cards/links
- [ ] Hover: `transition-colors duration-200` (no layout shift)
- [ ] Text contrast ≥ 4.5:1 (`--color-ink` on `--color-surface`)
- [ ] Visible `:focus-visible` rings
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive: 375, 768, 1024, 1440px
- [ ] Internal nav: `next/link` not raw `<a>`

---

## Intelligence CLI (from repo root)

```bash
# Module-level design system suggestions (adapt, don't copy colors blindly)
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py \
  "<module keywords>" --design-system -p "ThesisOS" --format markdown

# UX / a11y / animation
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py "focus keyboard" --domain ux

# Stack (Next.js App Router)
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py "<topic>" --stack nextjs
```

Skill path: `.cursor/skills/ui-ux-pro-max/SKILL.md`

---

## Related

| Artifact | Role |
|----------|------|
| `docs/product/UX-ALIGNMENT-REVIEW.md` | Governance gate: Product → UX → UI |
| `design-system/thesisos/px2-research-workspace-ui-spec.md` | PX-2 UI spec (frozen at qualification) |
| `design-system/thesisos/px3-knowledge-experience-ui-spec.md` | PX-3 UI spec (**FROZEN**) |
| `design-system/thesisos/product-patterns.md` | Cross-milestone patterns (inspector rail, etc.) |
| `docs/product/PX-DESIGN-WORKFLOW.md` | ASEP PX EWO design pipeline |
| `docs/product/design-system-v1.md` | Frozen token spec |
| `.cursor/skills/impeccable/SKILL.md` | Craft, contrast, browser QA |
