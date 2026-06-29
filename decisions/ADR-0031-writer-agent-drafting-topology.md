# ADR-0031: Writer Capability & Drafting Topology (M6)

- Status: **Accepted** (2026-06-29) — Architect-approved at M6.0 with the four design-review recommendations incorporated (writer-as-capability, `DraftResult` isolation, draft/published lifecycle, versioning-as-change-stream). The M6 analogue of ADR-0027 (activates one reserved route and adds one Business node); review order follows Constitution C7.
- Governance: Consistent with the Runtime Constitution (C1–C8, esp. **C8 extension via ports**) and ADR-0030 (R1–R8, esp. **R1/R2 ports + composition root**).
- Context: M5 promoted the Agent Runtime Platform and froze the runtime contract. ADR-0027 §3 wired only `conversation`/`grounded_chat` and **reserved** `writer`/`critic`/`citation`/`document`. M6 is the writer milestone. `contracts/agents/writer.json` is frozen (reads `plan, retrieved_context, messages`; writes `draft, citations`; errors `empty_context, generation_failed`), and `GraphState.draft`/`citations` already exist (ADR-0007) — so M6 adds a node + a route **without changing GraphState**. The review of the M6 design added a key constraint: the writer must be an **interchangeable capability** producing a **pure result**, with persistence handled by a different layer.

- Decision:

  ### 1. Activate the reserved `writer` route (M6 topology)

  M6 extends the M5 topology (ADR-0027 §1) by activating the reserved `writer` route. No existing route changes.

  ```text
  START → supervisor → planner → router → memory_context → [route_after_router]
        ├─ route=conversation  ──► conversation_node ──► END                       (M5, unchanged)
        ├─ route=grounded_chat ──► retriever_node ──► conversation_node ──► END      (M5, unchanged)
        └─ route=writer        ──► retriever_node ──► writer_node ──► END            (M6, NEW)
  ```

  The writer route is **grounded by construction** (`retriever_node` before `writer_node`); `memory_context_node` (M2) runs for every route. `retriever_node`/`memory_context_node` bodies are unchanged (C6).

  ### 2. The writer is a CAPABILITY, not a special node (Rec. 1)

  The writer is modeled as a stable **capability/port**, not hard-coded logic:

  ```text
  WriterCapability:   async write_grounded(brief: WriterBrief) -> DraftResult
  ```

  - **Capability (port, Business).** `write_grounded()` is the contract the graph + route depend on — never on a concrete writer. Today it is implemented by **`writer-agent`** (the default LLM writer). Tomorrow `writer-v2`, `writer-fast`, `writer-reasoning`, `writer-local`, … implement the same port and are swapped **at the composition root** with **no change to topology, route, or GraphState** (C8; ADR-0030 R1/R2). The Capability Graph tracks variants as alternative implementations of one node.
  - **`make_writer_node(writer)` (Business, `backend/app/graph/writer.py`)** is a thin **adapter**: it wraps a `WriterCapability`, calls `write_grounded()`, and maps the result into the frozen GraphState partial. It is not the writer logic.
  - **`WriterBrief`** is the pure input the route assembles from frozen state: `plan`, `retrieved_context`, `messages` (and nothing else). No execution metadata.

  ### 3. The writer returns a pure `DraftResult` — isolation from persistence (Rec. 4)

  The writer capability knows **nothing** about `ChapterService`, REST, the database, or the Event Bus. It returns only a value object:

  ```text
  DraftResult:
    draft:      str                  # the prose
    citations:  list[CitationRef]    # ⊆ retrieved sources (§5)
    metadata:   dict                 # model id, route, brief echo — non-state
    reasoning:  str | None           # optional rationale (debug / Critic-ready, M9)
    metrics:    dict                 # tokens, durations, counts
  ```

  A **different layer** decides what to do with a `DraftResult` — **save / show / discard / compare**. Consequences: the writer is completely pure; the Critic (M9), diffing, and alternative renderers become trivial to add; nothing in the writer path touches storage.

  **Contract-true GraphState mapping.** `writer_node` maps `DraftResult` → `{messages(+assistant), draft, citations, errors}` **only** — exactly `contracts/agents/writer.json`. `metadata`/`reasoning`/`metrics` ride the **custom stream / Event Bus**, never GraphState (frozen, ADR-0007). The LLM seam is injected (`astream`, streaming `token`/`usage` chunks like `conversation_node`); the writer MUST NOT import `app.db`, `app.runtime`, telemetry, or a concrete domain service (R1/R3/R8/C3).

  ### 4. Route vocabulary & selection

  `writer` joins the **wired** route enum (`graph/orchestration/constants.py`), additively:

  - the router LLM may emit `route=writer`; `coerce_*_route` maps a recognized `writer` to the wired route;
  - heuristic fallback (mirrors `RETRIEVAL_KEYWORDS`): drafting intents (`write/draft/redigi/scrivi/componi` a chapter/section) bias toward `writer`; non-drafting turns keep defaulting to `conversation`/`grounded_chat`;
  - `router.json` route enumeration updated additively if enumerated. No GraphState change (route is a `str`).

  ### 5. Citation discipline (anti-hallucination)

  `DraftResult.citations` (and thus `GraphState.citations`) contain `CitationRef`s **only** for sources present in `retrieved_context`: `source_id` MUST be a `document_id`/`chunk_id` from the turn's `retrieved_context`; non-mapping citations are dropped before the node returns. Full hallucination gating is the Critic (M9); M6 MUST NOT emit invented `source_id`s. The writer does not format a bibliography or resolve CSL-JSON (Citation agent, M7).

  ### 6. Draft persistence is decoupled from the graph (M6)

  The writer route produces an **ephemeral** `DraftResult` (streamed + mapped to `GraphState.draft`/`citations`); it does **not** persist a chapter. Durable persistence is a separate concern handled through `/chapters` + `ChapterService` (ADR-0032), which consumes a draft on an explicit user action. Rationale: keeps GraphState frozen (no `chapter_id`; ADR-0007), keeps the writer pure (R1/R3/R8), and matches the writer contract (output is `draft, citations`).

  **Rejected for M6:** auto-persisting via a `RunContext` chapter target + composition-root persist hook. Viable later (RunContext is config, not GraphState — ADR-0014); deferred until outline-driven writing (M8).

  ### 7. Error handling (continue degraded)

  Consistent with ADR-0027 §5: writer contract errors append to `GraphState.errors` and do not abort the turn.

  | Condition | Behavior |
  |-----------|----------|
  | `empty_context` (no `retrieved_context`) | append error; best-effort ungrounded draft; **no** citations |
  | `generation_failed` (LLM error) | append error; finalize the turn with no draft |

  ### 8. Boundaries preserved

  - M1 `/chat` → `ConversationService` → `astream` → SSE seam unchanged externally.
  - M4 `retriever_node` and M2 `memory_context_node` bodies unchanged (C6); `conversation`/`grounded_chat` byte-for-byte unchanged.
  - `build_graph` wraps `writer_node` → `NodeStarted`/`NodeCompleted`/`NodeFailed` (phase `implement`) on the Event Bus — **no** Business telemetry (R8/C3); zero-subscriber runtime stays valid (C4/R6).
  - M6 does **not** implement outline tree management, `/outline`, the `ChapterCreated` product event (M8), the critic loop (M9), or citation formatting/persistence (M7).

