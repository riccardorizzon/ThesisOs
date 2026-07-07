# PX-6 — Polish Experience

> **Product Specification v1** · 2026-07-07  
> **Status:** RATIFIED — PX6-EWO-001  
> **Builds on:** PX-5 Research (promoted @ `px5-complete`)  
> **Terminal milestone:** Product v2.0 release candidate

---

## 0. Document purpose

Self-contained product specification for **PX-6 Polish** — production readiness across
Writing, Sources, Knowledge, Research, and Settings. Closes deferred platform
limitations (W-06) and UX gaps from PX-1…PX-5.

---

## 1. Product thesis

```text
PX-5 = Research  →  How do I explore the landscape?
PX-6 = Polish    →  Is the thesis workflow production-ready?
```

Sequential closure: PX-1 → … → PX-6 → **Product v2.0**.

---

## 2. Capabilities map

| ID | Capability | Operator outcome |
|----|------------|------------------|
| **PX-6.1** | Citation format validator | Detect invalid numeric cites; suggest author-date |
| **PX-6.2** | Bibliography export + print | Export approved sources as BibTeX; print view |
| **PX-6.3** | Multi-project switch | Switch between thesis projects with data isolation |
| **PX-6.4** | Outline drag reorder | Reorder chapters in Writing outline |
| **PX-6.5** | Settings depth | Project prefs, citation style, export defaults |
| **PX-6.6** | Typography polish | Academic font pairing; visual refinement |
| **PX-6.7** | Performance pass | Targeted bundle and canvas perf fixes |

---

## 3. Module boundary matrix

| Surface | Milestone | Route | PX-6 adds |
|---------|-----------|-------|-----------|
| Cite picker + markers | PX-2 | Writing | Validator integration |
| Citation index flags | PX-3 | Sources, Knowledge | Live `Da verificare` badges |
| Concept model | PX-4 | `/knowledge/*` | Project isolation |
| Research canvas | PX-5 | `/research/canvas` | Perf audit only |
| **Citation validator** | **PX-6** | Writing, proposals | Full W-06 mitigation |
| **Bibliography export** | **PX-6** | Sources Bibliografia | BibTeX + print |
| **Multi-project** | **PX-6** | AppShell | Active switcher |
| **Outline reorder** | **PX-6** | Writing outline | Drag-drop persist |
| **Settings** | **PX-6** | `/settings` | Replace M0 stub |
| OR-6 inference enforcement | thesis-agent | Runtime | Read-only — not re-proven |

---

## 4. W-06 mitigation architecture

**Problem:** OR-6 qualified PASS\* with W-06 as Platform Limitation (`docs/KNOWN_LIMITATIONS.md` §2).

**PX-6 approach — product validation layer:**

| Layer | Behavior |
|-------|----------|
| Detection | Deterministic rules flag `[n]` numeric cites |
| Suggestion | Propose `(Author, YYYY)` from linked source metadata |
| Gating | Block **Applica** on AI proposals with unresolved invalid cites (override optional) |
| Messaging | Replace "validatore in arrivo" with live status |
| Documentation | KNOWN_LIMITATIONS §2 → partially mitigated |

**Classification:** Product mitigation — not OR-6 oracle re-run. Do not claim deterministic LLM author-date.

---

## 5. Citation validator (PX-6.1)

### 5.1 Rules

| Pattern | Status | Code |
|---------|--------|------|
| `(Author, YYYY)` | valid | `valid_author_date` |
| `Author (YYYY)` | valid | `valid_author_date_alt` |
| `[@AuthorYear]` linked marker | valid | `valid_linked` |
| `[1]`, `[2]` … | invalid | `invalid_numeric` |
| Unknown format | review | `needs_review` |

### 5.2 Surfaces

- Writing `MarkdownEditor` — inline highlight on invalid segments
- AI panel — flag before Applica; block until resolved or override
- Sources Bibliografia — aggregate invalid count
- Knowledge citation index — `Da verificare` badge wired to engine

### 5.3 API

`POST /citations/validate` — body: `{ text, sources?: SourceRef[] }` → `{ issues: Issue[] }`

---

## 6. Bibliography export (PX-6.2)

### 6.1 Formats

| Format | MIME | Scope |
|--------|------|-------|
| BibTeX | `application/x-bibtex` | Approved sources only, academic order |
| Print | `text/html` | Bibliografia tab print stylesheet |

### 6.2 API

`GET /projects/{project_id}/sources/bibliography/export?format=bibtex`

Filename: `{project_id}-bibliografia.bib`

---

## 7. Multi-project (PX-6.3)

### 7.1 Model

- `projects` registry: `id`, `display_name`, `created_at`
- Default `thesis-agent` preserved
- All domain APIs scoped by `project_id` (INV-KM-2, ADR-0040)

### 7.2 UX

- `ProjectSwitcher` — dropdown, persist selection in `localStorage`
- Session continuity (PX2-EWO-006) keyed per project
- Create project from template (blank thesis scaffold)

### 7.3 API

- `GET /projects` — list projects
- `POST /projects` — create project

---

## 8. Outline reorder (PX-6.4)

- Drag-drop in `WritingOutline`
- `PATCH /chapters/reorder` — `{ ordered_ids: string[] }`
- Preserve chapter status lifecycle on reorder

---

## 9. Settings depth (PX-6.5)

Replace M0 stub at `/settings`:

| Section | Content |
|---------|---------|
| Progetto | Display name, active project id |
| Citazioni | Preferred style (author-date default) |
| Export | Default bibliography format |
| Scorciatoie | Link to command palette help |

---

## 10. Typography (PX-6.6)

Per `design-system/thesisos/MASTER.md`:

- Headings: Crimson Pro (`next/font`)
- Body: Atkinson Hyperlegible (`next/font`)
- Preserve frozen color tokens

---

## 11. Performance (PX-6.7)

- Lazy-load Research canvas chunk
- Document perf budget in spec
- No feature expansion on canvas

---

## 12. PX-6 exclusions

| Feature | Owner |
|---------|-------|
| Real-time collaboration | Out of roadmap v2 |
| Separate Reviewer/Planner agents | ADR supersession required |
| MB2 Runtime / Program Trace | px-exec |
| LLM model replacement | thesis-agent ops |
| Full PDF parse pipeline | PX-3 |

---

## 13. Qualification acceptance (QWO-PX6-001)

| # | Criterion |
|---|-----------|
| AC-1 | Validator flags numeric `[n]`; suggests author-date when source linked |
| AC-2 | AI proposal with invalid cite blocked or requires override before Applica |
| AC-3 | Bibliography export produces valid BibTeX for approved sources |
| AC-4 | KNOWN_LIMITATIONS §2 documents partial W-06 mitigation |
| AC-5 | Project switcher lists ≥2 projects; active project scopes API calls |
| AC-6 | Switching project shows isolated concepts/sources |
| AC-7 | Outline drag reorder persists across reload |
| AC-8 | Settings page has project prefs (not stub) |
| AC-9 | Custom fonts loaded; MASTER typography updated |
| AC-10 | `make ci` green; PX-1…PX-5 regression preserved |
| AC-11 | OR-1…OR-7 live stack regression green |

---

## WO-TRACE

```text
PX-5 PROMOTED → AUTHORIZE PX-6 → PX6-EWO-001 (this document)
  → Waves B–E implementation → QWO-PX6-001 → px6-complete
```
