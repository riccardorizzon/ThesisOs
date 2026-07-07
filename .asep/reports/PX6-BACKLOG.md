# PX-6 — Polish Milestone Backlog

> **Authority:** ASEP design session  
> **Date:** 2026-07-07  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-6 Polish  
> **Authorization:** `.asep/reports/PX6-AUTHORIZATION-20260707.md`  
> **Status:** **DESIGN** — not registered in program yaml until Architect review

---

## Functional objective (PX-6)

Close the **Product v2.0** promise — turn deferred platform limitations and UX gaps
into production-ready polish across Writing, Sources, Knowledge, Research, and Settings.

**Product thesis** (`thesisos-product-ux-v1.md` §10):

```text
PX-5 = Research  →  How do I explore the landscape? (spatial canvas)
PX-6 = Polish      →  Is the thesis workflow production-ready?
```

PX-6 is the **terminal milestone** of `thesisos-product-v2`. Success = QWO-PX6-001 PASS
+ `px6-complete` tag + Product v2.0 release candidate.

---

## Authoritative sources (not agent-invented)

| Artifact | Role |
|----------|------|
| `docs/product/specs/thesisos-product-ux-v1.md` | §10 milestone map; W-06 note §12 |
| `docs/product/specs/px2-research-workspace-experience-v2.md` | §26 W-06; outline reorder §12 |
| `docs/product/specs/px3-knowledge-experience-v2.md` | §13.5–13.6 bibliography + W-06 flags |
| `docs/product/specs/px5-research-experience-v1.md` | §15 exclusions → PX-6 owners |
| `docs/KNOWN_LIMITATIONS.md` | W-06 Platform Limitation — mitigation architecture |
| `docs/asep-capability-model.md` | §4E Platform Limitation vs Capability Failure |
| `design-system/thesisos/MASTER.md` | PX-6 typography candidate |
| `frontend/lib/projectContext.ts` | ADR-0040 `project_id` scaffolding |
| `frontend/components/navigation/ProjectSwitcher.tsx` | Disabled stub — activate in PX-6 |
| `docs/px5-promotion.md` | Post-promotion deferred scope |
| `decisions/ADR-0039-ai-interaction-model.md` | Modes/actions — not separate agents |

**Deferred to post-v2 / out of scope:** real-time collaboration, collaborative
annotations, full PDF parse pipeline, MB2 runtime internals, LLM model replacement,
separate Reviewer/Planner agent topology (requires Product ADR supersession).

---

## Capability map

| ID | Capability | Primary surfaces | Wave |
|----|------------|------------------|------|
| **PX-6.1** | Citation format validator (W-06 mitigation) | Writing, Sources, AI proposals | B |
| **PX-6.2** | Bibliography export + print | Sources Bibliografia | C |
| **PX-6.3** | Multi-project switch + isolation | AppShell, all modules | D |
| **PX-6.4** | Outline drag reorder | Writing outline | E |
| **PX-6.5** | Settings depth | `/settings` | E |
| **PX-6.6** | Typography + visual polish | Global design tokens | E |
| **PX-6.7** | Cross-surface performance pass | Canvas, Writing, Knowledge | E |

---

## W-06 mitigation architecture (design decision)

**Problem:** OR-6 qualified PASS\* with W-06 as Platform Limitation — residual numeric
`[n]` cites may appear in LLM output despite inference enforcement
(`docs/KNOWN_LIMITATIONS.md` §2).

