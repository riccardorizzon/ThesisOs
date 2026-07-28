# Confirmed Findings Remediation — Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every confirmed open finding from the ThesisOS audit (Jul 2026) so CI is deterministic, multi-thesis isolation holds under ADR-0047, concurrency contracts return 409 (not 500), and Docker builds never bake secrets.

**Architecture:** Five gated waves. Wave 0 is already done (writer routing). Waves A–D ship Product Plane fixes only; Wave E is optional product tuning. Each wave ends with a focused pytest/vitest/`make` gate before the next starts. Prefer the existing atomic pattern in `MemoryService` over new abstractions.

**Tech Stack:** FastAPI, SQLAlchemy async + Postgres, LangGraph, Next.js 15, pytest, vitest, Docker Compose, OpenAPI YAML under `contracts/openapi/`.

## Global Constraints

- Product Plane only (`backend/app/`, `frontend/`, `contracts/`, `docker*`, `.dockerignore`) — do **not** change ASEP Core / SoR / Constitution unless a task explicitly says so.
- TDD: failing test first for every behavioral change.
- Smallest correct diff; match surrounding style.
- Never claim tests pass without running them.
- Do not commit unless the operator asks.
- Protect `thesis-agent` data: no destructive live cleanup against the real thesis DB; use `thesisos_test` or ephemeral projects.
- Preserve INV-MTW-1 legacy (optional `project_id` on many GET/PATCH/DELETE) unless a task upgrades a specific endpoint to **required** scope — then document the API change in OpenAPI.

---

## Finding inventory (source of truth)

### Already closed — do not re-implement

| ID | Finding | Evidence |
|----|---------|----------|
| C0 | Writer route shadowed by retrieval short-circuit | Commit `f32ddae6`; `router.py` parse-failure-only fallback; M6 suite green; live Cap. 4 draft OK |
| C0b | AddToBibliographyButton red | Frontend 2/2 pass |
| C0c | Manuscript uncommitted | Committed in `b2b6db49`; clean tree |

### Must fix (this plan)

| ID | Finding | Wave |
|----|---------|------|
| A1 | `.env` bakeable into Docker image | A |
| A2 | Document storage in `/tmp` without volume | A |
| B1 | Chapter optimistic lock non-atomic | B |
| B2 | Document optimistic lock non-atomic | B |
| B3 | Writer/soft-fail persists empty assistant bubble | B |
| B4 | Demo seed in `list()` never commits → ghost chapters | B |
| C1 | Task upsert omits `project_id` | C |
| C2 | Chapter reorder loads/updates all projects | C |
| C3 | Export markdown unscoped | C |
| C4 | Proposal accept without chapter ownership check | C |
| D1 | OpenAPI missing live routes + no CI drift gate | D |
| D2 | Test DB pollution / flaky full suite | D |

### Defer (Wave E — optional, after A–D)

| ID | Finding | Why defer |
|----|---------|-----------|
| E1 | FTS `english` on Italian corpus | Product/tuning; embeddings already multilingual |
| E2 | Substring `RETRIEVAL_KEYWORDS` false positives | Behavioral; needs word-boundary design + eval fixtures |
| E3 | Require `project_id` on all by-id chapter/document/memory routes | Breaks INV-MTW-1; needs ADR amendment |
| E4 | Alembic↔ORM model drift (`alembic check`) | Large; separate migration hygiene plan |
| E5 | Docs mirrors (`architecture.md`, graph.md) stale | Docs-only; not a runtime defect |

---

## File map (by wave)

