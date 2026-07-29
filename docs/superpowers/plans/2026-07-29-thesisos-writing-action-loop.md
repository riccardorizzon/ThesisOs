# Writing Action Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only tool loop for Writing panel `verify` and `find-sources` so the AI can search the corpus multiple times before drafting, while `rewrite`/`expand` stay on the legacy single-pass path.

**Architecture:** New Runtime module `backend/app/runtime/action_loop/` (registry, risk, permissions, loop runner). Two-phase pipeline: retrieval tool loop → existing writer + citation enforcement. Branch in `writing_actions.py` by action id. Optional SSE `step` events + frontend progress (Phase 4).

**Tech Stack:** Python 3.11+, FastAPI, LiteLLM (Vertex), existing `RetrievalService`, React/TypeScript frontend SSE client.

**Spec:** `docs/superpowers/specs/2026-07-29-thesisos-writing-action-loop-design.md`  
**ADR:** `decisions/ADR-0049-writing-action-loop.md`  
**Research:** `docs/superpowers/research/2026-07-29-openworker-writing-loop-notes.md`

## Global Constraints

- **No** LangGraph `/chat` topology changes (ADR-0027 M12 deferred).
- **No** `openworker`, `aisuite`, or MCP in product runtime.
- **Vertex-only** LLM (ADR-0002); tool calling via LiteLLM extension only.
- Loop actions **must not** PATCH chapters or memory; Proposal flow unchanged (ADR-0045).
- Max **6** retrieval loop iterations (server-enforced).
- v1 tools are **read-only** (`RiskClass.READ` → auto-allow).
- Do **not** commit unless the operator explicitly requests a commit.
- Run `make ci` before claiming phase complete.

## File Map

| Path | Responsibility |
|------|----------------|
| `decisions/ADR-0049-writing-action-loop.md` | Architecture decision (Phase 0) |
| `docs/superpowers/research/2026-07-29-openworker-writing-loop-notes.md` | Phase 0 study notes |
| `backend/app/runtime/action_loop/types.py` | `ActionLoopContext`, `LoopResult`, `ToolCallRecord`, `AssistantTurn` |
| `backend/app/runtime/action_loop/risk.py` | `RiskClass`, `classify()` |
| `backend/app/runtime/action_loop/permissions.py` | `PermissionEngine`, `Decision`, `Mode` |
| `backend/app/runtime/action_loop/registry.py` | `ToolRegistry`, `ToolSpec` |
| `backend/app/runtime/action_loop/loop.py` | `ActionLoopRunner` |
| `backend/app/runtime/action_loop/tools/corpus.py` | `search_corpus` factory |
| `backend/app/runtime/action_loop/tools/context.py` | `get_selection_context` factory |
| `backend/app/runtime/action_loop/tools/__init__.py` | `build_panel_tools(context)` |
| `backend/app/llm/base.py` | Extend protocol with optional tool completion |
| `backend/app/llm/litellm_client.py` | `acompletion_with_tools` |
| `backend/app/services/writing/action_loop_runner.py` | Orchestrates loop + writer for panel |
| `backend/app/api/writing_actions.py` | Branch loop vs legacy actions |
| `backend/tests/test_action_loop_*.py` | Unit tests |
| `backend/tests/test_writing_action_loop_api.py` | API integration |
| `frontend/lib/aiActions.ts` | Parse `step` SSE event |
| `frontend/components/writing/WritingAiPanel.tsx` | Show progress steps |
| `frontend/components/writing/WritingAiPanel.test.tsx` | Step UI tests |

---

## Phase 0 — Study & ADR (no product code)

**Exit criteria:** Research notes + ADR-0049 exist; operator sign-off on spec.

### Task 0: Lock research and ADR

**Files:**
- Create: `docs/superpowers/research/2026-07-29-openworker-writing-loop-notes.md` ✅
- Create: `decisions/ADR-0049-writing-action-loop.md` ✅
- Create: `docs/superpowers/specs/2026-07-29-thesisos-writing-action-loop-design.md` ✅

