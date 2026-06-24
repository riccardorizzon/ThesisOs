# Memory Architecture

> Sources: M2 spec (`docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md`), ADR-0003, ADR-0015, ADR-0017, ADR-0018, code. **Status: Phases 1–6 implemented; promotion pending.**

## Design principle (ADR-0003)

Custom memory on Postgres — structured, manually editable, versioned. **No Mem0 in core** (deferred M15–M16).

## Memory vs knowledge (ADR-0015)

Two categories, one table in M2 (`temporary_unified_model: true`):

| Category | Kinds | Role | Prompt injection (M2) |
|----------|-------|------|------------------------|
| **Operational** | `user`, `thesis`, `decision`, `editable` | System-facing context | `editable` always; `user`/`thesis` when pinned |
| **Knowledge items** | `concept`, `citation` | User thesis knowledge | **Never** in M2 graph path |

`concept` / `citation` are **`future_extraction_candidates`** — may move to dedicated tables or link to `documents`/`sources`/`notes` in M3–M6.

**Memory ≠ notes:** `notes` table holds document/chapter anchors (M0); memory rows are a separate admin-managed layer until ingestion links them.

## Data model (implemented)

```text
memories
  id, kind, key?, title?, content, pinned, source, version, metadata, created_at, updated_at

memory_versions          (ADR-0017 — append-only history)
  id, memory_id→memories, version, title?, content, metadata, source, changed_at
```

- **Singleton kinds:** `user`, `thesis`, `editable` — partial unique indexes on canonical keys.
- **Restore:** read-only history; `restore_version` **deferred** (no rollback API in M2).

## Write path (sole port)

```text
REST /memory  ──┐
Graph (M5+)   ──┼──► MemoryService ──► memories + memory_versions
Agents (M5+)  ──┘         ▲
                          │ only writer
                    (no direct DB from API/graph)
```

## Read paths

| Consumer | Scope |
|----------|-------|
| Admin UI / REST | All six kinds; list filter `GET /memory?q=` (ILIKE only — ADR-0018) |
| `load_prompt_context()` | Operational only: `editable`, pinned `user`, pinned `thesis` |
| M4 retriever (future) | Knowledge items + documents via embeddings — **not M2** |

## Query model (ADR-0018)

```yaml
semantic_search: forbidden (M2)
embeddings: forbidden (M2)
vector_index: forbidden (M2)
GET /memory/search: forbidden
retrieval: deferred_to_m4
```

Admin list uses `q=` substring filter only — not a retrieval layer.

## Prompt context contract (Phase 2 service; Phase 6 graph)

```yaml
memory_context:
  transient_only: true
```

```text
Memory DB → load_prompt_context() → PromptContext (structured)
           → render_prompt_context() → LLM wire text (separate)
           → NOT persisted to GraphState / messages table
```

Output shape: `PromptContext { editable[], user[], thesis[], conversation_id? }`.

## API (Phase 3 — implemented)

| Method | Path |
|--------|------|
| GET | `/memory` |
| POST | `/memory` |
| GET | `/memory/{id}` |
| PATCH | `/memory/{id}` |
| DELETE | `/memory/{id}` |
| GET | `/memory/{id}/versions` |

## Graph integration (Phase 6 — implemented)

```text
START → memory_context_node → conversation_node → END
```

- `app/graph/memory_context.py` — reads `thread_id` from LangGraph config as `conversation_id`.
- Loads via `MemoryService.load_prompt_context()` only; renders via `render_prompt_context()`.
- Prepends one `Message(role="system", …)` to `state.messages` for the turn wire.
- Does **not** load `concept`, `citation`, or `decision`.
- Does **not** rewrite `conversation_node` or `ConversationService`.
- **Critic verified:** `transient_only` — no new GraphState fields; system rows not written to `messages` table by service.

## GraphState (frozen)

- `memory_ops: list[MemoryOp]` exists; `MemoryService.apply_ops()` hook present; **not executed in chat loop until M5+**.
- No new GraphState fields in M2.

## Events (not yet wired)

- `MemoryUpdated { memory_id, kind }` — catalog exists; `services/events/bus.py` still stub.

## Embeddings

- `embeddings` table unused for memory in M2. M4 may add `owner_type='memory'`.

## UI (Phase 4 — Memory Administration)

Admin tooling at `/memory` — not a knowledge workspace. Kind badges for manual validation.

## Relationship to conversation memory

| System | Purpose |
|--------|---------|
| `messages` + checkpoints | Chat transcript + graph working state (M1) |
| `memories` | Durable, editable cross-conversation knowledge (M2) |

Checkpoints must **not** be treated as authoritative for memory content (ADR-0015).
