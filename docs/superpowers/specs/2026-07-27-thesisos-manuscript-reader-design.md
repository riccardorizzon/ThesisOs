# ThesisOS — Manuscript Reader Design

- **Date:** 2026-07-27
- **Status:** Design approved in session; specification ready for implementation
- **Scope:** Product-plane frontend — new Manoscritto module for ordered thesis reading and structure control
- **Decision:** Lightweight read-only manuscript surface; edit always opens Writing; ADR-0036 amended for a sixth primary nav module (Manoscritto)

---

## 1. Context and Goal

Writing (`/writing`) is an authoring workspace: outline, markdown editor, AI rail, reorder.
There is no dedicated surface to **review all chapters in order**, read them as a book,
and keep structure under control (status, word counts, in-chapter sections).

**Goal (v1):** a Manoscritto module where the researcher can:

1. See the full thesis structure in order (chapters + heading sections)
2. Read one chapter at a time with a persistent table of contents
3. Jump chapter ↔ section and navigate Prev / Next
4. Open Writing when they want to change text (no inline edit in Manoscritto)

**Non-goals (v1):**

- Inline or embedded editing in Manoscritto
- New backend APIs or persisted section entities
- Reading-progress “letto / da rileggere” tracking
- PDF/export redesign, AI panel, or Review merge into this view
- Removing or replacing Writing

---

## 2. Product Decisions

| Topic | Choice |
|-------|--------|
| Purpose | Control overview **and** sequential reading |
| Placement | New primary sidebar module (not inside Writing or Review) |
| Layout | TOC left + chapter reader right |
| Editing | Read-only; **Modifica** navigates to `/writing/[chapterId]` |
| TOC depth | Chapters + `#`/`##` sections + status + word counts |
| Implementation style | Lightweight page on existing chapter APIs |

**Future evolution (out of v1 scope, keep in mind):**

- Native edit in Manoscritto (read/edit toggle or dual mode)
- Possible retirement or demotion of Writing to an “advanced” authoring mode
- Optional light resume (“last opened chapter”) and later soft reading progress

v1 must not block that path: keep Manoscritto as a clean module boundary, reuse chapter
client/editor primitives rather than forking chapter domain logic.

---

## 3. Information Architecture

### Navigation

Insert **Manoscritto** between Writing and Sources:

```text
Home
Research
Writing
Manoscritto   ← new
Sources
Knowledge
─────────
Settings
```

### Routes

| Route | Behavior |
|-------|----------|
| `/manuscript` | Load ordered chapters; select first chapter (or empty state) |
| `/manuscript/[chapterId]` | Same workspace focused on that chapter |

Label in UI: **Manoscritto**. Path segment: `manuscript` (English slug, consistent with `/writing`, `/sources`).

### ADR-0036 amendment (required)

- Primary nav gains Manoscritto; **INV-IA-1** becomes: sidebar contains exactly the
  **six** primary modules listed (Home, Research, Writing, Manoscritto, Sources,
  Knowledge) + Settings.
- Route map adds `/manuscript`, `/manuscript/[chapterId]` → module Manoscritto.
- Compliance: no silent nav addition — this ADR update ships with the feature.

Adjunct surfaces (`/review`, `/ai`) remain outside primary nav.

---

## 4. UX Layout

### Desktop (two panels)

**Left — TOC (~280px)**

- Chapters sorted by `order_index`
- Per chapter: title, status badge (`draft` \| `review` \| `approved` \| `published`),
  `word_count`
- Nested under each chapter: sections from `parseMarkdownSections(content_md)`
  (same heading rules as Writing)
- Header summary: chapter count + total words
- Active chapter highlighted; active section highlighted when scrolled/selected
- Click chapter → load reader; click section → open that chapter and scroll to heading anchor

**Right — Reader**

- Header: chapter title, status, word count
- Body: **rendered markdown** (not a textarea)
- Actions: **Prev** / **Next** (by outline order) · **Modifica** → `/writing/[chapterId]`
- No inline edit toggle in v1

### Mobile

- TOC in a drawer / sheet
- Reader full-width
- Prev / Next and Modifica remain available

### Empty and edge states

