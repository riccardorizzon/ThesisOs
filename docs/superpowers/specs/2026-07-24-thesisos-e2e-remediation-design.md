# ThesisOS End-to-End Remediation Design

**Date:** 2026-07-24  
**Status:** Approved for implementation planning  
**Plane:** Product — `backend/app/`, `frontend/`, product E2E and local deployment ingress  
**Objective:** Correct every actionable defect found by the July 24 real-user E2E audit, preserve the active thesis, and repeat the complete product simulation with evidence.

## 1. Scope and decisions

This remediation covers the audit findings in five independently testable waves:

1. Browser API routing and streaming reliability.
2. Thesis data integrity and lifecycle.
3. Academic sources, citations, uploads, and notes.
4. Product UX polish.
5. Targeted data cleanup and full E2E requalification.

Operator decisions:

- Use a contract-first, wave-based remediation rather than isolated patches.
- Keep the application unauthenticated for now; public-ingress authentication is an accepted residual risk and is not part of this change.
- Hide `/research/guided` until a complete guided trail exists.
- Add hard deletion for user-created theses with double confirmation.
- Protect `thesis-agent` and `demo-thesis` from project deletion.
- Put manual notes inside Knowledge rather than adding a top-level navigation module.
- Keep uploaded sources as candidates until the user explicitly adds them to the bibliography.
- Block applying AI output with unlinked author-date citations, while preserving an explicit override.
- Rebuild the demo from synthetic, neutral content; do not derive it from the owner’s thesis.
- Clean only known demo/QA data. Preserve `thesis-agent`, `thesis-002`, and every project not explicitly whitelisted.

## 2. Non-goals

- No authentication, user accounts, or session-login system.
- No Engineering Runtime, ASEP governance, Runtime Constitution, or file-SoR changes.
- No completion of the guided-research feature.
- No broad redesign of the six-module information architecture in ADR-0036.
- No destructive cleanup based on titles, text patterns, dates, or heuristics.
- No mutation of the real thesis during automated tests.

## 3. Global invariants

### 3.1 Data safety

- `thesis-agent` cannot be deleted by service, API, UI, maintenance script, or data migration.
- `demo-thesis` cannot be deleted as a project; only its synthetic demo content may be replaced.
- Project deletion requires an exact project-id confirmation in the API request.
- The UI requires two operator actions: open the destructive dialog, then type the requested confirmation value.
- Cleanup may delete only exact project IDs `thesis-003` and `thesis-004` and may reset only rows scoped to `demo-thesis`.
- Before cleanup, create a PostgreSQL backup and a read-only snapshot of `thesis-agent` counts and deterministic content hashes for projects, chapters, chapter versions, documents, chunks, sources, conversations, messages, memories, notes, proposals, and citations.
- After cleanup and after E2E qualification, reproduce the snapshot and require equality.

### 3.2 Project isolation

- Every read and write remains scoped by `project_id` per ADR-0047 INV-MTW-2.
- Browser clients derive scope from the active project helper; SSR derives scope from the active-project cookie.
- Destructive tests use an ephemeral project and remove it through the public product contract.
- Existing direct FastAPI paths remain backward compatible.

### 3.3 Product behavior

- No raw JavaScript, JSON parsing, SQL, parser, milestone, or stack-trace text is rendered to a user.
- No operation may report success unless its durable write completed.
- No user-authored chapter may become hidden or protected because of its title.
- No disabled or incomplete capability is advertised as available.

## 4. Wave 1 — Browser API and streaming reliability

### 4.1 Dedicated browser namespace

The browser API base becomes `/api`.

- Browser: `apiBaseUrl()` returns `/api`.
- SSR and backend-to-backend calls continue to use `INTERNAL_API_BASE_URL` or `NEXT_PUBLIC_API_BASE_URL`.
- Next rewrites `/api/<backend-path>` to `<backend-upstream>/<backend-path>`.
- nginx proxies `/api/` to FastAPI after stripping `/api`.
- Existing direct ingress paths such as `/chat` and `/documents` remain available for backwards-compatible external API clients.
- Legacy UI routes `/chat`, `/documents/*`, and `/memory/*` continue to redirect for browser navigation without colliding with product API requests.

The API-prefix registry remains the single frontend list of proxied backend surfaces. Tests must prove:

- every frontend browser client emits `/api/...`;
- `/chat` navigation still redirects to `/ai`;
- `/api/chat` never redirects;
- `/api/documents` and `/api/memory` return JSON;
- nginx and Next cover the same backend paths.

### 4.2 Defensive streaming contract

Create one shared streaming-response guard used by chat and writing actions:

- Reject non-2xx responses before reading the body.
- Require `Content-Type: text/event-stream`.
- Map known statuses (`409`, `413`/`422`, `503`) to stable Italian messages.
- Map unknown statuses and malformed streams to a generic retryable error.
- Treat a stream ending without `done` or `error` as an interrupted response.
- Preserve `AbortError` as user cancellation, not a failure.

