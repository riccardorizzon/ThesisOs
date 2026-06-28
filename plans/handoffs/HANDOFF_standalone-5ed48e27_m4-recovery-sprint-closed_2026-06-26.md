# M4 Recovery Sprint closed — product dogfood validated; M5 authorized next

**Date:** 2026-06-26
**Status:** COMPLETED
**Bead(s):** none
**Epic:** none
**Chain:** `standalone-5ed48e27` seq `1`
**Parent:** `none — first in chain`
**Prior chain:** none — first in chain

---

## Reference Documents

- `dogfood-m4.md` — end-to-end dogfood evidence (upload → chat → follow-up)
- `docs/m4-recovery-final-report.md` — closure report (objectives, risks, M5 recommendations)
- `docs/m4-freeze.md` — **M4 pipeline frozen** (no refactor without reproducible bug + tests)
- `docs/CHANGELOG.md` — product changelog (M4 Recovery section)
- `docs/architecture.md` §6.1 — M4 runtime graph (memory → retriever → conversation)
- `knowledge/context/current-state.md` — snapshot post-recovery
- `knowledge/context/next-actions.md` — M5 active + residual backlog R4-OP/UX/M
- `plans/m5-tool-router-plan.md` — next milestone plan
- `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md` — frozen M5 spec

---

## The Goal

Recover ThesisOS M4 after **real thesis dogfood** showed CI-green code failed in production-like usage: chat answered from Gemini prior knowledge (grounding broken), large documents failed indexing (Vertex token limits), async embed failures were silent, Docker images lacked parser deps, and native markdown ingestion was missing.

Operating mode throughout: **product-first** — no ASEP/MB2 expansion, no GraphState schema changes, minimal diffs, sequential phases with user approval before implementation, regression tests + real-document validation before commits.

**End state achieved:** M4 Recovery Sprint **CLOSED**. Full workflow validated on *The Craftsman* corpus (438 chunks). User authorized M5 Tool Router **after** closure checklist; M5 not started in this session.

---

## Where We Are

### Product state (runtime, local Docker)

- Stack running: `docker compose` backend `:8000`, frontend `:3000`, Postgres with pgvector
- Primary real corpus indexed: `c31abf2c-a069-4919-b7fb-5eeb6cbebc19` — *The Craftsman full markdown*, 438 chunks, `parser=markdown`, `status=indexed`
- Secondary indexed docs: PDFs (Docling or PyMuPDF), multiple test uploads from recovery validation
- Chat: grounded answers with SSE `sources` events + inline `[N]` citations
- Memory: M2 thesis memory injects via `memory_context_node`; not persisted in message history
- **M4 pipeline frozen** per `docs/m4-freeze.md`

### Git state

- **Branch:** `main`
- **Working tree:** clean except untracked `infra/dev-vm/` (dev VM tooling, not part of recovery commits)
- **Recovery + closure commits:** 13 commits from `054331a` through `0b52c3d` (see Evidence table)

### Regression gates (repeatable)

| Command | What | Last result |
|---------|------|-------------|
| `make unit-m4-recovery` | 53 pytest tests (M4 scope) | 53/53 pass |
| `make dogfood-m4` | `bin/dogfood-m4-run.sh` E2E smoke | DOGFOOD PASS |
| `make status` | Developer cockpit snapshot | added this session |

### Phase completion summary

| Phase | Status | Key deliverable |
|-------|--------|-----------------|
| P1 Grounding | ✅ | `prompt_wire.compose_prompt_wire()` |
| P2 Parser Pipeline | ✅ | Docker `.[parsers]`, Docling `do_ocr=False` |
| P3 Embedding Reliability | ✅ | `plan_embedding_batches`, `record_index_error` |
| P4 Markdown | ✅ | `MarkdownParser`, `.md`/`.txt` |
| P5 Dogfood | ✅ | `dogfood-m4.md` |
| Closure | ✅ | freeze, changelog, backlog, final report |

### M5 state

- **Not started** — user authorized resume of product track with M5 after closure report
- Blocker for implementation: Critic §12 sign-off on frozen M5 spec (ADR-0027)
- Must respect `docs/m4-freeze.md` when rewiring graph

---

## What We Tried (Chronological)

