# Open Questions

> Consolidated from M0 spec §19, M1 spec §11, `docs/m1-promotion.md` (known non-blockers), and STATE. Each has an owner milestone where it gets resolved. Closed questions move to `decisions/`.

## Resolved in M1 (now decisions)
- LiteLLM↔Vertex streaming shape → mapped to `TokenChunk` (works; usage chunk
  missing, see Q2). → `decisions/technical-decisions.md`.
- Async DB driver → psycopg3 async session. → resolved.
- PostgresSaver custom schema → `langgraph` schema works (ADR-0012). → resolved.
- Concurrent streams on one conversation → in-process whole-turn lock + `409`. → resolved.

## Resolved in M2 (now architecture / ADRs)
- Memory vs knowledge boundary → operational vs knowledge items; `temporary_unified_model` (ADR-0015, M2 spec §3.1).
- Pre-retrieval query vs M4 retrieval → ADR-0018 (`q=` only; no semantic search in M2).
- Service-first sequencing → Service → API → Admin UI → Knowledge → Graph (Architect 2026-06-24).
- `restore_version` → deferred (history read-only in M2).

## Open

### Q1 — pgvector index vs model-agnostic embeddings (M4) — HIGH
`embeddings` is model/dimension-tagged. M2 **forbids** embeddings on memory (ADR-0018).
Index strategy (partition by `model`) is decided and implemented in **M4** when retrieval is built.

### Q2 — Token usage on Vertex streaming (M2)
LiteLLM's Vertex stream didn't surface a usage chunk → `agent_runs.output = {}`.
Try `stream_options={"include_usage": True}` or a separate non-stream usage call.
Accounting fidelity only.

### Q3 — SSE through Cloud Run (M1 close)
Confirm streaming + `ping=15` heartbeat survive Cloud Run buffering/idle timeouts
for single-user latency. Verify in prod (M1 dev was local).

### Q4 — Frontend prod API URL (M1/M2)
`NEXT_PUBLIC_API_BASE_URL` is build-time inlined but not a Docker `ARG`. Decide and
implement the build-arg wiring so the prod frontend reaches the prod backend.

### Q5 — Job durability (before M11)
In-process worker is fine for M0–M6; a durable queue (Cloud Run Jobs / Cloud Tasks)
is needed before M11. When and which?

### Q6 — `db-f1-micro` sizing (M3/M4)
Fine for scaffolding; reassess instance size under ingestion + embeddings load.

### Q7 — Cloud Run cold starts (M11)
Acceptable for single-user now; revisit (min instances / warmups) at hardening.

### Q8 — Re-enable Cloud Build CI (when org policy allows)
M0 hit PERMISSION_DENIED; currently buildx + `gcloud run deploy`. Re-enable with the
right CB SA roles.

### Q9 — Tracing depth (M1/M11)
Full `TracerProvider` + Cloud Trace/Logging exporter + tracing the LLM abstraction
(so every run/step is traced) lands in M1/M11. What's the exact exporter wiring?

### Q10 — Conversation titling (M2 optional / post-M2)
M1 uses "New Conversation". Heuristic or LLM titling deferred; not gate-blocking for M2.

### Q11 — Detailed scope for M13/M14/M17 (later)
"Research", "NotebookLM-like", and "Voice" are roadmap-named but unspecified. Each
needs an Architect-frozen design spec before implementation (ADR-0001).

### Q12 — Mem0 reintroduction (M15–M16)
When core memory is mature, how/whether to layer Mem0-style auto-extraction on top
of the custom memory (ADR-0003 defers it here).