- [ ] **Step 1: Read OpenWorker source (patterns only)**

Skim (do not copy):
- https://github.com/andrewyng/openworker/blob/main/coworker/engine.py
- https://github.com/andrewyng/openworker/blob/main/coworker/risk.py
- https://github.com/andrewyng/openworker/blob/main/coworker/tools/registry.py

Annotate in research notes if anything differs from spec assumptions.

- [ ] **Step 2: Vertex tool-calling spike (manual)**

Run in dev environment with configured Vertex:

```python
import asyncio
import litellm

async def main():
    resp = await litellm.acompletion(
        model="vertex_ai/gemini-2.0-flash",
        messages=[{"role": "user", "content": "Search for craftsmanship"}],
        tools=[{
            "type": "function",
            "function": {
                "name": "search_corpus",
                "description": "Search thesis corpus",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        }],
        tool_choice="auto",
        vertex_project="YOUR_PROJECT",
        vertex_location="YOUR_LOCATION",
    )
    print(resp.choices[0].message)

asyncio.run(main())
```

Expected: response includes `tool_calls` OR documents fallback need in ADR.

- [ ] **Step 3: Mark ADR status**

If spike passes: keep ADR-0049 as **Proposed** until Phase 3 ships, then **Accepted**.  
If spike fails: add "Contingency: scripted multi-search" subsection to ADR before Phase 1.

---

## Phase 1 — Action loop foundations (no UX change)

**Exit criteria:** Unit tests pass for risk, permissions, registry, loop with fake LLM.

### Task 1: Core types

**Files:**
- Create: `backend/app/runtime/action_loop/__init__.py`
- Create: `backend/app/runtime/action_loop/types.py`
- Test: `backend/tests/test_action_loop_types.py`

**Interfaces:**
- Produces: `ActionLoopContext`, `AssistantTurn`, `ToolCall`, `LoopStep`, `LoopResult`

- [ ] **Step 1: Write failing type tests**

```python
# backend/tests/test_action_loop_types.py
from app.runtime.action_loop.types import ActionLoopContext, ToolCall, AssistantTurn

def test_action_loop_context_fields():
    ctx = ActionLoopContext(
        action="verify",
        project_id="p1",
        selection_text="sel",
        chapter_content="chapter",
        context_summary="rules",
    )
    assert ctx.action == "verify"
    assert ctx.project_id == "p1"

def test_assistant_turn_tool_calls_default_empty():
    turn = AssistantTurn(content="done", tool_calls=[], finish_reason="stop")
    assert turn.tool_calls == []
```

- [ ] **Step 2: Run test — expect FAIL**

Run: `cd backend && pytest tests/test_action_loop_types.py -v`  
Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement types**

```python
# backend/app/runtime/action_loop/types.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ActionLoopContext:
    action: str
    project_id: str | None
    selection_text: str | None
    chapter_content: str
    context_summary: str | None

@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass(frozen=True)
class AssistantTurn:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None

@dataclass(frozen=True)
class ToolCallRecord:
    name: str
    arguments: dict[str, Any]
    result_summary: str

@dataclass(frozen=True)
class LoopStep:
    label: str
    detail: str | None = None

@dataclass
class LoopResult:
    chunks: list  # RetrievedChunk — typed at integration
    steps: list[LoopStep]
    tool_calls: list[ToolCallRecord]
```

- [ ] **Step 4: Run test — expect PASS**

### Task 2: Risk classification

**Files:**
- Create: `backend/app/runtime/action_loop/risk.py`
- Test: `backend/tests/test_action_loop_risk.py`

- [ ] **Step 1: Write failing tests**

```python
from app.runtime.action_loop.risk import RiskClass, classify, is_consequential

def test_builtin_read_tools():
    assert classify("search_corpus") is RiskClass.READ
    assert classify("get_selection_context") is RiskClass.READ

def test_unknown_tool_is_read_by_default():
    assert classify("unknown_tool") is RiskClass.READ

def test_consequential_excludes_read():
    assert is_consequential(RiskClass.READ) is False
    assert is_consequential(RiskClass.WRITE_LOCAL) is True
```

