# ThesisOS — M2 "Memory System" Design Spec

- **Date:** 2026-06-24
- **Status:** Approved with conditions (Architect 2026-06-24) — implementation authorized for Phase 1+
- **Scope:** Milestone M2 only — the complete memory foundation (6 kinds, CRUD, versioning, persistence, observability, minimal UI, LangGraph extension). **NOT** ingestion, embeddings, retrieval, RAG, multi-agent execution, or citation generation.
- **Authors:** ThesisOS Builder Team
- **Builds on:** M1 Conversation System (tag `m1-complete` on `main`; frozen seam: `/chat`, `ConversationService`, single-node LangGraph, `GraphState`, `RunContext`, `LLMClient`)
- **New ADRs:** 0015 (memory ownership), 0017 (memory versioning), 0018 (memory query model). ADR-0016 (Editable Memory) **not created** — fully covered by ADR-0003 + §4 of this spec.

---

## 1. Goals

M2 delivers the **memory foundation** that M3–M6 (and later M15–M16 Mem0 layering) will consume.

**M2 MUST ship:**

1. **Six memory kinds** on Postgres: `user`, `thesis`, `concept`, `citation`, `decision`, `editable` (ADR-0003).
2. **Persistent, editable, versionable, queryable, observable** memory records with a clear ownership model (ADR-0015).
3. **`MemoryService`** — domain logic for CRUD, optimistic concurrency, version history, and event emission.
4. **`/memory` REST API** — list, detail, create, update, delete (additive OpenAPI realization of M0 stubs + path extensions).
5. **`memory_versions` history table** — append-only snapshots on every content/metadata change (ADR-0017).
6. **`MemoryUpdated` event** — persisted to `events` via the event bus (ADR-0006); payload per `contracts/events/events.json`.
7. **LangGraph extension** — add a **pre-turn** `memory_context_node` that loads `editable` (+ pinned `user`/`thesis`) memory and injects it into the LLM wire messages. **Do not rewrite** the M1 `conversation_node` or `ConversationService` seam.
8. **Minimal frontend** — memory list, detail, create, update (no Notion clone, no advanced workspace).
9. **Tests** — CRUD, versioning, persistence, restart recovery, migration, API, drift (M0+M1 suites stay green).
10. **Knowledge update** — `knowledge/` reflects M2 scope and promotion gate.

**Success criterion:** A user can create and edit thesis memory through the UI and API; changes survive restart; version history is queryable; the `editable` page is injected into chat context; no frozen contracts are broken.

---

## 2. Non-goals (hard boundary)

M2 explicitly **does NOT** implement:

| Forbidden | Deferred to |
|-----------|-------------|
| Document upload / parsing / chunking | M3 |
| Embeddings generation or `embeddings` writes | M3/M4 |
| Hybrid / vector retrieval, `/search`, pgvector index strategy | M4 |
| RAG, retriever agent, `retrieved_context` population | M4 |
| Writer / planner / router / supervisor agents | M5–M6 |
| Citation agent, CSL-JSON generation, `/citations` | M7 |
| Mem0 or automatic memory extraction | M15–M16 |
| Full Notion-like workspace UI | M15+ |
| Changes to `GraphState` shape, `RunContext`, `LLMClient` Protocol, `TokenChunk` | Frozen (ADR-0007, 0011, 0014) |
| Rewriting `ConversationService` orchestration or `/chat` SSE protocol | Frozen M1 seam |
| LangGraph checkpoint schema changes | ADR-0012 (`langgraph` schema owned by PostgresSaver) |

If it is not on the Goals list, it does not belong in M2.

---

## 3. Memory taxonomy

All six kinds live in the **`memories`** table with a `kind` discriminator (ADR-0003). They are **not** one homogeneous category — they split into two architectural roles:

### 3.1 Memory vs knowledge (critical boundary)

> **Are memories operational system entities or user knowledge content?**  
> **Both — but the distinction must stay explicit to avoid debt through M6.**

| Category | Kinds | Role | M2 prompt injection | Future home |
|----------|-------|------|---------------------|-------------|
| **Operational memory** | `user`, `thesis`, `decision`, `editable` | System-facing context the assistant must honor | `editable` always; `user`/`thesis` when pinned; `decision` never | Stays in `memories` |
| **Knowledge items** | `concept`, `citation` | User thesis knowledge; will relate to `documents`, `sources`, `chapters`, `notes` in M3–M6 | **Never** in M2 (not a masked retriever) | **Extraction candidates** — may move to dedicated tables later |