### 1. Phase 1 investigation — grounding pipeline trace

- **Hypothesis:** `retrieved_context` populated but never consumed.
- **Method:** Read `memory_context_node` → `retriever_node` → `conversation_node` on `main`.
- **Result:** Confirmed. `conversation_node` built wire from `state.messages` only. Retriever tests passed in isolation; no end-to-end grounding test existed.
- **User approval:** Investigation report approved; requested `compose_prompt_wire` helper (not ad-hoc injection in node) and 3-commit split (grounding / SSE / citations).

### 2. Phase 1 implementation — `compose_prompt_wire`

- **Changes:** New `backend/app/graph/prompt_wire.py`; `conversation_node` calls `compose_prompt_wire(state)` merging memory prefix + grounding into one system block.
- **Tests:** `backend/tests/test_grounding.py` (5 tests including persistence guard).
- **Commits:** `054331a`, `4840a3f`, `dbc2921`.
- **Dogfood:** Chat cited Sennett definition with `[5,6]`; `sources` SSE emitted; DB assistant messages lack `Sources:` block.

### 3. Phase 2 investigation — parser / Docker

- **Hypothesis:** Docling unavailable in container → unconditional PyMuPDF fallback.
- **Findings:** (a) Dockerfile lacked `.[parsers]` and `COPY contracts/`; (b) default Docling OCR init failed with `RapidOCR torch.PP-OCRv6.det.small`; (c) `libxcb` was secondary issue.
- **Fix:** Dockerfile apt libs + `.[parsers]` + contracts; `PdfPipelineOptions.do_ocr=False` for born-digital PDFs.
- **Validation:** Upload PDF → `parser=docling`, `status=indexed` (~26s first parse cold start).
- **Commits:** `b11640f`, `8f957b0`, `7b777f1`.

### 4. Phase 3 investigation — embedding batching + async observability

- **Hypothesis:** Single `llm.embed(all_chunks)` exceeds Vertex ~20k token cap; `_parse_in_background` swallows failures.
- **Confirmed on `main`:** One request for all chunks; except → `log.warning` only, doc stays `parsed`.
- **User constraints:** No retriever/pgvector/GraphState changes; deterministic batching; no magic retries; atomic index.
- **Implementation:** `plan_embedding_batches` (14k token / 250 chunk caps), `_embed_with_retry` (3 attempts, permanent errors immediate), `record_index_error`.
- **Validation:** 438 chunks → 14 batches; re-index embedded 438; failure sim → `parsed` + `index_failed:`, 0 partial embeddings.
- **Commits:** `cad84b9`, `12e039b`.

### 5. Phase 4 — markdown ingestion

- **Changes:** `MarkdownParser`, route in `parse_document`, extend `VALID_SOURCE_TYPES` + extension map.
- **Reuse:** `markdown_to_chunks()` shared with Docling export (already in `base.py` from P2).
- **Tests:** 35 document/parser tests; 5 markdown-specific.
- **Commits:** `b3a7968`, `10cac5d`.

### 6. Phase 5 — dogfood workflow

- **Script:** `bin/dogfood-m4-run.sh` (initial); hardened in closure with assertions + exit codes.
- **Evidence:** `dogfood-m4.md`; live run upload → index → search → memory → chat → follow-up PASS.
- **Commit:** `b39fcbb`.

### 7. Closure checklist (user-requested)

- Working tree clean (except `infra/dev-vm/`)
- Updated `docs/architecture.md`, `docs/CHANGELOG.md`, `knowledge/context/*`
- Residual backlog in `next-actions.md` (R4-OP1/2/3, R4-UX1/2, R4-M1/2)
- `make dogfood-m4`, `make unit-m4-recovery` Makefile targets
- `docs/m4-freeze.md`, `docs/m4-recovery-final-report.md`
- **Commit:** `0b52c3d`

### 8. Operational blockers encountered (not product bugs)

- **Docling cold start ~26s** — first PDF parse loads 770 torch weights; shell timeouts interrupted validation until explicit 5min timeout.
- **Docker rebuild 7–12 min** — Docling ML deps; background builds completed but slow feedback loop.
- **No local `python3-venv`** on dev VM — tests run via Docker `python:3.12-slim` container with `--network host` + Postgres.
- **`test_packaging.py` path** — fails when only `backend/` mounted; fixed with ancestor walk + skipif.