- [ ] **Step 2: Implement risk.py** (mirror OpenWorker taxonomy, v1 builtins)

- [ ] **Step 3: Run tests — PASS**

### Task 3: Permission engine (read-only v1)

**Files:**
- Create: `backend/app/runtime/action_loop/permissions.py`
- Test: `backend/tests/test_action_loop_permissions.py`

- [ ] **Step 1: Test auto-allow read tools**

```python
from pathlib import Path
from app.runtime.action_loop.permissions import PermissionEngine, Mode
from app.runtime.action_loop.risk import RiskClass, classify

def test_interactive_allows_read():
    engine = PermissionEngine(workspace_root=Path("/tmp"))
    d = engine.check("search_corpus", {"query": "craft"}, classify("search_corpus"))
    assert d.allowed is True
    assert d.needs_user is False
```

- [ ] **Step 2: Implement minimal PermissionEngine.check()**

- [ ] **Step 3: Run tests — PASS**

### Task 4: Tool registry

**Files:**
- Create: `backend/app/runtime/action_loop/registry.py`
- Test: `backend/tests/test_action_loop_registry.py`

- [ ] **Step 1: Test register and execute**

```python
from app.runtime.action_loop.registry import ToolRegistry

def test_registry_execute():
    reg = ToolRegistry()

    def echo_query(query: str) -> dict:
        """Echo a query."""
        return {"query": query}

    reg.register(echo_query)
    assert reg.execute("echo_query", {"query": "x"}) == {"query": "x"}
    schemas = reg.schemas()
    assert schemas[0]["function"]["name"] == "echo_query"
```

- [ ] **Step 2: Implement ToolRegistry** (manual schema from function name + docstring or explicit dict)

- [ ] **Step 3: Run tests — PASS**

### Task 5: Action loop runner (fake provider)

**Files:**
- Create: `backend/app/runtime/action_loop/loop.py`
- Test: `backend/tests/test_action_loop_runner.py`

**Interfaces:**
- Consumes: `ToolRegistry`, `PermissionEngine`, callable `complete(messages, tools) -> AssistantTurn`
- Produces: `LoopResult` with accumulated tool results and steps

- [ ] **Step 1: Test two-iteration loop then stop**

```python
import pytest
from app.runtime.action_loop.loop import ActionLoopRunner
from app.runtime.action_loop.registry import ToolRegistry
from app.runtime.action_loop.permissions import PermissionEngine
from app.runtime.action_loop.types import AssistantTurn, ToolCall

@pytest.mark.asyncio
async def test_loop_runs_tools_until_no_tool_calls():
    calls = {"n": 0}

    async def fake_complete(messages, tools):
        calls["n"] += 1
        if calls["n"] == 1:
            return AssistantTurn(
                content=None,
                tool_calls=[ToolCall(id="1", name="search_corpus", arguments={"query": "a"})],
                finish_reason="tool_calls",
            )
        return AssistantTurn(content="done", tool_calls=[], finish_reason="stop")

    reg = ToolRegistry()
    reg.register(lambda query: {"hits": 1})  # name search_corpus via register alias in test setup

    runner = ActionLoopRunner(
        registry=reg,
        permissions=PermissionEngine(workspace_root=__import__("pathlib").Path("/tmp")),
        complete=fake_complete,
        max_iterations=6,
    )
    result = await runner.run(messages=[{"role": "user", "content": "find sources"}])
    assert calls["n"] == 2
    assert result.steps
```

- [ ] **Step 2: Implement ActionLoopRunner**

Key behaviors:
- Increment iteration counter; break at max
- For each tool call: permission check → execute → append tool message
- Emit step callback optional: `on_step(LoopStep)`
- Dedupe chunk accumulation in Task 7

- [ ] **Step 3: Run tests — PASS**

### Task 6: LLM tool calling seam

**Files:**
- Modify: `backend/app/llm/base.py`
- Modify: `backend/app/llm/litellm_client.py`
- Test: `backend/tests/test_litellm_tools.py`