```yaml
temporary_unified_model: true          # M2–M5: single `memories` table for all six kinds
future_extraction_candidates:
  - concept                            # may become `concepts` table or link to `notes` (M3–M6)
  - citation                           # may merge with `sources`/`citations` (M7); not CSL generation in M2
```

M2 **does not** conflate knowledge items with operational memory in the chat path. CRUD and UI list all six kinds; **`memory_context_node` reads operational kinds only** (§9.2).

**Memory ≠ notes:** The existing `notes` table (M0) holds document/chapter-anchored annotations. `concept`/`citation` memories in M2 are **placeholders** for thesis knowledge stored in the unified table until M3–M6 define proper relations. Do not merge or duplicate `notes` in M2.

### 3.2 Kind reference

| Kind | Category | Purpose | Cardinality | Typical `key` | Prompt injection (M2) |
|------|----------|---------|-------------|---------------|------------------------|
| **user** | operational | Preferences, language, writing style | Singleton (`key=user`) | `user` | Yes, if `pinned=true` |
| **thesis** | operational | Title, scope, research question, outline summary | Singleton (`key=thesis`) | `thesis` | Yes, if `pinned=true` |
| **decision** | operational | Explicit choices made during the thesis work | Many | optional slug | **No** |
| **editable** | operational | Always-on rules page (e.g. *"Use APA7. Academic register."*) | Singleton (`key=editable`) | `editable` | **Always** |
| **concept** | knowledge | Authors, theories, definitions the user tracks | Many | slug, e.g. `bourdieu-habitus` | **No** — UI/CRUD only |
| **citation** | knowledge | Source pointers, page refs, DOI notes (not full CSL — that is `sources` in M7) | Many | optional slug | **No** — UI/CRUD only |

### Record shape (API / domain model)

Each memory record exposes:

| Field | Source | Notes |
|-------|--------|-------|
| `id` | `memories.id` | UUID |
| `kind` | `memories.kind` | One of six kinds |
| `title` | `memories.title` (**new column**, additive migration) | Human display name; falls back to `key` or first line of `content` in responses if null |
| `content` | `memories.content` | Markdown/plain text body |
| `metadata` | `memories.metadata` | JSONB; refs to `document_id`, `source_id`, tags, etc. |
| `created_at` | `memories.created_at` | Immutable |
| `updated_at` | `memories.updated_at` | Bumped on every successful write |
| `version` | `memories.version` | Monotonic integer; optimistic-lock token |

**Preserved M0 columns (not in public API summary but used internally):**

| Field | Purpose |
|-------|---------|
| `key` | Stable slug; **unique per `(kind, key)`** where `key IS NOT NULL` (ADR-0015) |
| `pinned` | When true, included in chat prompt injection alongside `editable` |
| `source` | Provenance: `user` \| `system` \| `agent` (M2 writes `user` for API/UI; `agent` reserved for M5+) |

### `MemoryOp` (GraphState, frozen)

The existing `MemoryOp(op, kind, key, content)` in `GraphState` is the **agent write intent** format. M2 does **not** change this shape. The memory agent (M5+) will append ops; M2 provides `MemoryService.apply_ops(ops)` as a hook but does **not** wire agent-driven ops into the chat loop yet.

---

## 4. Memory ownership

See **ADR-0015** for the normative decision. Summary:

```text
┌─────────────────────────────────────────────────────────────┐
│  System of record: public.memories (+ memory_versions)      │
│  Owned by: MemoryService                                    │
│  NOT owned by: LangGraph checkpoints, embeddings, chunks    │
└─────────────────────────────────────────────────────────────┘

Singleton kinds (user, thesis, editable):
  - Exactly one active row per kind (enforced by unique index on kind WHERE key = canonical)
  - Created lazily on first access or via seed migration

Multi kinds (concept, citation, decision):
  - Unbounded rows; key optional (auto-slug from title if omitted)

Write paths:
  1. REST /memory (user UI) — primary M2 path; source=user
  2. MemoryService.apply_ops (GraphState memory_ops) — hook only in M2; full wiring in M5+
  3. Event consumers — read-only in M2

Read paths:
  1. REST /memory (UI, external tools) — all six kinds
  2. memory_context_node (LangGraph pre-turn loader) — **operational kinds only**: editable, pinned user, pinned thesis
  3. M4 retriever — will READ knowledge items + documents via embeddings; M2 does not implement this
```