---

## Key Decisions

1. **`compose_prompt_wire()` centralizes prompt assembly** — rejected ad-hoc grounding injection inside `conversation_node`; rejected separate grounding system message (user requested single composed wire).
2. **Three-commit split for P1** — grounding pipeline / SSE sources / citation metadata independently testable (user mandate).
3. **Docling `do_ocr=False`** — rejected fixing RapidOCR config (M3 defers scanned PDF OCR); born-digital thesis PDFs parse cleanly; PyMuPDF remains PDF fallback.
4. **Batch caps 14k tokens / 250 chunks** — headroom under Vertex ~20k; rejected unbounded single request (root cause of 438-chunk failure).
5. **Retry only transient errors** — `400`/`BadRequest`/`INVALID_ARGUMENT` fail immediately; rejected blind retry on permanent errors.
6. **Index failure = `parsed` + `error_message`** — rejected new DB status enum; `index_failed:` prefix in `error_message` (no schema migration).
7. **Embeddings written only after all batches succeed** — preserves atomicity; partial vectors never flushed mid-failure.
8. **M4 pipeline frozen post-recovery** — no further retrieval/grounding/embedding refactors except reproducible bugs + regression tests (user closure mandate).
9. **Product-first over ASEP** — MB2 deferred; M5 next; dogfood as advancement criterion.
10. **Rejected starting M5 in same session** — user wanted closure checklist + final report before M5.

---

## Evidence & Data

### Recovery commit log

| Hash | Summary |
|------|---------|
| `054331a` | fix(m4): wire retrieved_context via prompt_wire composer |
| `4840a3f` | feat(m4): SSE sources events |
| `dbc2921` | feat(m4): GraphState.citations propagation |
| `b11640f` | fix(m4): Docker parsers + contracts |
| `8f957b0` | fix(m4): Docling do_ocr=False |
| `7b777f1` | test(m4): packaging Dockerfile path fix |
| `cad84b9` | fix(m4): batch embeddings under Vertex limits |
| `12e039b` | fix(m4): record_index_error async observability |
| `b3a7968` | feat(m4): native markdown/text ingestion |
| `10cac5d` | test(m4): markdown regression tests |
| `b39fcbb` | docs(m4): dogfood-m4.md + runner script |
| `0b52c3d` | docs(m4): closure — freeze, changelog, backlog |

### Test counts

| Suite | Count | Result |
|-------|------:|--------|
| M4 recovery (`make unit-m4-recovery`) | 53 | pass |
| Full backend (with Postgres) | 140+ | 7 failures unrelated (memory DB pollution, uncommitted scope) |
| Phase 4 document tests | 35 | pass |

### Craftsman full markdown — embedding batch plan (P3 validation)

```
chunks=438  batches=14  budget=(14000 tokens, 250 count)
 batch  1: n=37  est_tokens=13866
 batch  2: n=34  est_tokens=13759
 ...
 batch 14: n=31  est_tokens=13756
```

Re-index result: `embedded=438`, `status=indexed`, `embeddings=438`.

### Dogfood chat sample (P5)

- Turn 1: `"desire to do a job well for its own sake" [5]` referencing *Dogfood M4 Sennett excerpt*
- Turn 2: follow-up on motivation with citations `[2,3,4,7]`
- `sources` SSE: 10 chunks with metadata per turn
- DB persistence: `Sources: False` in assistant message content

### Document IDs (live environment)

| ID | Title | Chunks | Parser | Status |
|----|-------|-------:|--------|--------|
| `c31abf2c-a069-4919-b7fb-5eeb6cbebc19` | The Craftsman full markdown | 438 | markdown | indexed |
| `8246a26d-f148-4594-9f13-8e2edb968e19` | Dogfood M4 Sennett excerpt | 1 | markdown | indexed |

### Regression test file inventory

```
tests/test_grounding.py           — 5
tests/test_embedding_batching.py  — 8
tests/test_retrieval_service.py   — 7 (+ batch failure, multi-batch)
tests/test_index_observability.py — 2
tests/test_markdown_ingestion.py  — 5
tests/test_document_parsers.py    — 8
tests/test_retriever_node.py      — 3
tests/test_search_api.py          — 3
tests/test_packaging.py           — 2
```

