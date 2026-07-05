# Design System v1 — ThesisOS Product

> **PX1-EWO-002** · Status: **Active** (PX-1 Foundation)  
> Layer: Business (Product Plane) · ADR-0034 Research OS positioning

---

## Principles

- **Minimal cognitive friction** — calm surfaces, one accent, clear hierarchy
- **Research workspace** — paper-like neutrals, ink-blue accent (not chat-app purple)
- **Template-neutral** — no thesis-specific chrome; project content fills modules
- **System fonts v1** — no custom font loading until PX-6 polish

---

## Color tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#fafaf9` | Page background |
| `--color-surface` | `#ffffff` | Cards, active nav, panels |
| `--color-surface-muted` | `#f5f5f4` | Sidebar, secondary panels |
| `--color-border` | `#e7e5e4` | Dividers, card borders |
| `--color-border-strong` | `#d6d3d1` | Emphasized borders |
| `--color-ink` | `#1c1917` | Primary text |
| `--color-ink-muted` | `#57534e` | Secondary text |
| `--color-ink-subtle` | `#78716c` | Labels, meta |
| `--color-accent` | `#1e4d6b` | Links, progress ring, focus |
| `--color-accent-subtle` | `#e8f0f5` | Accent backgrounds |
| `--color-success` | `#166534` | Approved status |
| `--color-warning` | `#a16207` | Review / pending |
| `--color-danger` | `#b91c1c` | Errors, blocked |

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