**PX-6 approach — product validation layer (mitigation #2):**

| Layer | PX-6 responsibility | Still NOT guaranteed |
|-------|---------------------|----------------------|
| Detection | Deterministic rules flag numeric bracket cites in editor, proposals, pasted text | — |
| Metadata assist | Suggest `(Author, YYYY)` from linked source record when available | — |
| Gating | Optional block on **Applica** for AI proposals with unresolved invalid cites | LLM always emits author-date |
| Messaging | Replace "validatore in arrivo" stubs with live validator status | Oracle W-06 re-proof |
| Documentation | Amend KNOWN_LIMITATIONS §2 → **partially mitigated** (engineering change) | Model replacement |

**Classification:** Product mitigation — not a thesis-agent OR-6 oracle re-run. Do not
claim deterministic author-date in UI copy. Preserve PASS\* disposition.

**Forbidden:** Prompt-only iteration on writer route as sole W-06 fix.

---

## Milestone DAG (all waves)

```text
PX-5 PROMOTED (px5-complete)
      ↓
PX6-EWO-001  Polish Experience Spec + UX foundation     Wave A
      ↓
PX6-EWO-002  Citation validation engine (rules + API)   Wave B
      ↓
PX6-EWO-003  Writing + AI proposal validator UI         Wave B
      ↓
PX6-EWO-004  Sources/Knowledge flags + W-06 doc sync    Wave B
      ↓
PX6-INTEGRATION-A  Validator cross-surface review
      ↓
      ├────────────────────────┬────────────────────────┐
      ▼                        ▼                        │
PX6-EWO-005              PX6-EWO-007                     │  parallel
Export API + UI          Projects API + switcher          │  after INT-A
      │                        │                        │
      └────────────────────────┴────────────────────────┘
                               ↓
PX6-INTEGRATION-B  Export + multi-project merge review
      ↓
      ├──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              │
PX6-EWO-009    PX6-EWO-010    PX6-EWO-011          │  parallel
Outline reorder Settings depth Typography polish    │
      └──────────────┴──────────────┴──────────────┘
                               ↓
PX6-EWO-012  Performance audit + targeted fixes      Wave E
      ↓
PX6-INTEGRATION-C  Final milestone merge review
      ↓
QWO-PX6-001  Milestone qualification
      ↓
PX6-EWO-013  Milestone promotion (px6-complete)
```

**First executable EWO:** `PX6-EWO-001` (spec-only; no code).

**Parallel dispatch:**

- **PX6-EWO-005** (export) and **PX6-EWO-007** (multi-project) after PX6-INTEGRATION-A
- **PX6-EWO-009**, **010**, **011** after PX6-INTEGRATION-B

---

## Wave summaries

### Wave A — Spec foundation

Establish normative PX-6 product spec and UI spec before any implementation.

| EWO | Title | Depends on |
|-----|-------|------------|
| **PX6-EWO-001** | Polish Experience Spec + UX foundation | PX-5 promoted |

**Exit:** Product spec ratified; boundary matrix signed; UI spec draft; proposal PASS.

---

### Wave B — Citation validator (W-06 mitigation)

| EWO | Title | Category | Depends on |
|-----|-------|----------|------------|
| **PX6-EWO-002** | Citation validation engine | Grounding | PX6-EWO-001 |
| **PX6-EWO-003** | Writing + AI proposal validator UI | Alignment | PX6-EWO-002 |
| **PX6-EWO-004** | Sources/Knowledge flags + limitations sync | Alignment | PX6-EWO-002 |
| **PX6-INTEGRATION-A** | Validator cross-surface review | Release | EWO-002…004 |

**PX6-EWO-002 deliverables:**

- `backend/app/services/citation/validation.py` — deterministic rules
- `GET /citations/validate` or validate-on-save hook
- Rules: numeric `[n]` → `invalid_numeric`; `(Author, YYYY)` → `valid`; cite markers from PX-2 flow → `valid_linked`
- Unit tests with px2 §26 exemplar strings

**PX6-EWO-003 deliverables:**

- Inline highlights in `MarkdownEditor` for invalid cites
- AI proposal preview: flag before Applica; optional hard block
- Verify action copy per px2 §26 (upgrade from stub)
- Remove "validatore in arrivo" footer where validator active

**PX6-EWO-004 deliverables:**

- Sources Bibliografia + Knowledge citation index: `Da verificare` badge wired to engine
- `docs/KNOWN_LIMITATIONS.md` §2 partial mitigation amendment (authorized doc change)
- Regression: PX-2 cite flow, PX-3 flags preserved

**Integration-A exit:** AC-1…AC-4 (see QWO draft §16); `make ci` green.

---

### Wave C — Export / print

| EWO | Title | Category | Depends on |
|-----|-------|----------|------------|
| **PX6-EWO-005** | Bibliography export API + UI | Alignment | PX6-INTEGRATION-A |
| **PX6-EWO-006** | Print stylesheet + export dialog polish | Infrastructure | PX6-EWO-005 |

**PX6-EWO-005 deliverables:**

- `GET /sources/bibliography/export?format=bibtex|ris` (approved sources only, academic order per px3 §13.5)
- Sources **Bibliografia** tab: Export button + format picker
- Filename: `{project_id}-bibliografia.{ext}`

**PX6-EWO-006 deliverables:**

- Print-friendly CSS for bibliography view
- Optional "Stampa bibliografia" action
- Empty-state when no approved sources

---

### Wave D — Multi-project

| EWO | Title | Category | Depends on |
|-----|-------|----------|------------|
| **PX6-EWO-007** | Projects domain + API | Grounding | PX6-INTEGRATION-A |
| **PX6-EWO-008** | Project switcher + context isolation | Infrastructure | PX6-EWO-007 |
| **PX6-INTEGRATION-B** | Export + multi-project merge review | Release | EWO-005…008 |

**PX6-EWO-007 deliverables:**

- `projects` table or extend existing model; CRUD list/create (min: list + switch)
- `GET /projects`, `POST /projects` (create blank thesis project from template)
- Default `thesis-agent` preserved; no data migration required for single-project users

**PX6-EWO-008 deliverables:**

- Activate `ProjectSwitcher` — dropdown of projects, persist selection (`localStorage` + session)
- Wire `resolveProjectContext()` to active project across Home, Writing, Sources, Knowledge, Research
- Knowledge isolation regression: concepts scoped by `project_id` (INV-KM-2)
- Session continuity (PX2-EWO-006) scoped per project

**Integration-B exit:** Switch project → isolated corpus; export respects active project; AC-5…AC-7.

---

### Wave E — UX polish

| EWO | Title | Category | Depends on |
|-----|-------|----------|------------|
| **PX6-EWO-009** | Outline drag reorder | Alignment | PX6-INTEGRATION-B |
| **PX6-EWO-010** | Settings depth | Alignment | PX6-INTEGRATION-B |
| **PX6-EWO-011** | Typography + visual polish | Infrastructure | PX6-INTEGRATION-B |
| **PX6-EWO-012** | Performance audit + fixes | Infrastructure | EWO-009…011 |
| **PX6-INTEGRATION-C** | Final merge review | Release | EWO-012 |

**PX6-EWO-009:** Drag-drop chapter reorder in `WritingOutline`; `PATCH /chapters/reorder`;
preserve PX-2 status lifecycle on reorder.

**PX6-EWO-010:** Replace Settings stub — project display name, citation style preference,
export defaults, keyboard shortcuts link; sections per product §10 "settings depth".

**PX6-EWO-011:** Load Crimson Pro + Atkinson Hyperlegible via `next/font`; update
`MASTER.md` status; audit contrast and line-length; no uupm palette override.

**PX6-EWO-012:** Bundle audit; lazy-load heavy Research canvas chunk; viewport culling
regression; document perf budget in spec.

---

### Wave F — Qualification + promotion

| EWO | Title | Depends on |
|-----|-------|------------|
| **QWO-PX6-001** | Milestone qualification | PX6-INTEGRATION-C |
| **PX6-EWO-013** | Milestone promotion | QWO-PX6-001 PASS |

---

## Boundary matrix (mandatory in spec)

| Capability | Owner | Route / surface |
|------------|-------|-----------------|
| Cite picker + markers | PX-2 | Writing editor |
| Citation index + flags (stub) | PX-3 | Sources, Knowledge |
| Concept model + graph | PX-4 | `/knowledge/*` |
| Research canvas | PX-5 | `/research/canvas` |
| **Citation validator (full)** | **PX-6** | Writing, Sources, proposals |
| **Bibliography export** | **PX-6** | Sources Bibliografia |
| **Multi-project switch** | **PX-6** | AppShell `ProjectSwitcher` |
| **Outline reorder** | **PX-6** | Writing outline |
| **Settings depth** | **PX-6** | `/settings` |
| OR-6 inference enforcement | thesis-agent | Runtime graph — read-only |
| MB2 Program Trace | px-exec | Not PX-6 |

---

## QWO-PX6-001 acceptance criteria (draft)

| # | Criterion |
|---|-----------|
| AC-1 | Validator flags numeric `[n]` in editor; suggests author-date when source linked |
| AC-2 | AI proposal with invalid cite blocked or requires explicit override before Applica |
| AC-3 | Sources Bibliografia export produces valid BibTeX for approved sources |
| AC-4 | KNOWN_LIMITATIONS §2 documents partial W-06 mitigation |
| AC-5 | Project switcher lists ≥2 projects; active project scopes API calls |
| AC-6 | Switching project shows isolated concepts/sources (no cross-project bleed) |
| AC-7 | Outline drag reorder persists chapter order across reload |
| AC-8 | Settings page has project prefs (not stub) |
| AC-9 | Custom fonts loaded; MASTER typography phase updated |
| AC-10 | `make ci` green; PX-1…PX-5 regression preserved |
| AC-11 | OR-1…OR-7 live stack regression green |

---

## Program registration (pending develop)

When Architect approves this backlog, register in `thesisos-product-v2.yaml`:

```yaml
px6_workorder_backlog:
  - id: PX6-EWO-001
    milestone: PX-6
    status: proposed
    # … (full entries per wave above)
```

Update milestone block:

```yaml
PX-6:
  title: Polish
  status: authorized
  authorization_receipt: .asep/reports/PX6-AUTHORIZATION-20260707.md
  backlog: .asep/reports/PX6-BACKLOG.md
  first_executable_ewo: PX6-EWO-001
```

---

## Execution model

Engineering program (not conformance). Product code only in `frontend/` and
`backend/app/` per program constraints.

```text
AUTHORIZE PX-6 (milestone) ✓
      ↓
DESIGN PX-6 backlog (this document)
      ↓
ASEP: develop PX6-EWO-001  →  spec ratification
      ↓
AUTHORIZE PX-6 Wave B  →  validator EWOs
      ↓
… waves C–F …
      ↓
QWO-PX6-001  →  px6-complete  →  Product v2.0 RC
```

---

## Risk register

| Risk | Mitigation |
|------|------------|
| W-06 scope creep into OR-6 re-qualification | Keep product-layer only; document in KNOWN_LIMITATIONS |
| Multi-project breaks session continuity | Per-project session state keys; integration test |
| Export format errors on edge-case metadata | BibTeX escape tests; empty bibliography state |
| Font CDN perf regression | `next/font` self-host; measure LCP in EWO-012 |
| Outline reorder vs chapter status lifecycle | Reorder API preserves status; no auto-demote |

---

## WO-TRACE

```text
PX-5 PROMOTED → AUTHORIZE PX-6 → DESIGN PX6-BACKLOG
  → PX6-EWO-001 (spec) → Wave B validator → … → QWO-PX6-001 → px6-complete
```
