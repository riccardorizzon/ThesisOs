# ThesisOS Remediation Wave 3 — Academic Workflows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make bibliography, citation validation, uploads, and manual notes coherent and trustworthy for academic work.

**Architecture:** Approved project sources are the citation authority. Uploaded sources have an explicit candidate→approved transition. Knowledge hosts a project-scoped Notes view backed by the existing durable memory API. Upload validation uses one shared allowlist and performs pre-persistence content checks.

**Tech Stack:** FastAPI, SQLAlchemy, React, TypeScript, Vitest, pytest, Playwright.

## Global Constraints

- Citation validation never claims factual truth; it verifies linkage to approved project sources.
- AI application may be blocked; manual chapter autosave may not.
- Every source/memory operation remains project-scoped.
- Supported uploads: PDF, EPUB, DOCX, Markdown, plain text.
- No production code before a failing test.
- Do not create git commits unless explicitly requested.

---

### Task 1: Author-date citation extraction and linkage

**Files:**
- Modify: `backend/app/services/citation/validation.py`
- Modify: `backend/app/schemas/citation.py`
- Modify: `backend/tests/test_citation_validation.py`
- Modify: `frontend/lib/citationValidation.ts`
- Modify: `frontend/lib/citationValidation.test.ts`

**Interfaces:**
- Adds issue code `unlinked_author_date`.
- Produces semantically equivalent backend/frontend source matching.

- [ ] **Step 1: Add shared behavioral fixtures**

Use equivalent test cases in Python and TypeScript:

```text
(Benjamin, 1936)                  → linked
Benjamin (1936)                   → linked
(Glaser & Strauss, 1967)          → linked when source author contains both surnames
(Glaser e Strauss, 1967)          → linked
(FantomaAutore, 2050)             → unlinked_author_date, blocking
[2]                               → invalid_numeric, blocking
```

Normalize Unicode, apostrophes, punctuation, `&`, and Italian `e`.

- [ ] **Step 2: Run validators RED**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_citation_validation.py
cd ../frontend && npm test -- lib/citationValidation.test.ts
```

Expected: fabricated author-date is currently accepted.

- [ ] **Step 3: Implement minimal extraction and matching**

Backend and frontend must expose:

```text
extract_author_date_citations(text)
normalize_author_tokens(author)
is_linked_citation(citation, sources)
```

Match year exactly and require each cited surname token to appear in one approved source author string.

- [ ] **Step 4: Include source ID in issues**

Extend issue schemas with optional `source_id` only for linked diagnostics and preserve existing fields. For unlinked citations, `suggestion` is “Aggiungi o collega questa fonte alla bibliografia”.

- [ ] **Step 5: Run validators GREEN**

Run Step 2. Expected: PASS with identical fixtures.

### Task 2: Project-aware citation validation API and AI gate

**Files:**
- Modify: `backend/app/api/citations.py`
- Modify: `backend/app/services/sources/repository.py`
- Modify: `backend/tests/test_citation_validation.py`
- Create: `frontend/lib/citationClient.ts`
- Create: `frontend/lib/citationClient.test.ts`
- Modify: `frontend/components/writing/WritingAiPanel.tsx`
- Modify: `frontend/components/writing/WritingAiPanel.test.tsx`
- Modify: `frontend/components/writing/CitationValidatorBanner.tsx`
- Create: `frontend/components/writing/CitationValidatorBanner.test.tsx`

**Interfaces:**
- `CitationValidateRequest` accepts `project_id`.
- The API loads approved source refs when caller does not supply explicit refs.
- `WritingAiPanel` calls the project-scoped API after stream completion.

- [ ] **Step 1: Write failing API tests**

Create two projects with distinct approved sources. Require a citation linked in project A to be unlinked in project B. Require no cross-project source lookup.

- [ ] **Step 2: Run API tests RED**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_citation_validation.py
```

- [ ] **Step 3: Implement approved-source lookup**

Add a repository method returning:

```py
list[dict[str, str | int | None]]
```

for `corpus_status == "approvata"` and exact `project_id`.

- [ ] **Step 4: Write failing citation client and AI panel tests**

Require:

- unlinked author-date disables “Applica”;
- banner names the unmatched citation;
- “Applica comunque” enables the existing explicit override;
- a linked citation does not block;
- “Applica” stays disabled while server validation is pending;
- transport failure shows “Verifica citazioni non disponibile” and requires
  explicit override rather than silently allowing application;
- manual editor behavior is untouched.

- [ ] **Step 5: Implement project-scoped validation and banner**

`citationClient.validate(projectId, text)` posts to `/citations/validate`. On
stream completion, the panel validates the final draft and stores returned
issues. The local validator provides immediate numeric-format feedback only;
the backend response is authoritative for bibliography linkage.

