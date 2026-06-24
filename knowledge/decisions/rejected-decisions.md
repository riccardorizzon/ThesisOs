# Rejected & Deferred Decisions

> Consolidated from the "Alternatives considered" sections of `decisions/ADR-0002/0003/0011/0012/0013/0014`, M0 spec §19, and M1 spec §11. Recording these prevents re-litigating settled questions.

## Rejected (do not revisit without new evidence)

| Option | Why rejected | Source |
|--------|--------------|--------|
| **Cursor API as the runtime LLM generator** | Agent/coding-oriented, **no embeddings**; would make the build tool a runtime dependency | ADR-0002, spec §19, architecture §2 |
| **Replace `generate() -> str` with a streaming signature** | Breaking change to a frozen contract | ADR-0011 |
| **Stream only via LangGraph-native tokens (ChatLiteLLM/ChatVertexAI inside the node)** | Dissolves the hand-owned LiteLLM seam into framework magic; couples streaming to LangGraph internals | ADR-0011 |
| **Put streaming in a free function outside the Protocol** | Splits the LLM surface into two inconsistent call paths with no shared contract | ADR-0011 |
| **Manage LangGraph checkpoint tables in Alembic** | Couples the domain schema to LangGraph's version-dependent internal layout; breaks on upgrade | ADR-0012 |
| **Custom checkpointer over a ThesisOS-owned table** | Reimplements a maintained library for no M1 benefit | ADR-0012 |
| **Let checkpoint tables land unmanaged + undocumented in `public`** | Erodes the meaning of the domain contract / drift gate | ADR-0012 |
| **Populate the `vertex-config` secret now (`{project,location,model}` JSON)** | Duplicates `config.py`; second source of truth; drift risk; no M1 value | ADR-0013 |
| **Put execution ids (conversation_id/trace_id) directly on `GraphState`** | Changes the frozen domain contract; pollutes every checkpoint with transport data | ADR-0014 |
| **Pass loose kwargs (conversation_id, trace_id, …) through every layer** | Unstructured, ever-growing arg list; error-prone; no single contract | ADR-0014 |
| **Defer `RunContext` until M12** | Retrofitting an execution boundary after services/graph exist is the rewrite the seam-first strategy avoids | ADR-0014 |
| **Public Cloud Run invoker by default (`allUsers`)** | No app auth (single-user) → anyone with the URL could use the assistant and burn Vertex credits; default is private/auth-invoker | runbook §3 |

## Deferred (intentionally not now; scheduled later)

| Option | Deferred to | Why | Source |
|--------|-------------|-----|--------|
| **Mem0-style automatic memory extraction** | M15–M16 | Core memory is custom + manually editable first | ADR-0003 |
| **Multi-provider LiteLLM fallback / routing** | when needed | YAGNI; the seam keeps it open | ADR-0002 |
| **pgvector HNSW/IVFFlat index + partition-by-model strategy** | M2/M4 | Index needs a fixed dim; decide when retrieval is built | spec §19 |
| **Durable job queue (Cloud Run Jobs / Cloud Tasks)** | before M11 | In-process worker fine for M0–M6 | ADR-0009, spec §19 |
| **Full TracerProvider + Cloud Trace/Logging exporter + LLM tracing** | M1/M11 | M0 ships the instrumentation hook + JSON logs + `/metrics` | spec §13 |
| **Automatic conversation titling (LLM)** | M2 | YAGNI in M1; title is literal "New Conversation" | M1 spec §5 |
| **`db-f1-micro` upsizing** | M3/M4 | Fine for scaffolding; reassess at ingestion/embedding load | spec §19 |
| **Re-enable Cloud Build CI** | when org policy allows | M0 hit PERMISSION_DENIED; used buildx | m0-promotion |
| **Cheaper single-VM `e2-small` + docker-compose deploy** | (documented fallback, not chosen) | Cloud Run chosen for dev/prod parity | spec §14, architecture §8 |

## Re-evaluation triggers
- Reconsider Cursor-as-runtime **only if** Vertex proves insufficient for Italian
  academic prose (spec §19).
- Reconsider `vertex-config` when a concrete need appears (multi-provider fallback,
  dynamic routing, per-agent models, A/B testing) — ADR-0013.