| Wave | Primary files |
|------|----------------|
| A | `.dockerignore`, `docker-compose.yml`, `backend/app/core/config.py` (env docs only if needed) |
| B | `backend/app/services/chapter/service.py`, `backend/app/services/document/service.py`, `backend/app/services/demo_seed.py`, `backend/app/services/conversation/service.py`, `backend/app/graph/writer.py`, related tests |
| C | `backend/app/services/task/service.py`, `backend/app/graph/conversation.py`, `backend/app/api/chapters.py`, `backend/app/api/export.py`, `backend/app/services/proposal/service.py`, `frontend/lib/chapterClient.ts`, `frontend/lib/proposalClient.ts` |
| D | `contracts/openapi/openapi.yaml`, `Makefile` / `bin/check-openapi-drift.sh`, `backend/tests/conftest.py`, heavy DB test modules |
| E | `constants.py` / `coerce.py`, migration for FTS (optional new revision), docs |

---

## Prerequisite (operator)

- [ ] **P0: Push existing commits** (writer fix + manuscript already on branch)

```bash
cd "/home/ricky/agent thesis"
git status -sb   # expect: feat/companion-persistence ahead 4, clean
git push -u origin feat/companion-persistence
```

Expected: remote updated; no new code required for C0.

**Wave 0 gate (already green — re-run if unsure):**

```bash
cd backend && .venv/bin/python -m pytest -q \
  tests/test_m6_writer_route.py \
  tests/test_m6_writing_eval.py \
  tests/test_m6_writing_integration.py \
  tests/test_router_node.py
```

Expected: all passed.

---

## Wave A — Build & storage hygiene

**Gate:** `docker compose config` valid; image build does not copy `.env`; documents volume mounted.

### Task A1: Exclude secrets from Docker build context

**Files:**
- Modify: `.dockerignore`
- Test: shell assertion (no pytest needed)

**Interfaces:**
- Produces: build context that never includes `.env` / `.env.*`

- [ ] **Step 1: Write failing check**

```bash
# Expect FAIL today: .env is NOT listed
rg -n '^\.env' .dockerignore || echo "MISSING_ENV_EXCLUDE"
```

Expected: `MISSING_ENV_EXCLUDE`

- [ ] **Step 2: Update `.dockerignore`**

Append (keep existing entries):

```gitignore
.env
.env.*
**/.env
**/.env.*
backend/.env
**/secrets/
**/backups/
```

- [ ] **Step 3: Verify**

```bash
rg -n '\.env' .dockerignore
docker compose build backend 2>&1 | tail -5
# Optional: confirm layer does not contain host .env
docker compose run --rm --no-deps backend sh -c 'test ! -f /app/.env && echo NO_ENV_IN_IMAGE || echo ENV_PRESENT'
```

Note: if the running compose mounts or injects env via environment keys, that is fine — the file must not be in the image filesystem from `COPY`.

Expected: `NO_ENV_IN_IMAGE` (or rebuild after ensuring build context has no forced copy). If `ENV_PRESENT` only because a volume mount exists in an override file, document it; default `docker-compose.yml` must not mount host `.env` into the image as a file copy.

- [ ] **Step 4: Commit (when operator asks)**

```bash
git add .dockerignore
git commit -m "$(cat <<'EOF'
fix(docker): exclude .env files from image build context

EOF
)"
```

### Task A2: Persist uploaded documents across container recreate

**Files:**
- Modify: `docker-compose.yml`
- Optionally document: `backend/app/core/config.py` default remains `/tmp/thesisos-documents` **inside** container; compose overrides via env + volume

**Interfaces:**
- Consumes: `Settings.document_storage_local_dir` (`config.py`)
- Produces: named volume mounted at that path

- [ ] **Step 1: Add volume to compose**

Under `backend.environment` add:

```yaml
DOCUMENT_STORAGE_LOCAL_DIR: /data/documents
```

Under `backend.volumes` add (keep `.asep` mount):

```yaml
- document_data:/data/documents
```

Under top-level `volumes:` add:

```yaml
document_data:
```

Exact env key must match the Settings field name convention used by pydantic-settings in this repo (`document_storage_local_dir` → typically `DOCUMENT_STORAGE_LOCAL_DIR`). Confirm in `backend/app/core/config.py` before wiring.