The chat UI must:

- show a visible progress state;
- expose an “Interrompi” action while streaming;
- remove an empty optimistic assistant bubble on failure;
- show a retryable error rather than hanging silently.

### 4.3 Document and memory clients

Document and memory clients use `/api`, validate response content types, and map technical failures to product copy. `DocumentIndexStatusBanner` accepts both historical `parsed` and canonical `indexed` terminal states and never renders exception text.

## 5. Wave 2 — Data integrity and lifecycle

### 5.1 Chapter provenance by project, not title

Remove dogfood title blocklists and title-substring quarantine logic.

- `owned` and `all` scopes return every chapter in the requested owned project.
- `demo` scope returns chapters scoped to `demo-thesis`.
- Demo chapters are non-deletable because their project is `demo-thesis`.
- Migration seeds may remain protected only through stable migration metadata already embedded in their content, never through user-visible title matching.
- Titles such as “Prova”, “Craftsmanship”, “Reti neurali”, and “E2E export” are valid user titles.

### 5.2 Chapter validation

Chapter create and title update:

- trim surrounding whitespace;
- reject empty-after-trim titles;
- enforce a maximum length of 200 characters;
- return 422 for invalid input;
- apply the same constraints in the create/edit UI.

### 5.3 Synthetic demo and idempotent copy

`demo-thesis` contains a small synthetic outline:

1. Introduzione
2. Quadro teorico
3. Metodologia
4. Analisi
5. Conclusioni

Demo content is neutral and synthetic. `copy-demo-structure`:

- reads only chapters whose `project_id` is `demo-thesis`;
- copies title, hierarchy, and order, but not authored content;
- compares normalized titles inside the destination project;
- is idempotent across repeated calls;
- never searches all projects and never uses title markers.

### 5.4 Project deletion

Add `DELETE /projects/{project_id}` with a body containing
`confirmation_project_id`.

- Return 403 for `thesis-agent` and `demo-thesis`.
- Return 404 for unknown projects.
- Return 422 when confirmation does not exactly match.
- Delete only rows with the target `project_id`, in one transaction.
- Use this dependency order: `agent_steps` for scoped `agent_runs`; scoped
  `agent_runs`; `messages`; `conversations`; `proposals`; `citations`; `notes`;
  embeddings for scoped document chunks; `chunks`; `sources`; `documents`;
  `chapter_versions`; `chapters`; `memory_versions`; `memories`;
  `concept_source_links` and `concept_relations`; `concepts`; `tasks`; `events`.
  Each child selection is derived from an already project-scoped root ID.
- Remove the project registry row last.
- Roll back the entire transaction on any failure.

The settings UI exposes deletion only for deletable owned projects. After success, it clears project-scoped browser state, activates `thesis-agent`, and navigates home.

### 5.5 Conversation lifecycle

- A new conversation starts as “Nuova conversazione”.
- After the first user message is durably written, generate a deterministic title from collapsed message text, capped at 72 characters without an extra LLM call.
- Add project-scoped rename and delete endpoints.
- Conversation deletion removes its messages and related run/checkpoint state according to existing foreign-key contracts.
- The conversation list exposes rename and delete controls and groups long histories without rendering hundreds of indistinguishable rows.

## 6. Wave 3 — Academic workflows

### 6.1 Linked citation validation

Extend deterministic validation with `unlinked_author_date`.

- Parse parenthetical and narrative author-date forms used by ThesisOS outputs.
- Normalize accents, punctuation, `&`, “e”, and multi-author surnames.
- Match against approved bibliography sources in the active project.
- Numeric citations remain invalid.
- A well-formed but unmatched citation is a blocking AI-application issue.
- After generation, the writing panel calls the project-scoped citation-validation
  API and keeps “Applica” disabled while validation is pending. Local validation
  remains an immediate format check, not the authority for project linkage.
- The writing UI shows the unmatched citation and suggests linking or adding a source.
- “Applica comunque” remains available and is explicit.
- Manual chapter editing and autosave remain unblocked.

Backend and frontend validators use the same fixtures and semantic rules.

### 6.2 Candidate-to-bibliography promotion

Add a project-scoped source action that changes an uploaded source from
`candidata` to `approvata`.

- The source list/detail explains candidate status.
- User-uploaded candidates expose “Aggiungi alla bibliografia”.
- The action is idempotent.
- Bibliography export includes approved sources only.
- An empty export state explains that candidate sources must be added first.
- Missing year is represented consistently as `n.d.`; title and author remain editable through the source/document metadata contract.

### 6.3 Notes inside Knowledge

Knowledge gains two internal views: “Concetti” and “Note”.

- “Concetti” preserves the current default.
- “Note” reuses project-scoped memory/note clients and supports create, list, edit, pin, version history, and delete.
- `/memory` remains a legacy redirect to `/knowledge?view=notes`.
- No new top-level navigation item is introduced, preserving ADR-0036 INV-IA-1.

