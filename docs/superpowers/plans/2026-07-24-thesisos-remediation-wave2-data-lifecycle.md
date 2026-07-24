# ThesisOS Remediation Wave 2 — Data Integrity and Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Guarantee that user content cannot disappear because of its title, provide a curated demo, and complete safe project/conversation lifecycles.

**Architecture:** `project_id` is the only provenance boundary for chapters. Synthetic demo rows use deterministic IDs in `demo-thesis`. Project deletion is a protected, all-or-nothing service transaction. Conversation title/rename/delete behavior remains project-scoped.

**Tech Stack:** FastAPI, Pydantic v2, SQLAlchemy async, PostgreSQL, React, Vitest, pytest, Playwright.

## Global Constraints

- Never delete or mutate `thesis-agent` as part of this wave.
- Protect `thesis-agent` and `demo-thesis` at the service layer, not only in UI.
- No title/string heuristic may decide provenance, visibility, or deletability.
- Tests use `thesisos_test`; no destructive tests against the live database.
- Do not create git commits unless explicitly requested.

---

### Task 1: Chapter title contract

**Files:**
- Modify: `backend/app/schemas/chapter.py`
- Modify: `backend/tests/test_chapters_api.py`
- Modify: `backend/tests/test_chapter_service.py`
- Modify: `frontend/components/writing/CreateChapterButton.tsx`
- Modify: `frontend/components/writing/CreateChapterButton.test.tsx`

**Interfaces:**
- Produces: `ChapterTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]`.
- Applies to create and metadata/update title.

- [ ] **Step 1: Write failing backend tests**

Add parameterized API assertions:

```py
@pytest.mark.parametrize("title", ["", "   ", "A" * 201])
async def test_create_rejects_invalid_title(client, title):
    response = await client.post("/chapters", json={"project_id": "thesis-002", "title": title})
    assert response.status_code == 422
```

Add:

```py
async def test_create_trims_title(client):
    response = await client.post("/chapters", json={"project_id": "thesis-002", "title": "  Introduzione  "})
    assert response.json()["title"] == "Introduzione"
```

Cover PATCH with whitespace and 201 characters.

- [ ] **Step 2: Run backend tests RED**

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_chapters_api.py -k "invalid_title or trims_title"
```

Expected: FAIL because titles are unconstrained.

- [ ] **Step 3: Implement the shared Pydantic title type**

Use:

```py
from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

ChapterTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]
```

Apply to `ChapterCreate.title` and optional update title.

- [ ] **Step 4: Write and run frontend validation test RED**

Require an inline error for empty/overlong values and a `maxLength={200}` input. Run:

```bash
cd frontend && npm test -- components/writing/CreateChapterButton.test.tsx
```

- [ ] **Step 5: Implement frontend validation and run GREEN**

Trim before submit, preserve the dialog on validation error, and display Italian copy. Run backend and frontend commands again; expect PASS.

### Task 2: Remove title-based dogfood quarantine

**Files:**
- Modify: `backend/app/services/chapter/service.py`
- Modify: `backend/tests/test_chapter_service.py`
- Modify: `backend/tests/test_multi_thesis_isolation.py`

**Interfaces:**
- Produces: chapter visibility determined by requested `project_id`.
- Produces: demo deletability determined by `row.project_id == "demo-thesis"`.

- [ ] **Step 1: Replace old expectations with failing regression tests**

Delete tests that enshrine title blocklists and add:

```py
@pytest.mark.parametrize("title", ["Prova", "Craftsmanship", "Reti neurali", "E2E export"])
async def test_owned_chapter_visibility_never_depends_on_title(db_session, title):
    record = await ChapterService().create(
        ChapterCreate(project_id="thesis-002", title=title),
        session=db_session,
    )
    items = await ChapterService().list(
        ChapterListFilters(project_id="thesis-002", scope="owned"),
        session=db_session,
    )
    assert record.id in {item.id for item in items}
    assert record.deletable is True
```

Add:

```py
async def test_demo_project_chapters_are_protected_by_project_id(...):
    record = await svc.create(ChapterCreate(project_id="demo-thesis", title="Any title"), ...)
    assert (await svc.get(record.id, session=db_session)).deletable is False
```

- [ ] **Step 2: Run service tests RED**

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_chapter_service.py tests/test_multi_thesis_isolation.py
```

Expected: title regressions fail under `_DOGFOOD_EXACT_TITLES`.

- [ ] **Step 3: Remove quarantine helpers**

Remove `_DOGFOOD_TITLE_MARKERS`, `_DOGFOOD_EXACT_TITLES`,
`_sanitize_demo_title`, and `_is_quarantined_dogfood`.

Use:

```py
def _chapter_is_deletable(row: models.Chapter) -> bool:
    if resolve_project_id(row.project_id) == DEMO_THESIS_ID:
        return False
    if _is_migration_seed(row):
        return False
    return True
```

`_apply_scope` returns the already project-filtered rows; `scope` remains accepted for compatibility but cannot apply title heuristics.

- [ ] **Step 4: Run tests GREEN**

Run the command from Step 2. Expected: PASS and no title blocklist remains.