- [ ] **Step 1: Add protocol method + test with monkeypatched litellm**

```python
@pytest.mark.asyncio
async def test_litellm_client_acompletion_with_tools(monkeypatch):
    class FakeMsg:
        content = None
        tool_calls = [{"id": "t1", "function": {"name": "search_corpus", "arguments": '{"query":"x"}'}}]

    class FakeChoice:
        message = FakeMsg()
        finish_reason = "tool_calls"

    class FakeResp:
        choices = [FakeChoice()]

    async def fake_acompletion(**kwargs):
        assert "tools" in kwargs
        return FakeResp

    monkeypatch.setattr("app.llm.litellm_client.litellm.acompletion", fake_acompletion)
    from app.llm.litellm_client import LiteLLMClient
    client = LiteLLMClient(project="p", location="europe-west1", model="gemini-2.0-flash")
    turn = await client.acompletion_with_tools([{"role": "user", "content": "hi"}], tools=[{"type": "function", "function": {"name": "search_corpus", "parameters": {"type": "object", "properties": {}}}}])
    assert turn.tool_calls[0].name == "search_corpus"
```

- [ ] **Step 2: Implement `acompletion_with_tools` mapping LiteLLM response → `AssistantTurn`**

- [ ] **Step 3: Run tests — PASS**

**Phase 1 gate:** `pytest backend/tests/test_action_loop_*.py backend/tests/test_litellm_tools.py -v`

---

## Phase 2 — Read-only domain tools

**Exit criteria:** Tools call real `RetrievalService` in unit tests with fake service.

### Task 7: search_corpus tool

**Files:**
- Create: `backend/app/runtime/action_loop/tools/corpus.py`
- Create: `backend/app/runtime/action_loop/tools/__init__.py`
- Test: `backend/tests/test_action_loop_tools_corpus.py`

- [ ] **Step 1: Test tool returns chunk summaries**

Use `FakeRetrievalService` pattern from `test_writing_actions_api.py`.

- [ ] **Step 2: Implement factory**

```python
def make_search_corpus_tool(*, retrieval_service, project_id: str | None, accumulate: list):
    async def search_corpus(query: str, limit: int = 10) -> dict:
        """Search the thesis corpus for relevant passages."""
        ...
    return search_corpus
```

- Dedupe into `accumulate: list[RetrievedChunk]` by `chunk_id`
- Cap `limit` at 10

- [ ] **Step 3: Run tests — PASS**

### Task 8: get_selection_context tool

**Files:**
- Create: `backend/app/runtime/action_loop/tools/context.py`
- Test: `backend/tests/test_action_loop_tools_context.py`

- [ ] **Step 1: Test returns selection + truncated chapter**

- [ ] **Step 2: Implement** (pure read from `ActionLoopContext`, max 4000 chars chapter excerpt)

- [ ] **Step 3: Run tests — PASS**

### Task 9: build_panel_tools helper

**Files:**
- Modify: `backend/app/runtime/action_loop/tools/__init__.py`

- [ ] **Step 1: Export `build_panel_tools(ctx, retrieval_service, accumulate) -> ToolRegistry`**

Registers both tools with correct names for `risk.classify`.

**Phase 2 gate:** `pytest backend/tests/test_action_loop_tools_*.py -v`

---

## Phase 3 — Wire verify + find-sources

**Exit criteria:** API uses loop for two actions; rewrite unchanged; integration test shows multi-search.

### Task 10: Panel orchestrator service

**Files:**
- Create: `backend/app/services/writing/action_loop_runner.py`
- Test: `backend/tests/test_writing_action_loop_service.py`

**Interfaces:**
- Consumes: `LLMClient`, `RetrievalService`, `ActionLoopContext`, `LLMWriter` / writer prompts
- Produces: `DraftResult`, step callbacks

- [ ] **Step 1: Test orchestrator runs loop then writer**

