# Recurring Problems & Playbooks

> Patterns that recur during ThesisOS development, with the standard fix. Sources: M1 review fixes (`plans/builder/STATE.yaml`, commits), specs §8/§11, ADRs.

## P1 — "I need to change a frozen contract"
**Symptom:** a milestone seems to require a new `GraphState` field, a wider
`TokenChunk`, or a domain schema change.
**Playbook:** Stop. Try the **additive** path first (new method, new value object,
new external schema) — that's how M1 added streaming/RunContext/langgraph without
breaking anything. If a frozen contract genuinely must change, write a **new ADR**
that supersedes the old one; do not silently edit. (ADR-0001/0007/0011/0014.)

## P2 — SSE streaming breakage
**Symptom:** garbled/missing tokens, client never finalizes, frames split wrong.
**Playbook:** Ensure CRLF-safe framing and correct frame boundaries (blank-line
split); ignore `ping`; finalize on `done`; surface `error`. There's a regression
test (C1). Keep the named-event protocol (`token/ping/done/error`).

## P3 — Orchestration run left in `running`
**Symptom:** `agent_runs.status` stuck after a crash/disconnect.
**Playbook:** Finalize the run on **every** exit path. Use `try/except/finally` with
`asyncio.shield` for the disconnect/cancel path (status `cancelled`). Pattern is in
`ConversationService` (I1 fix).

## P4 — Blocking the event loop on the streaming path
**Symptom:** stalls/latency during streaming.
**Playbook:** Use the **async** DB session (`session_async.py`, psycopg3) on the
request/stream path; never the sync engine there.

## P5 — Concurrent runs corrupting a conversation
**Symptom:** two streams writing the same conversation.
**Playbook:** One active run per conversation. Acquire the in-process lock for the
**whole turn**, assign new conversations a server id up front, reject the second
with `409 conversation_busy`. Release in `finally`. (spec §8/§11.)

## P6 — LLM not configured
**Symptom:** chat called without Vertex/ADC.
**Playbook:** `get_llm_client()` returns `NotConfiguredLLM`; `/chat` returns `503
llm_not_configured` **before** opening the stream (or `event: error` if already
open). Never a stack trace. (ADR-0013, spec §8.)

## P7 — Drift test fails after adding external tables
**Symptom:** schema drift test red because a tool created tables.
**Playbook:** Put tool tables in their **own schema** (ADR-0012 pattern), create via
the tool's `setup()`, exclude from Alembic/`schema.sql`, document in `contracts/db/`.
The drift test renders only `Base.metadata`, so it stays green.

## P8 — Secrets / config sprawl
**Symptom:** tempted to add a config secret or read env vars ad hoc.
**Playbook:** `config.py` is the single source of truth for runtime LLM config; use
ADC, not API keys (ADR-0013). Add a secret only for a concrete need.

## P9 — Cloud Build PERMISSION_DENIED
**Symptom:** `gcloud builds submit` fails on org policy.
**Playbook:** Grant CB SA `run.admin`/`artifactregistry.writer`/`serviceAccountUser`;
if blocked, build with `docker buildx` (linux/amd64) and `gcloud run deploy`.

## P10 — Parallel-build merge conflicts
**Symptom:** implementer worktrees collide.
**Playbook:** One file owner per wave; smaller `owned_files`; sequence colliding
packets into separate waves; never two implementers in one worktree; sync barrier
between waves.

## P11 — Claiming "done" without proof
**Symptom:** gate item marked green without evidence.
**Playbook:** Run the command, paste the output. Verification-before-completion;
gates are evidence-backed (ADR-0010).
