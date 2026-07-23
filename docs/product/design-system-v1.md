# Design System v1 — ThesisOS Product

> **PX1-EWO-002** · Status: **Active** (PX-1 Foundation)  
> Layer: Business (Product Plane) · ADR-0034 Research OS positioning

---

## Principles

- **Minimal cognitive friction** — calm surfaces, one accent, clear hierarchy
- **Research workspace** — dark neutral surfaces (Cursor-like), green accent (not chat-app purple)
- **Template-neutral** — no thesis-specific chrome; project content fills modules
- **System fonts v1** — no custom font loading until PX-6 polish

---

## Color tokens

Dark theme. Tokens are stored as space-separated RGB channels (e.g. `20 20 20`)
so Tailwind opacity modifiers work (`bg-warning/10` → `rgb(var(--color-warning) / 0.1)`).

| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#141414` | Page background |
| `--color-surface` | `#1c1c1c` | Cards, active nav, panels |
| `--color-surface-muted` | `#232323` | Sidebar, secondary panels |
| `--color-border` | `#2e2e2e` | Dividers, card borders |
| `--color-border-strong` | `#4d4d4d` | Emphasized borders |
| `--color-ink` | `#ededed` | Primary text |
| `--color-ink-muted` | `#a8a8a8` | Secondary text |
| `--color-ink-subtle` | `#8c8c8c` | Labels, meta |
| `--color-ink-inverse` | `#0f1210` | Text on solid accent/status fills |
| `--color-accent` | `#2ea043` | Links, primary buttons, focus |
| `--color-accent-muted` | `#3bb54f` | Hover on primary buttons |
| `--color-accent-subtle` | `#16281b` | Accent-tinted backgrounds |
| `--color-accent-ring` | `#46c55a` | Focus ring, progress ring |
| `--color-success` | `#3fb950` | Approved status |
| `--color-warning` | `#d29922` | Review / pending |
| `--color-danger` | `#f85149` | Errors, blocked |

Contrast rules (verified WCAG AA):

- All ink tones hit ≥4.5:1 on every surface tone.
- `text-accent` / status text hit ≥4.5:1 on `bg`, `surface`, and their own `/10` tints.
- Solid accent/status fills (buttons, badges) use `text-ink-inverse` (dark label),
  **not** `text-white` — white fails AA on the green/amber/red fills.

Source: `frontend/styles/tokens.css`

---

## Typography tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--font-sans` | system UI stack | All UI copy |
| `--font-mono` | monospace stack | Code, IDs |
| `--text-xs` … `--text-2xl` | 0.75–1.5 rem | Type scale |
| `--weight-normal/medium/semibold` | 400/500/600 | Emphasis |

Tailwind mapping: `text-xs` … `text-2xl`, `font-medium`, `font-semibold`

---

## Spacing tokens

| Token | Value |
|-------|-------|
| `--space-1` | 0.25rem |
| `--space-2` | 0.5rem |
| `--space-3` | 0.75rem |
| `--space-4` | 1rem |
| `--space-6` | 1.5rem |
| `--space-8` | 2rem |

Layout: `--sidebar-width` (13rem), `--panel-width` (20rem), `--content-max-width` (72rem)

**PX-2 workspace tokens** (see `px2-research-workspace-ui-spec.md`):

| Token | Value |
|-------|-------|
| `--outline-width` | 15rem (240px) |
| `--rail-width` | 20rem (320px) |
| `--editor-min-width` | 30rem (480px) |

---

## Radius & shadow

| Token | Value |
|-------|-------|
| `--radius-sm/md/lg` | 0.375 / 0.5 / 0.75 rem |
| `--shadow-sm/md` | subtle elevation |

---

## Core components (PX-1)

| Component | Path | Role |
|-----------|------|------|
| **AppShell** | `frontend/components/AppShell.tsx` | Sidebar + main + optional right panel |
| **ProgressRing** | `frontend/components/ProgressRing.tsx` | Home deterministic progress (ADR-0040) |
| **EntityCard** | `frontend/components/EntityCard.tsx` | Entity summary stub (sources, chapters, concepts) |

---

## Usage

```tsx
import { ProgressRing } from "@/components/ProgressRing";
import { EntityCard } from "@/components/EntityCard";

<ProgressRing value={42} label="Avanzamento" sublabel="Capitoli approvati" />
<EntityCard entityType="chapter" title="Cap. 1" subtitle="Introduzione" href="/writing/1" />
```

Semantic Tailwind classes: `bg-bg`, `bg-surface`, `text-ink`, `text-ink-muted`, `border-border`, `text-accent`, `bg-accent-subtle`.

---

## Design intelligence (PX EWOs)

For Home, Writing, Sources, and later PX milestones, follow:

- **Workflow:** `docs/product/PX-DESIGN-WORKFLOW.md`
- **ui-ux-pro-max:** `.cursor/skills/ui-ux-pro-max/` (CLI design system + UX checklist)
- **Page overrides:** `design-system/thesisos/pages/`
- **Master (adapted):** `design-system/thesisos/MASTER.md`

Frozen tokens in this document **override** ui-ux-pro-max color suggestions.

---

## WO-TRACE

```text
PX1-EWO-002 → design-system-v1.md + tokens.css → PX1-EWO-003 Home
```