---

## Code Analysis

### Graph topology (frozen)

```text
START → memory_context_node → retriever_node → conversation_node → END
```

### `compose_prompt_wire(state)` — `backend/app/graph/prompt_wire.py`

- Splits leading system messages (M2 memory prefix) from conversation tail
- Appends `render_grounding_prompt(retrieved_context)` into combined system block
- `format_grounding_sources()` for SSE metadata

### `plan_embedding_batches(texts, max_tokens=14000, max_count=250)`

- Uses `estimate_tokens()` = `len(text)//4`, min 1
- Preserves order; indices reassembled after batch embed calls
- Single chunk >14k still one batch (residual risk R4-M2)

### `_embed_with_retry(texts)` — max 3 attempts, backoff 0.5s × attempt

- Permanent: substring match `BadRequest`, `INVALID_ARGUMENT`, `400`
- `NotImplementedError` from LiteLLM → `EmbedFailedError`

### `record_index_error(document_id, message)`

- Sets `error_message = f"index_failed: {message}"[:2000]`
- Status remains `parsed`

### Parser routing — `parse_document()`

```text
markdown/text → MarkdownParser (no Docling)
pdf/docx/epub → Docling primary → PyMuPDF fallback (PDF only)
```

### Docker — `docker/backend.Dockerfile`

- apt: libxcb1, libgl1, etc.
- `pip install ".[parsers]"`
- `COPY contracts/ /contracts/`

---

## Files Changed (session aggregate)

### Source code (recovery)

- `backend/app/graph/prompt_wire.py` — **new** prompt composer
- `backend/app/graph/conversation.py` — uses compose_prompt_wire, sources SSE, citations
- `backend/app/graph/retriever.py` — RetrievedChunk metadata passthrough
- `backend/app/schemas/graph_state.py` — optional fields on RetrievedChunk
- `backend/app/services/conversation/service.py` — forward sources SSE
- `backend/app/services/retrieval/service.py` — batching + retry
- `backend/app/services/document/service.py` — record_index_error
- `backend/app/api/documents.py` — split parse/embed error handling
- `backend/app/services/document/parsers/markdown_parser.py` — **new**
- `backend/app/services/document/parsers/__init__.py` — markdown route
- `backend/app/services/document/parsers/docling_parser.py` — do_ocr=False
- `backend/app/services/document/parsers/base.py` — markdown_to_chunks shared
- `backend/app/schemas/document.py` — markdown/text source types
- `docker/backend.Dockerfile` — parsers + contracts

### Tests (recovery)

- `backend/tests/test_grounding.py`
- `backend/tests/test_embedding_batching.py`
- `backend/tests/test_index_observability.py`
- `backend/tests/test_markdown_ingestion.py`
- `backend/tests/test_retrieval_service.py` — extended
- `backend/tests/test_document_service.py` — markdown + format guard fix
- `backend/tests/test_document_api.py` — unsupported format fix
- `backend/tests/test_packaging.py`

### Docs & tooling (closure)

- `dogfood-m4.md`
- `docs/m4-recovery-final-report.md`
- `docs/m4-freeze.md`
- `docs/CHANGELOG.md`
- `docs/m4-promotion.md` — recovery addendum
- `docs/architecture.md` §6.1
- `knowledge/context/current-state.md`
- `knowledge/context/next-actions.md` — residual backlog
- `bin/dogfood-m4-run.sh` — hardened E2E runner
- `bin/status.sh` — developer cockpit
- `Makefile` — `status`, `unit-m4-recovery`, `dogfood-m4`

### Untracked (not committed)

- `infra/dev-vm/` — create-vm.sh, README.md

---

## User Feedback & Preferences (REQUIRED)

