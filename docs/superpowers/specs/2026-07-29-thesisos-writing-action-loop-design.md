# ThesisOS Writing Action Loop — Design Spec

- **Status:** Draft (operator-approved scope B + surface A + actions A)
- **Date:** 2026-07-29
- **Scope:** Phases 0–5 — thin action loop for Writing panel `verify` and `find-sources`, inspired by OpenWorker patterns, **not** a port of OpenWorker/aisuite.
- **Out of scope:** LangGraph `/chat` topology changes (M12), MCP, multi-provider LLM, desktop/OS tools, Slack/mail automations, rewrite/expand in v1 loop.

---

## 1. Problem

Today every Writing panel action follows the same pipeline:

```text
POST /writing/actions
  → build one retrieval query
  → single corpus search (0–10 chunks)
  → single LLM generation
  → SSE stream draft
  → user adds Proposal (chapter unchanged until accept)
```

For **Verifica** and **Trova fonti**, one search is often insufficient: the model cannot reformulate queries, compare result sets, or re-read selection vs chapter before answering.

OpenWorker’s useful pattern is not the desktop shell — it is:

1. **Tool registry** — named capabilities with JSON schemas
2. **Turn loop** — model ↔ tool until done or cap
3. **Risk classification** — gate side effects before execution
4. **Out-of-band approval** — for consequential actions (ThesisOS already has this via Proposals for writes)

ThesisOS should adopt (1)–(3) in a **domain-specific, read-only** harness for two panel actions first.

---

## 2. Goals

| ID | Goal |
|----|------|
| G1 | `verify` and `find-sources` may run **multiple corpus searches** per request |
| G2 | `rewrite` and `expand` **unchanged** in v1 (single-pass path preserved) |
| G3 | Output still flows **Proposal → accept** — no silent chapter mutation (INV-COMP-5 / ADR-0045) |
| G4 | Stay inside **Runtime layer** boundaries (ADR-0030); no LangGraph topology change |
| G5 | Vertex-only LLM seam preserved (ADR-0002); tool calling via LiteLLM extension |
| G6 | Optional UI progress steps for loop actions (Phase 4) |

---

## 3. Non-goals

- Importing `openworker`, `aisuite`, or `coworker/` into product runtime
- General tool calling in `/chat` or Supervisor→Planner→Router graph
- Shell, filesystem, browser, MCP connectors
- Replacing `ProposalService` with OpenWorker-style per-tool approval cards (v1 tools are read-only → auto-allow)
- Multi-provider model router

---

## 4. Reference study (Phase 0)

Study these OpenWorker files **as patterns only** (no copy-paste into product):

| OpenWorker | Takeaway for ThesisOS |
|------------|----------------------|
| `coworker/engine.py` (`TurnEngine`) | Async loop, max iterations, concurrent safe reads |
| `coworker/tools/registry.py` | Register callables + JSON schemas |
| `coworker/risk.py` | `read` / `write_local` / `exec` / `external` taxonomy |
| `coworker/permissions.py` | `Decision(allowed, needs_user)` before execute |
| `coworker/tools/plan.py` | Out-of-band approval for mode switch (future; not v1) |

Deliverable: `docs/superpowers/research/2026-07-29-openworker-writing-loop-notes.md` (1–2 pages).

New ADR: **`decisions/ADR-0049-writing-action-loop.md`** — freezes module location, layer, invariants, M12 relationship.

---

## 5. Architecture

### 5.1 Layer placement (ADR-0030)

```text
Business     : app/graph/writer.py, app/services/writing/panel.py
               (prompt assembly, DraftResult — unchanged contract)

Runtime      : app/runtime/action_loop/*  ← NEW
               app/api/writing_actions.py (branch by action)
               app/services/conversation/ (SSE transport pattern reused)

Infrastructure : app/llm/litellm_client.py (+ tool-capable completion)
               app/services/retrieval/service.py (injected into tools)
```

Dependencies flow **downward**. Tools call `RetrievalService` via injection at composition root (`writing_actions.py`), not via graph nodes.

### 5.2 Two-phase pipeline (recommended)

Separate **retrieval loop** from **draft generation** to keep citation enforcement:

```text
Phase A — Retrieval loop (tool calling)
  Model + tools: search_corpus, get_selection_context
  Max 6 iterations (configurable)
  Accumulate RetrievedChunk[] (dedupe by chunk_id)
  Emit SSE step events (Phase 4)

Phase B — Draft generation (existing path)
  compose_writing_panel_wire(..., retrieved_context=accumulated)
  generate_with_citation_enforcement(...)
  SSE token + done (unchanged)
```

Why not one loop until final text? Academic citation discipline and existing tests live in Phase B; mixing tool JSON and prose streaming complicates the writer port.

### 5.3 Module layout

```text
backend/app/runtime/action_loop/
  __init__.py
  risk.py              # RiskClass enum + classify()
  permissions.py       # PermissionEngine (v1: read-only auto-allow)
  registry.py          # ToolRegistry + ToolSpec
  loop.py              # ActionLoopRunner
  types.py             # LoopStep, LoopResult, ToolCallRecord

backend/app/runtime/action_loop/tools/
  __init__.py
  corpus.py            # search_corpus tool factory
  context.py           # get_selection_context tool factory
```

### 5.4 Tools (v1)

| Tool | Risk | Args | Behavior |
|------|------|------|----------|
| `search_corpus` | `read` | `query: str`, `limit?: int` (default 10, max 10) | Calls `RetrievalService.search`; returns chunk summaries |
| `get_selection_context` | `read` | _(none — uses session context)_ | Returns selection + truncated chapter excerpt |

Session context (`ActionLoopContext`) is passed at runner construction — not global state.

### 5.5 Risk & permissions (v1)