### Task 3: Synthetic demo seed and idempotent copy

**Files:**
- Create: `backend/app/services/demo_seed.py`
- Create: `backend/tests/test_demo_seed.py`
- Modify: `backend/app/services/project_registry.py`
- Modify: `backend/app/services/chapter/service.py`
- Modify: `backend/tests/test_chapter_service.py`
- Modify: `frontend/components/workspace/DemoWorkspaceBanner.tsx`
- Create: `frontend/components/workspace/DemoWorkspaceBanner.test.tsx`

**Interfaces:**
- Produces:

```py
DEMO_CHAPTERS: tuple[DemoChapterSeed, ...]
async def ensure_demo_seed(session: AsyncSession) -> None
async def reset_demo_seed(session: AsyncSession) -> None
```

- [ ] **Step 1: Write failing seed tests**

Assert exactly five deterministic demo rows, stable order/titles, second ensure creates nothing, and reset touches only `demo-thesis`.

```py
assert [row.title for row in rows] == [
    "Introduzione", "Quadro teorico", "Metodologia", "Analisi", "Conclusioni"
]
```

- [ ] **Step 2: Run tests RED**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_demo_seed.py
```

- [ ] **Step 3: Implement deterministic seed**

Use fixed UUID strings and `INSERT ... ON CONFLICT (id) DO UPDATE` scoped to `demo-thesis`. `ensure_demo_seed` does not delete unknown rows; only explicit `reset_demo_seed` deletes existing demo rows.

- [ ] **Step 4: Rewrite copy-demo regression tests**

Require:

- source rows come only from `demo-thesis`;
- target cannot be `demo-thesis`;
- first copy creates five empty chapters;
- second copy creates zero;
- same titles in another thesis do not affect target;
- no authored demo content is copied.

- [ ] **Step 5: Implement copy source and target guard**

Query:

```py
select(models.Chapter).where(models.Chapter.project_id == DEMO_THESIS_ID)
```

Normalize destination titles with `strip().casefold()`.

- [ ] **Step 6: Fix demo banner destination test RED**

Mock `getLastPersonalProjectId()` and require:

```ts
expect(chapterClient.copyDemoStructure).toHaveBeenCalledWith("thesis-002");
```

If no valid owned thesis exists, the banner must create one before copying. It must never use `demo-thesis` as the destination.

- [ ] **Step 7: Implement frontend destination and run GREEN**

Extend `chapterClient.copyDemoStructure(projectId?: string)` and pass the last owned project explicitly. Run:

```bash
cd frontend && npm test -- components/workspace/DemoWorkspaceBanner.test.tsx
cd ../backend && .venv/bin/python -m pytest -q tests/test_demo_seed.py tests/test_chapter_service.py
```

### Task 4: Protected project deletion service and API

**Files:**
- Modify: `backend/app/services/project_registry.py`
- Modify: `backend/app/api/project_registry.py`
- Modify: `backend/tests/test_project_registry.py`
- Modify: `backend/tests/test_multi_thesis_isolation.py`

**Interfaces:**
- Produces:

```py
class ProjectDeleteRequest(BaseModel):
    confirmation_project_id: str

class ProtectedProjectError(Exception): ...
class ProjectConfirmationError(Exception): ...

async def delete_project(
    self,
    project_id: str,
    body: ProjectDeleteRequest,
) -> bool
```

- [ ] **Step 1: Write failing service tests**

Cover:

- `thesis-agent` and `demo-thesis` raise `ProtectedProjectError`;
- mismatch confirmation raises `ProjectConfirmationError`;
- unknown returns `False`;
- a populated `thesis-002` is deleted across all 11 project-root tables and dependent tables;
- a populated `thesis-agent` snapshot is unchanged;
- injected failure halfway rolls back all rows.

- [ ] **Step 2: Run tests RED**

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_project_registry.py tests/test_multi_thesis_isolation.py -k "delete"
```

- [ ] **Step 3: Implement one transaction with explicit dependency order**

Use SQLAlchemy `delete()` expressions. Select scoped IDs first, then delete:

1. `agent_steps`, `agent_runs`;
2. `messages`, `conversations`;
3. `proposals`, `citations`, `notes`;
4. embeddings for scoped chunks, then chunks;
5. sources, documents;
6. chapter versions, chapters;
7. memory versions, memories;
8. concept links/relations, concepts;
9. tasks, events;
10. project row.

Commit once; roll back on every exception.

- [ ] **Step 4: Add API error mapping**

`DELETE /projects/{project_id}` maps:

- 204 success;
- 403 `protected_project`;
- 404 `project_not_found`;
- 422 `project_confirmation_mismatch`.

- [ ] **Step 5: Run service/API tests GREEN**

Run the command from Step 2 plus:

```bash
.venv/bin/python -m pytest -q tests/test_project_registry.py tests/test_multi_thesis_isolation.py
```

### Task 5: Double-confirmation project deletion UI

**Files:**
- Modify: `frontend/lib/projectsClient.ts`
- Create: `frontend/components/settings/DeleteProjectPanel.tsx`
- Create: `frontend/components/settings/DeleteProjectPanel.test.tsx`
- Modify: `frontend/app/settings/page.tsx`
- Modify: `frontend/lib/projectPrefs.ts`

