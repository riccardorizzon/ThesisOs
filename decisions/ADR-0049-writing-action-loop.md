# ADR-0049: Writing Panel Action Loop

- **Status:** Proposed
- **Plane:** Product (Runtime layer)
- **Context:** Writing panel actions (`verify`, `find-sources`) use a single corpus search before generation. OpenWorker demonstrates value in multi-step tool loops with risk classification. ThesisOS needs domain-specific retrieval depth without importing OpenWorker, changing LangGraph topology (M12), or breaking Proposal-based HITL (ADR-0045).
- **Decision:**

  ### Action loop module

  Introduce `backend/app/runtime/action_loop/` as **Runtime layer** infrastructure (ADR-0030):

  - `ToolRegistry`, `ActionLoopRunner`, `RiskClass`, `PermissionEngine`
  - Read-only tools v1: `search_corpus`, `get_selection_context`

  ### Two-phase pipeline for loop actions

  1. **Retrieval loop** — LLM tool calling, max 6 iterations, accumulate `RetrievedChunk[]`
  2. **Draft generation** — existing `compose_writing_panel_wire` + `generate_with_citation_enforcement`

  ### Action routing

  - `verify`, `find-sources` → loop path
  - `rewrite`, `expand` → legacy single-pass path (unchanged in v1)

  ### Boundaries

  - No changes to LangGraph `/chat` topology (ADR-0027 M12 deferred)
  - No `openworker` / `aisuite` product dependencies
  - Vertex-only LLM via extended LiteLLM seam (ADR-0002)

  ### Invariants

  - **INV-WAL-1:** Loop actions MUST NOT mutate chapters/memory directly
  - **INV-WAL-2:** Citation enforcement preserved on final draft
  - **INV-WAL-3:** Proposal accept remains sole chapter promotion path

- **Consequences:** Better retrieval quality for verify/find-sources; small LLM latency increase; new SSE `step` events (Phase 4). Cost accepted for domain fit.
- **Alternatives considered:**
  - Import aisuite — rejected (governance + dep boundary)
  - Fixed multi-search script without tool calls — rejected (doesn't establish reusable loop)
  - Full M12 graph re-entry — rejected (scope; ADR-0027)

- **References:** ADR-0002, ADR-0027, ADR-0030, ADR-0039, ADR-0045; spec `docs/superpowers/specs/2026-07-29-thesisos-writing-action-loop-design.md`

## Phase 5 — Extensions (deferred)

Future work is documented here only; **not authorized** by this ADR. Each item requires its own preconditions and governance review before implementation.

| Extension | Preconditions / constraints |
|-----------|------------------------------|
| Enable loop for `rewrite` / `expand` | Phase 3 stable on `verify` / `find-sources`; `get_selection_context` value proven in production |
| `propose_edit` tool (`write_local`) | Permission engine `needs_user`; outputs flow through Proposal API — **never** direct chapter PATCH |
| MCP bridge | Separate ADR; do not mix MCP connectors into the panel action loop |
| M12 graph re-entry | ADR-0027 amendment required; do not bolt LangGraph `/chat` topology changes onto the panel loop |