- Consequences:
  - The writer is a swappable capability behind a port; future models/strategies need no topology or contract change (extensibility per the review).
  - A pure `DraftResult` cleanly separates *generation* from *what to do with the output*, enabling Critic/diff/compare/alternate renderers without touching the writer.
  - Contract-true: `writer.json` honored as-is; GraphState frozen; one node + one edge + additive route vocabulary.
  - A writer turn pays retrieval + a long generation on top of three M5 orchestration calls → higher latency (`B_write`); acceptable for M6, optimization deferred (M11), mitigated by streaming.
  - Carry-forward: `draft` may persist in the checkpoint across turns (same class as ADR-0027 `plan`/`task`/`route`); the writer overwrites it (set semantics) each turn.

- Alternatives considered:
  - **Hard-coded writer node (no capability/port)** — rejected; the review requires interchangeable writer implementations (`writer-v2/fast/reasoning/local`) without topology change.
  - **Writer returns a GraphState partial directly (no `DraftResult`)** — rejected; couples generation to state shape and hides `reasoning`/`metrics`; the value object keeps the writer pure and future-proof.
  - **Reuse `conversation_node` for drafting** — rejected; violates the writer contract.
  - **Ungrounded writer route (no retriever)** — rejected; writer value + citations need context (`empty_context` covers no-results).
  - **Auto-persist draft → chapter via RunContext + hook** — deferred (§6).
  - **Add a `chapter_id`/`draft_target` GraphState field** — rejected; violates ADR-0007.

- References: ADR-0007, ADR-0014, ADR-0024, ADR-0027, ADR-0030, ADR-0032, ADR-0033; `docs/runtime-constitution.md` (C8); `docs/runtime-contract.md` §5; `contracts/agents/writer.json`; `knowledge/agents/writer-agent.md`; `docs/superpowers/specs/2026-06-29-thesisos-m6-writing-workspace-design.md`.