- [ ] **Step 6: Run API/UI tests GREEN**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_citation_validation.py
cd ../frontend && npm test -- lib/citationClient.test.ts components/writing/WritingAiPanel.test.tsx components/writing/CitationValidatorBanner.test.tsx
```

### Task 3: Candidate source promotion

**Files:**
- Modify: `backend/app/services/sources/repository.py`
- Modify: `backend/app/services/sources/service.py`
- Modify: `backend/app/api/sources.py`
- Modify: `backend/tests/test_sources_db.py`
- Modify: `backend/tests/test_sources_api.py`
- Modify: `frontend/lib/sourcesClient.ts`
- Create: `frontend/components/sources/AddToBibliographyButton.tsx`
- Create: `frontend/components/sources/AddToBibliographyButton.test.tsx`
- Modify: `frontend/components/sources/SourceKnowledgeCard.tsx`
- Modify: `frontend/components/sources/SourceApiDetailView.tsx`

**Interfaces:**
- Produces:

```text
POST /projects/{project_id}/sources/{slug}/bibliography
```

- Returns the updated `SourceListItem`.

- [ ] **Step 1: Write failing backend tests**

Cover candidate→approved, second call idempotency, cross-project 404, unknown source 404, and bibliography export inclusion only after promotion.

- [ ] **Step 2: Run backend tests RED**

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_sources_db.py tests/test_sources_api.py
```

- [ ] **Step 3: Implement repository/service/API**

Update only:

```sql
UPDATE sources
SET corpus_status = 'approvata',
    knowledge_state = 'linked'
WHERE project_id = :project_id AND slug = :slug
RETURNING ...
```

Keep the operation idempotent and scoped.

- [ ] **Step 4: Write failing frontend tests**

Candidate cards expose “Aggiungi alla bibliografia”; approved cards do not. Success refreshes the card; failure shows product-safe copy.

- [ ] **Step 5: Implement client/button integration**

Add:

```ts
export async function addSourceToBibliography(
  slug: string,
  projectId?: string,
): Promise<SourceListItem>
```

- [ ] **Step 6: Run source suites GREEN**

Run backend Step 2 and:

```bash
cd frontend && npm test -- components/sources/AddToBibliographyButton.test.tsx
```

### Task 4: Bibliography empty state and metadata consistency

**Files:**
- Modify: `frontend/components/sources/BibliographyExportBar.tsx`
- Create: `frontend/components/sources/BibliographyExportBar.test.tsx`
- Modify: `frontend/components/sources/SourcesEnrichedList.tsx`
- Modify: `backend/app/services/sources/bibliography.py`
- Modify: `backend/tests/test_sources_db.py`

**Interfaces:**
- `BibliographyExportBar` receives approved and candidate counts.
- Missing year renders `n.d.` consistently.

- [ ] **Step 1: Write failing tests**

Require:

- zero approved + candidates displays “Aggiungi almeno una fonte candidata alla bibliografia”;
- export button is disabled when approved count is zero;
- after promotion export contains the uploaded title/author and `n.d.`;
- BibTeX escaping remains valid.

- [ ] **Step 2: Run tests RED**

```bash
cd frontend && npm test -- components/sources/BibliographyExportBar.test.tsx
cd ../backend && .venv/bin/python -m pytest -q tests/test_sources_db.py -k bibliography
```

- [ ] **Step 3: Implement counts and copy**

Derive counts from `initialSources` in `SourcesEnrichedList`; pass them to the bar. Preserve approved-only backend export.

- [ ] **Step 4: Run tests GREEN**

Run Step 2. Expected: PASS.

### Task 5: Notes view inside Knowledge

**Files:**
- Create: `frontend/components/knowledge/KnowledgeWorkspace.tsx`
- Create: `frontend/components/knowledge/KnowledgeWorkspace.test.tsx`
- Create: `frontend/components/knowledge/notes/KnowledgeNotesPanel.tsx`
- Create: `frontend/components/knowledge/notes/KnowledgeNotesPanel.test.tsx`
- Modify: `frontend/components/MemoryForm.tsx`
- Modify: `frontend/components/MemoryList.tsx`
- Modify: `frontend/app/knowledge/page.tsx`
- Modify: `frontend/app/memory/page.tsx`
- Modify: `frontend/app/memory/new/page.tsx`
- Modify: `frontend/app/memory/[id]/page.tsx`

**Interfaces:**
- Knowledge query: `?view=concepts|notes`.
- Notes use `memoryClient` and project scope already provided by `withProject`.

- [ ] **Step 1: Write failing workspace tests**

Require:

- Concepts is default.
- “Note” tab loads project-scoped memory records.
- `/memory`, `/memory/new`, and `/memory/{id}` redirect to `/knowledge?view=notes`.
- No top-level navigation item is added.

