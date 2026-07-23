# Tiered Gemini Chat Latency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Route orchestration through Gemini 3.5 Flash-Lite, route thesis production through
Gemini 3.6 Flash, and reduce chat time-to-first-token while preserving the complete LangGraph.

> **Status 2026-07-23 (complete):** Tasks 1–5 done. Full CI green (`make ci` exit 0).
> Deployed via docker compose rebuild; `/ready` 200; container config verified
> `global gemini-3.6-flash gemini-3.5-flash-lite`. Live evidence (3 resume + 3 ordinary
> turns): resume median first token **2.15s** (≤5s), ordinary median **5.16s** (≤8s);
> resume orchestration nodes at **0ms** in `agent_steps`; ordinary orchestration on
> Flash-Lite (~0.8–1.4s/node). Grounded turn emitted `sources`; Writer branch confirmed
> `retriever → writer` (11.0s writer node). Diagnostic conversations/runs/tasks deleted
> (verified 0 residues); backend logs clean. Deployed E2E: 9/9 passed.
> Persistence contract verified live on top (ADR-0046): «la salvo» and «basta per oggi»
> now write memory rows (v6→v7, v12→v13) before confirming; real continuity rows
> restored afterwards via versioned memory API.

**Architecture:** Keep the current graph topology and inject a second LLM client only into
Supervisor, Planner and Router. Deterministically classify the Companion resume marker inside
those nodes, and stream non-academic model chunks immediately while retaining buffered
academic citation enforcement.

**Tech Stack:** Python 3.12, FastAPI, LangGraph, LiteLLM, Vertex AI, pytest, PostgreSQL, SSE.

## Global Constraints

- Use only GA models: `gemini-3.6-flash` and `gemini-3.5-flash-lite`.
- Set the Vertex default location to `global`.
- Do not change the `/chat` request or SSE event contracts.
- Do not remove, reorder or bypass LangGraph nodes.
- Preserve academic citation validation and Companion `replace` repair.
- Preserve Grounded `Retriever → Conversation` and Writer `Retriever → Writer` branches.
- Do not commit the existing working tree unless the user explicitly requests a commit.

## File Map

- Modify `backend/app/core/config.py`: model-tier defaults.
- Modify `backend/app/llm/factory.py`: response and orchestration client factories.
- Modify `backend/app/graph/conversation.py`: inject model tiers and select streaming policy.
- Create `backend/app/graph/companion/protocol.py`: Companion marker contract.
- Modify `backend/app/graph/workspace_context.py`: consume the shared marker contract.
- Modify `backend/app/graph/supervisor.py`: deterministic resume plan.
- Modify `backend/app/graph/planner.py`: deterministic resume plan preservation.
- Modify `backend/app/graph/router.py`: deterministic resume route.
- Modify `backend/app/graph/inference_enforcement.py`: immediate non-academic streaming.
- Modify `backend/app/services/conversation/service.py`: production composition root.
- Modify relevant backend tests listed per task.

---

### Task 1: Configure and construct the two GA model tiers

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/llm/factory.py`
- Modify: `backend/tests/test_llm_factory.py`

**Interfaces:**
- Produces: `get_llm_client() -> LLMClient`
- Produces: `get_orchestration_llm_client() -> LLMClient`
- Produces setting: `settings.gemini_orchestration_model: str`

- [x] **Step 1: Write failing factory tests**

Add assertions that the response and orchestration factories use distinct models and the
global endpoint:

```python
from app.llm.factory import get_llm_client, get_orchestration_llm_client


def test_factory_uses_tiered_models(monkeypatch):
    import app.llm.factory as mod

    monkeypatch.setattr(mod.settings, "google_cloud_project", "thesisos-prod")
    monkeypatch.setattr(mod.settings, "vertex_location", "global")
    monkeypatch.setattr(mod.settings, "gemini_model", "gemini-3.6-flash")
    monkeypatch.setattr(
        mod.settings,
        "gemini_orchestration_model",
        "gemini-3.5-flash-lite",
    )

    response = get_llm_client()
    orchestration = get_orchestration_llm_client()

    assert response._location == "global"
    assert response._model == "gemini-3.6-flash"
    assert orchestration._location == "global"
    assert orchestration._model == "gemini-3.5-flash-lite"
```

Extend the unconfigured test to assert both factories return `NotConfiguredLLM`.

- [x] **Step 2: Run the tests and confirm RED**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_llm_factory.py
```

Expected: failure because `gemini_orchestration_model` and
`get_orchestration_llm_client` do not exist.

- [x] **Step 3: Add model-tier settings**

Change the model defaults in `Settings`:

