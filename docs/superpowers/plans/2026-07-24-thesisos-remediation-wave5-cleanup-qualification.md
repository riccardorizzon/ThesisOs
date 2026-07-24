# ThesisOS Remediation Wave 5 — Cleanup and Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove only authorized QA/demo data, prove the real thesis is unchanged, and repeat the complete real-user E2E simulation against the rebuilt product.

**Architecture:** A deterministic project snapshot is the destructive-work guard. Cleanup uses exact project IDs and already-tested public/service contracts. Qualification creates one ephemeral thesis and removes it at the end; `thesis-agent` remains read-only.

**Tech Stack:** Python 3.12, psycopg, PostgreSQL/pg_dump, Docker Compose, pytest, Vitest, Playwright, Vertex AI.

## Global Constraints

- Exact cleanup whitelist: reset `demo-thesis`; delete `thesis-003` and `thesis-004`.
- Never delete or mutate `thesis-agent`.
- Preserve `thesis-002` and every unlisted project.
- Create and verify a restorable PostgreSQL backup before mutation.
- Abort and restore on any protected-snapshot mismatch.
- Do not create git commits unless explicitly requested.

---

### Task 1: Deterministic protected-project snapshot

**Files:**
- Create: `scripts/project-snapshot.py`
- Create: `backend/tests/test_project_snapshot.py`

**Interfaces:**
- Command:

```bash
python3 scripts/project-snapshot.py \
  --database-url "$DATABASE_URL" \
  --project-id thesis-agent \
  --output /tmp/thesis-agent-snapshot.json
```

- Output contains per-aggregate row count and SHA-256 digest plus an overall digest.

- [ ] **Step 1: Write failing snapshot tests**

Load a test project with chapters, versions, documents/chunks/sources, conversations/messages, memory/versions, notes, proposals/citations, concepts/links, tasks, runs/steps, and events. Assert:

- deterministic output across repeated runs;
- mutation changes the relevant digest;
- another project’s mutation does not change the protected digest;
- unsupported/nonexistent project exits non-zero.

- [ ] **Step 2: Run test RED**

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_project_snapshot.py
```

- [ ] **Step 3: Implement canonical serialization**

For each project-root table, select rows by `project_id`, select dependent rows through scoped IDs, sort by primary key, serialize datetimes/UUID/JSON deterministically, and hash canonical JSON. Never include volatile query-order metadata.

The output shape is:

```json
{
  "project_id": "thesis-agent",
  "aggregates": {
    "chapters": {"count": 0, "sha256": "..."}
  },
  "overall_sha256": "..."
}
```

- [ ] **Step 4: Run test GREEN**

Run Step 2. Expected: PASS.

### Task 2: Explicit demo reset command

**Files:**
- Create: `scripts/reset-demo-thesis.py`
- Create: `backend/tests/test_reset_demo_thesis.py`

**Interfaces:**
- Requires both `--project-id demo-thesis` and `--confirm demo-thesis`.
- Calls `reset_demo_seed` in one transaction.

- [ ] **Step 1: Write failing safety tests**

Require rejection for missing confirmation, any project other than `demo-thesis`, and confirmation mismatch. Require exact five synthetic rows after success and no change to owned projects.

- [ ] **Step 2: Run tests RED**

```bash
cd backend && .venv/bin/python -m pytest -q tests/test_reset_demo_thesis.py
```

- [ ] **Step 3: Implement guarded command**

The script must check arguments before opening a write transaction. It may not accept wildcard, comma-separated, or inferred IDs.

- [ ] **Step 4: Run tests GREEN**

Run Step 2. Expected: PASS.

### Task 3: Full real-user Playwright journey

**Files:**
- Create: `tests/e2e/thesisos-real-user-remediation.spec.ts`
- Modify: `tests/e2e/fixtures.ts`

**Interfaces:**
- Test fixture creates a uniquely named ephemeral thesis and returns its ID.
- `afterAll` deletes that exact project using the confirmation contract.

- [ ] **Step 1: Write E2E scenarios before final stack verification**

Cover:

1. first-time project creation and switch;
2. chapter creation, title validation, writing, autosave, versions, reorder;
3. source upload (PDF/MD/TXT), indexing, search and RAG;
4. unsupported/disguised files;
5. source promotion and BibTeX export;
6. AI rewrite/verify/find-sources/expand, cancellation, proposal queue, review accept/reject;
7. linked/unlinked citation gate and override;
8. Notes CRUD, pinning, versions, deletion;
9. chat continuity, context switch, deterministic title, rename/delete;
10. concurrent-turn 409, client abort, max-length input;
11. demo synthetic content and copy idempotency;
12. legacy redirects and `/api` non-collision;
13. project deletion double confirmation and protected-project absence.

Every scenario records console errors, page errors, failed requests, and unexpected 4xx/5xx.

- [ ] **Step 2: Prove tests detect the old failure class**

Before the rebuilt stack is used, run the API-boundary/chat scenario against an intentionally direct `/chat` request fixture and require it to report the redirect. Remove the intentional fixture after this assertion is proven; production selectors stay `/api`.

- [ ] **Step 3: Keep all destructive selectors scoped**

The test must never select `thesis-agent` for a mutation. Add an assertion in the fixture:

```ts
if (projectId === "thesis-agent" || projectId === "demo-thesis") {
  throw new Error("Refusing destructive E2E action on protected project");
}
```

### Task 4: Pre-cleanup backup and snapshot

**Files:**
- Create runtime artifacts only under `backups/` and `/tmp`; do not add them to git.

- [ ] **Step 1: Verify exact live project registry**

```bash
curl --fail localhost:8000/projects
```

Require `thesis-agent`; inspect exact IDs. Stop if `thesis-003` or `thesis-004` does not match the audit-created QA projects.

- [ ] **Step 2: Create PostgreSQL backup**

Verify `backups/` exists, then run:

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
docker exec agentthesis-db-1 pg_dump -U thesisos -d thesisos -Fc \
  > "backups/pre-e2e-remediation-${STAMP}.dump"
test -s "backups/pre-e2e-remediation-${STAMP}.dump"
docker exec -i agentthesis-db-1 pg_restore --list \
  < "backups/pre-e2e-remediation-${STAMP}.dump" > /tmp/thesisos-backup-list.txt
test -s /tmp/thesisos-backup-list.txt
```

