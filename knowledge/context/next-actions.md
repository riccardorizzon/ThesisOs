# Next Actions — 100-task backlog

> Grounded in the repo (contracts, gates, known debt, roadmap). **Updated 2026-06-24 after M2 Phase 6.**

Legend: `[Pn]` priority · `dep:` dependency · 🔴 blocks promotion · 🟡 debt · 🟢 net-new · ✅ done.

---

## IMMEDIATE — M2 Promotion (P0)

- **T029f** [P0] 🔴 Merge `m2-memory-system` → `main`; tag `m2-complete`. dep: Phases 1–6 ✅, Critic/QA ✅
- **T029e** [P1] 🟢 Wire `MemoryUpdated` event (optional M2 close-out). dep: event bus

## M2 Phases 1–6 ✅ (completed on `m2-memory-system`)

- **T017** ✅ M2 spec frozen + ADR-0015/0017/0018
- **T019** ✅ MemoryService
- **T020** ✅ `/memory` API
- **T025** ✅ Memory Administration UI (+ Vitest T016 partial)
- **T027** ✅ Memory tests (service + API)
- **T029a–d** ✅ Phase 6 graph + Critic + QA

---

## M3 — Document System (P0 next milestone)

Requires Architect-frozen M3 spec before implementation. No embeddings, retrieval, or writer agents.

---

## A. Close M1 cloud deploy (P1 — optional parallel, non-blocking M2 tag locally)
- **T002** [P0] 🔴 Build M1 frontend image (amd64) and push to Artifact Registry. dep: T012
- **T003** [P0] 🔴 `gcloud run deploy thesisos-backend` with the M1 image (Vertex env + Cloud SQL connection already wired by Terraform). dep: T001
- **T004** [P0] 🔴 `gcloud run deploy thesisos-frontend` with the M1 image. dep: T002,T003
- **T005** [P0] 🔴 Verify `PostgresSaver.setup()` creates the `langgraph` schema + checkpoint tables on Cloud SQL at first prod boot. dep: T003
- **T006** [P0] 🔴 Apply domain migration on Cloud SQL if needed (`alembic upgrade head` via Cloud SQL proxy); confirm `0001_initial`. dep: T003
- **T007** [P0] 🔴 Live prod smoke: authenticated `POST /chat` streams real Gemini (or graceful `503`); confirm `event: token … done`, CRLF framing. dep: T003,T005
- **T008** [P0] 🔴 Verify checkpoint tables are in schema `langgraph` (not `public`) on Cloud SQL; domain tables untouched. dep: T005
- **T009** [P0] 🟡 Confirm SSE + `ping=15` survive Cloud Run buffering/idle timeouts (resolves Q3). dep: T007
- **T010** [P0] 🔴 Update `docs/m1-promotion.md`: flip `cloud_run_deploy`/`langgraph_schema_cloud` to green with evidence. dep: T007,T008
- **T011** [P0] 🔴 Merge `m1-conversation-system` → `main`, tag `m1-complete`, release `v0.0.2-m1` (`finishing-a-development-branch`). dep: T010
- **T012** [P0] 🟡 Add `ARG/ENV NEXT_PUBLIC_API_BASE_URL` to `docker/frontend.Dockerfile` before `npm run build`; pass the prod backend URL (resolves Q4). dep: —

---

## B. M1 carry-over debt (P0/P1 — small, do alongside M2 start)

- **T013** [P1] 🟡 Capture token usage on Vertex streaming (`stream_options={"include_usage": True}` or non-stream usage call) → fill `agent_runs.output.usage` (resolves Q2). dep: T011
- **T014** [P1] 🟡 Add an integration test for `ConversationService.stream_turn` (fake LLM + real/throwaway DB): user+assistant persisted, AgentRun `done`, tokens ordered. dep: T011
- **T015** [P1] 🟡 Add a test exercising the client-disconnect path → AgentRun `cancelled`. dep: T014
- **T016** [P1] 🟢 Add a frontend test runner (e.g. Vitest) + a `postChatStream` SSE-parser unit test (CRLF, partial frames). dep: T011

---

## C. M2 — Memory (P0) — Phase 6 remainder only

Tasks T017–T025, T027 largely ✅. See IMMEDIATE section above.

---

## D. M3 — Ingestion (P1) — requires frozen M3 spec first

