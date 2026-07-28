# Live Docker Realign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the running Docker stack serve the same fixed code as git HEAD and restore Vertex LLM so live chat works again.

**Architecture:** Two layers are out of sync today: (1) the backend **image** was built at 14:44 UTC before remediation commits, and (2) compose never injects `GOOGLE_CLOUD_PROJECT` into the container, so `get_llm_client()` returns `NotConfiguredLLM`. Fix by wiring LLM env in the gitignored `docker-compose.override.yml` (local-only secrets/config), rebuilding backend (and frontend if public URL still needed), then smoke-testing chat + scoped export against the live container—not pytest.

**Tech Stack:** Docker Compose, FastAPI backend image (`docker/backend.Dockerfile`), Vertex AI via ADC on GCE VM service account, `backend/.env` / compose `environment`.

## Global Constraints

- Do **not** bake `backend/.env` into the image (`.dockerignore` must keep excluding `.env`).
- Prefer `docker-compose.override.yml` (already gitignored) for local LLM env — do not commit secrets or project IDs that belong only on this VM unless they are already public in docs.
- Do **not** bind-mount `./backend` into the container (override comment: breaks incomplete WIP / diverges from image).
- Product Plane only; no ASEP/SoR changes.
- Preserve named volume `document_data` (do not `docker compose down -v` unless operator explicitly accepts data loss).
- On this GCE VM, Vertex auth is expected via the attached compute service account (metadata ADC), not a host-mounted `application_default_credentials.json` (that file is currently absent).

---

## Why this is needed (plain language)

| World | What it is | Status now |
|-------|------------|------------|
| **Working tree / git** | Code on disk + pushed commits | Fixed; pytest/vitest green |
| **Running container** | Process serving `:8000` | Old image (14:44) + empty `GOOGLE_CLOUD_PROJECT` |

Pytest green does **not** update Docker. Until rebuild + env wiring:

1. Live chat returns `503 llm_not_configured`.
2. Live export still uses the pre-Wave-C handler (no required `project_id`).
3. PDF bytes that lived only in old `/tmp` may be missing even if DB rows remain (volume `document_data` only helps after Wave A was in the image).

---

## File map

| File | Role |
|------|------|
| `docker-compose.override.yml` | Local-only: LLM env (+ optional ADC mount if not on GCE SA) |
| `docker-compose.yml` | Already has `DOCUMENT_STORAGE_LOCAL_DIR` + `document_data` — leave as-is |
| `backend/.env` | Source of truth for project id on host (`GOOGLE_CLOUD_PROJECT`, `VERTEX_LOCATION`) — never COPY into image |
| `bin/beta-public-open.sh` | Optional: re-open public tunnel after frontend rebuild |

---

### Task 1: Wire LLM config into compose override (no image secrets)

**Files:**
- Modify: `docker-compose.override.yml` (gitignored)
- Read: `backend/.env` (host values only)

**Interfaces:**
- Consumes: `Settings.google_cloud_project` ← env `GOOGLE_CLOUD_PROJECT`
- Produces: backend container env with non-empty project so `get_llm_client()` returns `LiteLLMClient`

- [ ] **Step 1: Confirm host `.env` has project**

```bash
cd "/home/ricky/agent thesis"
# Print keys only — do not paste secrets into chat logs
sed 's/=.*/=<set>/' backend/.env
```

Expected: lines for `GOOGLE_CLOUD_PROJECT` and `VERTEX_LOCATION` both `<set>`.

- [ ] **Step 2: Confirm container is empty today (failing baseline)**

```bash
docker compose exec -T backend printenv GOOGLE_CLOUD_PROJECT || true
curl -s -o /tmp/chat_before.json -w "%{http_code}\n" \
  -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"ping"}'
cat /tmp/chat_before.json
```

Expected: empty project; HTTP `503` with `"code":"llm_not_configured"`.

- [ ] **Step 3: Update override with LLM environment**

Replace/extend `docker-compose.override.yml` so `backend.environment` includes (values copied from host `backend/.env`, not hardcoded in git):

```yaml
# Runtime mounts for public beta — do NOT bind-mount ./backend (breaks incomplete WIP).
services:
  backend:
    volumes:
      - ./.asep:/.asep:ro
      - ./knowledge/thesis-agent:/knowledge/thesis-agent:ro
      - document_data:/data/documents
    environment:
      DATABASE_URL: postgresql+psycopg://thesisos:thesisos@db:5432/thesisos
      APP_ENV: local
      THESIS_AGENT_KNOWLEDGE_ROOT: /knowledge/thesis-agent
      DOCUMENT_STORAGE_LOCAL_DIR: /data/documents
      GOOGLE_CLOUD_PROJECT: "<from backend/.env>"
      VERTEX_LOCATION: "<from backend/.env or global>"
      # Optional if models differ from Settings defaults:
      # GEMINI_MODEL: "gemini-3.6-flash"
      # GEMINI_ORCHESTRATION_MODEL: "gemini-3.5-flash-lite"
```

Notes:
- On this GCE VM with attached SA, do **not** require mounting `~/.config/gcloud/application_default_credentials.json` unless Step 5 still fails with auth errors.
- If later running on a laptop without GCE SA, add:

```yaml
      - ${HOME}/.config/gcloud/application_default_credentials.json:/gcp/adc.json:ro
    environment:
      GOOGLE_APPLICATION_CREDENTIALS: /gcp/adc.json
```