- [ ] **Step 3: Capture protected snapshot**

Run `project-snapshot.py` for `thesis-agent` and save the result outside git:

```bash
DATABASE_URL=postgresql://thesisos:thesisos@127.0.0.1:5432/thesisos \
  backend/.venv/bin/python scripts/project-snapshot.py \
  --project-id thesis-agent \
  --output /tmp/thesis-agent-before.json
```

- [ ] **Step 4: Capture preservation-only project list**

Record `thesis-002` and every non-whitelisted project with counts. No cleanup proceeds without this record.

### Task 5: Authorized targeted cleanup

- [ ] **Step 1: Reset demo only**

```bash
DATABASE_URL=postgresql+psycopg://thesisos:thesisos@127.0.0.1:5432/thesisos \
  backend/.venv/bin/python scripts/reset-demo-thesis.py \
  --project-id demo-thesis \
  --confirm demo-thesis
```

Require exactly the five approved synthetic titles.

- [ ] **Step 2: Delete exact QA projects through API**

For each exact ID:

```bash
curl --fail -X DELETE "localhost:8000/projects/thesis-003" \
  -H "Content-Type: application/json" \
  -d '{"confirmation_project_id":"thesis-003"}'

curl --fail -X DELETE "localhost:8000/projects/thesis-004" \
  -H "Content-Type: application/json" \
  -d '{"confirmation_project_id":"thesis-004"}'
```

Do not loop over discovered IDs. Use only these literals.

- [ ] **Step 3: Verify preservation**

Require:

- `thesis-agent`, `thesis-002`, `demo-thesis` still exist;
- only `thesis-003` and `thesis-004` are absent;
- demo has five synthetic chapters;
- protected snapshot equals `/tmp/thesis-agent-before.json`.

If unequal, stop and restore the backup before continuing.

### Task 6: Full automated gates

- [ ] **Step 1: Run repository CI**

```bash
make ci
```

Expected: lint, typecheck, backend/frontend/builder unit, drift, scope, isolation, API guards, and classification all PASS.

- [ ] **Step 2: Rebuild stack**

```bash
docker compose up --build -d
curl --fail localhost:8000/health
curl --fail localhost:3000/api/health
```

- [ ] **Step 3: Run all Playwright product tests**

```bash
cd tests/e2e
npx playwright test
```

Expected: all non-stub suites PASS. If the visual-regression stub is intentionally skipped, report it as skipped, not passed.

- [ ] **Step 4: Run the real-user remediation journey alone with trace**

```bash
npx playwright test thesisos-real-user-remediation.spec.ts --trace=on
```

Require zero unexpected console errors, page errors, failed requests, or 4xx/5xx.

### Task 7: Human requalification and final safety audit

- [ ] **Step 1: Repeat every primary surface as a user**

Visit Home, Research, Research Canvas, Writing, Review, AI, Sources, Source Upload, Source Detail, Knowledge Concepts, Knowledge Notes, and Settings at desktop and mobile breakpoints.

- [ ] **Step 2: Repeat red-team cases**

Ambiguous prompts, long messages, context switching, simultaneous send, cancel/restart, malformed files, Unicode/project names, invalid chapter titles, cross-project IDs, repeated demo copy, and protected deletion attempts.

- [ ] **Step 3: Capture final protected snapshot**

Write `/tmp/thesis-agent-after.json` and compare:

```bash
cmp /tmp/thesis-agent-before.json /tmp/thesis-agent-after.json
```

Expected: exit 0.

- [ ] **Step 4: Verify no test project remains**

The E2E ephemeral project must be absent. `thesis-003` and `thesis-004` remain absent. `thesis-002` remains present.

- [ ] **Step 5: Final repository inspection**

```bash
git diff --check
git status --short
```

List modified/untracked source and documentation files. Do not commit.

- [ ] **Step 6: Goal completion audit**

Map every audit finding to a test and runtime artifact, identify any residual risk, and run:

```bash
python3 .claude/skills/goal/scripts/claude_goal.py complete
```

Only after all evidence and protected snapshots are green.