- [ ] **Step 2: Verify**

```bash
docker compose up -d backend
docker compose exec backend sh -c 'echo "$DOCUMENT_STORAGE_LOCAL_DIR"; mkdir -p "$DOCUMENT_STORAGE_LOCAL_DIR" && touch "$DOCUMENT_STORAGE_LOCAL_DIR/.keep" && ls -la "$DOCUMENT_STORAGE_LOCAL_DIR"'
```

Expected: path `/data/documents`, writable.

- [ ] **Step 3: Commit (when operator asks)**

```bash
git add docker-compose.yml
git commit -m "$(cat <<'EOF'
fix(compose): persist document storage on a named volume

EOF
)"
```

**Wave A gate**

```bash
rg -n '\.env' .dockerignore
docker compose config >/dev/null && echo COMPOSE_OK
```

Expected: both OK.

---

## Wave B — Data integrity & chat persistence

**Gate:** chapter/document conflict tests pass; demo list commits; empty writer failure does not persist empty assistant.

### Task B1: Atomic chapter optimistic lock (mirror MemoryService)

**Files:**
- Modify: `backend/app/services/chapter/service.py` (`_update_content`, `_update_metadata`)
- Test: `backend/tests/test_chapter_service.py`

**Interfaces:**
- Consumes: `ChapterContentUpdate.expected_version`, `ChapterMetadataUpdate.expected_version`
- Produces: `UPDATE … WHERE id AND version = expected RETURNING` then append version row; raise `ChapterWriteConflictError` if no row returned
- Reference pattern: `backend/app/services/memory/service.py:277–293`

- [ ] **Step 1: Write failing concurrency test**

Add to `backend/tests/test_chapter_service.py`:

```python
async def test_concurrent_content_update_second_gets_conflict(db_session):
    svc = ChapterService()
    created = await svc.create(
        ChapterCreate(title="Lock me", content_md="v1", project_id="thesis-002"),
        session=db_session,
    )
    await db_session.commit()

    # First writer wins with expected_version=created.version
    await svc.update_content(
        created.id,
        ChapterContentUpdate(content_md="v2", expected_version=created.version),
        session=db_session,
    )
    await db_session.commit()

    # Stale writer still holds old expected_version
    with pytest.raises(ChapterWriteConflictError):
        await svc.update_content(
            created.id,
            ChapterContentUpdate(content_md="stale", expected_version=created.version),
            session=db_session,
        )
```

(Adapt imports/`ChapterCreate` fields to match existing fixtures in that file.)

- [ ] **Step 2: Run — expect FAIL or pass-only-by-luck on check-then-act**

```bash
cd backend && .venv/bin/python -m pytest -q \
  tests/test_chapter_service.py::test_concurrent_content_update_second_gets_conflict -v
```

If current check-then-act already raises conflict on sequential stale version, keep the test (it locks the contract) and add a unit test that mocks two overlapping updates if needed. The **implementation** must still switch to `UPDATE…RETURNING`.

- [ ] **Step 3: Implement `_update_content` with atomic UPDATE**

Replace get+mutate with:

```python
from sqlalchemy import update

async def _update_content(...):
    values = {
        "content_md": data.content_md,
        "word_count": _word_count(data.content_md),
        "version": models.Chapter.version + 1,  # or explicit data.expected_version + 1 in values
        "updated_at": datetime.now(timezone.utc),
    }
    # Prefer: set version = expected_version + 1 in .values
    result = await session.execute(
        update(models.Chapter)
        .where(
            models.Chapter.id == chapter_id,
            models.Chapter.version == data.expected_version,
        )
        .values(
            content_md=data.content_md,
            word_count=_word_count(data.content_md),
            version=data.expected_version + 1,
            updated_at=datetime.now(timezone.utc),
        )
        .returning(models.Chapter)
    )
    row = result.scalar_one_or_none()
    if row is None:
        existing = await session.get(models.Chapter, chapter_id)
        if existing is None:
            raise ChapterNotFoundError(chapter_id)
        raise ChapterWriteConflictError(
            chapter_id,
            expected_version=data.expected_version,
            actual_version=existing.version,
        )
    self._append_change(session, row, change_kind="EDIT")
    await session.flush()
    return self._to_record(row)
```