All v1 tools are `RiskClass.READ` → **auto-allow** in `Mode.INTERACTIVE`.

Permission engine exists so Phase 5 can add `propose_edit` (`write_local`) without redesign.

No LangGraph `interrupt()` in v1.

### 5.6 LLM tool calling seam

Extend `LLMClient` protocol optionally:

```python
async def acompletion_with_tools(
    messages: list[dict],
    *,
    tools: list[dict],
    model: str | None = None,
    params: dict | None = None,
) -> AssistantTurn: ...
```

`AssistantTurn` carries `content: str | None`, `tool_calls: list[ToolCall]`, `finish_reason`.

Implementation: `LiteLLMClient` delegates to `litellm.acompletion(..., tools=tools, tool_choice="auto")`.

Vertex Gemini tool calling verified in Phase 1 spike; if blocked, fallback is **fixed multi-search script** (Phase 3 contingency — document in ADR).

### 5.7 API / SSE contract

**Unchanged request body** for `POST /writing/actions`.

**Extended SSE events** (backward compatible):

| Event | When | Payload |
|-------|------|---------|
| `step` | Phase A tool start/end | `{ "phase": "retrieval", "label": "...", "detail"?: "..." }` |
| `token` | Phase B streaming | `{ "text": "..." }` (unchanged) |
| `done` | Complete | `{ "draft": "...", "meta"?: { "search_count": N, "chunk_count": M } }` |
| `error` | Failure | `{ "code", "message" }` (unchanged) |

Frontend: ignore unknown events; show steps only for `verify` / `find-sources`.

### 5.8 Action routing

```python
LOOP_ACTIONS = frozenset({"verify", "find-sources"})
LEGACY_ACTIONS = frozenset({"rewrite", "expand"})
```

`writing_actions.py`:

- `LOOP_ACTIONS` → `run_writing_panel_with_loop(...)`
- `LEGACY_ACTIONS` → existing `fetch_panel_retrieved_context` + `run_writing_panel_action`

Remove upfront `fetch_panel_retrieved_context` for loop actions (retrieval moves into loop).

---

## 6. Invariants

- **INV-WAL-1:** Loop actions MUST NOT PATCH chapters or memory directly.
- **INV-WAL-2:** Final draft MUST pass through existing citation enforcement when chunks present.
- **INV-WAL-3:** `rewrite` / `expand` behavior unchanged until Phase 5 explicitly enabled.
- **INV-WAL-4:** Max loop iterations enforced server-side (default 6).
- **INV-WAL-5:** Tool execution MUST NOT import `builder_engine` or mutate governance artifacts.
- **INV-WAL-6:** Product runtime MUST NOT depend on `openworker` / `aisuite` packages.

---

## 7. Testing strategy

| Layer | Tests |
|-------|-------|
| Unit | `risk`, `permissions`, `registry`, `loop` with fake provider |
| Tool unit | `search_corpus`, `get_selection_context` with fake retrieval |
| API | SSE includes `step` for verify; rewrite unchanged; embed failure 422 |
| Frontend | `aiActions` parses `step`; panel shows progress for loop actions |

Gate: `make ci` green; no regression on `test_writing_actions_api.py` legacy paths.

---

## 8. Phased delivery

| Phase | Deliverable | User-visible |
|-------|-------------|--------------|
| **0** | Research notes + ADR-0049 draft | No |
| **1** | `action_loop` core + LLM tools seam + unit tests | No |
| **2** | Read-only tools wired to RetrievalService | No |
| **3** | `verify` + `find-sources` on loop path | Yes (quality) |
| **4** | SSE `step` + panel progress UI | Yes (transparency) |
| **5** | Extension playbook (rewrite/expand, `propose_edit`) | Future |

**Deferred (Phase 5 — doc only, not in v1 scope):**

- **Rewrite / expand on loop path** — after Phase 3 is stable and selection-context retrieval is validated.
- **`propose_edit` (`write_local`)** — permission `needs_user`; must reuse Proposal API; never direct PATCH.
- **MCP bridge** — requires a separate ADR; not mixed with the panel loop.
- **M12 graph re-entry** — requires ADR-0027 amendment; panel loop remains lateral to `/chat` topology.

See ADR-0049 § Phase 5 — Extensions (deferred).

---

## 9. Success criteria (Phase 3 done)

1. Integration test: `find-sources` with fake LLM triggers **≥2** `search_corpus` calls before draft.
2. `rewrite` test unchanged (single retrieval path).
3. Draft still arrives via SSE `done`; Proposal flow unchanged in frontend.
4. No new GraphState fields; no `/chat` graph edits.

---

## 10. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Vertex tool calling unstable | Phase 1 spike; scripted multi-search fallback |
| Latency (multiple LLM round-trips) | Cap iterations; show steps in UI |
| Duplicate chunks | Dedupe by `chunk_id` in accumulator |
| Scope creep into M12 | ADR + plan explicitly forbid graph changes |

---

## 11. References

- ADR-0002 Vertex runtime
- ADR-0027 Multi-agent topology (M12 deferred)
- ADR-0030 Layer boundaries
- ADR-0031 Writer capability port
- ADR-0039 Lateral action runner
- ADR-0045 Companion / chapter safety
- OpenWorker README + `coworker/engine.py` (external reference)

---

## 12. Approaches considered

| Approach | Verdict |
|----------|---------|
| **A. Homemade action loop (chosen)** | Fits ASEP layers; minimal deps |
| B. Import aisuite | Rejected — wrong governance boundary |
| C. Fixed script (no tool calls) | Rejected — doesn't learn OpenWorker loop pattern |

---

**Operator decisions locked in this spec:**

- Scope **B** (study → thin domain harness)
- Surface **A** (Writing panel)
- Actions **A** first (`verify`, `find-sources`)
