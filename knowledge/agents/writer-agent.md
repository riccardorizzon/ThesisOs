# Writer Agent (Runtime)

> Type: Runtime LangGraph node (Business). Milestone: **M6**. Status: **implemented & qualified** (M6.1–M6.5; promotion M6.6). Sources: `contracts/agents/writer.json`, `backend/app/graph/writer.py`, `backend/app/schemas/draft.py`, ADR-0031 (capability & topology), ADR-0032/0033 (chapter store), `docs/m6-promotion.md`.

## Implementation (M6, ADR-0031)
- **Capability, not a special node:** `WriterCapability.write_grounded(brief) -> DraftResult` (port). `LLMWriter` is the default impl; `make_writer_node(writer)` is a thin adapter. Future `writer-v2/fast/reasoning/local` swap at the composition root with no topology change.
- **`DraftResult`** (`draft`, `citations`, `metadata`, `reasoning?`, `metrics`) is pure — isolated from `ChapterService`/REST/DB/Event Bus. The node maps only `draft`/`citations` to GraphState (writer.json); the rest rides the stream.
- **Route:** `writer` activated (ADR-0027 reserved) — `memory_context → retriever → writer → END`; selected on thesis-drafting intent (`coerce`).
- **Persistence boundary:** the writer never writes chapters; durable saves go through `ChapterService` (ADR-0032) via `/chapters`. Citations restricted to retrieved sources (no invented ids; full hallucination gating is the Critic, M9).

## Mission
Draft thesis prose — chapters/sections — grounded in the plan and retrieved
context, in the user's academic register (Italian), with citation markers.

## Responsibilities
- Generate `draft` from `plan` + `retrieved_context` + `messages` (via the LLM seam,
  streaming).
- Attach `citations` for claims it makes from retrieved sources.
- Back chapter creation/editing (`/chapters`, `chapters` table).

## Inputs (contract)
- `reads_state`: `plan`, `retrieved_context`, `messages`.

## Outputs (contract)
- `writes_state`: `draft`, `citations` (`state_mutations: draft = set,
  citations = set`).

## Allowed actions
- Call `generate()`/`astream()`; write `draft` + `citations`; write `chapters`.

## Forbidden actions
- Retrieving context itself (Retriever's job) or resolving final bibliographic
  formatting (Citation's job).
- Inventing sources (hallucinated citations are exactly what the Critic catches).
- Mutating `GraphState` fields other than `draft`/`citations`; adding fields (frozen).

## Dependencies
- **M4 Retriever** (`retrieved_context`), **M5 Planner/Router** (`plan`, `route`),
  **LLM seam**, **`chapters` table**. Followed by **M7 Citation** + **M9 Critic**.

## Promotion criteria (M6 gate, to be frozen in the M6 spec)
- Produces a coherent `draft` grounded in context with citation markers; chapter
  persistence works; streams via the existing seam.

## Failure modes (contract)
- `empty_context` — no retrieved context to write from.
- `generation_failed` — LLM generation error.
- (Design risk) ungrounded prose / hallucination — handed to the Critic (M9).

## Note on M1
In M1 the single `conversation_node` already sets `draft` (the assistant reply) as a
convenience; the real Writer agent (structured drafting from plan+context) is M6.