Apply the same pattern to `_update_metadata` (build `values` from non-None fields; keep PROMOTE vs EDIT change_kind logic).

- [ ] **Step 4: Run chapter service tests**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_chapter_service.py
```

Expected: all passed.

- [ ] **Step 5: Commit (when operator asks)**

```bash
git add backend/app/services/chapter/service.py backend/tests/test_chapter_service.py
git commit -m "$(cat <<'EOF'
fix(chapters): atomic optimistic lock on content and metadata updates

EOF
)"
```

### Task B2: Atomic document optimistic lock

**Files:**
- Modify: `backend/app/services/document/service.py` (`_update` ~316–341)
- Test: `backend/tests/test_document_service.py` (extend optimistic lock test)

**Interfaces:**
- Same pattern as Task B1 / MemoryService
- Raise existing document write-conflict exception type used by API (keep status mapping)

- [ ] **Step 1: Extend/strengthen `test_update_optimistic_lock`** to assert conflict on stale `expected_version` after a successful update (same sequential pattern as B1).

- [ ] **Step 2: Run — confirm current contract**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_document_service.py::test_update_optimistic_lock -v
```

- [ ] **Step 3: Replace check-then-act with `UPDATE…WHERE version…RETURNING`**

- [ ] **Step 4: Full document service suite**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_document_service.py
```

Expected: all passed.

- [ ] **Step 5: Commit (when operator asks)**

```bash
git add backend/app/services/document/service.py backend/tests/test_document_service.py
git commit -m "$(cat <<'EOF'
fix(documents): atomic optimistic lock on update

EOF
)"
```

### Task B3: Do not persist empty assistant on writer soft-failure

**Files:**
- Modify: `backend/app/services/conversation/service.py` (~432–437)
- Optionally: emit SSE `error` when graph ended with writer `generation_failed` and empty parts
- Test: `backend/tests/test_m6_writing_integration.py` or `tests/test_conversation_graph.py`

**Interfaces:**
- Consumes: streamed `parts`, final graph state `errors`
- Produces: either (a) no assistant row + `error` event, or (b) assistant row only when `"".join(parts).strip()` non-empty; finalize status `"error"` when writer failed with empty draft

- [ ] **Step 1: Failing test**

```python
async def test_writer_generation_failed_does_not_persist_empty_assistant(...):
    # Use existing FailLLM / generation_failed harness from test_m6_writing_integration
    # After stream_turn / graph run:
    # - no Message(role=assistant, content="") in DB for that conversation
    # - client saw error event OR done with non-empty clarification — pick one contract and stick to it
```

Recommended contract (minimal UX break):

1. If `parts` empty **and** graph `errors` contains `agent=="writer"` / `generation_failed` → yield `error` (`code=generation_failed`), finalize `status="error"`, **do not** call `_persist_assistant`.
2. Otherwise keep current done path.

- [ ] **Step 2: Run — expect FAIL** (today persists empty)

```bash
cd backend && .venv/bin/python -m pytest -q \
  tests/test_m6_writing_integration.py -k generation_failed -v
```

- [ ] **Step 3: Implement in `stream_turn` before `_persist_assistant`**

```python
assistant_text = "".join(parts)
snap = await graph.aget_state(cfg)
# ... task extraction ...
writer_failed = False
if snap and snap.values:
    for err in snap.values.get("errors") or []:
        agent = getattr(err, "agent", None) or (err.get("agent") if isinstance(err, dict) else None)
        message = getattr(err, "message", None) or (err.get("message") if isinstance(err, dict) else None)
        if agent == "writer" and message == "generation_failed":
            writer_failed = True
            break

