# Lessons Learned

> Derived from the M0/M1 specs, plans, ADRs, promotion gates, and `plans/builder/STATE.yaml`. These are patterns that worked (or bit us) and should guide future milestones.

## What worked

1. **Seam-first beats agents-first.** M1's explicit goal was *not* "have agents
   early" but to **freeze the orchestration seam** (LangGraph + checkpointer +
   `ConversationService` + SSE + RunContext) with a single node, so M2–M18 extend
   the graph instead of rewriting `/chat`. (M1 spec §1.) This is the highest-leverage
   decision in the project.
2. **Additive contract evolution.** M1 needed streaming but `GraphState`/`generate()`
   were frozen. The answer was additive: add `astream`/`TokenChunk`, a separate
   `RunContext`, and an external `langgraph` schema — **zero breaking changes**
   (ADR-0011/0012/0014). Reach for "extend", not "modify".
3. **Evidence-backed gates.** Nothing was self-declared; every gate item has a
   reproducible command + observed output (`docs/m0-promotion.md`,
   `docs/m1-promotion.md`). This caught real issues and made "done" objective.
4. **Dev = Prod via identical images.** The local docker-compose stack validated M1
   against **real** Vertex/Gemini before any cloud deploy, de-risking promotion.
5. **YAGNI as a first-class decision (ADR-0013).** Refusing to populate `vertex-config`
   avoided a second config source of truth. Defer until a concrete need.
6. **Keep the system of record singular.** `messages` is the chat truth; the
   checkpoint is derived/rebuildable. This avoided a "two sources of truth" bug and
   let the node skip an `add_messages` reducer (kept `GraphState` frozen).
7. **Parallel builds need hard isolation.** Worktrees + `file_locks` +
   one-owner-per-wave + sync barriers prevented overlapping edits.

## What bit us (and the fix)

1. **SSE framing (CRLF).** The first client parser mishandled CRLF frames → fixed +
   regression test (`f26885c`). Lesson: SSE clients must be CRLF- and
   frame-boundary-robust.
2. **Runs stuck `running` on disconnect.** Needed `AgentRun` finalization on **every**
   path; fixed with `asyncio.shield` in a `finally` (status `cancelled`) (`7fa7ba1`).
   Lesson: always finalize run/step records in `finally`.
3. **Vertex streaming usage missing.** LiteLLM's Vertex stream didn't surface a usage
   chunk → `agent_runs.output = {}`. Needs `stream_options={"include_usage": True}`.
   Lesson: verify provider streaming returns usage before relying on it.
4. **Cloud Build org policy.** `gcloud builds submit` → PERMISSION_DENIED; worked
   around with `docker buildx`. Lesson: validate CI IAM/org-policy early.
5. **Async engine deps.** The async SQLAlchemy engine needed
   `sqlalchemy[asyncio]`+greenlet (`9ae5e4a`). Lesson: pin the async extras explicitly.
6. **Streaming path test gap.** `ConversationService.stream_turn` ended up validated
   only via live smoke, not a unit test. Lesson: add an integration test for the
   streaming path (carry into M2).

## Meta-lessons
- **Write the IS-NOT list.** Both specs spend as much effort on anti-goals as goals;
  this is what kept scope honest.
- **The plan is the analysis.** For M1 the written plan replaced wave-1 explorers
  (STATE note) — a detailed TDD plan can stand in for an exploration wave.
- **Record deferrals where they'll be found** — gate "known follow-ups" + open
  questions, so they resurface at the right milestone.
