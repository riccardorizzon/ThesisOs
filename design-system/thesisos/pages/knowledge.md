# Knowledge Module — Design Overrides (PX-3)

> **Status:** FROZEN — see full spec  
> **Product:** `docs/product/specs/px3-knowledge-experience-v2.md`  
> **UI:** `design-system/thesisos/px3-knowledge-experience-ui-spec.md`

---

## Routes

| Route | Screen |
|-------|--------|
| `/knowledge` | Knowledge Explorer |
| `/knowledge/[conceptSlug]` | Explain Page (signature) |
| `/knowledge/graph` | Knowledge Graph |
| `/knowledge/authors` | Author index |
| `/knowledge/authors/[authorSlug]` | Author page |
| `/knowledge/citations` | Citation index |

---

## Key layouts

- **Explorer:** filter rail 240px + featured concept + mode toggle + grid/list
- **Explain:** regions A–L; sticky header + action bar; local graph max 12 nodes
- **Graph:** toolbar + canvas (15 default) + preview 320px; List view fallback at 100

---

## Inspector

AI lateral overlay 320px (PP-1) — Explain remains visible.

---

## Copy locale

Italian operator content; English nav labels.