if writer_failed and not assistant_text.strip():
    await self._finalize(run_id, conv_id, status="error", usage=usage, task_id=task_id, error="generation_failed")
    finalized = True
    await self._emit(EventType.RUN_COMPLETED, rc, project_id=effective_project_id, status="error")
    yield {"event": "error", "data": {"code": "generation_failed", "message": "Draft generation failed"}}
else:
    message_id = await self._persist_assistant(conv_id, assistant_text)
    ...
```

(Adjust to match exact `AgentError` shape in GraphState.)

- [ ] **Step 4: Re-run M6 writing integration + conversation persistence tests**

```bash
cd backend && .venv/bin/python -m pytest -q \
  tests/test_m6_writing_integration.py \
  tests/test_conversation_graph.py \
  tests/test_chat_endpoint.py
```

Expected: all passed.

- [ ] **Step 5: Commit (when operator asks)**

```bash
git add backend/app/services/conversation/service.py backend/tests/test_m6_writing_integration.py
git commit -m "$(cat <<'EOF'
fix(chat): skip empty assistant persist on writer generation failure

EOF
)"
```

### Task B4: Commit demo seed when listing demo project

**Files:**
- Modify: `backend/app/services/chapter/service.py` (`list` method ~86–93)
- Test: `backend/tests/test_demo_seed.py` / `test_chapter_service.py`

**Interfaces:**
- When `session is None` and filters resolve to `DEMO_THESIS_ID`, `_list` → `ensure_demo_seed` → **`commit`** before return
- When caller-provided `session` is used, do **not** commit (caller owns txn); document that API path uses service-owned session

- [ ] **Step 1: Failing test**

```python
async def test_list_demo_persists_seeded_chapters_across_sessions():
    svc = ChapterService()
    first = await svc.list(ChapterListFilters(project_id=DEMO_THESIS_ID))
    assert first  # seeded
    # New session / new service call must still GET by id
    again = await svc.get(first[0].id)
    assert again.id == first[0].id
```

- [ ] **Step 2: Run — expect FAIL (404 or empty on second get)**

- [ ] **Step 3: Fix `list()`**

```python
async def list(...):
    filters = filters or ChapterListFilters()
    if session is not None:
        return await self._list(session, filters)
    async with AsyncSessionLocal() as s:
        rows = await self._list(s, filters)
        await s.commit()  # persist demo seed side-effects
        return rows
```

Ensure `_list` still only seeds for demo project (existing `ensure_demo_seed` guard).

- [ ] **Step 4: Run**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_demo_seed.py tests/test_chapter_service.py -k demo
```

Expected: all passed.

- [ ] **Step 5: Commit (when operator asks)**

```bash
git add backend/app/services/chapter/service.py backend/tests/test_demo_seed.py
git commit -m "$(cat <<'EOF'
fix(chapters): commit demo seed when listing demo project

EOF
)"
```

**Wave B gate**

```bash
cd backend && .venv/bin/python -m pytest -q \
  tests/test_chapter_service.py \
  tests/test_document_service.py \
  tests/test_m6_writing_integration.py \
  tests/test_demo_seed.py
```

Expected: all passed.

---

## Wave C — Multi-thesis hard scope (ADR-0047)

**Gate:** `tests/test_multi_thesis_isolation.py` + targeted task/reorder/export/proposal tests green; frontend clients pass `project_id` where required.

### Task C1: Task upsert writes `project_id`

**Files:**
- Modify: `backend/app/services/task/service.py`
- Modify: `backend/app/graph/conversation.py` (planner persist hook — pass `project_id` from RunContext/config)
- Test: `backend/tests/test_task_service.py`, `tests/test_conversation_task_lifecycle.py`

**Interfaces:**
- `upsert_from_task_ref(..., project_id: str)`
- Insert/update sets `project_id` (never rely on DB default alone for new rows)

- [ ] **Step 1: Failing test**

