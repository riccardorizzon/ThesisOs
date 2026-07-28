# Ops Perfection Priorities — Operational Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or subagent-driven-development only for tasks marked **DO NOW**. Do not execute deferred items unless the operator re-authorizes.

**Goal:** Decide what is actually required to keep ThesisOS beta-usable vs cosmetic “perfection,” and give a sequenced ops checklist.

**Architecture:** Runtime already serves HEAD + Vertex + persistent `document_data`. RAG reads **chunks/embeddings in Postgres**, not original PDF bytes. Originals matter only for download/re-parse. Ops discipline (rebuild + audit) prevents the next live/code drift.

**Tech Stack:** Docker Compose, Postgres, Vertex, `bin/audit-document-storage.sh`, Sources upload UI.

## Global Constraints

- Do not `docker compose down -v` (destroys `document_data` / `pgdata`).
- Do not bake `.env` into the image; use `docker-compose.override.yml` + `env_file`.
- Prefer re-upload of a **small curated set** of thesis sources over bulk re-ingest of 61 dogfood rows.
- Wave E product polish stays out of scope unless explicitly authorized.

---

## Verdict: is each priority really necessary?

| ID | Action | Necessary for beta MVP? | Necessary for “perfect”? | Decision |
|----|--------|-------------------------|--------------------------|----------|
| **P0** | Live allineato, LLM, volume | **Yes — already done** | Yes | **KEEP / MONITOR** |
| **P1** | Re-upload fonti importanti | **No** if you only chat/write/RAG | **Yes** if you need Download PDF / re-parse / fix failed Sennett | **OPTIONAL — do only curated set** |
| **P2** | Rebuild + audit after deploy | **Yes** as habit (5 min) | Yes | **DO NOW as runbook** |
| **P3** | Docling in image / parser path | **No** — PyMuPDF fallback exists; 60/61 docs already usable | Only if new complex PDF fails and markdown isn’t enough | **DEFER until a real failed upload** |
| **P4** | Wave E polish | **No** | Product GA, not ops | **DEFER** |

### Why P1 is not mandatory

Evidence (2026-07-29):

- 60 documents `indexed`/`parsed`, 2239 chunks, 2208 embeddings.
- Live search returns grounded hits (Sennett / pratica manuale).
- Writer Cap. 4 smoke used RAG sources successfully.
- **0 originals on disk** — hurts **download/re-parse only**, not retrieval of already-indexed text.

Re-upload **only** when you need at least one of:

1. Download original from Sources UI  
2. Re-parse after parser fix  
3. Replace a failed/corrupt document (`The Craftsman` failed: `parser_unavailable: docling` — try markdown or PyMuPDF path on re-upload)

### Why P3 is not mandatory now

Dockerfile already notes PyMuPDF fallback when Docling deps are missing. Enabling full Docling is image-size + build-time cost. Trigger only if a **new** PDF upload fails end-to-end in beta.

### Why P4 is not “ops perfection”

FTS language, retrieval keyword boundaries, Research basket are product polish. They do not restore live integrity. Keep them on the remediation Wave E backlog.

---

## Target state (honest “good enough”)

Call ThesisOS **ops-complete for beta** when:

1. `curl localhost:8000/health` and `/ready` OK  
2. `POST /chat` streams tokens (no `llm_not_configured`)  
3. Export without `project_id` → 422  
4. `bash bin/audit-document-storage.sh` runs and you understand the report  
5. After any code pull: rebuild backend before claiming live fixed  
6. *(Optional)* Curated thesis PDFs re-uploaded so originals exist on `document_data`

Items 1–5 = **required**. Item 6 = **nice-to-have for your thesis corpus**.

---

## Operational runbook

### Task 0: Baseline check (every session / after reboot)

**Files:** none  
**Gate:** commands below

- [ ] **Step 1: Stack**

```bash
cd "/home/ricky/agent thesis"
docker compose ps
curl -sf http://localhost:8000/health && curl -sf http://localhost:8000/ready
```

Expected: backend/frontend/db Up; health + ready OK.

- [ ] **Step 2: LLM**