**Boundary vs LangGraph checkpoints (ADR-0012):** Checkpoints hold **orchestration working state** (`GraphState`, including `memory_ops` scratch). The `memories` table is **domain truth** for long-term memory — same pattern as `messages` vs checkpoint (M1 spec §5). M2 must never store memory content in checkpoints as a second source of truth.

**Boundary vs M4 retrieval:** M2 query = SQL filters (`kind`, `key`, `pinned`, `q` ILIKE on title/content). M4 retrieval = embedding similarity over `embeddings` joined to owners. M2 does not write embeddings; M4 will optionally embed memory rows then.

---

## 5. Database design

### 5.1 Existing table (unchanged columns, one additive column)

```sql
-- memories (M0) + M2 additive column
ALTER TABLE memories ADD COLUMN IF NOT EXISTS title TEXT;
-- title nullable; API layer derives display title when null
```

All other M0 columns remain: `id`, `kind`, `key`, `content`, `pinned`, `source`, `version`, `metadata`, `created_at`, `updated_at`.

### 5.2 New table: `memory_versions` (ADR-0017)

Append-only history. One row per committed version (including v1 on create).

```sql
CREATE TABLE memory_versions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id   UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    version     INTEGER NOT NULL,
    title       TEXT,
    content     TEXT NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    source      VARCHAR(16) NOT NULL,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (memory_id, version)
);
CREATE INDEX idx_memory_versions_memory_id ON memory_versions(memory_id);
```

### 5.3 Indexes and constraints (M2)

```sql
-- Singleton enforcement (partial unique indexes)
CREATE UNIQUE INDEX uq_memories_kind_user
    ON memories (kind) WHERE kind = 'user' AND key = 'user';
CREATE UNIQUE INDEX uq_memories_kind_thesis
    ON memories (kind) WHERE kind = 'thesis' AND key = 'thesis';
CREATE UNIQUE INDEX uq_memories_kind_editable
    ON memories (kind) WHERE kind = 'editable' AND key = 'editable';

-- Multi-kind slug uniqueness (when key present)
CREATE UNIQUE INDEX uq_memories_kind_key
    ON memories (kind, key) WHERE key IS NOT NULL;

-- List/filter performance
CREATE INDEX idx_memories_kind ON memories (kind);
CREATE INDEX idx_memories_updated_at ON memories (updated_at DESC);
```

### 5.4 Migrations

- **Alembic `0002_memory_system`**: add `title`, create `memory_versions`, add indexes.
- **Contract sync**: regenerate `contracts/db/schema.sql` from models (drift test).
- **Seed (optional, idempotent)**: insert empty singleton rows for `user`, `thesis`, `editable` if missing — enables prompt injection and UI without manual bootstrap.

### 5.5 What M2 does NOT touch

- `embeddings` table (no rows written)
- `langgraph.*` checkpoint tables
- Any of the other 12 domain tables except `events` (via bus)

---

## 6. API design

Realize and extend the M0 `/memory` stub. **Additive OpenAPI changes only** — no breaking changes to existing paths.

### 6.1 Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/memory` | List memories (filterable) |
| `POST` | `/memory` | Create memory |
| `GET` | `/memory/{id}` | Get one memory by id |
| `PATCH` | `/memory/{id}` | Update memory (optimistic lock) |
| `DELETE` | `/memory/{id}` | Delete memory (history retained via ON DELETE CASCADE on versions — **design choice: soft-delete alternative rejected**; use DELETE + versions table as audit) |
| `GET` | `/memory/{id}/versions` | List version history |
| `GET` | `/memory/{id}/versions/{version}` | Get specific version snapshot |

### 6.2 Schemas (OpenAPI components)