```python
async def test_upsert_stores_project_id(db_session):
    svc = TaskService()
    ref = TaskRef(id=str(uuid.uuid4()), title="Scoped")
    await svc.upsert_from_task_ref(
        ref, owner_agent="planner", plan_steps=["a"], project_id="thesis-002", session=db_session
    )
    await db_session.commit()
    row = await db_session.get(models.Task, ref.id)
    assert row.project_id == "thesis-002"
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement**

Add `project_id` to `_upsert` `.values(...)` and to `on_conflict_do_update` `set_` only if product rules allow project migration (prefer: **do not** change `project_id` on conflict — keep original).

Wire graph hook:

```python
# conversation.py planner on_task_ref
project_id = (config.get("configurable") or {}).get("project_id")
await task_service.upsert_from_task_ref(..., project_id=project_id or "thesis-agent")
```

- [ ] **Step 4: Run**

```bash
cd backend && .venv/bin/python -m pytest -q \
  tests/test_task_service.py \
  tests/test_conversation_task_lifecycle.py
```

- [ ] **Step 5: Commit (when operator asks)**

```bash
git commit -m "$(cat <<'EOF'
fix(tasks): persist project_id on planner task upsert

EOF
)"
```

### Task C2: Scope chapter reorder to one project

**Files:**
- Modify: `backend/app/schemas/chapter.py` (`ChapterReorderRequest` — add `project_id: str`)
- Modify: `backend/app/api/chapters.py` (`PATCH /chapters/reorder`)
- Modify: `backend/app/services/chapter/service.py` (`_reorder`)
- Modify: `frontend/lib/chapterClient.ts` (pass active project)
- Test: `backend/tests/test_chapters_api.py`, `tests/test_multi_thesis_isolation.py`

**Interfaces:**
- `_reorder(session, data)` loads only `Chapter.project_id == data.project_id`
- Reject IDs belonging to another project with 404 or 409 (prefer 404 to avoid leak)

- [ ] **Step 1: Failing test** — create chapters in `thesis-agent` and `thesis-002`; reorder with only thesis-002 ids + `project_id=thesis-002`; assert thesis-agent `order_index` unchanged.

- [ ] **Step 2: Implement scoped `select` + API/schema + frontend**

```python
rows = (
    await session.execute(
        select(models.Chapter).where(models.Chapter.project_id == data.project_id)
    )
).scalars().all()
```

- [ ] **Step 3: Run**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_chapters_api.py tests/test_multi_thesis_isolation.py
cd frontend && npm run test -- --run chapterClient
```

- [ ] **Step 4: Commit (when operator asks)**

### Task C3: Scope export markdown

**Files:**
- Modify: `backend/app/api/export.py`
- Modify: `frontend/lib/chapterClient.ts` (`exportMarkdown`)
- Test: `backend/tests/test_export_api.py`

**Interfaces:**
- `GET /export/chapters/{chapter_id}.md?project_id=...` (required query param)
- Service: get chapter then `_scope_error` / compare `chapter.project_id`

- [ ] **Step 1: Failing test** — export with wrong `project_id` → 404; correct → 200 body.

- [ ] **Step 2: Implement + update frontend `withProject` / query string**

- [ ] **Step 3: Run export + writing ExportMenu tests**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_export_api.py
cd frontend && npm run test -- --run ExportMenu
```

- [ ] **Step 4: Commit (when operator asks)**

### Task C4: Proposal accept validates chapter ownership

**Files:**
- Modify: `backend/app/services/proposal/service.py` (accept path ~184–236)
- Test: `backend/tests/test_proposals_api.py`
- Modify: `frontend/lib/proposalClient.ts` — pass `project_id` on accept/reject

**Interfaces:**
- Before `ChapterService.update_content`, load chapter; require `chapter.project_id == proposal.project_id` (and match `expected_project_id` when provided)
- Require `project_id` query/body on accept/reject API

- [ ] **Step 1: Failing test** — proposal for project A, chapter secretly from project B (or mismatched) → reject with 404/409; no content change.

- [ ] **Step 2: Implement ownership check + frontend pass-through**

- [ ] **Step 3: Run**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_proposals_api.py
```