- **T030** [P2] 🔴 Architect: freeze the M3 design spec (parsers, chunking, job flow, GCS) + ADRs. dep: T029
- **T031** [P2] Planner: M3 plan + packets. dep: T030
- **T032** [P2] 🟢 Implement durable-ish job execution behind `services/jobs/` (in-process worker now; interface ready for Cloud Run Jobs/Tasks). dep: T031
- **T033** [P2] 🟢 Realize `POST /upload` (store file in GCS `documents` bucket; create `documents` row `status=uploaded`; enqueue ingestion job). dep: T032
- **T034** [P2] 🟢 Implement ingestion pipeline: Docling / PyMuPDF / OCR → text. dep: T033
- **T035** [P2] 🟢 Chunking → `chunks` rows (chunk_index, page_from/to, section_path, token_count). dep: T034
- **T036** [P2] 🟢 Emit `DocumentUploaded` + `ChunkCreated` events. dep: T035
- **T037** [P2] 🟢 Implement the `document` graph node per `contracts/agents/document.json` (reads `task`; appends `errors`). dep: T035
- **T038** [P2] 🟢 Realize `GET /documents`, `GET /documents/{id}`. dep: T033
- **T039** [P2] 🟢 Realize `POST /summarize` (job-backed). dep: T032,T034
- **T040** [P2] 🟢 Frontend: implement the `library` route (upload, list, status, document view). dep: T033,T038
- **T041** [P2] 🟢 Tests: parse fixtures (pdf/epub/docx), chunking, job lifecycle, events, error paths (`parse_failed`,`unsupported_format`). dep: T034,T035
- **T042** [P2] 🔴 M3 promotion gate + merge + tag `m3-complete`. dep: T036,T037,T038,T039,T040,T041

---

## E. M4 — Retrieval (P2) — frozen M4 spec first

- **T043** [P2] 🔴 Architect: freeze the M4 spec — **resolve Q1** (pgvector index strategy: partition by `model`) + ADR. dep: T042
- **T044** [P2] Planner: M4 plan + packets. dep: T043
- **T045** [P2] 🟢 Implement `LiteLLMClient.embed()` for `text-multilingual-embedding-002` (was `NotImplementedError`). dep: T043
- **T046** [P2] 🟢 Embedding pipeline: embed chunks → `embeddings` (model/dimension-tagged, `owner_type='chunk'`, content_hash). dep: T045,T035
- **T047** [P2] 🔴 Implement the pgvector index strategy (partition by `model`; HNSW/IVFFlat per partition) via migration. dep: T043,T046
- **T048** [P2] 🟢 Implement hybrid search (vector + keyword) over `chunks`/`embeddings`. dep: T046,T047
- **T049** [P2] 🟢 Realize `POST /search`. dep: T048
- **T050** [P2] 🟢 Implement the `retriever` node per `contracts/agents/retriever.json` (writes `retrieved_context`). dep: T048
- **T051** [P2] 🟢 Tests: embedding determinism (fake), ranking, `embed_failed`/`no_results`, index correctness, drift (partitions excluded/handled). dep: T046,T048
- **T052** [P2] 🔴 M4 promotion gate + merge + tag `m4-complete`. dep: T049,T050,T051

---

## F. M5 — Tool Router / Orchestration (P2) — frozen M5 spec first

- **T053** [P2] 🔴 Architect: freeze the M5 spec (Supervisor→Planner→Router topology, routing rules, multi-node graph) + ADRs. dep: T052
- **T054** [P2] Planner: M5 plan + packets. dep: T053
- **T055** [P2] 🟢 Implement the `supervisor` node (reads `messages,task`; writes `plan,route`). dep: T054
- **T056** [P2] 🟢 Implement the `planner` node (reads `messages,plan`; writes `plan,task`). dep: T054
- **T057** [P2] 🟢 Implement the `router` node (reads `plan,messages`; writes `route`). dep: T054
- **T058** [P2] 🔴 Compose the multi-node graph (Supervisor→Planner→Router→{retriever,memory,…}) extending the seam; conditional edges by `route`. dep: T055,T056,T057,T050,T021
- **T059** [P2] 🟢 Populate `tasks` table from planner output (AgentOS work loop); record `agent_steps` per phase. dep: T056
- **T060** [P2] 🟢 Tests: routing decisions, plan creation, `no_objective`/`no_route`/`unplannable`, end-to-end graph traversal (fake LLM). dep: T058
- **T061** [P2] 🔴 M5 promotion gate + merge + tag `m5-complete`. dep: T058,T059,T060

---

## G. M6 — Writing (P2) — frozen M6 spec first

- **T062** [P2] 🔴 Architect: freeze the M6 spec (chapter drafting from plan+context, streaming, citation markers) + ADRs. dep: T061
- **T063** [P2] Planner: M6 plan + packets. dep: T062
- **T064** [P2] 🟢 Implement the `writer` node (reads `plan,retrieved_context,messages`; writes `draft,citations`). dep: T063,T058
- **T065** [P2] 🟢 Realize `POST /chapters` + chapter CRUD on the `chapters` tree. dep: T063
- **T066** [P2] 🟢 Frontend: implement the `workspace` route (draft editor, streamed writing, chapter view). dep: T065,T064
- **T067** [P2] 🟢 Tests: draft generation grounded in context, `empty_context`/`generation_failed`, chapter persistence. dep: T064,T065
- **T068** [P2] 🔴 M6 promotion gate + merge + tag `m6-complete` (**M0–M6 = usable product milestone**). dep: T064,T065,T066,T067

---

## H. M7 — Citations (P3)

