# Writer Agent (Runtime)

> Type: Runtime LangGraph node. Milestone: **M6**. Status: designed (contract frozen), not implemented. Sources: `contracts/agents/writer.json`, M0 spec §10, `contracts/openapi/openapi.yaml` (`/chapters`), ADR-0002/0007.

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