- [ ] **Step 4: Recreate backend with new env (code still old until Task 2)**

```bash
docker compose up -d backend
docker compose exec -T backend printenv GOOGLE_CLOUD_PROJECT
```

Expected: non-empty project id matching `.env`.

- [ ] **Step 5: Commit**

No git commit — `docker-compose.override.yml` is gitignored by design.

---

### Task 2: Rebuild backend image from current HEAD

**Files:**
- Build context: repo root + `docker/backend.Dockerfile`
- No source edits required if HEAD already contains Waves A–D

**Interfaces:**
- Produces: container `/app/app/api/export.py` with `project_id: str = Query(min_length=1)`

- [ ] **Step 1: Confirm HEAD and unclean tree**

```bash
cd "/home/ricky/agent thesis"
git status -sb
git rev-parse --short HEAD   # expect 11b7bd39 or later on feat/companion-persistence
```

Expected: clean working tree; branch tracking origin.

- [ ] **Step 2: Prove container still has old export signature**

```bash
docker compose exec -T backend sed -n '18,22p' /app/app/api/export.py
```

Expected before rebuild: `async def export_chapter_markdown(chapter_id: str):` (no Query).

- [ ] **Step 3: Rebuild and recreate backend**

```bash
docker compose build backend
docker compose up -d backend
# wait for health
for i in $(seq 1 30); do
  curl -sf http://localhost:8000/health && break
  sleep 1
done
```

Expected: `{"status":"ok"}` (or equivalent health payload).

- [ ] **Step 4: Prove new export contract in the running image**

```bash
docker compose exec -T backend sed -n '18,22p' /app/app/api/export.py
curl -s -w "\nHTTP %{http_code}\n" \
  "http://localhost:8000/export/chapters/00000000-0000-0000-0000-000000000000.md"
curl -s -w "\nHTTP %{http_code}\n" \
  "http://localhost:8000/export/chapters/00000000-0000-0000-0000-000000000000.md?project_id=thesis-agent"
```

Expected:
- Signature includes `project_id: str = Query(...)`.
- Missing query → **422** (validation), not 404-from-service.
- With query + unknown uuid → **404** `chapter_not_found`.

- [ ] **Step 5: Commit**

No commit unless Dockerfile/compose.yml needed a tracked fix (should not).

---

### Task 3: Live smoke — chat + writer path

**Files:**
- None (runtime verification only)

**Interfaces:**
- Consumes: `POST /chat` SSE stream
- Produces: evidence that LLM is configured (no `llm_not_configured`)

- [ ] **Step 1: Configured LLM gate**

```bash
curl -s -N -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Di in una frase cos'\''è ThesisOS."}' \
  | head -c 800
```

Expected: SSE `token` / `done` events; **must not** contain `"code":"llm_not_configured"`.

If auth fails (403/ADC/permission): stop and fix GCE SA / Vertex AI API enablement — do not weaken `.dockerignore`.

- [ ] **Step 2: Writer smoke (optional but recommended)**

New conversation via UI or API with an explicit drafting prompt (Italian Cap. draft). Expect a non-empty assistant draft, not Companion opening script alone.

- [ ] **Step 3: Document any missing uploads**

```bash
# If a document row exists but parse/retrieve fails, re-upload into /data/documents volume
docker compose exec -T backend sh -c 'ls -la "$DOCUMENT_STORAGE_LOCAL_DIR" | head'
```

Expected: writable `/data/documents`. Re-upload only if operator confirms missing files.

---

### Task 4: Refresh public beta URL (if still using cloudflare tunnel)

**Files:**
- Run: `bin/beta-public-open.sh` (rebuilds frontend with `NEXT_PUBLIC_API_BASE_URL`)

**Interfaces:**
- Produces: public same-origin URL with rebuilt frontend pointing at tunnel

- [ ] **Step 1: Re-run beta open (reuse URL if possible)**

```bash
cd "/home/ricky/agent thesis"
# Prefer reuse:
# BETA_PUBLIC_URL=https://indexes-ghz-joan-stronger.trycloudflare.com bash bin/beta-public-open.sh
bash bin/beta-public-open.sh
```

Expected: script prints `App:` URL; `/health` and `/` return 200 through the tunnel.

- [ ] **Step 2: Public chat smoke**

```bash
PUBLIC_URL=$(rg -o 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/thesisos-beta-public.env | head -1)
curl -s -N -X POST "$PUBLIC_URL/chat" \
  -H 'Content-Type: application/json' \
  -d '{"message":"ping breve"}' | head -c 400
```

Expected: stream without `llm_not_configured`.

- [ ] **Step 3: Commit**

No commit.

---

## Acceptance checklist

- [ ] `docker compose exec backend printenv GOOGLE_CLOUD_PROJECT` non-empty
- [ ] Running `export.py` requires `project_id` (422 without it)
- [ ] Live `POST /chat` does not return `llm_not_configured`
- [ ] Backend image built from current HEAD after Wave A–D
- [ ] `document_data` volume still present (`docker volume ls | rg document_data`)
- [ ] `.env` still absent from image filesystem (`test ! -f /app/.env` or `/app/backend/.env`)

## Out of scope

- Wave E (FTS language, retrieval keyword word-boundaries)
- Committing `docker-compose.override.yml`
- Re-parsing every historical PDF unless a specific document fails at runtime