- [ ] **Step 4: Commit (when operator asks)**

**Wave C gate**

```bash
cd backend && .venv/bin/python -m pytest -q \
  tests/test_multi_thesis_isolation.py \
  tests/test_task_service.py \
  tests/test_chapters_api.py \
  tests/test_export_api.py \
  tests/test_proposals_api.py
```

Expected: all passed.

---

## Wave D — Contracts & deterministic CI

**Gate:** OpenAPI includes new/missing product routes; drift script in `make ci`; full `make unit` green twice in a row on fresh `thesisos_test`.

### Task D1: Sync OpenAPI + drift guard

**Files:**
- Modify: `contracts/openapi/openapi.yaml`
- Create: `bin/check-openapi-drift.sh` (or extend existing contract check)
- Modify: `Makefile` (`ci` / `check` target list)
- Test: script exit codes + optional pytest that loads YAML paths

**Minimum paths to add (must match FastAPI routers):**

| Path | Source |
|------|--------|
| `/projects/{project_id}/knowledge/*` (list existing routes in `api/knowledge.py`) | knowledge |
| `/projects/{project_id}/companion/resume` | projects |
| `/writing/actions` | writing_actions |
| `PATCH /chapters/reorder` | chapters |
| Export query `project_id` once Task C3 lands | export |

- [ ] **Step 1: Inventory routes**

```bash
cd backend && .venv/bin/python - <<'PY'
from app.main import app
for r in app.routes:
    if hasattr(r, "methods") and hasattr(r, "path"):
        print(sorted(r.methods), r.path)
PY
```

Diff against `contracts/openapi/openapi.yaml` paths.

- [ ] **Step 2: Add missing path items** (request/response schemas can be minimal `object` stubs if full schemas are heavy — but `operationId` + method + path required)

- [ ] **Step 3: Drift script**

`bin/check-openapi-drift.sh` must fail if FastAPI routes under `/chapters`, `/writing`, `/projects/{project_id}/knowledge`, `/companion`, `/export` are absent from OpenAPI. Implementation sketch: generate route set from app; load YAML paths; set difference non-empty → exit 1.

- [ ] **Step 4: Wire `make openapi-drift` into `make ci`**

- [ ] **Step 5: Run**

```bash
make openapi-drift
make check
```

- [ ] **Step 6: Commit (when operator asks)**

### Task D2: Deterministic test DB isolation

**Files:**
- Modify: `backend/tests/conftest.py`
- Modify: worst offenders (e.g. `tests/test_sources_api.py` autouse seed) to use `db_session` or truncate before seed
- Document: recreate `thesisos_test` recipe in plan appendix

**Interfaces:**
- Prefer: autouse fixture that truncates public tables **once per test module** that marks `@pytest.mark.usefixtures("db_session")`, OR expand `db_session` usage
- Do **not** truncate between tests that share intentional fixtures without resetting seed

Concrete minimal approach:

1. Add `pytest` fixture `clean_db` (function-scoped) = current truncate helper.
2. Convert `test_sources_api.py` autouse seed to: truncate → seed → yield (or seed only inside tests that need catalog).
3. Ensure `ensure-test-db.sh` failures are not swallowed silently when alembic mid-upgrade fails (exit non-zero already — keep it).

- [ ] **Step 1: Reproduce flake protocol**

