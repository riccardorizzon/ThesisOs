# Home Page — Design Overrides (PX1-EWO-003 · PX-2 delta)

> **Page:** `/` (Home)  
> **Spec:** `docs/product/specs/thesisos-product-ux-v1.md` §5.1 · PX-2: `px2-research-workspace-experience.md` §6.4  
> **UI spec:** `design-system/thesisos/px2-research-workspace-ui-spec.md` §7  
> Overrides `design-system/thesisos/MASTER.md` for this page only.

---

## Purpose

Invite work — not administer. No OR-7 jargon.

---

## Layout (not landing-page hero)

```text
┌─────────────────────────────────────────────────────────┐
│  ProgressRing + phase label          [ Continua → ]     │
├─────────────────────────────────────────────────────────┤
│  Quick actions: Ricerca · Scrittura · Revisione · Import  │
├─────────────────────────────────────────────────────────┤
│  Recent activity (EntityCard list)                      │
└─────────────────────────────────────────────────────────┘
```

- **Max width:** `var(--content-max-width)` (72rem)
- **No** centered marketing hero, no single giant CTA
- Progress: **deterministic stub** until chapters API wired (ADR-0040 INV-PS-1)

---

## Components

| Block | Component |
|-------|-----------|
| Progress | `ProgressRing` |
| Continue | Link → last writing chapter (stub `/writing` until activity API) |
| Quick actions | 4 action links (Research, Writing, revision flow, import) |
| Activity | `EntityCard` × N placeholders |

---

## Copy (Italian operator)

| Element | Text |
|---------|------|
| Progress label | Avanzamento tesi |
| Continue | Continua |
| Quick: research | Ricerca |
| Quick: writing | Scrittura |
| Quick: review | Revisione |
| Quick: import | Importa documento |

---

## uupm queries used

```bash
python3 .cursor/skills/ui-ux-pro-max/scripts/search.py \
  "research workspace home dashboard progress continue actions" \
  --design-system -p "ThesisOS" --format markdown

python3 .cursor/skills/ui-ux-pro-max/scripts/search.py \
  "dashboard card list layout" --stack nextjs
```

---

## PX-2 delta

| Element | Change |
|---------|--------|
| Continua | Deep link restores chapter, section, panel tab, peeked source |
| Progress ring | Live from chapter statuses (ADR-0040) |
| Activity cards | Proposal types: Aggiornamento proposto, Decisione vincolante, Nuova fonte, Chiudi sessione |
| Sidebar badge | Home nav shows pending proposal count when > 0 |
| Revisione quick action | → `/review` |

**Continua** remains primary CTA (`bg-accent`); sr-only sublabel includes chapter + section.

---

## Pre-delivery (Home-specific)

- [x] `/` renders Home — **not** redirect to `/chat` (ADR-0036 INV-IA-2)
- [x] ProgressRing shows numeric % from stub formula
- [x] All action targets use `Link`
- [x] Empty activity state with invitation to act (not blank)
- [ ] PX-2: Continua restores full session state (AC-9)
- [ ] PX-2: Activity cards reflect live proposals