1. **Product-first trial** — ThesisOS = feature acceleration; ASEP = maintenance; 3-condition gate for ASEP changes.
2. **Do not expand ASEP/MB2/constitution** unless real product blocker meets 3-condition gate.
3. **Sequential phases** — investigate → root cause → propose → **wait for approval** → implement → test → dogfood → commit.
4. **Phase 1 adjustment:** use `compose_prompt_wire` helper, not independent grounding system message in conversation_node.
5. **Phase 1 commit split:** grounding / SSE sources / citations — independently testable.
6. **Phase 3 constraints:** no retriever/pgvector/schema changes; no magic retries; atomic indexed status.
7. **Regression tests mandatory** every phase; validate on real thesis documents before commit.
8. **No merge until validation** — report before merge authorized.
9. **Approved M4 Recovery closure** then M5 — not M5 before closure checklist.
10. **Distinguish residual backlog:** operational vs UX vs maintenance (explicit in closure request).
11. **Freeze M4 pipeline** — no further refactoring except reproducible bugs.
12. **Dogfood continuous** as primary advancement criterion for M5+.
13. **Italian language** used in several steering messages — user comfortable with Italian for process/review.
14. **Operational issues (cold start, Docker build, no venv)** are productivity not architecture — don't prioritize unless blocking milestones.

---

## Where We're Going

1. **M5 Tool Router** — obtain Critic §12 sign-off on frozen M5 spec (ADR-0027); then implement supervisor/planner/router per `plans/m5-tool-router-plan.md`.
2. **Graph rewire** — extend graph *before* retriever; keep M4 nodes frozen (`docs/m4-freeze.md`); `route=grounded_chat` uses existing retriever path.
3. **Gate every M5 increment** — `make unit-m4-recovery` + `make dogfood-m4` green before promotion.
4. **M6 Writing** follows M5 — usable thesis product line (M1–M6).
5. **UX backlog R4-UX1** — frontend `sources` SSE panel; likely M6 workspace, not M5 blocker.
6. **Maintenance R4-M1** — re-index legacy `parsed` documents stuck from pre-P3 failures.

---

## Risks & Blockers

| Risk | Severity | Mitigation |
|------|----------|------------|
| M5 graph rewire breaks grounding | Medium | M4 freeze + dogfood gate |
| Critic §12 not signed | High | Blocks M5 implementation start |
| Frontend no sources UI | Medium | Backlog R4-UX1; backend ready |
| Chunk >14k tokens | Low | R4-M2; rare with current chunking |
| `infra/dev-vm/` untracked | Low | Decide commit or gitignore next session |
| Dev VM no python3-venv | Low | Continue Docker-based pytest |

---

## Open Questions

1. **M5 start scope** — full graph rewire vs incremental supervisor node first?
2. **`infra/dev-vm/`** — commit to repo or keep local tooling?
3. **Tag `m4-recovery-complete`?** — user did not request git tag; only commits on main.
4. **Re-index legacy docs** — one-shot script vs manual `/documents/{id}/index`?

---

## Quick Start for Next Session

```bash
# Verify stack
make up
make status
curl -fsS http://localhost:8000/health

# M4 regression (must stay green during M5)
make unit-m4-recovery
make dogfood-m4

# Read closure + freeze before touching graph
cat docs/m4-freeze.md
cat docs/m4-recovery-final-report.md

# Key files for M5 planning
docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md
plans/m5-tool-router-plan.md
backend/app/graph/conversation.py   # current graph build_graph()
decisions/ADR-0027-*              # if exists

# Real corpus sanity
curl -s http://localhost:8000/documents/c31abf2c-a069-4919-b7fb-5eeb6cbebc19 | jq .status,.chunk_count,.parser

# Next action
Obtain Critic §12 sign-off on M5 spec, then implement supervisor node (T055)
without modifying frozen M4 nodes per docs/m4-freeze.md
```

---

## Pre-Recovery Bug Symptoms (what dogfood showed)

These were the **original blocking issues** that triggered the recovery sprint. All four are fixed and regression-tested; listed here so the next session does not re-investigate closed bugs.

| Symptom | Root cause (confirmed) | Fix location |
|---------|------------------------|--------------|
| Chat answers from Gemini prior knowledge, not corpus | `conversation_node` ignored `retrieved_context` | `prompt_wire.compose_prompt_wire()` |
| Large doc (438 chunks) fails indexing silently | Single `llm.embed(all)` exceeds Vertex ~20k token cap | `plan_embedding_batches()` |
| Doc stuck at `parsed` after embed failure | `_parse_in_background` logged warning only | `record_index_error()` |
| PDF always `parser=pymupdf` in Docker | Missing `.[parsers]`, Docling OCR init crash | `docker/backend.Dockerfile`, `do_ocr=False` |
| `.md` upload rejected or wrong parser | No native markdown route | `MarkdownParser` |

