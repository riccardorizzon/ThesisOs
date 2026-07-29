# M8 — Outline — Promotion

**Status:** **Proposed template** — fill gates after implementation + qualify.  
**Spec:** `docs/superpowers/specs/2026-07-29-thesisos-m8-outline-design.md` (**Proposed**).  
**ADR:** 0055 (Outline Tree & Publish) — Proposed until M8.0.

## Summary

M8 delivers thesis **outline tree management** over `chapters`: `GET`/`PUT /outline`, `ChapterService` move/reorder/reparent, `ChapterCreated` emission, explicit `published` status, and `/outline` UI — without GraphState changes or chapter RAG.

## Capability map (fill at ship)

| Capability | Milestone | Commit |
|------------|-----------|--------|
| Spec + ADR-0055 Accepted | M8.0 | _TBD_ |
| ChapterService tree ops | M8.1 | _TBD_ |
| `/outline` API | M8.2 | _TBD_ |
| `ChapterCreated` outbox | M8.3 | _TBD_ |
| Frontend outline | M8.4 | _TBD_ |
| Qualification + promotion | M8.5 | _TBD_ |

## Promotion gates

```yaml
adrs: proposed_pending_accept
tree_ops: pending                 # move/reorder/reparent + cycle reject
outline_get: pending
outline_put_ops: pending
optimistic_lock: pending
chapter_created_event: pending
published_transition: pending     # explicit only; approved not auto
chapters_api_regression: pending  # M6 /chapters green
content_md_omitted_from_outline: pending
outline_ui: pending
graphstate: unchanged
chapter_rag: false
m0_through_m7_tests: pending      # include grounding if promoted
scope_creep: false
documentation: pending
knowledge_updated: pending
```

Live:

```yaml
dogfood_outline_reorder: pending
dogfood_chapter_created: pending
m8_tag: pending                   # tag m8-complete
```

## Tags

| Tag | SHA | Meaning |
|-----|-----|---------|
| `m8-complete` | _TBD_ | Qualified Outline baseline |

## Explicit non-goals at promotion

- M7 grounding/citation work (separate milestone)
- Critic loop / auto-`approved` (M9)
- Chapter embeddings / outline semantic search