```python
@pytest.mark.asyncio
async def test_run_panel_with_loop_accumulates_chunks_before_draft(monkeypatch):
    search_count = {"n": 0}

    async def fake_complete(messages, tools):
        search_count["n"] += 1
        if search_count["n"] < 2:
            return AssistantTurn(content=None, tool_calls=[ToolCall(id="1", name="search_corpus", arguments={"query": f"q{search_count['n']}"})])
        return AssistantTurn(content=None, tool_calls=[], finish_reason="stop")

    # assert final DraftResult uses accumulated chunks count >= 1
    # assert search_count["n"] >= 2
```

- [ ] **Step 2: Implement `run_writing_panel_with_loop`**

Pipeline:
1. Build system prompt: action instructions + context_summary (reuse `WRITING_PANEL_ACTIONS` text)
2. Run `ActionLoopRunner` with `build_panel_tools`
3. `compose_writing_panel_wire(..., retrieved_context=accumulated)`
4. `generate_with_citation_enforcement`
5. Return `DraftResult` with metadata: `search_count`, `chunk_count`, `loop_action: true`

- [ ] **Step 3: Run tests — PASS**

### Task 11: API branch

**Files:**
- Modify: `backend/app/api/writing_actions.py`
- Test: `backend/tests/test_writing_action_loop_api.py`

- [ ] **Step 1: Test verify uses loop path (monkeypatch orchestrator)**

```python
def test_verify_uses_action_loop(client, monkeypatch):
    seen = {}

    async def fake_loop(**kwargs):
        seen["loop"] = True
        return DraftResult(draft="Verifica ok.", citations=[], metadata={"loop_action": True})

    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_with_loop", fake_loop)

    with client.stream("POST", "/writing/actions", json={"action": "verify", "chapter_content": "Cap"}) as resp:
        body = "".join(resp.iter_text())
    assert seen.get("loop") is True
    assert "Verifica ok." in body
```

- [ ] **Step 2: Test rewrite still uses legacy path**

```python
def test_rewrite_skips_action_loop(client, monkeypatch):
    async def fail_loop(**kwargs):
        raise AssertionError("loop should not run")

    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_with_loop", fail_loop)
    # existing FakeWriter path still works
```

- [ ] **Step 3: Implement routing**

```python
LOOP_ACTIONS = frozenset({"verify", "find-sources"})

# in event_gen():
if req.action in LOOP_ACTIONS:
    result = await run_writing_panel_with_loop(...)
else:
    retrieved_context = await fetch_panel_retrieved_context(...)
    result = await run_writing_panel_action(...)
```

Remove upfront `fetch_panel_retrieved_context` for loop actions.

- [ ] **Step 4: Run full writing tests**

Run: `pytest backend/tests/test_writing_actions_api.py backend/tests/test_writing_action_loop_api.py -v`

**Phase 3 gate:** Integration test proves ≥2 searches for find-sources with fake LLM.

---

## Phase 4 — Progress visibility (SSE steps + UI)

**Exit criteria:** User sees "Sto cercando…" steps for verify/find-sources; rewrite unchanged UI.

### Task 12: Backend SSE step events

**Files:**
- Modify: `backend/app/api/writing_actions.py`
- Modify: `backend/app/services/writing/action_loop_runner.py`
- Test: `backend/tests/test_writing_action_loop_api.py`

- [ ] **Step 1: Test SSE contains step events**

```python
def test_verify_stream_includes_step_events(client, monkeypatch):
    async def fake_loop(*, on_step=None, **kwargs):
        if on_step:
            on_step(LoopStep(label="Ricerca nel corpus", detail="craftsmanship"))
        return DraftResult(draft="Ok.", citations=[], metadata={})

    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_with_loop", fake_loop)
    with client.stream("POST", "/writing/actions", json={"action": "verify", "chapter_content": "x"}) as resp:
        body = "".join(resp.iter_text())
    assert "event: step" in body
    assert "Ricerca nel corpus" in body
```

- [ ] **Step 2: Wire `on_step` → yield SSE**

```python
yield {"event": "step", "data": json.dumps({"phase": "retrieval", "label": step.label, "detail": step.detail})}
```