```python
vertex_location: str = "global"
gemini_model: str = "gemini-3.6-flash"
gemini_orchestration_model: str = "gemini-3.5-flash-lite"
```

- [x] **Step 4: Implement the focused factories**

Refactor `backend/app/llm/factory.py` to use one private constructor:

```python
def _get_client(model: str):
    if settings.google_cloud_project:
        return LiteLLMClient(
            project=settings.google_cloud_project,
            location=settings.vertex_location,
            model=model,
        )
    return NotConfiguredLLM()


def get_llm_client():
    return _get_client(settings.gemini_model)


def get_orchestration_llm_client():
    return _get_client(settings.gemini_orchestration_model)
```

- [x] **Step 5: Run focused tests and confirm GREEN**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_llm_factory.py tests/test_litellm_client.py
```

Expected: all selected tests pass.

---

### Task 2: Inject the fast orchestration client without changing graph topology

**Files:**
- Modify: `backend/app/graph/conversation.py`
- Modify: `backend/app/services/conversation/service.py`
- Modify: `backend/tests/test_m5_graph_topology.py`
- Modify: `backend/tests/test_companion_chat_wiring.py`

**Interfaces:**
- Consumes: `get_orchestration_llm_client()`
- Produces:
  `build_graph(llm, *, orchestration_llm: LLMClient | None = None, checkpointer, ...)`

- [x] **Step 1: Write a failing dual-client graph test**

Add a test that supplies separate fakes:

```python
async def test_orchestration_and_response_use_separate_clients(in_memory_checkpointer):
    response = OrchestrationLLM(stream_parts=["answer"])
    orchestration = OrchestrationLLM()
    graph = build_graph(
        response,
        orchestration_llm=orchestration,
        checkpointer=in_memory_checkpointer,
        memory_service=_StubMemory(),
    )
    cfg = {"configurable": {"thread_id": "tiered-models"}}

    chunks = [
        chunk
        async for chunk in graph.astream(
            GraphState(messages=[Message(role="user", content="Hello")]),
            cfg,
            stream_mode="custom",
        )
    ]

    assert orchestration.generate_calls == 3
    assert response.generate_calls == 0
    assert response.last_stream_messages is not None
    assert any(chunk.get("type") == "token" for chunk in chunks)
```

- [x] **Step 2: Run the focused test and confirm RED**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_m5_graph_topology.py::test_orchestration_and_response_use_separate_clients
```

Expected: failure because `build_graph` rejects `orchestration_llm`.

- [x] **Step 3: Route graph responsibilities to the correct client**

In `build_graph`, resolve the optional tier and use it only for the three planning nodes:

```python
orchestrator = orchestration_llm or llm

g.add_node(
    "supervisor_node",
    node("supervisor", make_supervisor_node(orchestrator), "plan"),
)
g.add_node(
    "planner_node",
    node(
        "planner",
        make_planner_node(orchestrator, on_task_ref=on_task_ref),
        "plan",
    ),
)
g.add_node(
    "router_node",
    node("router", make_router_node(orchestrator), "plan", route_event=True),
)
```

Keep Conversation and Writer on the original `llm`.

- [x] **Step 4: Wire both clients in the production composition root**

Import `get_orchestration_llm_client` in `ConversationService` and construct the graph with:

```python
graph = build_graph(
    get_llm_client(),
    orchestration_llm=get_orchestration_llm_client(),
    checkpointer=saver,
    task_service=self._task_service,
    emitter=self._event_bus,
    run_context=rc,
)
```

Update service tests that monkeypatch `get_llm_client` to also monkeypatch
`get_orchestration_llm_client`, using the same fake unless the test specifically verifies
model separation.

- [x] **Step 5: Verify topology and service wiring**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_m5_graph_topology.py \
  tests/test_companion_chat_wiring.py \
  tests/test_conversations_api.py \
  tests/test_runtime_observability.py
