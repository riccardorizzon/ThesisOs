# M7 — Grounding Engine (Wave 1 Citations) — Promotion

**Status:** **Proposed template** — fill gates to `green` only after implementation + qualify.  
**Branch:** _(TBD at M7.0 freeze)_  
**Spec:** `docs/superpowers/specs/2026-07-29-thesisos-m7-grounding-engine-design.md` (**Proposed** → must be Frozen/Accepted before code).  
**ADRs:** 0053 (Citation Capability & Topology), 0054 (Bibliography Styles) — Proposed until M7.0.  
**Naming:** Product Track **M7 Grounding Engine** — distinct from ADR-0044 Product Hardening.

## Summary

M7 Wave 1 adds a **Citation capability** and activates the reserved ADR-0027 `citation` route so `CitationRef` markers resolve against project `sources`, persist via `CitationService`, and render APA7/MLA/Chicago bibliographies — **without** GraphState changes and without regressing ADR-0044 validate/BibTeX surfaces.

## Capability map (fill at ship)

| Capability | Milestone | Commit |
|------------|-----------|--------|
| Spec + ADR-0053/0054 Accepted | M7.0 | _TBD_ |
| Citation capability + node (unwired) | M7.1 | _TBD_ |
| Citation route wiring | M7.2 | _TBD_ |
| CitationService + styles + REST | M7.3 | _TBD_ |
| Qualification | M7.4 | _TBD_ |
| Promotion | M7.5 | _TBD_ |

## Promotion gates

Deterministic gates (target — all must be `green` before tag):

```yaml
adrs: proposed_pending_accept   # → accepted at M7.0
citation_capability: pending
citation_isolation: pending       # no db/runtime imports in capability
citation_node: pending            # maps to citations/errors only
citation_route: pending           # separate route; no writer autchain
existing_routes_unchanged: pending
resolve_discipline: pending       # unresolved_source + id/slug map
citation_service_sole_writer: pending
styles_apa7: pending
styles_mla: pending
styles_chicago: pending
bibliography_api: pending
citations_api: pending
validate_bibtex_reuse: pending    # ADR-0044 paths still green
graphstate: unchanged
m0_through_m6_tests: pending
scope_creep: false                # no outline/critic/evidence Wave-1
documentation: pending
knowledge_updated: pending
```

Live stack gates (after `make up` + ADC):

```yaml
dogfood_citation_resolve: pending
dogfood_bibliography_styles: pending
benchmarks_recorded: pending      # optional B_cite smoke
m7_grounding_tag: pending         # tag m7-grounding-complete
```

## Tags (apply only after gates green)

| Tag | SHA | Meaning |
|-----|-----|---------|
| `m7-grounding-complete` | _TBD_ | Qualified Wave 1 baseline (**immutable**) |

## Explicit non-goals at promotion

- Evidence/confidence/provenance UI (M7.x)
- `/outline`, `ChapterCreated` (M8)
- Critic loop / `CritiqueCompleted` (M9)
- Claiming identity with Product Hardening M7 / `v2.0.0-rc.2`
