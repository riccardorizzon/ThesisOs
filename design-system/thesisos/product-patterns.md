# ThesisOS Product Patterns

> **Status:** ACTIVE · Cross-milestone · **Owner:** UX & Design System Lead  
> **Precedence:** Product specs define *when*; this document defines *how* (visual/interaction)

Recurring patterns promoted from PX-2/PX-3 UX work. Engineering implements via shared components.

---

## PP-1 — Inspector rail (320px)

| Property | Value |
|----------|-------|
| Width | `--rail-width` (20rem / 320px) |
| Collapse | `⌘\` |
| Background | `bg-surface-muted` |
| Tabs | Underline active indicator 2px accent |

**Used in:** Writing right rail (PX-2), Source reader inspector (PX-3), Explain AI overlay (PX-3), Graph preview panel (PX-3).

---

## PP-2 — ContextBar (live)

Persistent scope strip; counts from Context Packet. Warning amber for binding decisions.

**PX-3 delta:** concept count chip → Explain Page when selection overlaps concept.

---

## PP-3 — No silent writes

AI **Applica**, import, annotation link, concept merge → proposal queue → atomic or explicit approve.

---

## PP-4 — Knowledge Object envelope

All PX-3 entities share: title, subtitle, summary, lifecycle badge, confidence chip, link counts, provenance.

Type-specific pages render specializations (§3 product spec).

---

## PP-5 — Lifecycle badges

`Candidato · Validato · Collegato · Citato in tesi · Deprecato` — unified across Explorer, cards, graph nodes.

Maps to corpus `candidata/approvata/esclusa` where applicable (§4.3 product spec).

---

## PP-6 — Session continuity

Restore: scroll, panel tab, trail, graph focus, last-read source. Arc-style “continue where you left off.”

---

## PP-7 — Command palette discovery

`⌘K` groups: Vai a… · Concetti · Fonti · Azioni. Shortcuts never override browser defaults without workspace focus.

---

## PP-8 — Empty / loading / error tone

Italian plain language; inviting empty states; skeleton without blocking primary interaction; no stack traces.

---

## PP-9 — Explain Page as concept canonical view

KR-13: one canonical concept detail — `/knowledge/[conceptSlug]`. No duplicate concept surfaces elsewhere.

---

## PP-10 — Bounded graph (PX-3)

Default 15 nodes, 1-hop; hard limit 100 with List view fallback (KR-12). PX-5 canvas is separate milestone.

---

## WO-TRACE

```text
PX-2 UI spec + PX-3 UI spec → product-patterns.md
```
