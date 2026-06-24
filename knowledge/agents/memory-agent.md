# Memory Agent (Runtime)

> Type: Runtime LangGraph node. Milestone: **M2**. Status: designed (contract frozen), not implemented. Sources: `contracts/agents/memory.json`, ADR-0003, M0 spec §8, `architecture/memory.md`, `contracts/events/events.json`.

## Mission
Maintain the user's long-term, editable, versioned memory (6 kinds) and inject the
`editable` memory into the system prompt — without ever writing memory the user
can't see/edit.

## Responsibilities
- Apply `memory_ops` to the `memories` table (upsert/delete), versioned.
- Surface relevant memories into the conversation; inject the `editable` "Notion
  page" into the prompt.
- Emit `MemoryUpdated { memory_id, kind }` events.
- Back the `/memory` CRUD endpoints (M2).

## Inputs (contract)
- `reads_state`: `messages`, `memory_ops`.

## Outputs (contract)
- `writes_state`: `memory_ops` (`state_mutations: memory_ops = append`).
- `MemoryOp { op[upsert|delete], kind[user|thesis|concept|citation|decision|editable], key, content? }`.

## Allowed actions
- Read/write `memories`; bump `version`; emit `MemoryUpdated`; read history for
  context.

## Forbidden actions
- Automatic, invisible memory extraction (Mem0-style auto-extraction is deferred to
  **M15–M16**, ADR-0003).
- Mutating `GraphState` fields other than `memory_ops`.
- Adding `GraphState` fields (frozen).

## Dependencies
- **`memories` table** (exists since M0), **event bus** (ADR-0006), **the M1 graph
  seam** (memory node is *added* to it).

## Promotion criteria (M2 gate, to be frozen in the M2 spec)
- 6-kind CRUD via `/memory`; versioning; `editable` injected into prompts;
  `MemoryUpdated` emitted; memory node extends the graph without rewriting the seam.

## Failure modes (contract)
- `write_conflict` — concurrent/version conflict on a memory write.
- (Design risk) prompt bloat from over-injecting memory — mitigate with
  pinning/selection.
