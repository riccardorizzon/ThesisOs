# ThesisOS — M7 "Grounding Engine" Design Spec

- **Date:** 2026-07-29
- **Status:** **Proposed** — Architect freeze required before implementation (ADR-0001). Does **not** authorize code until Accepted + Critic sign-off.
- **Scope:** Milestone **M7 Grounding Engine** (Product Track) — Wave 1 delivers the **Citations** slice: resolve `CitationRef` → `sources`, persist `citations`, style render (APA7/MLA/Chicago), activate reserved `citation` route. Later M7.x waves (evidence / confidence / provenance hooks) are named here but **out of Wave 1 implementation**.
- **Naming (hard):** This is **not** ADR-0044 "M7 Product Hardening" (`v2.0.0-rc.2`). Documents, tags, and gates use **Grounding** / `m7-grounding-*` vocabulary.
- **Builds on:** M6 Writing Workspace (`m6-complete` / `m6-main`), M4 Retrieval, frozen `GraphState.citations` / `CitationRef`, `contracts/agents/citation.json`, `sources`/`citations` tables, ADR-0044 DB-backed sources + `/citations/validate` + BibTeX export (reuse, do not duplicate).
- **New ADRs (Proposed):** ADR-0053 (Citation Capability & Topology), ADR-0054 (Bibliography Styles).
- **Authors:** ThesisOS Builder Team

---

## 1. Vision

M7 makes writer citation markers **trustworthy and exportable**:

```text
Acquire (M3) → Index (M4) → Plan & Route (M5) → WRITE (M6)
  → CITE / GROUND (M7 Wave 1) → Outline (M8) / Critique (M9)
```

After Wave 1, a turn routed to `citation` resolves in-state `CitationRef`s against project `sources`, writes durable `citations` rows (via a Business service), and exposes styled bibliography (APA7 / MLA / Chicago). GraphState stays frozen.

**Success criterion (one sentence):** a `/chat` turn with `route=citation` runs the reserved citation path, resolves every `CitationRef.source_id` to a `sources` row (or records `unresolved_source`), persists citation rows for an optional chapter, and `GET /bibliography?style=` returns correctly styled entries — without changing `GraphState` and without regressing M0–M6 / ADR-0044 surfaces.

---

## 2. Objective, scope & non-goals

### 2.1 Objective

Deliver a **Citation capability** (port + node + route) and **bibliography style surface** as Wave 1 of the Grounding Engine, against frozen contracts, reusing ADR-0044 source inventory.

### 2.2 In scope — Wave 1 MUST ship

| # | Deliverable |
|---|-------------|
| 1 | **`CitationCapability` + `citation` node** — `resolve(brief) -> ResolvedCitations` (pure port); adapter maps → frozen `citations` + errors; contract `citation.json` |
| 2 | **Activate reserved `citation` route** — separate route (not chained after writer); typical path: `memory_context → (optional retriever) → citation_node → END` |
| 3 | **Resolve discipline** — `CitationRef.source_id` must match a project `sources.id` (or slug→id map defined in ADR-0053); else `unresolved_source` |
| 4 | **`CitationService`** — sole writer for `citations` table; optional `chapter_id` link; no writes from graph node body |
| 5 | **Style renderers** — APA7, MLA, Chicago from `sources.csl_json` + locator (ADR-0054) |
| 6 | **REST** — realize `POST /citations`, `GET /bibliography?style=`; align OpenAPI (un-deprecate or clearly supersede legacy stubs); keep `/citations/validate` and BibTeX export as complementary surfaces |
| 7 | **Qualification + promotion** — `qualify-m7-grounding` / dogfood + `docs/m7-grounding-promotion.md` + tag `m7-grounding-complete` |

### 2.3 Deferred — M7.x (named, not Wave 1)

| Deferred | Wave |
|----------|------|
| Evidence / claim–span linking beyond citation markers | M7.x |
| Confidence scores on grounding decisions | M7.x |
| Full provenance DAG / traceability UI | M7.x |
| Auto-chain `writer → citation` on every draft turn | later (own decision) |

### 2.4 Non-goals (hard boundary)

| Forbidden in M7 Grounding Wave 1 | Deferred to |
|----------------------------------|---------------|
| Outline tree ops, `/outline`, `ChapterCreated` | M8 |
| Critic / revise loop, `CritiqueCompleted`, auto-`approved` | M9 |
| New / changed `GraphState` fields | Frozen (ADR-0007) |
| Duplicate source catalog / replace ADR-0044 inventory | — |
| Engineering Runtime / builder_engine changes | Platform Track |
| Confusing this milestone with Product Hardening M7 | — |