```

Expected: all selected tests pass and existing edge assertions remain unchanged.

---

### Task 3: Add the deterministic Companion resume path inside existing nodes

**Files:**
- Create: `backend/app/graph/companion/protocol.py`
- Modify: `backend/app/graph/workspace_context.py`
- Modify: `backend/app/graph/supervisor.py`
- Modify: `backend/app/graph/planner.py`
- Modify: `backend/app/graph/router.py`
- Modify: `backend/tests/test_companion_chat_wiring.py`

**Interfaces:**
- Produces: `COMPANION_OPEN_MARKER = "__companion_open__"`
- Produces: `COMPANION_OPEN_UTTERANCE = "Continuiamo da ieri"`
- Produces: `is_companion_open(text: str | None) -> bool`

- [x] **Step 1: Write the failing fast-path integration test**

Update `_run_graph` to accept distinct response and orchestration fakes, then add:

```python
async def test_companion_open_skips_orchestration_llm_but_keeps_graph_context():
    loader = _FakeWorkspaceLoader()
    response = OrchestrationLLM(stream_parts=["Riprendiamo §3.6."])
    orchestration = OrchestrationLLM()
    graph = build_graph(
        response,
        orchestration_llm=orchestration,
        checkpointer=InMemorySaver(),
        memory_service=_StubMemory(),
        workspace_loader=loader,
    )
    config = {
        "configurable": {
            "thread_id": "resume-fast-path",
            "project_id": THESIS_AGENT_PROJECT_ID,
        }
    }

    chunks = [
        chunk
        async for chunk in graph.astream(
            GraphState(
                messages=[Message(role="user", content="__companion_open__")]
            ),
            config,
            stream_mode="custom",
        )
    ]

    assert orchestration.generate_calls == 0
    assert loader.project_ids == [THESIS_AGENT_PROJECT_ID]
    assert response.last_stream_messages is not None
    assert any(chunk.get("type") == "token" for chunk in chunks)
```

- [x] **Step 2: Run the test and confirm RED**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_companion_chat_wiring.py::test_companion_open_skips_orchestration_llm_but_keeps_graph_context
```

Expected: `orchestration.generate_calls == 3`.

- [x] **Step 3: Centralize the marker contract**

Create `backend/app/graph/companion/protocol.py`:

```python
COMPANION_OPEN_MARKER = "__companion_open__"
COMPANION_OPEN_UTTERANCE = "Continuiamo da ieri"


def is_companion_open(text: str | None) -> bool:
    return bool(text and text.strip() == COMPANION_OPEN_MARKER)
```

Import these values in `workspace_context.py` and remove its duplicate constants. Replace
the direct equality checks with `is_companion_open(raw_utterance)`.

- [x] **Step 4: Short-circuit only model inference in the three nodes**

In Supervisor, before `request_json`:

```python
if is_companion_open(last_user_message(state.messages)):
    return {
        "plan": Plan(steps=["Resume the current thesis focus"]),
        "route": DEFAULT_ROUTE,
        "errors": errors,
    }
```

In Planner:

```python
if is_companion_open(last_user_message(state.messages)):
    return {
        "plan": state.plan or Plan(steps=["Resume the current thesis focus"]),
        "task": state.task,
        "errors": errors,
    }
```

In Router:

```python
if is_companion_open(user_message):
    return {"route": DEFAULT_ROUTE, "errors": errors}
```

These returns remain inside the node functions, so instrumentation and checkpoints still
record all three nodes.

- [x] **Step 5: Verify resume, ordinary, Grounded and Writer routes**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_companion_chat_wiring.py \
  tests/test_m5_graph_topology.py \
  tests/test_m6_writer_route.py \
  tests/test_router_node.py \
  tests/test_supervisor_node.py
```

Expected: all selected tests pass.

---

### Task 4: Stream non-academic responses immediately

**Files:**
- Modify: `backend/app/graph/inference_enforcement.py`
- Modify: `backend/app/graph/conversation.py`
- Modify: `backend/tests/test_inference_enforcement.py`
- Modify: `backend/tests/test_companion_chat_wiring.py`

**Interfaces:**
- Preserves:
  `generate_with_citation_enforcement(...) -> tuple[str, dict, bool]`
- Preserves SSE event types: `token`, `replace`, `sources`, `done`, `error`.

- [x] **Step 1: Write a failing chunk-level streaming test**

Add a fake that yields two chunks and assert they are emitted separately:

```python
class ChunkedLLM:
    async def astream(self, messages, *, model=None, params=None):
        yield type("Chunk", (), {"text": "Primo ", "metadata": {}})()
        yield type("Chunk", (), {"text": "secondo.", "metadata": {}})()


async def test_non_academic_response_streams_each_chunk_immediately():
    emitted: list[str] = []

    text, _, retried = await generate_with_citation_enforcement(
        ChunkedLLM(),
        [{"role": "user", "content": "Ciao"}],
        academic=False,
        emit=lambda event: emitted.append(event["text"]),
    )

    assert text == "Primo secondo."
    assert emitted == ["Primo ", "secondo."]
    assert not retried
```

Keep the existing academic tests asserting a single accepted emission after validation.

- [x] **Step 2: Run the test and confirm RED**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_inference_enforcement.py::test_non_academic_response_streams_each_chunk_immediately
```

Expected: current output is emitted as one combined string.