```yaml
Memory:
  type: object
  required: [id, kind, title, content, metadata, created_at, updated_at, version]
  properties:
    id: { type: string, format: uuid }
    kind: { type: string, enum: [user, thesis, concept, citation, decision, editable] }
    title: { type: string }
    content: { type: string }
    metadata: { type: object }
    key: { type: string, nullable: true }
    pinned: { type: boolean }
    source: { type: string, enum: [user, system, agent] }
    created_at: { type: string, format: date-time }
    updated_at: { type: string, format: date-time }
    version: { type: integer, minimum: 1 }

MemoryCreate:
  type: object
  required: [kind, content]
  properties:
    kind: { ... }
    title: { type: string }
    content: { type: string }
    metadata: { type: object }
    key: { type: string }
    pinned: { type: boolean, default: false }

MemoryUpdate:
  type: object
  properties:
    title: { type: string }
    content: { type: string }
    metadata: { type: object }
    pinned: { type: boolean }
    expected_version: { type: integer, description: "Required for optimistic lock" }

MemoryVersion:
  type: object
  required: [version, content, changed_at]
  properties:
    version: { type: integer }
    title: { type: string }
    content: { type: string }
    metadata: { type: object }
    source: { type: string }
    changed_at: { type: string, format: date-time }
```

### 6.3 List query parameters (ADR-0018)

**No dedicated search endpoint.** There is no `GET /memory/search` in M2 — M4 owns real retrieval via `POST /search`. List filtering uses query params on `GET /memory` only:

| Param | Type | Description |
|-------|------|-------------|
| `kind` | string | Filter by kind |
| `key` | string | Exact key match |
| `pinned` | boolean | Filter pinned |
| `q` | string | Case-insensitive substring match on `title` + `content` (SQL `ILIKE` — **not** semantic search) |
| `limit` | int | Default 50, max 200 |
| `offset` | int | Pagination offset |

### 6.4 Error responses

| Code | When |
|------|------|
| `404` | Unknown id |
| `409` | Optimistic lock failure (`write_conflict`) — matches memory agent contract |
| `422` | Invalid kind, missing required fields |
| `400` | Singleton kind violation (second `editable` create) |

All errors use frozen `Error { code, message }` schema.

---

## 7. Memory lifecycle

```text
CREATE
  POST /memory
    → validate kind + singleton rules
    → INSERT memories (version=1, source=user)
    → INSERT memory_versions (v1 snapshot)
    → publish MemoryUpdated
    → return Memory

READ
  GET /memory, GET /memory/{id}
    → MemoryService query (no side effects)

UPDATE
  PATCH /memory/{id} + expected_version
    → SELECT ... FOR UPDATE (or compare version in UPDATE WHERE)
    → if version mismatch → 409 write_conflict
    → increment version, UPDATE memories, INSERT memory_versions
    → publish MemoryUpdated
    → return Memory

DELETE
  DELETE /memory/{id}
    → reject if singleton kind (user/thesis/editable) — 400 cannot_delete_singleton
    → DELETE memories (CASCADE versions)
    → publish MemoryUpdated with deleted=true in payload extension OR separate event (M2: payload includes memory_id + kind; consumers treat missing row as deleted)

RESTART RECOVERY
  → memories + memory_versions durable in Postgres
  → no in-memory cache required; MemoryService reads DB on every request
  → LangGraph checkpoint independent; memory_context_node reads fresh from DB each turn
```

### Event: `MemoryUpdated`

Per `contracts/events/events.json`:

```json
{ "memory_id": "uuid", "kind": "editable" }
```

M2 wires `services/events/bus.py` to persist to `events` table (minimal in-process dispatcher — no Pub/Sub).

---

## 8. Versioning strategy

See **ADR-0017**. Normative rules:

1. **Current version** lives on `memories.version` (fast reads, lock token).
2. **History** lives in `memory_versions` (append-only, never updated).
3. **Optimistic concurrency**: every `PATCH` requires `expected_version`; mismatch → `409` / agent error `write_conflict`.
4. **No branching** in M2 — linear version history only.
5. **History yes; rollback no:**

```yaml
restore_version: deferred    # no POST /memory/{id}/restore/{version} in M2
```

M2 ships read-only version history (`GET .../versions`). Restore/rollback is explicitly deferred — users may copy from history manually via PATCH.

---

## 9. LangGraph integration strategy

