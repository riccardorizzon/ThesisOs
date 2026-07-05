# Review Workspace — Design Overrides (PX-2)

> **Route:** `/review`  
> **Product spec:** `docs/product/specs/px2-research-workspace-experience.md` §8  
> **UI spec:** `design-system/thesisos/px2-research-workspace-ui-spec.md` §6.6, §9

---

## Layout

```text
ContextBar
┌─────────────────────────────────────────────────────────────┐
│ Chapter / section selector                                  │
├────────────────────────────┬────────────────────────────────┤
│ Originale (read-only)      │ Proposta                       │
├────────────────────────────┴────────────────────────────────┤
│ Action bar: Accetta · Accetta parziale · Rifiuta · Modifica │
├─────────────────────────────────────────────────────────────┤
│ Revision history (last 5) — collapsible sidebar or footer   │
└─────────────────────────────────────────────────────────────┘
```

Not a three-panel Writing layout. Full-width compare workspace.

---

## Diff styling

| Change type | Style |
|-------------|-------|
| Addition | `bg-success/10` |
| Removal | `bg-danger/10 line-through` |
| Selection hunk | `ring-2 ring-accent` |

AI proposals labeled "Proposta AI" in meta strip.

---

## Actions

| Button | Variant | Behavior |
|--------|---------|----------|
| Accetta | primary accent | Confirm → persist |
| Accetta parziale | secondary | Requires hunk selection |
| Rifiuta | ghost danger | Confirm → discard proposal |
| Modifica | ghost | Return to Writing with proposal |

---

## Empty state

"Nessuna revisione in sospeso" — CTA "Avvia revisione" → chapter selector or `/writing`.

---

## Entry points

| From | URL |
|------|-----|
| Home Revisione | `/review` |
| Writing AI / rail | `/review?chapter=[id]` |
| Outline menu | Status → In revisione + optional `/review?chapter=` |

---

## Components

| Block | Component |
|-------|-----------|
| Compare | `ReviewCompare` |
| Selector | `ChapterSectionSelect` |
| History | `RevisionHistoryList` |