---

## Failed Approaches (do not retry)

1. **Separate grounding system message in conversation_node** — user rejected; wanted single composed wire via helper.
2. **Fix RapidOCR / torch PP-OCRv6 for Docling** — deferred to M3 scanned-PDF scope; `do_ocr=False` sufficient for born-digital thesis PDFs.
3. **New DB status enum for index failures** — rejected; use `parsed` + `index_failed:` prefix in `error_message`.
4. **Unbounded embed retry on all errors** — rejected; permanent 400/BadRequest must fail fast.
5. **GraphState schema changes for grounding** — rejected for recovery; used transient system message composition instead.
6. **Starting M5 before closure checklist** — user explicitly deferred until freeze + final report complete.
7. **ASEP/MB2 work during recovery** — blocked by product-first operating mode.

---

## M4 Freeze Reference (verbatim scope)

From `docs/m4-freeze.md` — **forbidden without new ADR:**

- GraphState field additions for retrieval/grounding
- Bypassing retriever to inject chunk text into `/chat`
- Changing pgvector partition strategy (ADR-0024)
- Replacing batching with unbounded single-request embed calls

**Allowed:** bug fixes + regression tests + dogfood; additive contracts not altering frozen GraphState fields; M5 graph extensions that **consume** `retrieved_context` without rewriting M4 nodes.

---

## Residual Backlog (registered, not in scope of recovery)

Copied from `knowledge/context/next-actions.md` §M4 Recovery residual — pull only when blocking product milestones.

### Operational

| ID | Item | Notes |
|----|------|-------|
| R4-OP1 | Docling cold start ~26 s | First PDF parse loads torch weights; dev UX only |
| R4-OP2 | Docker backend rebuild ~7–12 min | Docling ML deps; CI cache strategy TBD |
| R4-OP3 | No local `python3-venv` on dev VM | Tests via Docker; `make install` needs `python3.12-venv` |

### UX

| ID | Item | Milestone hint |
|----|------|----------------|
| R4-UX1 | Frontend does not render `sources` SSE | M6 workspace or M5 follow-up |
| R4-UX2 | `error_message` on `parsed` docs not prominent | M3 library route polish |

### Maintenance

| ID | Item | Notes |
|----|------|-------|
| R4-M1 | Re-index legacy `parsed` documents | Pre-P3 failures; `POST /documents/{id}/index` |
| R4-M2 | Single chunk >14k est. tokens | May fail Vertex; future M3 chunk split |

---

## Session Start Context

This session did **not** begin with a paste-prompt handoff (Tier A). No prior handoff files existed in `plans/handoffs/`. Work was initiated as **M4 Product Recovery Sprint** with explicit phase-gated workflow from user steering messages (Italian + English mix for process review).

Operating mode trial (from 2026-06-25, not ADR): ThesisOS = feature acceleration; ASEP = maintenance; 3-condition gate for ASEP changes.

---

## M5 Entry Criteria (from closure report)

Before writing M5 graph code:

1. Critic §12 sign-off on `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`
2. Read `plans/m5-tool-router-plan.md` for T055–T061 task breakdown
3. Confirm `make unit-m4-recovery` and `make dogfood-m4` green on current `main`
4. Extend graph **before** retriever; route `grounded_chat` through existing M4 path
5. Do not modify frozen modules in `docs/m4-freeze.md` table

---

## Related Handoffs

None — first handoff in chain `standalone-5ed48e27`.

---

## Identifier Staleness Check

All key identifiers verified present in codebase (grep 2026-06-26):

| Identifier | Found |
|------------|-------|
| `compose_prompt_wire` | `prompt_wire.py`, `conversation.py` |
| `plan_embedding_batches` | `retrieval/service.py`, tests |
| `record_index_error` | `document/service.py`, `documents.py` |
| `MarkdownParser` | `parsers/markdown_parser.py` |
| `do_ocr=False` | `docling_parser.py` |
| `make dogfood-m4` | `Makefile` |
| `make unit-m4-recovery` | `Makefile` |

No stale references from parent (no parent).