M2 **extends** the graph; it does not rewrite M1.

### 9.1 Target topology

```text
START → memory_context_node → conversation_node → END
```

Same checkpointer, same `thread_id = conversation_id`. `ConversationService` unchanged except it calls `build_graph()` that includes the new node.

### 9.2 `memory_context_node` behavior

**M2 read scope (hard restriction):** the node loads **only**:

```text
editable          # always
pinned user       # if pinned=true
pinned thesis     # if pinned=true
```

It must **not** load `concept`, `citation`, or unpinned `decision` rows. Loading knowledge items into the prompt would be a masked retriever — that is M4's job.

1. Call `MemoryService.load_prompt_context()` — returns structured block for operational kinds only (see above).
2. Prepend a **system** message to the wire messages passed to the LLM:

```text
You are assisting with a thesis. The following persistent memory applies:

[EDITABLE MEMORY]
{editable.content}

[USER PREFERENCES]   (if pinned user memory exists)
{user.content}

[THESIS CONTEXT]    (if pinned thesis memory exists)
{thesis.content}
```

3. Return `{}` (no GraphState mutation) — injection is **runtime-only** for the LLM call inside `conversation_node`, OR return updated `messages` with a system prefix **only in the wire passed to astream**, not persisted to `messages` table.

**Critical design choice:** System prompt injection must **not** pollute the `messages` system of record. Implementation: `memory_context_node` sets a transient field via custom stream metadata OR `conversation_node` accepts pre-loaded system prefix from graph state... but GraphState is frozen.

**Resolution (no GraphState change):** `memory_context_node` returns `{"messages": [system_msg, *state.messages]}` for checkpoint purposes, but `ConversationService` already loads history from DB and builds initial state. The node chain handles injection:

- `memory_context_node`: reads DB, prepends `Message(role="system", content=...)` to `state.messages` for this turn only
- `conversation_node`: streams LLM, appends assistant reply
- `ConversationService` persists only **user** and **assistant** rows to DB (filters out system on persist — **additive behavior in service** limited to excluding role=system from `_persist_assistant` path, OR persist assistant only as today)

**M1 persist path today:** persists user before stream; assistant after. System message from memory node lives only in graph checkpoint for the turn — acceptable because editable memory is re-loaded each turn from DB.

### 9.2.1 `memory_context`: transient only (GraphState unchanged)

```yaml
memory_context:
  transient_only: true
```

Normative flow — memory content is **never** a new GraphState field:

```text
Memory DB (memories table)
        ↓
memory_context_node   ← reads operational kinds only
        ↓
prompt injection      ← prepends system Message to wire for this turn
        ↓
conversation_node → LLM
        ↓
messages table      ← persists user + assistant only (no system rows)
```