```bash
docker compose exec -T backend printenv GOOGLE_CLOUD_PROJECT
curl -sf -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' -d '{"message":"ping"}'
```

Expected: non-empty project; HTTP `200`.

- [ ] **Step 3: Storage audit**

```bash
bash bin/audit-document-storage.sh
```

Expected: script completes. Missing originals are OK for RAG; note any new `failed` rows.

---

### Task 1 (P2): Deploy discipline — **DO NOW / always**

**When:** after `git pull` / merge that touches `backend/` or Docker files.

- [ ] **Step 1: Rebuild backend**

```bash
cd "/home/ricky/agent thesis"
docker compose up -d --build backend
# wait
for i in $(seq 1 30); do curl -sf http://localhost:8000/health && break; sleep 1; done
```

- [ ] **Step 2: Contract smoke**

```bash
# export must require project_id
curl -s -o /dev/null -w "%{http_code}\n" \
  "http://localhost:8000/export/chapters/00000000-0000-0000-0000-000000000000.md"
# expect 422
bash bin/audit-document-storage.sh | head -40
```

- [ ] **Step 3: Optional public tunnel**

```bash
# only if beta URL needed
BETA_PUBLIC_URL=https://indexes-ghz-joan-stronger.trycloudflare.com \
  bash bin/beta-public-open.sh
```

**Commit:** none (ops only).

---

### Task 2 (P1): Curated re-upload — **OPTIONAL**

**Do this only if** you need originals for thesis sources you still have locally.

**Recommended set (example — adjust to what you have on disk):**

| Priority | Source | Why |
|----------|--------|-----|
| A | Outline-Master / Stigmata Framework / Core Theory Map | Structure + RAG anchors |
| B | Sennett Craftsman (or markdown excerpt) | Failed row + frequent writer grounding |
| C | Benjamin / other core PDF you still open in UI | Download UX |

- [ ] **Step 1: List what you still have locally** (outside Docker). Skip anything you don’t have — do not hunt 61 dogfood files.

- [ ] **Step 2: Upload via UI**

Open `https://indexes-ghz-joan-stronger.trycloudflare.com/sources/upload` (or localhost:3000) → upload → wait for `parsed`/`indexed`.

- [ ] **Step 3: Re-audit**

```bash
bash bin/audit-document-storage.sh
```

Expected: `Original on disk` ≥ number of successful new uploads.

- [ ] **Step 4: Optional cleanup of dead failed row**

Only if a duplicate good upload exists: delete the failed document from Sources UI (or leave it — cosmetic).

**Do not** bulk re-upload all 61 rows (noise from dogfood tests).

---

### Task 3 (P3): Parser / Docling — **DEFER**

**Trigger to reopen:** a **new** PDF upload fails with `parser_unavailable: docling` **and** PyMuPDF fallback also fails.

Then open a dedicated plan: add Docling deps to `docker/backend.Dockerfile` or document “upload as `.md` / OCR externally.”

Until then: prefer `.md` or text-extractable PDF.

---

### Task 4 (P4): Wave E polish — **DEFER**

Tracked in `docs/superpowers/plans/2026-07-28-confirmed-findings-remediation.md` (E1–E5) and PX-5 Wave E backlog. Not part of this ops plan.

---

## Weekly 10-minute checklist

```text
[ ] docker compose ps — all Up
[ ] /health + /ready
[ ] chat ping → 200
[ ] bash bin/audit-document-storage.sh — no surprise new failures
[ ] if code changed this week → rebuild backend (Task 1)
[ ] if you needed a PDF download and it 404’d → curated re-upload (Task 2)
```

---

## Acceptance: “ops-perfect” vs “product-perfect”

| Bar | Criteria | Status target |
|-----|----------|---------------|
| **Ops-perfect (this plan)** | Tasks 0+1 habit; P1 only if needed; P3/P4 deferred | Achievable today |
| **Product-perfect** | Wave E + auth + human beta cohort + GA | Separate program |

---

## Out of scope

- Rebuilding entire corpus blindly  
- Committing secrets / `docker-compose.override.yml`  
- Enabling Docling “just in case”  
- Wave E implementation
