# Sources Module — Design Overrides (PX-3 enrichment)

> **Status:** FROZEN — see full spec  
> **PX-2:** peek, cite, lightweight search (frozen)  
> **PX-3:** `docs/product/specs/px3-knowledge-experience-v2.md` §12–15  
> **UI:** `design-system/thesisos/px3-knowledge-experience-ui-spec.md` §5.4–5.5, §7

---

## Layout

```text
ContextBar (when ?chapter= context present)
┌─────────────────────────────────────────────────────────────┐
│ Search + filter chips (candidata / approvata / esclusa)     │
├─────────────────────────────────────────────────────────────┤
│ EntityCard grid (2–3 cols @ 1440px)                         │
└─────────────────────────────────────────────────────────────┘
```

Detail route: reader layout — metadata strip + body + action bar.

---

## Source card

| Field | Style |
|-------|-------|
| Title | `text-sm font-medium` |
| Author · year | `text-xs text-ink-muted` |
| Status | `StatusBadge` |
| Tags | Chip row, read-only |

Excluded: visible in list with `Esclusa` badge; card not dimmed but cite actions disabled in detail.

---

## Reader

| Zone | Spec |
|------|------|
| Metadata | Author, year, status, tags — `border-b`, `py-3` |
| Body | Prose `max-w-[65ch]` |
| Actions | Cita · Collega capitolo · Apri in Writing |
| Nav | Prev/Next when from search results |

Excluded reader: callout `border-danger/20 bg-danger/5` with plain-language reason; Cita disabled.

---

## Sticky return chip

When URL carries chapter context:

`fixed bottom-6 right-6` pill — "Torna a Scrittura" → `/writing/[chapterId]` preserving state.

---

## Empty / loading

| State | Pattern |
|-------|---------|
| No results | "Nessuna fonte trovata" + Modifica ricerca |
| Loading | Top progress bar; metadata then body stagger |
| Search | 200ms debounce, inline spinner in field |

---

## Components

| Block | Component |
|-------|-----------|
| Grid | `EntityCard` |
| Reader | `SourceReader` |
| Picker | `SourcePicker` (modal, shared with Writing) |
| Status | `StatusBadge` |