`GraphState` shape is **unchanged** (ADR-0007). Injection is transient: either a system `Message` prepended for the LLM wire within the node chain, or equivalent runtime-only handling — it must not be written to `messages`, must not add GraphState fields, and must not become checkpoint-authoritative memory (checkpoints may carry the turn's working `messages` list; domain truth remains `memories` + DB reload each turn).

### 9.3 `memory_ops` (deferred execution)

The memory agent contract says it **appends** to `memory_ops`. M2 ships `MemoryService.apply_ops(state.memory_ops)` but does **not** add a post-turn node that executes ops during chat. Agent-driven memory writes land in M5 when the memory agent node is added. This avoids scope creep while honoring the frozen agent contract shape.

### 9.4 Conversation titling (Q10)

**Deferred sub-feature within M2 if capacity allows:** after first assistant reply, set `conversations.title` from first ~60 chars of user message (heuristic, no LLM). Not required for M2 promotion gate; listed as Phase 6 optional in the plan.

---

## 10. Future retrieval integration (M4+)

M2 deliberately stops at SQL query semantics so M4 can layer retrieval without duplication:

| Concern | M2 (this milestone) | M4 (retrieval) |
|---------|---------------------|----------------|
| Query | `GET /memory?kind=&q=` ILIKE | `POST /search` hybrid vector + keyword |
| Storage | `memories` + `memory_versions` | Same tables (read) |
| Embeddings | None | `embeddings(owner_type=memory, owner_id=...)` |
| GraphState | `memory_ops` scratch only | `retrieved_context` populated by retriever |
| Prompt | Full editable + pinned injection | Retrieved chunks appended separately |

**Integration contract for M4:** Retriever may embed memory `content` and query via pgvector; it must not fork a parallel memory store. Memory CRUD remains exclusively via `MemoryService`.

---

## 11. Promotion gate

M2 is complete only when **all** are true:

```yaml
memory_crud: green          # POST/GET/PATCH/DELETE /memory work end-to-end
versioning: green           # optimistic lock + history table + version list API
persistence: green          # data survives container restart
restart_recovery: green     # list/detail returns same data after docker compose restart
migration: green            # alembic 0002 upgrades cleanly on fresh and existing DBs
api_tests: green            # httpx tests for all /memory endpoints
drift_tests: green          # schema.sql matches models; langgraph schema still excluded
m0_m1_tests: green          # full backend suite + ruff clean
graphstate: unchanged       # no field additions/removals (ADR-0007)
runcontext: unchanged       # ADR-0014
llmclient: unchanged        # ADR-0011 TokenChunk + Protocol
conversation_system: unchanged  # /chat SSE protocol + ConversationService contract intact
contracts: additive_only    # OpenAPI + schema.sql updated additively; agent/event contracts unchanged
langgraph: extended         # memory_context_node added; conversation_node untouched
scope_creep: false          # nothing from §2 Non-goals shipped
documentation: complete     # this spec, ADRs, plan, docs/m2-promotion.md
knowledge_updated: true     # current-state, project-memory, milestones, open-questions
frontend: minimal_green     # list, detail, create, update pages wired to /memory
events: green               # MemoryUpdated persisted to events table
```

Forbidden until gate passes: ingestion, embeddings, retrieval, RAG, writer agents, citation generation, Mem0.

---

## 12. Critic checklist (pre-implementation)

| Risk | Mitigation |
|------|------------|
| Duplication with M4 retrieval | M2 = SQL only; no embeddings; document boundary in §10 |
| Duplication with LangGraph checkpoints | memories = domain truth; checkpoints = working state; §4, §9 |
| Contract drift | Drift test + additive-only OpenAPI review |
| Scope creep | §2 hard list; memory_ops execution deferred to M5 |
| GraphState pressure | No new fields; injection via message prepend in node |
| Singleton race on create | DB unique indexes + service-level upsert for singleton kinds |

---

## 13. Observability

- Structured logs on MemoryService CRUD (memory_id, kind, version, duration).
- OpenTelemetry spans: `memory.create`, `memory.update`, `memory.load_prompt_context`.
- `GET /metrics` unchanged; optional counter `thesisos_memory_writes_total{kind}` if trivial.

---

## 14. UI requirements (minimal)

| Screen | Behavior |
|--------|----------|
| **List** (`/memory`) | Table/cards grouped by kind; filter by kind; link to detail |
| **Detail** (`/memory/[id]`) | Show title, content, metadata, version, timestamps; version history list |
| **Create** (`/memory/new`) | Form: kind, title, content, pinned |
| **Update** (detail inline or edit mode) | PATCH with expected_version; show 409 conflict message |

No rich editor, no block-based Notion UI, no drag-and-drop workspace.

---

## 15. Open questions (resolved in this spec)

| ID | Question | Resolution |
|----|----------|------------|
| Q10 | Conversation titling | Optional heuristic in M2 Phase 6; not gate-blocking |
| — | `title` vs M0 `key` | Add `title` column; keep `key` for slugs (§5.1) |
| — | Soft vs hard delete | Hard delete; audit via `memory_versions` until delete cascades |
| — | System message pollution | Inject via node; do not persist system rows to `messages` |

---

## 16. References

- ADR-0003 Custom Memory Layer
- ADR-0006 Event Driven
- ADR-0007 State Contract (GraphState frozen)
- ADR-0012 External Infrastructure Schemas
- ADR-0014 RunContext Separation
- ADR-0015 Memory Ownership (new)
- ADR-0017 Memory Versioning (new)
- ADR-0018 Memory Query Model (new)
- `contracts/agents/memory.json`
- `contracts/events/events.json`
- `docs/superpowers/specs/2026-06-24-thesisos-m1-conversation-system-design.md`