| State | Behavior |
|-------|----------|
| No chapters | Message + CTA to Writing |
| Chapter with empty content | “Ancora vuoto” + Modifica / link to Writing |
| Unknown `chapterId` | Message + return to `/manuscript` / first chapter |
| Network failure | Same retry/error patterns as Writing chapter load |

---

## 5. Architecture

### Backend

**No new APIs.** Reuse:

- `GET /chapters?project_id=…` — ordered list (title, status, word_count, order_index, …)
- `GET /chapters/{chapter_id}` — full `content_md` for reader + section parse

Sections are **not** first-class entities; they are derived client-side from markdown
headings (existing `parseMarkdownSections`).

### Frontend units

| Unit | Responsibility |
|------|----------------|
| `app/manuscript/page.tsx` | Route entry |
| `app/manuscript/[chapterId]/page.tsx` | Deep-link entry |
| `ManuscriptWorkspace` | Orchestrates TOC + reader, chapter load, Prev/Next |
| `ManuscriptToc` | Ordered structure, status, words, section tree |
| `ManuscriptReader` | Rendered markdown + header actions |
| `nav.ts` / `routes.ts` | Register module and paths |
| ADR-0036 | Six primary modules + Settings |

Reuse: `chapterClient`, `parseMarkdownSections`, existing status badge/visual language from
Writing outline where practical. Prefer a dedicated markdown **renderer** for reading
(not the editing textarea). If a shared renderer does not exist, add a small read-only
markdown view used only by Manoscritto (or extract a shared primitive if trivial).

### Data flow

```text
projectId
  → GET /chapters
  → ManuscriptToc (order, status, words; sections need content or lazy fetch)
  → select chapterId
  → GET /chapters/{id}
  → parseMarkdownSections → TOC section rows for active (or all, if list payloads include content)
  → ManuscriptReader renders content_md
  → Modifica → router.push(/writing/{chapterId})
```

**Section rows for inactive chapters:** `GET /chapters` returns full `content_md`
per chapter in the list payload. Build the section tree from list results directly.
If any row lacks content, fetch that chapter once via `GET /chapters/{id}` and merge
into workspace cache. Do not add a new backend “outline with sections” endpoint in v1.

### Errors

- Missing chapter: soft empty state, do not crash
- Save/edit: N/A in this module (Writing owns mutations)

---

## 6. Testing and Done Criteria

### Done when

1. Sidebar shows Manoscritto; ADR-0036 / INV-IA-1 updated to six primary modules + Settings
2. `/manuscript` shows ordered TOC with status, word counts, and heading sections
3. Selecting a chapter or section opens/focuses the reader (section scrolls to anchor)
4. Prev / Next walks chapters in outline order
5. **Modifica** navigates to `/writing/[chapterId]`; no inline editor in Manoscritto
6. Empty states for no chapters / empty chapter / bad id are handled

### Tests (minimum)

- Unit: TOC ordering; section parsing feeding TOC rows
- Component: chapter/section selection; Prev/Next; Modifica href/navigation
- Registry: `PRODUCT_ROUTES` / `PRIMARY_NAV` include manuscript; IA count assertion updated

---

## 7. Out of Scope / Follow-ups

- Edit-in-Manoscritto and Writing consolidation
- Persisted sections / server-side outline tree
- Reading progress and “resume where I left off” (optional later; localStorage last chapter is a cheap follow-up)
- Export-all / print stylesheet
- AI affordances inside Manoscritto
- **Revisiona** action on the reader toolbar (v2): navigate to
  `/review?chapter={chapterId}` — Review stays an adjunct workflow; Manoscritto
  only adds a contextual entry point. Not in v1.

---

## 8. References

- ADR-0036 Information Architecture (`decisions/ADR-0036-information-architecture.md`)
- ADR-0039 Writing three-panel layout (boundary: Writing stays authoring)
- Chapter API: `backend/app/api/chapters.py`
- Writing outline / sections: `frontend/components/writing/WritingOutline.tsx`,
  `parseMarkdownSections` in `frontend/components/writing/MarkdownEditor.tsx`
- Nav/routes: `frontend/lib/nav.ts`, `frontend/lib/routes.ts`