**Interfaces:**
- Produces:

```ts
export async function deleteProject(
  projectId: string,
  confirmationProjectId: string,
): Promise<void>;
```

- [ ] **Step 1: Write failing client/component tests**

Require:

- no delete panel for `thesis-agent` or `demo-thesis`;
- first button opens a modal;
- confirmation button stays disabled until exact ID is typed;
- API receives path ID and body confirmation;
- success clears project-scoped keys, switches to `thesis-agent`, and navigates `/`;
- API failure keeps the project active and displays product-safe copy.

- [ ] **Step 2: Run tests RED**

```bash
cd frontend
npm test -- components/settings/DeleteProjectPanel.test.tsx
```

- [ ] **Step 3: Implement client and UI**

The destructive button copy is “Elimina definitivamente questa tesi”. The dialog names the thesis and requires exact project ID. Use no `window.confirm`.

- [ ] **Step 4: Run tests GREEN**

Run Step 2. Expected: PASS.

### Task 6: Conversation title, rename, and delete backend

**Files:**
- Modify: `backend/app/schemas/conversation.py`
- Modify: `backend/app/services/conversation/service.py`
- Modify: `backend/app/api/conversations.py`
- Modify: `backend/tests/test_conversation_service.py`
- Modify: `backend/tests/test_conversations_api.py`

**Interfaces:**
- Produces:

```py
def conversation_title_from_message(text: str, limit: int = 72) -> str
async def rename_conversation(conversation_id: str, project_id: str, title: str)
async def delete_conversation(conversation_id: str, project_id: str)
```

- [ ] **Step 1: Write failing deterministic title tests**

Cover whitespace collapse, newline removal, Unicode, 72-character cap, and no overwrite of an explicitly renamed title.

- [ ] **Step 2: Write failing API lifecycle tests**

Require project-scoped PATCH/DELETE, cross-project 404, message deletion, and no effect on another project.

- [ ] **Step 3: Run tests RED**

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_conversation_service.py tests/test_conversations_api.py
```

- [ ] **Step 4: Implement title on first durable user turn**

During chat setup, if the title is null or in the placeholder set
`{"New Conversation", "Nuova conversazione"}`, assign the deterministic title before the existing commit.

- [ ] **Step 5: Implement scoped rename/delete endpoints**

Use:

```text
PATCH  /conversations/{id}?project_id=...
DELETE /conversations/{id}?project_id=...
```

Rename accepts a trimmed 1–120 character title. Delete removes dependent messages/runs/steps before the conversation row in one transaction.

- [ ] **Step 6: Run backend tests GREEN**

Run Step 3. Expected: PASS.

### Task 7: Conversation lifecycle UI

**Files:**
- Modify: `frontend/lib/conversationClient.ts`
- Modify: `frontend/components/ConversationList.tsx`
- Modify: `frontend/components/AiChatView.tsx`
- Modify: `frontend/components/AiChatView.test.tsx`

**Interfaces:**
- Produces `renameConversation` and `deleteConversation`.
- `ConversationList` receives an optional `onDeleted(id)` callback.

- [ ] **Step 1: Write failing component tests**

Require:

- title menu exposes “Rinomina” and “Elimina”;
- rename input submits trimmed text;
- delete requires confirmation and calls scoped API;
- deleting active conversation returns to `/`;
- newly titled conversation is refreshed after `done`;
- a list of repeated legacy placeholders uses date fallback until renamed.

- [ ] **Step 2: Run tests RED**

```bash
cd frontend && npm test -- components/AiChatView.test.tsx
```

- [ ] **Step 3: Implement menu and client calls**

Keep row selection separate from menu actions and preserve keyboard accessibility.

- [ ] **Step 4: Run tests GREEN**

Run Step 2. Expected: PASS.

### Task 8: Wave 2 integration gate

- [ ] **Step 1: Run focused backend suites**

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_chapter_service.py \
  tests/test_chapters_api.py \
  tests/test_demo_seed.py \
  tests/test_project_registry.py \
  tests/test_multi_thesis_isolation.py \
  tests/test_conversation_service.py \
  tests/test_conversations_api.py
```

- [ ] **Step 2: Run focused frontend suites**

```bash
cd frontend
npm test -- \
  components/writing/CreateChapterButton.test.tsx \
  components/workspace/DemoWorkspaceBanner.test.tsx \
  components/settings/DeleteProjectPanel.test.tsx \
  components/AiChatView.test.tsx
npx tsc --noEmit
```

- [ ] **Step 3: Add/run a lifecycle Playwright test**

Create an ephemeral thesis, create chapters named “Prova” and “Craftsmanship”, verify visibility, rename/delete a conversation, copy demo twice, verify five unique titles, then delete the ephemeral thesis through the double-confirmation UI. Require protected-project controls to be absent on `thesis-agent`.

- [ ] **Step 4: Inspect scope**

```bash
git diff --check
git status --short
```

Do not touch live demo/QA data yet. Cleanup happens only in Wave 5 after backup.