- [ ] **Step 3: Extend done payload**

```python
{"draft": draft, "meta": {"search_count": N, "chunk_count": M}}
```

### Task 13: Frontend SSE + UI

**Files:**
- Modify: `frontend/lib/aiActions.ts`
- Modify: `frontend/lib/aiActions.test.ts`
- Modify: `frontend/components/writing/WritingAiPanel.tsx`
- Modify: `frontend/components/writing/WritingAiPanel.test.tsx`

- [ ] **Step 1: Extend event type**

```typescript
export type WritingActionStreamEvent =
  | { event: "token"; data: { text: string } }
  | { event: "step"; data: { phase: "retrieval"; label: string; detail?: string } }
  | { event: "done"; data: { draft: string; meta?: { search_count?: number; chunk_count?: number } } }
  | { event: "error"; data: { code: string; message: string } };
```

- [ ] **Step 2: Panel state `steps: LoopStep[]` — append on step event, clear on new action**

Show list above stream area when `activeActionId` is `verify` or `find-sources`.

Italian copy examples:
- "Ricerca nel corpus…"
- "Lettura del contesto…"
- "Preparazione della risposta…"

- [ ] **Step 3: Tests — step events render**

Run: `cd frontend && npm test -- WritingAiPanel aiActions`

**Phase 4 gate:** Manual smoke — Trova fonti shows ≥1 step before tokens.

---

## Phase 5 — Extension playbook (document only; do not implement in this plan)

**Purpose:** Close the roadmap without scope creep.

### Task 14: Extension ADR addendum (doc task)

**Files:**
- Modify: `decisions/ADR-0049-writing-action-loop.md` (add "Phase 5" section)

Document future work:

| Item | Preconditions |
|------|---------------|
| Enable loop for `rewrite` / `expand` | Phase 3 stable; add `get_selection_context` value proven |
| Add `propose_edit` tool (`write_local`) | Permission `needs_user` + reuse Proposal API — never direct PATCH |
| MCP bridge | Separate ADR; not mixed with panel loop |
| M12 graph re-entry | ADR-0027 amendment; do not bolt onto panel loop |

- [ ] **Step 1: Write Phase 5 section in ADR-0049**
- [ ] **Step 2: Add "Deferred" section to spec if not present**

**No code tasks in Phase 5 for this plan.**

---

## Contingency: Vertex tool calling unavailable

If Task 0 spike fails:

### Task C1: Scripted multi-search fallback

**Files:**
- Create: `backend/app/services/writing/scripted_retrieval.py`
- Modify: `backend/app/services/writing/action_loop_runner.py`

Behavior without tool calls:
1. Search with `build_retrieval_query` (selection)
2. Search with first 500 chars of chapter (if find-sources)
3. Search with LLM-extracted keywords via single `generate()` call (optional)
4. Proceed to Phase B draft

Feature flag: `WRITING_LOOP_MODE=scripted|tools` in config.

---

## Verification checklist (plan complete)

- [ ] Phase 0: research + ADR + Vertex spike documented
- [ ] Phase 1: `action_loop` unit tests green
- [ ] Phase 2: corpus + context tools green
- [ ] Phase 3: verify/find-sources on loop; rewrite legacy
- [ ] Phase 4: SSE step + UI progress
- [ ] Phase 5: extension doc in ADR
- [ ] `make ci` green

---

## Execution order summary

```text
Phase 0 (study) ──► Phase 1 (core loop) ──► Phase 2 (tools)
                                              │
                                              ▼
                                    Phase 3 (API wire)
                                              │
                                              ▼
                                    Phase 4 (UI steps)
                                              │
                                              ▼
                                    Phase 5 (doc only)
```

Estimated effort:
- Phase 0: 0.5–1 day
- Phase 1–2: 2–3 days
- Phase 3: 1–2 days
- Phase 4: 1 day
- Phase 5: 0.5 day (documentation)

---

**Plan complete.** Implementation options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks
2. **Inline Execution** — execute tasks in session with checkpoints

Which approach do you want for implementation?