- [x] **Step 3: Add the direct non-academic stream branch**

At the beginning of `generate_with_citation_enforcement`:

```python
if not academic:
    parts: list[str] = []
    usage: dict = {}
    async for chunk in llm.astream(wire):
        if chunk.text:
            parts.append(chunk.text)
            if emit is not None:
                emit({"type": "token", "text": chunk.text})
        if chunk.metadata.get("usage"):
            usage = chunk.metadata["usage"]
    return "".join(parts), usage, False
```

Leave the existing buffered academic path below it.

- [x] **Step 4: Let thesis Companion chat use direct streaming when non-academic**

In `make_conversation_node`, pass the citation-enforced callback only for academic turns:

```python
generate = generate_cited if academic else None
text, usage, _retried = await generate_with_companion_enforcement(
    llm,
    wire,
    ctx=companion_ctx,
    emit=_emit,
    generate=generate,
)
```

This lets Companion enforcement stream the first pass and retain its existing `replace`
event when a repair is needed.

- [x] **Step 5: Verify streaming and enforcement behavior**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_inference_enforcement.py \
  tests/test_academic_production.py \
  tests/test_companion_chat_wiring.py
```

Expected: non-academic chunks are separate; academic retry and Companion replacement remain
green.

---

### Task 5: Full qualification, deployment and latency evidence

**Files:**
- Modify only if verification exposes a scoped defect.
- Evidence source: command output and `agent_steps` timing rows.

**Interfaces:**
- Consumes the completed model tiers, fast path and streaming behavior.
- Produces a verified local/public deployment with no temporary test records.

- [x] **Step 1: Run all focused backend graph suites**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q \
  tests/test_llm_factory.py \
  tests/test_litellm_client.py \
  tests/test_m5_graph_topology.py \
  tests/test_m6_writer_route.py \
  tests/test_m6_writing_integration.py \
  tests/test_inference_enforcement.py \
  tests/test_companion_chat_wiring.py \
  tests/test_conversations_api.py
```

Expected: all selected tests pass.

- [x] **Step 2: Run the repository gate**

Run:

```bash
make ci
```

Expected: exit code `0`; backend, frontend, Builder Engine, schema drift and classification
checks pass.

- [x] **Step 3: Rebuild and redeploy the backend**

Run:

```bash
docker compose build backend
docker compose up -d --no-deps --force-recreate backend
curl --retry 15 --retry-delay 2 --retry-all-errors --fail \
  http://127.0.0.1:8000/ready
```

Expected: readiness `200`, with DB and configuration true.

- [x] **Step 4: Verify the deployed model configuration**

Run:

```bash
docker compose exec -T backend python -c \
  "from app.core.config import settings; print(settings.vertex_location, settings.gemini_model, settings.gemini_orchestration_model)"
```

Expected:

```text
global gemini-3.6-flash gemini-3.5-flash-lite
```

- [x] **Step 5: Measure three resume and three ordinary turns**

Use fixed, unique diagnostic conversation UUIDs. For each streamed request record:

- HTTP header latency;
- first SSE `token` latency;
- final `done` latency;
- per-node rows from `agent_steps`.

Acceptance:

```text
resume median first token <= 5 seconds
ordinary median first token <= 8 seconds
resume orchestration nodes execute with near-zero duration
ordinary orchestration uses Flash-Lite
```

- [x] **Step 6: Exercise live Grounded and Writer branches**

Send one source-grounded question and one explicit drafting request. Confirm from
`agent_steps` and SSE:

```text
Grounded: retriever → conversation, with sources event
Writer:   retriever → writer
```

Record the set of task IDs before the smoke test so any tasks created by the diagnostic can
be identified precisely.

- [x] **Step 7: Remove only diagnostic records**

In one transaction, delete `agent_steps`, `agent_runs`, `messages`, conversations and any
task IDs created by the diagnostic UUIDs. Verify each diagnostic conversation count is zero.
Do not delete pre-existing thesis conversations or tasks.

- [x] **Step 8: Run deployed browser E2E**

Run:

```bash
cd tests/e2e
PLAYWRIGHT_SKIP_WEBSERVER=1 \
PLAYWRIGHT_BASE_URL=http://127.0.0.1:3000 \
E2E_API_BASE_URL=http://127.0.0.1:8000 \
npm test -- m7-product-flow.spec.ts
```

Expected: 9 tests pass.

- [x] **Step 9: Inspect recent logs**

Inspect backend/frontend logs since deployment. Accept no traceback, HTTP 5xx or failed
graph node. Report existing future-compatibility warnings separately rather than treating
them as latency regressions.