- **T069** [P3] 🔴 Architect: freeze the M7 spec (CSL-JSON → APA7/MLA/Chicago) + ADRs. dep: T068
- **T070** [P3] 🟢 Implement CSL-JSON source ingestion into `sources`; resolve `CitationRef`→source. dep: T069
- **T071** [P3] 🟢 Implement the `citation` node (reads `draft,citations`; writes resolved `citations`). dep: T070,T064
- **T072** [P3] 🟢 Style renderers (APA7/MLA/Chicago) from CSL-JSON with locators. dep: T070
- **T073** [P3] 🟢 Realize `POST /citations`, `GET /bibliography?style=apa7`. dep: T072
- **T074** [P3] 🟢 Tests: per-style rendering, `unresolved_source`, locator handling. dep: T072
- **T075** [P3] 🔴 M7 promotion gate + merge + tag `m7-complete`. dep: T071,T073,T074

---

## I. M8 — Outline (P3)

- **T076** [P3] 🔴 Architect: freeze the M8 spec (outline/chapter tree mgmt) + ADRs. dep: T068
- **T077** [P3] 🟢 Realize `GET/PUT /outline` over the self-referencing `chapters` tree. dep: T076
- **T078** [P3] 🟢 Emit `ChapterCreated` events; chapter status workflow (planned→…→final). dep: T077
- **T079** [P3] 🟢 Frontend: implement the `outline` route (tree edit, reorder, status). dep: T077
- **T080** [P3] 🔴 M8 promotion gate + merge + tag `m8-complete`. dep: T077,T078,T079

---

## J. M9 — Critic (P3)

- **T081** [P3] 🔴 Architect: freeze the M9 spec (hallucination/redundancy review, revise loop) + ADRs. dep: T068
- **T082** [P3] 🟢 Implement the `critic` node (reads `draft,retrieved_context`; writes `critique`); emit `CritiqueCompleted`. dep: T081,T064
- **T083** [P3] 🟢 Wire the writer→critic→(revise) loop with a pass/fail gate. dep: T082
- **T084** [P3] 🟢 Tests: detects unsupported claims/redundancy, `critique.passed` gating. dep: T082
- **T085** [P3] 🔴 M9 promotion gate + merge + tag `m9-complete`. dep: T082,T083,T084

---

## K. M10 — QA (P3)

- **T086** [P3] 🔴 Architect: freeze the M10 spec (independent QA gate over outputs; `agent_steps.phase='qa'`). dep: T085
- **T087** [P3] 🟢 Implement the QA verification step/agent + evidence recording on `agent_steps`. dep: T086
- **T088** [P3] 🟢 Tests: QA blocks on red, records evidence, distinct from critic. dep: T087
- **T089** [P3] 🔴 M10 promotion gate + merge + tag `m10-complete`. dep: T087,T088

---

## L. M11 — GCP Hardening (P2–P3, partly pull-forward)

- **T090** [P2] 🟢 Full `TracerProvider` + Cloud Trace/Logging exporter + trace the LLM abstraction (every run/step traced) (resolves Q9). dep: T011
- **T091** [P2] 🟢 Durable job queue: move `services/jobs/` to Cloud Run Jobs / Cloud Tasks (resolves Q5). dep: T032
- **T092** [P3] 🟢 Reassess Cloud SQL instance size under ingestion/embedding load (resolves Q6). dep: T042,T052
- **T093** [P3] 🟢 Cloud Run cold-start mitigation (min instances/warmups) (resolves Q7). dep: T011
- **T094** [P2] 🟢 Re-enable Cloud Build CI with correct CB SA roles (resolves Q8). dep: T011
- **T095** [P3] 🟢 Consider encrypted remote Terraform backend (GCS) for state (DB password) (R10). dep: —
- **T096** [P3] 🔴 M11 promotion gate + merge + tag `m11-complete`. dep: T090,T091,T094

---

## M. M12–M18 — Autonomy track (P4) — each needs a frozen spec

- **T097** [P4] 🟢 M12 Multi-Agent: full Supervisor-led execution; per-agent token accounting via `RunContext`/`agent_runs`. dep: T058,T013
- **T098** [P4] 🟢 M13/M14: freeze specs for Research mode + NotebookLM-like experience (resolves Q11). dep: T068
- **T099** [P4] 🟢 M15–M16: editable knowledge base + reintroduce Mem0-style auto-extraction over custom memory (resolves Q12). dep: T029
- **T100** [P4] 🟢 M17 Voice + M18 Autonomous Assistant: freeze specs; close the full AgentOS loop (observe→…→promote autonomously). dep: T097,T099

---

## How to use this list
- Work **top-down by priority**; never start a milestone's implementation tasks
  before its design spec is frozen (the `Txxx Architect: freeze …` task) and the
  previous milestone is tagged.
- Each milestone ends with a 🔴 gate+merge+tag task — that is its definition of done.
- Update task statuses here and in `context/current-state.md` as work completes; move
  resolved open questions to `decisions/`.