```bash
# From clean DB
cd backend && .venv/bin/python - <<'PY'
import psycopg
with psycopg.connect("postgresql://thesisos:thesisos@localhost:5432/postgres", autocommit=True) as c:
    c.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='thesisos_test' AND pid<>pg_backend_pid()")
    c.execute("DROP DATABASE IF EXISTS thesisos_test")
    c.execute("CREATE DATABASE thesisos_test")
PY
cd "/home/ricky/agent thesis" && bash bin/ensure-test-db.sh
cd backend && .venv/bin/python -m pytest -q 2>&1 | tee /tmp/pytest1.txt | tail -5
cd backend && .venv/bin/python -m pytest -q 2>&1 | tee /tmp/pytest2.txt | tail -5
```

Both runs must end with the same pass count (target: 0 failed).

- [ ] **Step 2: Fix isolation in offending modules until two consecutive full `pytest -q` are green**

- [ ] **Step 3: Commit (when operator asks)**

**Wave D gate**

```bash
make openapi-drift
make ci
# Run unit twice — both green
```

---

## Wave E — Optional product tuning (after A–D)

### Task E1: FTS language (decision required)

Options:

1. Keep `english` (status quo) — document as known limitation.
2. Switch generated column + queries to `'simple'` or `'italian'` — **requires new Alembic revision** rebuilding `chunks` FTS column; schedule downtime/reindex.

Do not start without operator choice.

### Task E2: Word-boundary retrieval keywords

- Change `has_retrieval_intent` to regex `\b` / token split for short ambiguous tokens: `search`, `cite`, `source`, `paper`.
- Keep phrase keywords (`according to`, `what does`) as substring.
- Extend `tests/test_orchestration_helpers.py` with cases: `"research methods"` must **not** force grounded solely due to `search`; `"search my library"` must.

### Task E3: Mandatory project_id on by-id CRUD

- Requires ADR-0047 follow-up / INV-MTW-1 amendment.
- Out of scope until authorized.

---

## Execution order & parallelization

```text
P0 push
  → Wave A (A1 parallel with A2)
  → Wave B (B1 parallel with B2, then B3, then B4)
  → Wave C (C1 parallel with C2, then C3 parallel with C4)
  → Wave D (D1 after C path changes; D2 anytime after B)
  → Wave E only if prioritized
```

Independent pairs may use parallel subagents only if they touch disjoint files.

---

## Definition of Done (whole program)

- [ ] All Must-fix IDs A1–D2 closed with tests
- [ ] `make ci` green on a freshly migrated `thesisos_test`
- [ ] Second consecutive `cd backend && .venv/bin/python -m pytest -q` green
- [ ] Docker build does not contain host `.env`
- [ ] Document volume survives `docker compose up -d --force-recreate backend`
- [ ] OpenAPI drift gate fails when a new FastAPI route is added without YAML
- [ ] Multi-thesis: reorder/export/proposal/task cannot mutate or leak across projects in automated tests
- [ ] Writer `generation_failed` with empty draft does not leave empty assistant rows
- [ ] Closed findings C0/C0b/C0c remain green (`make qualify-m6`)

---

## Risk notes

| Risk | Mitigation |
|------|------------|
| Reorder/export API shape change breaks frontend | Ship frontend client in same task; Playwright smoke on writing export |
| Atomic UPDATE breaks version append ordering | Keep `_append_change` after successful RETURNING row |
| OpenAPI stubs too thin | Prefer real response schemas from existing Pydantic models where cheap |
| Full pytest still flakes on shared Postgres with live stack | Stop `backend` container during `make ci` or use dedicated test DB port |

---

## Appendix — recreate test DB (ops)

```bash
cd "/home/ricky/agent thesis/backend"
.venv/bin/python - <<'PY'
import psycopg
with psycopg.connect("postgresql://thesisos:thesisos@localhost:5432/postgres", autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'thesisos_test' AND pid <> pg_backend_pid()")
        cur.execute("DROP DATABASE IF EXISTS thesisos_test")
        cur.execute("CREATE DATABASE thesisos_test")
print("ok")
PY
cd "/home/ricky/agent thesis" && bash bin/ensure-test-db.sh
```

Never run this against the `thesisos` (dev/prod data) database name.