```yaml
outline_management: false
critic_loop: false
graphstate_change: false
writer_citation_autochain: false
product_hardening_scope: false
```

---

## 3. Architecture

### 3.1 Topology (Wave 1)

Additive route only (Constitution C6 — existing routes byte-stable):

```text
START → supervisor → planner → router → memory_context → [route_after_router]
  ├─ … existing M5/M6 routes unchanged …
  └─ route=citation ──► citation_node ──► END     (M7 Wave 1, NEW)
```

**Decision (locked):** `citation` is a **separate router-selected route**, not an automatic edge after `writer`. The node reads existing `draft` + `citations` from GraphState (checkpoint / prior turn).

### 3.2 Capability port (ADR-0053)

```text
CitationCapability:  async resolve(brief: CitationBrief) -> ResolvedCitations

CitationBrief:   draft, citations (CitationRef[]), project_id, allowed_source_ids?
ResolvedCitations:
  citations: list[CitationRef]   # resolved / normalized
  unresolved: list[str]          # source_ids that failed
  rendered: dict[str, str] | None  # optional style→string for stream metadata
```

- Node adapter maps to `{citations, errors}` only — never imports DB/Event Bus.
- Persistence: REST/`CitationService` (or composition-root hook), mirroring Writer/Chapter split (ADR-0031/0032).

### 3.3 Reuse of ADR-0044 surfaces

| Surface | M7 Wave 1 stance |
|---------|------------------|
| `sources` table (CSL-JSON, slug, project_id) | **System of record** for resolution |
| `GET …/sources`, bibliography BibTeX export | Keep; bibliography styles add APA/MLA/Chicago text/HTML (or plain) via `/bibliography` |
| `POST /citations/validate` | Keep; citation resolve must be consistent with validate rules |

### 3.4 Data

- **Read:** `sources` (by id/slug within `project_id`)
- **Write:** `citations` (`source_id`, optional `chapter_id`, `locator`, prefix/suffix)
- **No migration required** if schema already matches `contracts/db/schema.sql` (verify at M7.0); additive columns only if Critic/Architect require

---

## 4. API & contracts

| Contract | Action |
|----------|--------|
| `contracts/agents/citation.json` | Authoritative — reads `draft,citations`; writes `citations`; error `unresolved_source` |
| OpenAPI `/citations` POST | **LOCKED:** un-deprecate and realize (replace 501); request includes refs + optional `chapter_id` / `project_id` |
| OpenAPI `/bibliography` GET | **LOCKED:** un-deprecate and realize `?style=apa7\|mla\|chicago` (+ `project_id`); BibTeX export path stays complementary (ADR-0044) |
| Events | No new product event required for Wave 1 |

---

## 5. Internal milestones

| Sub | Name | Output |
|-----|------|--------|
| **M7.0** | Spec + ADRs Accepted | this spec + ADR-0053/0054 Accepted, Critic sign-off |
| **M7.1** | Citation capability + node (unwired) | port + fake-LLM/unit tests |
| **M7.2** | Route wiring | `citation` route + instrumentation |
| **M7.3** | CitationService + styles + REST | persist + APA/MLA/Chicago + OpenAPI |
| **M7.4** | Qualification | qualify + dogfood + style fixture suite |
| **M7.5** | Promotion | `docs/m7-grounding-promotion.md`, knowledge mirror, tag `m7-grounding-complete` |

---

## 6. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Naming collision with Product Hardening M7 | Explicit vocabulary in every doc; separate promotion doc/tag |
| `source_id` vs slug mismatch from writer | ADR-0053 defines resolution map; tests for both |
| Scope creep into evidence/confidence | Hard deferral table §2.3 |
| Regressing validate/BibTeX | Contract tests that ADR-0044 paths stay green |
| Style fidelity (CSL subset) | ADR-0054 freezes supported field subset; golden fixtures |

---

## 7. Critic checklist (pre-implementation)

- [ ] No GraphState field added
- [ ] No automatic writer→citation edge in Wave 1
- [ ] `CitationService` sole writer for `citations`
- [ ] ADR-0044 sources/validate/BibTeX reused, not forked
- [ ] M8/M9 surfaces untouched
- [ ] Status remains Proposed until Architect Accepts

---

## 8. References

- `knowledge/project/roadmap.md` (M7 Grounding Engine)
- `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md`
- `decisions/ADR-0027`, `ADR-0031`, `ADR-0044`, Proposed `ADR-0053`, `ADR-0054`
- `contracts/agents/citation.json` · `contracts/db/schema.sql` (`sources`, `citations`)
- `docs/m7-grounding-promotion.md`
- Format reference: M6 design spec