### 6.4 Upload contract

Supported formats are PDF, EPUB, DOCX, Markdown, and plain text.

- UI copy, file input accept list, TypeScript unions, OpenAPI behavior, and backend parser allowlist agree.
- Unsupported extensions or MIME types return 415 before document creation.
- PDF uploads require a PDF signature and a successful parser-open preflight.
- A disguised text file named `.pdf` fails immediately with a product-safe message.
- Historical `text`, `markdown`, `parsed`, and `indexed` values remain readable.

## 7. Wave 4 — UX polish

### 7.1 Onboarding

The coach-mark backdrop does not intercept unrelated pointer input. The empty-state “Crea capitolo” action remains operable, and the tutorial can be skipped by pointer or keyboard.

### 7.2 Guided research

- Remove the guided card and “trail guidato” promise from the Research hub.
- `/research/guided` redirects to `/research`.
- Remove it from the public product-route registry.
- Preserve the implementation files only if they are not loaded or advertised.

### 7.3 Prefetch and navigation

Disable automatic Next prefetch for high-cardinality chapter, source, and concept lists. Normal navigation remains client-side. This avoids dozens of aborted RSC requests without changing user behavior.

### 7.4 Session indicator

- Initialize a session start when absent.
- Display `<1m` during the first minute, then elapsed whole minutes.
- Refresh on the minute boundary.
- Preserve proposal-count behavior.
- Do not claim a duration when storage is invalid.

### 7.5 Progress and cancellation

Chat and writing AI surfaces use consistent “Generazione in corso” copy, accessible live regions, and a visible cancel action. Cancellation leaves durable runs in `cancelled`, preserves the user message, and does not create an empty assistant message.

## 8. Wave 5 — Cleanup and qualification

### 8.1 Cleanup order

1. Stop new mutations.
2. Create a timestamped PostgreSQL backup.
3. Record the protected `thesis-agent` snapshot.
4. Reset only `demo-thesis` content and insert the synthetic seed.
5. Delete exact QA projects `thesis-003` and `thesis-004` through the tested project-deletion contract.
6. Preserve `thesis-002` and all other projects.
7. Record and compare the protected snapshot.

Any mismatch stops the process and restores from backup before further work.

### 8.2 Automated qualification

Each behavior is implemented red-green-refactor. Final evidence includes:

- focused frontend Vitest suites;
- focused backend pytest suites against `thesisos_test`;
- project-isolation and destructive-operation integration tests;
- TypeScript typecheck and backend lint;
- schema/contract drift and isolation gates;
- full `make ci`;
- Playwright product journey on an ephemeral thesis:
  - create/switch/delete thesis;
  - upload and index each supported format;
  - reject invalid files;
  - search/RAG and citations;
  - create/edit/autosave chapter;
  - rewrite/verify/find-sources/expand;
  - queue/review/accept/reject proposal;
  - bibliography promotion/export;
  - notes CRUD/versioning;
  - chat continuity, rename/delete, context switching;
  - concurrent turn rejection, abort, maximum input, and malformed inputs;
  - demo exploration and copy idempotency;
  - legacy navigation redirects and `/api` non-collision.

### 8.3 Real-stack requalification

Rebuild and restart Docker, then repeat the original human E2E simulation against
`http://localhost:3000`.

- Automated destructive actions use only the ephemeral test project.
- `thesis-agent` is read-only during qualification.
- Capture screenshots and network/error logs for all primary surfaces.
- Require no unexpected 4xx/5xx, no uncaught console errors, no raw exception banners, and no cross-project retrieval.
- Compare the protected snapshot one final time.

## 9. Audit issue coverage

- C1, H1, E2: dedicated `/api` browser boundary.
- C2: defensive SSE contract and visible failure states.
- H2: project-based chapter provenance.
- H3: synthetic demo, idempotent copy, targeted cleanup.
- H4: conversation title, rename, delete, and manageable history.
- M1: linked author-date validation.
- M2: protected hard project deletion.
- M3: non-blocking coach marks.
- M4: chapter title constraints.
- M5: explicit bibliography promotion and empty-state explanation.
- M6: aligned upload allowlist and content preflight.
- L1: canonical status handling and product-safe errors.
- L2: targeted prefetch suppression.
- L3: accurate session duration.
- L4: hidden guided-research stub.
- E1: intentionally deferred by operator decision.
- E3: Notes view inside Knowledge.
- E4: consistent progress and cancellation.

## 10. Completion rule

The remediation is complete only when:

- every non-deferred issue above has an automated regression test;
- all final gates and the repeated real-user journey pass;
- `thesis-agent` pre/post snapshots match;
- the demo contains only the approved synthetic seed;
- QA projects created by the audit and requalification are absent;
- no known finding is silently relabeled as fixed without runtime evidence.