- [ ] **Step 2: Write failing notes CRUD tests**

Cover create, edit with expected version, pin, list versions, delete confirmation, empty state, API error, and Italian labels.

- [ ] **Step 3: Run frontend tests RED**

```bash
cd frontend
npm test -- \
  components/knowledge/KnowledgeWorkspace.test.tsx \
  components/knowledge/notes/KnowledgeNotesPanel.test.tsx
```

- [ ] **Step 4: Implement client workspace**

`KnowledgeWorkspace` renders tab buttons/links and mounts either existing `KnowledgeExplorer` or `KnowledgeNotesPanel`. Notes panel uses `memoryClient` directly and local component state; it does not create a second store.

- [ ] **Step 5: Localize reusable memory components**

Replace admin/developer labels (`Kind`, `Title`, `Pinned`, `Create memory`) with Italian product labels. Parameterize links so notes stay under `knowledge?view=notes`.

- [ ] **Step 6: Run tests GREEN**

Run Step 3 plus existing memory component/client suites.

### Task 6: Upload allowlist and content preflight

**Files:**
- Modify: `backend/app/schemas/document.py`
- Modify: `backend/app/services/document/service.py`
- Modify: `backend/app/api/documents.py`
- Modify: `backend/tests/test_document_service.py`
- Modify: `backend/tests/test_document_api.py`
- Modify: `frontend/lib/documentClient.ts`
- Modify: `frontend/app/sources/upload/page.tsx`
- Create: `frontend/app/sources/upload/page.test.tsx`
- Modify: `frontend/components/onboarding/CoachMark.tsx`

**Interfaces:**
- Shared formats: `.pdf,.epub,.docx,.md,.markdown,.txt`.
- Unsupported format response: HTTP 415 `unsupported_format`.
- Invalid PDF response: HTTP 415 `invalid_file_content`.

- [ ] **Step 1: Write failing backend tests**

Cover:

- all supported extensions accepted;
- `.exe` rejected with 415 and creates no document/source/storage object;
- `.pdf` without `%PDF-` signature rejected before persistence;
- parser/storage are not invoked for invalid content;
- historical markdown/text records remain readable.

- [ ] **Step 2: Run backend tests RED**

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_document_service.py tests/test_document_api.py -k "format or pdf or upload"
```

- [ ] **Step 3: Implement preflight**

Add:

```py
def validate_upload_content(source_type: str, data: bytes) -> None:
    if source_type == "pdf" and not data.startswith(b"%PDF-"):
        raise InvalidFileContentError("Il file selezionato non è un PDF valido.")
```

Call before creating any DB/storage rows. Map unsupported and invalid content to 415.

- [ ] **Step 4: Write failing frontend copy/type tests**

Require accepted extensions, visible copy naming all five formats, `DocumentSourceType` including `markdown` and `text`, and a safe 415 message.

- [ ] **Step 5: Implement UI/client alignment**

Use:

```ts
const ACCEPT = ".pdf,.epub,.docx,.md,.markdown,.txt";
```

Update onboarding copy from “PDF o Markdown” to the same product wording.

- [ ] **Step 6: Run backend/frontend tests GREEN**

Run Step 2 and:

```bash
cd frontend
npm test -- app/sources/upload/page.test.tsx lib/documentClient.test.ts
```

### Task 7: Wave 3 integration gate

- [ ] **Step 1: Run all academic focused suites**

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_citation_validation.py \
  tests/test_sources_db.py \
  tests/test_sources_api.py \
  tests/test_document_service.py \
  tests/test_document_api.py \
  tests/test_memory_service.py \
  tests/test_memory_api.py
```

```bash
cd frontend
npm test -- \
  lib/citationValidation.test.ts \
  components/writing/WritingAiPanel.test.tsx \
  components/writing/CitationValidatorBanner.test.tsx \
  components/sources/AddToBibliographyButton.test.tsx \
  components/sources/BibliographyExportBar.test.tsx \
  components/knowledge/KnowledgeWorkspace.test.tsx \
  components/knowledge/notes/KnowledgeNotesPanel.test.tsx \
  app/sources/upload/page.test.tsx
npx tsc --noEmit
```

- [ ] **Step 2: Add/run academic Playwright journey**

In an ephemeral thesis:

1. upload valid Markdown and PDF;
2. reject a disguised PDF and unsupported file;
3. search/retrieve uploaded content;
4. promote a candidate and export BibTeX;
5. generate AI text with linked and unlinked citations;
6. verify block and explicit override;
7. create/edit/pin/version/delete a note in Knowledge.

- [ ] **Step 3: Inspect scope**

```bash
git diff --check
git status --short
```

Do not clean the live database in this wave.
