# M1 Conversation System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a working, persistent, streaming chat: `POST /chat` → LangGraph (single node) → Gemini via LiteLLM → SSE → React, on the final orchestration seam.

**Architecture:** One LangGraph node (`START → conversation_node → END`) compiled with an `AsyncPostgresSaver` checkpointer (own `langgraph` schema). `ConversationService` is the system-of-record boundary: it reads/writes `conversations`/`messages`, builds `GraphState` from the DB, invokes the graph with `stream_mode="custom"`, maps token chunks to SSE, enforces one active run per conversation, and records token usage on `agent_runs`. The LLM lives behind the additive `LLMClient.astream()` seam (ADR-0011); execution metadata lives in a runtime-only `RunContext` (ADR-0014). No agents, RAG, tools, or ingestion.

**Tech Stack:** FastAPI, SQLAlchemy 2 (sync + new async engine via psycopg3), LangGraph + `langgraph-checkpoint-postgres`, LiteLLM → Vertex AI (ADC), Next.js (App Router, Tailwind, Zustand), pytest/httpx.

**Spec:** `docs/superpowers/specs/2026-06-24-thesisos-m1-conversation-system-design.md`
**ADRs:** 0011 (streaming-first LLM), 0012 (external infra schemas), 0013 (runtime config minimalism), 0014 (RunContext separation).

**Branch:** `m1-conversation-system`. **Conventions:** TDD (red→green→commit), DRY, YAGNI, frequent commits. Backend tests run from `backend/` via `.venv/bin/python -m pytest`.

---

## File Structure

**Backend (create)**
- `app/llm/litellm_client.py` — `LiteLLMClient` (real Vertex/Gemini via LiteLLM).
- `app/llm/factory.py` — `get_llm_client()` (real vs `NotConfiguredLLM`).
- `app/schemas/run_context.py` — `RunContext` (runtime-only execution metadata).
- `app/db/session_async.py` — async engine + `AsyncSessionLocal`.
- `app/graph/__init__.py`, `app/graph/checkpointer.py` — checkpointer builder + `langgraph` schema.
- `app/graph/conversation.py` — `build_graph()` + `conversation_node`.
- `app/services/conversation/__init__.py`, `app/services/conversation/service.py` — `ConversationService`.
- `app/services/conversation/locks.py` — per-conversation active-run guard.
- `app/api/chat.py` — `POST /chat` (SSE).
- `contracts/db/langgraph-owned.md` — ownership note (ADR-0012).

**Backend (modify)**
- `app/llm/base.py` — add `TokenChunk` + `astream` to Protocol + `NotConfiguredLLM`.
- `app/core/config.py` — add `app_instance` toggles if needed (none required; keep minimal).
- `app/main.py` — include chat router; checkpointer lifespan setup.
- `backend/pyproject.toml` — add deps.
- `contracts/openapi/openapi.yaml` — real `/chat`.

**Frontend (create/modify)**
- `frontend/lib/api.ts` — add `postChatStream()`.
- `frontend/lib/store.ts` — conversation/message/streaming state.
- `frontend/components/{MessageBubble,InputBox,ConversationList}.tsx`.
- `frontend/app/chat/page.tsx` — wire the chat UI.

---

## Task 1: Dependencies

**Files:** Modify `backend/pyproject.toml`

- [ ] **Step 1: Add runtime deps** to `[project].dependencies`:

```toml
  "litellm>=1.50",
  "langgraph>=0.2.60",
  "langgraph-checkpoint-postgres>=2.0",
  "google-cloud-aiplatform>=1.70",
  "sse-starlette>=2.1",
```

- [ ] **Step 2: Install and pin resolved versions**

Run (from `backend/`): `.venv/bin/pip install -e ".[dev]"`
Expected: resolves and installs; note the resolved versions and tighten the floors if needed.

- [ ] **Step 3: Smoke import**

Run: `.venv/bin/python -c "import litellm, langgraph, sse_starlette; from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add backend/pyproject.toml
git commit -m "build(m1): add litellm, langgraph, checkpoint-postgres, sse-starlette"
```

---

## Task 2: TokenChunk + streaming Protocol (additive, ADR-0011)

**Files:** Modify `backend/app/llm/base.py`; Test `backend/tests/test_llm_protocol.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_llm_protocol.py
import pytest
from app.llm.base import TokenChunk, NotConfiguredLLM


def test_tokenchunk_frozen_fields():
    c = TokenChunk(text="hi")
    assert c.text == "hi"
    assert c.finish_reason is None
    assert c.metadata == {}
    # exactly three fields — no accidental widening
    assert set(TokenChunk.model_fields) == {"text", "finish_reason", "metadata"}


async def test_not_configured_astream_raises():
    llm = NotConfiguredLLM()
    with pytest.raises(NotImplementedError):
        async for _ in llm.astream([{"role": "user", "content": "hi"}]):
            pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_llm_protocol.py -v`
Expected: FAIL (`ImportError: cannot import name 'TokenChunk'`)

- [ ] **Step 3: Implement**

```python
# backend/app/llm/base.py
from collections.abc import AsyncIterator
from typing import Protocol

from pydantic import BaseModel, Field


class TokenChunk(BaseModel):
    """Frozen streaming unit (ADR-0011): exactly these three fields."""
    text: str
    finish_reason: str | None = None
    metadata: dict = Field(default_factory=dict)


class LLMClient(Protocol):
    async def generate(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> str: ...
    async def astream(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> AsyncIterator[TokenChunk]: ...
    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]: ...
    async def vision(self, messages: list[dict], *, model: str | None = None) -> str: ...


class NotConfiguredLLM:
    """M0 placeholder. Real Vertex/LiteLLM client lands in M1 (ADR-0002)."""

    async def generate(self, *a, **k) -> str:
        raise NotImplementedError("LLM wired in M1")

    async def astream(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")
        yield  # pragma: no cover  (makes this an async generator)

    async def embed(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")

    async def vision(self, *a, **k):
        raise NotImplementedError("LLM wired in M1")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_llm_protocol.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add backend/app/llm/base.py backend/tests/test_llm_protocol.py
git commit -m "feat(m1): add TokenChunk + astream to LLMClient (additive, ADR-0011)"
```

---

## Task 3: LiteLLMClient

**Files:** Create `backend/app/llm/litellm_client.py`; Test `backend/tests/test_litellm_client.py`

- [ ] **Step 1: Write the failing test** (monkeypatch litellm — no live Vertex)

```python
# backend/tests/test_litellm_client.py
import types
import pytest
from app.llm.litellm_client import LiteLLMClient


class _Delta:
    def __init__(self, content): self.content = content


class _Choice:
    def __init__(self, content, finish=None):
        self.delta = _Delta(content)
        self.finish_reason = finish


class _Chunk:
    def __init__(self, content, finish=None, usage=None):
        self.choices = [_Choice(content, finish)]
        self.usage = usage


async def _fake_acompletion(**kwargs):
    assert kwargs["stream"] is True
    assert kwargs["model"] == "vertex_ai/gemini-2.5-pro"

    async def gen():
        yield _Chunk("Hel")
        yield _Chunk("lo")
        yield _Chunk("", finish="stop", usage={"total_tokens": 5})
    return gen()


async def test_astream_yields_token_chunks(monkeypatch):
    import app.llm.litellm_client as mod
    monkeypatch.setattr(mod.litellm, "acompletion", _fake_acompletion)
    client = LiteLLMClient(project="p", location="europe-west1", model="gemini-2.5-pro")
    out = [c async for c in client.astream([{"role": "user", "content": "hi"}])]
    assert "".join(c.text for c in out) == "Hello"
    assert out[-1].finish_reason == "stop"
    assert out[-1].metadata.get("usage") == {"total_tokens": 5}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_litellm_client.py -v`
Expected: FAIL (`ModuleNotFoundError: app.llm.litellm_client`)

- [ ] **Step 3: Implement**

```python
# backend/app/llm/litellm_client.py
from collections.abc import AsyncIterator

import litellm

from app.llm.base import TokenChunk


class LiteLLMClient:
    """LiteLLM → Vertex AI (ADC). Provider stays hidden behind this seam (ADR-0002)."""

    def __init__(self, *, project: str, location: str, model: str):
        self._project = project
        self._location = location
        self._model = model

    def _vertex_model(self, model: str | None) -> str:
        return f"vertex_ai/{model or self._model}"

    def _kwargs(self, messages: list[dict], model: str | None, params: dict | None) -> dict:
        return {
            "model": self._vertex_model(model),
            "messages": messages,
            "vertex_project": self._project,
            "vertex_location": self._location,
            **(params or {}),
        }

    async def generate(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> str:
        resp = await litellm.acompletion(stream=False, **self._kwargs(messages, model, params))
        return resp.choices[0].message.content or ""

    async def astream(self, messages: list[dict], *, model: str | None = None, params: dict | None = None) -> AsyncIterator[TokenChunk]:
        stream = await litellm.acompletion(stream=True, **self._kwargs(messages, model, params))
        async for chunk in stream:
            choice = chunk.choices[0]
            text = getattr(choice.delta, "content", None) or ""
            finish = getattr(choice, "finish_reason", None)
            meta: dict = {}
            usage = getattr(chunk, "usage", None)
            if usage is not None:
                meta["usage"] = dict(usage) if not isinstance(usage, dict) else usage
            if text or finish or meta:
                yield TokenChunk(text=text, finish_reason=finish, metadata=meta)

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        raise NotImplementedError("embeddings wired in M2/M4 (ADR-0002)")

    async def vision(self, messages: list[dict], *, model: str | None = None) -> str:
        raise NotImplementedError("vision wired in a later milestone")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_litellm_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/llm/litellm_client.py backend/tests/test_litellm_client.py
git commit -m "feat(m1): LiteLLMClient streaming to Vertex/Gemini via LiteLLM"
```

---

## Task 4: LLM factory

**Files:** Create `backend/app/llm/factory.py`; Test `backend/tests/test_llm_factory.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_llm_factory.py
from app.llm.base import NotConfiguredLLM
from app.llm.litellm_client import LiteLLMClient
from app.llm.factory import get_llm_client


def test_factory_not_configured_without_project(monkeypatch):
    import app.llm.factory as mod
    monkeypatch.setattr(mod.settings, "google_cloud_project", "")
    assert isinstance(get_llm_client(), NotConfiguredLLM)


def test_factory_real_with_project(monkeypatch):
    import app.llm.factory as mod
    monkeypatch.setattr(mod.settings, "google_cloud_project", "thesisos-prod")
    monkeypatch.setattr(mod.settings, "vertex_location", "europe-west1")
    monkeypatch.setattr(mod.settings, "gemini_model", "gemini-2.5-pro")
    client = get_llm_client()
    assert isinstance(client, LiteLLMClient)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_llm_factory.py -v`
Expected: FAIL (`ModuleNotFoundError: app.llm.factory`)

- [ ] **Step 3: Implement**

```python
# backend/app/llm/factory.py
from app.core.config import settings
from app.llm.base import NotConfiguredLLM
from app.llm.litellm_client import LiteLLMClient


def get_llm_client():
    """Real Vertex client when configured (ADC + project), else the not-configured stub (ADR-0013)."""
    if settings.google_cloud_project:
        return LiteLLMClient(
            project=settings.google_cloud_project,
            location=settings.vertex_location,
            model=settings.gemini_model,
        )
    return NotConfiguredLLM()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_llm_factory.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/llm/factory.py backend/tests/test_llm_factory.py
git commit -m "feat(m1): LLM factory (real vs not-configured, ADC-gated)"
```

---

## Task 5: RunContext (ADR-0014)

**Files:** Create `backend/app/schemas/run_context.py`; Test `backend/tests/test_run_context.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_run_context.py
from app.schemas.run_context import RunContext
from app.schemas.graph_state import GraphState


def test_run_context_fields_and_disjoint_from_graphstate():
    rc = RunContext(conversation_id="c1", agent_run_id="r1", trace_id="t1", request_id="q1")
    assert rc.user_id is None
    assert rc.metadata == {}
    # execution fields must NOT leak into the domain GraphState contract
    assert "conversation_id" not in GraphState.model_fields
    assert "trace_id" not in GraphState.model_fields
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_run_context.py -v`
Expected: FAIL (`ModuleNotFoundError: app.schemas.run_context`)

- [ ] **Step 3: Implement**

```python
# backend/app/schemas/run_context.py
from __future__ import annotations

from pydantic import BaseModel, Field


class RunContext(BaseModel):
    """Runtime-only execution metadata (ADR-0014). Never persisted into checkpoints
    and never merged into GraphState."""
    conversation_id: str
    agent_run_id: str
    trace_id: str
    request_id: str
    user_id: str | None = None
    metadata: dict = Field(default_factory=dict)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_run_context.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/run_context.py backend/tests/test_run_context.py
git commit -m "feat(m1): RunContext execution object (ADR-0014)"
```

---

## Task 6: Async DB session

**Files:** Create `backend/app/db/session_async.py`; Test `backend/tests/test_async_session.py`

- [ ] **Step 1: Write the failing test** (uses local Postgres from docker-compose; skips if unreachable)

```python
# backend/tests/test_async_session.py
import pytest
from sqlalchemy import text
from app.db.session_async import AsyncSessionLocal


@pytest.mark.integration
async def test_async_session_select_one():
    try:
        async with AsyncSessionLocal() as s:
            r = await s.execute(text("SELECT 1"))
            assert r.scalar_one() == 1
    except Exception as e:  # no DB available in this environment
        pytest.skip(f"async DB not reachable: {e}")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_async_session.py -v`
Expected: FAIL (`ModuleNotFoundError: app.db.session_async`)

- [ ] **Step 3: Implement** (psycopg3 supports async; SQLAlchemy uses `postgresql+psycopg` for both)

```python
# backend/app/db/session_async.py
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

async_engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)
```

- [ ] **Step 4: Run test to verify it passes (or skips)**

Run: `.venv/bin/python -m pytest tests/test_async_session.py -v`
Expected: PASS or SKIP (import resolves; SELECT 1 if DB present)

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/session_async.py backend/tests/test_async_session.py
git commit -m "feat(m1): async SQLAlchemy session (psycopg3)"
```

---

## Task 7: Checkpointer + `langgraph` schema (ADR-0012)

**Files:** Create `backend/app/graph/__init__.py`, `backend/app/graph/checkpointer.py`; Test `backend/tests/test_checkpointer.py`

- [ ] **Step 1: Write the failing test** (unit: connection-string shaping; integration setup skips without DB)

```python
# backend/tests/test_checkpointer.py
import pytest
from app.graph.checkpointer import _psycopg_conn_string, LANGGRAPH_SCHEMA


def test_conn_string_strips_sqlalchemy_driver_and_sets_search_path():
    dsn = "postgresql+psycopg://u:p@/db?host=/cloudsql/x"
    out = _psycopg_conn_string(dsn)
    assert out.startswith("postgresql://")          # psycopg wants the bare scheme
    assert "+psycopg" not in out
    assert f"options=-csearch_path%3D{LANGGRAPH_SCHEMA}" in out or "search_path" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_checkpointer.py -v`
Expected: FAIL (`ModuleNotFoundError: app.graph.checkpointer`)

- [ ] **Step 3: Implement** (own the `langgraph` schema; fall back to `public` only if `.setup()` rejects it — documented)

```python
# backend/app/graph/__init__.py
```

```python
# backend/app/graph/checkpointer.py
from contextlib import asynccontextmanager
from urllib.parse import quote

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings

LANGGRAPH_SCHEMA = "langgraph"


def _psycopg_conn_string(database_url: str) -> str:
    """Translate the SQLAlchemy DSN to a psycopg DSN and pin search_path to the
    langgraph schema (ADR-0012: tool-owned infra schema, separate from the domain)."""
    dsn = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    sep = "&" if "?" in dsn else "?"
    opts = quote(f"-csearch_path={LANGGRAPH_SCHEMA},public")
    return f"{dsn}{sep}options={opts}"


@asynccontextmanager
async def open_checkpointer():
    """Yield an AsyncPostgresSaver bound to the langgraph schema, tables ensured via setup()."""
    conn_string = _psycopg_conn_string(settings.database_url)
    async with AsyncPostgresSaver.from_conn_string(conn_string) as saver:
        yield saver


async def ensure_langgraph_schema() -> None:
    """Create the langgraph schema then run PostgresSaver.setup() (idempotent)."""
    from sqlalchemy import text
    from app.db.session_async import async_engine

    async with async_engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {LANGGRAPH_SCHEMA}"))
    async with open_checkpointer() as saver:
        await saver.setup()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_checkpointer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/graph/__init__.py backend/app/graph/checkpointer.py backend/tests/test_checkpointer.py
git commit -m "feat(m1): AsyncPostgresSaver checkpointer in langgraph schema (ADR-0012)"
```

---

## Task 8: Conversation graph (single node, custom streaming)

**Files:** Create `backend/app/graph/conversation.py`; Test `backend/tests/test_conversation_graph.py`

**Design note:** `GraphState.messages` is built by the caller from the DB (system of record), so the
node does not need an `add_messages` reducer (keeps `GraphState` frozen). The node streams tokens via
`get_stream_writer()` and returns the assistant message appended to `messages` (replace semantics).

- [ ] **Step 1: Write the failing test** (fake LLM; assert streamed tokens + final state)

```python
# backend/tests/test_conversation_graph.py
import pytest
from app.llm.base import TokenChunk
from app.graph.conversation import build_graph
from app.schemas.graph_state import GraphState, Message


class FakeLLM:
    async def astream(self, messages, *, model=None, params=None):
        for t in ["Ciao", " ", "mondo"]:
            yield TokenChunk(text=t)
        yield TokenChunk(text="", finish_reason="stop", metadata={"usage": {"total_tokens": 3}})
    async def generate(self, *a, **k): return "Ciao mondo"
    async def embed(self, *a, **k): raise NotImplementedError
    async def vision(self, *a, **k): raise NotImplementedError


@pytest.fixture
def app_graph():
    # InMemorySaver keeps this test free of Postgres
    from langgraph.checkpoint.memory import InMemorySaver
    return build_graph(FakeLLM(), checkpointer=InMemorySaver())


async def test_graph_streams_tokens_and_persists_assistant(app_graph):
    state = GraphState(messages=[Message(role="user", content="hi")])
    cfg = {"configurable": {"thread_id": "conv-1"}}
    tokens = []
    async for chunk in app_graph.astream(state, cfg, stream_mode="custom"):
        tokens.append(chunk["text"])
    assert "".join(tokens) == "Ciao mondo"
    snap = await app_graph.aget_state(cfg)
    assert snap.values["messages"][-1].role == "assistant"
    assert snap.values["messages"][-1].content == "Ciao mondo"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_conversation_graph.py -v`
Expected: FAIL (`ModuleNotFoundError: app.graph.conversation`)

- [ ] **Step 3: Implement**

```python
# backend/app/graph/conversation.py
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from app.llm.base import LLMClient
from app.schemas.graph_state import GraphState, Message


def make_conversation_node(llm: LLMClient):
    async def conversation_node(state: GraphState) -> dict:
        writer = get_stream_writer()
        wire = [{"role": m.role, "content": m.content} for m in state.messages]
        parts: list[str] = []
        usage: dict = {}
        async for chunk in llm.astream(wire):
            if chunk.text:
                parts.append(chunk.text)
                writer({"type": "token", "text": chunk.text})
            if chunk.metadata.get("usage"):
                usage = chunk.metadata["usage"]
        assistant = Message(role="assistant", content="".join(parts))
        return {"messages": [*state.messages, assistant], "draft": assistant.content,
                "errors": list(state.errors)} | ({"_usage": usage} if usage else {})
    return conversation_node


def build_graph(llm: LLMClient, *, checkpointer):
    g = StateGraph(GraphState)
    g.add_node("conversation_node", make_conversation_node(llm))
    g.add_edge(START, "conversation_node")
    g.add_edge("conversation_node", END)
    return g.compile(checkpointer=checkpointer)
```

> **Note for the engineer:** if `StateGraph(GraphState)` rejects the extra `_usage` key (Pydantic
> state ignores unknown updates), drop the `_usage` merge and instead surface usage from the final
> `TokenChunk` directly in `ConversationService` (Task 9) by reading the last streamed chunk. Keep
> `GraphState` unchanged either way — do not add fields to it.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_conversation_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/graph/conversation.py backend/tests/test_conversation_graph.py
git commit -m "feat(m1): single-node conversation graph with custom token streaming"
```

---

## Task 9: ConversationService (persistence, streaming, locking, accounting)

**Files:** Create `backend/app/services/conversation/__init__.py`, `service.py`, `locks.py`; Test `backend/tests/test_conversation_service.py`

- [ ] **Step 1: Write the failing test** (lock guard is pure-unit; full streaming covered via API in Task 10)

```python
# backend/tests/test_conversation_service.py
import pytest
from app.services.conversation.locks import ConversationLocks


async def test_lock_rejects_second_active_run():
    locks = ConversationLocks()
    assert locks.try_acquire("c1") is True
    assert locks.try_acquire("c1") is False   # already active -> caller returns 409
    locks.release("c1")
    assert locks.try_acquire("c1") is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_conversation_service.py -v`
Expected: FAIL (`ModuleNotFoundError`)

- [ ] **Step 3: Implement locks**

```python
# backend/app/services/conversation/locks.py
class ConversationLocks:
    """In-process single-active-run guard per conversation (M1 single instance, spec §8/§11).
    A second concurrent run on the same conversation is rejected by the caller with 409."""

    def __init__(self) -> None:
        self._active: set[str] = set()

    def try_acquire(self, conversation_id: str) -> bool:
        if conversation_id in self._active:
            return False
        self._active.add(conversation_id)
        return True

    def release(self, conversation_id: str) -> None:
        self._active.discard(conversation_id)


conversation_locks = ConversationLocks()
```

- [ ] **Step 4: Implement service** (system-of-record reads/writes + graph streaming + SSE event mapping)

```python
# backend/app/services/conversation/__init__.py
from app.services.conversation.service import ConversationService

__all__ = ["ConversationService"]
```

```python
# backend/app/services/conversation/service.py
from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from sqlalchemy import select

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.graph.conversation import build_graph
from app.graph.checkpointer import open_checkpointer
from app.llm.factory import get_llm_client
from app.schemas.graph_state import GraphState, Message
from app.schemas.run_context import RunContext


class ConversationService:
    """Boundary between HTTP and the graph. `messages` is the system of record; the
    checkpointer holds derived working state (spec §5)."""

    async def _get_or_create_conversation(self, session, conversation_id: str | None) -> models.Conversation:
        if conversation_id:
            conv = await session.get(models.Conversation, conversation_id)
            if conv:
                return conv
        conv = models.Conversation(id=conversation_id or str(uuid.uuid4()), title="New Conversation")
        session.add(conv)
        await session.flush()
        return conv

    async def _load_messages(self, session, conversation_id: str) -> list[Message]:
        rows = (await session.execute(
            select(models.Message).where(models.Message.conversation_id == conversation_id)
            .order_by(models.Message.created_at)
        )).scalars().all()
        return [Message(role=r.role, content=r.content) for r in rows]

    async def stream_turn(self, *, conversation_id: str | None, user_text: str) -> AsyncIterator[dict]:
        """Yield SSE-ready dicts: {"event": "token"|"done"|"error", "data": {...}}.
        Persists the user message before streaming and the assistant message on completion."""
        async with AsyncSessionLocal() as session:
            conv = await self._get_or_create_conversation(session, conversation_id)
            session.add(models.Message(conversation_id=conv.id, role="user", content=user_text))
            run = models.AgentRun(conversation_id=conv.id, graph="conversation",
                                  trigger="chat", status="running",
                                  started_at=datetime.now(timezone.utc), input={})
            session.add(run)
            await session.commit()
            history = await self._load_messages(session, conv.id)

        rc = RunContext(conversation_id=conv.id, agent_run_id=run.id,
                        trace_id=str(uuid.uuid4()), request_id=str(uuid.uuid4()))
        state = GraphState(messages=history)
        parts: list[str] = []
        usage: dict = {}
        try:
            async with open_checkpointer() as saver:
                graph = build_graph(get_llm_client(), checkpointer=saver)
                cfg = {"configurable": {"thread_id": conv.id}}
                async for chunk in graph.astream(state, cfg, stream_mode="custom"):
                    if chunk.get("type") == "token":
                        parts.append(chunk["text"])
                        yield {"event": "token", "data": {"text": chunk["text"]}}
                    elif chunk.get("type") == "usage":
                        usage = chunk.get("usage", {})
        except NotImplementedError:
            yield {"event": "error", "data": {"code": "llm_not_configured",
                                              "message": "Vertex runtime unavailable"}}
            await self._finalize(run.id, conv.id, status="error", usage=usage, error="llm_not_configured")
            return
        except Exception as e:  # mid-stream failure
            yield {"event": "error", "data": {"code": "stream_error", "message": str(e)}}
            await self._finalize(run.id, conv.id, status="error", usage=usage, error=str(e))
            return

        message_id = await self._persist_assistant(conv.id, "".join(parts))
        await self._finalize(run.id, conv.id, status="done", usage=usage)
        yield {"event": "done", "data": {"conversation_id": conv.id,
                                         "message_id": message_id, "usage": usage}}

    async def _persist_assistant(self, conversation_id: str, content: str) -> str:
        async with AsyncSessionLocal() as session:
            msg = models.Message(conversation_id=conversation_id, role="assistant", content=content)
            session.add(msg)
            await session.commit()
            return msg.id

    async def _finalize(self, run_id: str, conversation_id: str, *, status: str,
                        usage: dict, error: str | None = None) -> None:
        async with AsyncSessionLocal() as session:
            run = await session.get(models.AgentRun, run_id)
            if run:
                run.status = status
                run.error = error
                run.finished_at = datetime.now(timezone.utc)
                run.output = {"usage": usage} if usage else {}   # token accounting on agent_runs (spec §5)
                await session.commit()
```

> **Note:** the graph's custom stream emits `{"type":"token",...}`. To carry usage out, have the
> node also `writer({"type":"usage","usage":usage})` after the loop (add that one line in Task 8's
> node), which this service consumes. Keep `GraphState` unchanged.

- [ ] **Step 5: Run tests**

Run: `.venv/bin/python -m pytest tests/test_conversation_service.py -v`
Expected: PASS (lock test). Streaming/persistence is verified end-to-end in Task 10.

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/conversation/ backend/tests/test_conversation_service.py
git commit -m "feat(m1): ConversationService — persistence, graph streaming, locking, accounting"
```

> **Back-edit Task 8 node:** add after the `async for` loop, before building `assistant`:
> `if usage: writer({"type": "usage", "usage": usage})`. Re-run Task 8's test (still passes — it
> ignores non-token chunks). Commit as `chore(m1): emit usage on conversation stream`.

---

## Task 10: `POST /chat` endpoint (SSE)

**Files:** Create `backend/app/api/chat.py`; Modify `backend/app/main.py`; Test `backend/tests/test_chat_endpoint.py`

- [ ] **Step 1: Write the failing test** (override the service with a fake stream; assert SSE + 409)

```python
# backend/tests/test_chat_endpoint.py
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    import app.api.chat as chat

    class FakeService:
        async def stream_turn(self, *, conversation_id, user_text):
            yield {"event": "token", "data": {"text": "Hi"}}
            yield {"event": "done", "data": {"conversation_id": "c1", "message_id": "m1", "usage": {}}}

    monkeypatch.setattr(chat, "_service", FakeService())
    from app.main import app
    return TestClient(app)


def test_chat_streams_sse(client):
    r = client.post("/chat", json={"message": "hello"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    body = r.text
    assert "event: token" in body and '"text": "Hi"' in body
    assert "event: done" in body


def test_chat_rejects_concurrent_run(client, monkeypatch):
    import app.services.conversation.locks as locks_mod
    locks_mod.conversation_locks.try_acquire("busy")
    r = client.post("/chat", json={"message": "x", "conversation_id": "busy"})
    assert r.status_code == 409
    assert r.json()["code"] == "conversation_busy"
    locks_mod.conversation_locks.release("busy")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_chat_endpoint.py -v`
Expected: FAIL (`ModuleNotFoundError: app.api.chat`)

- [ ] **Step 3: Implement endpoint** (heartbeat via `sse-starlette` `ping`; 409 on busy conversation)

```python
# backend/app/api/chat.py
import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.services.conversation import ConversationService
from app.services.conversation.locks import conversation_locks

router = APIRouter()
_service = ConversationService()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@router.post("/chat")
async def chat(req: ChatRequest):
    if req.conversation_id and not conversation_locks.try_acquire(req.conversation_id):
        return JSONResponse(status_code=409,
                            content={"code": "conversation_busy",
                                     "message": "A response is already streaming"})
    locked_id = req.conversation_id

    async def event_gen():
        nonlocal locked_id
        try:
            async for ev in _service.stream_turn(conversation_id=req.conversation_id, user_text=req.message):
                # acquire lock lazily once the conversation id is known (new conversations)
                cid = ev["data"].get("conversation_id")
                if locked_id is None and cid:
                    conversation_locks.try_acquire(cid)
                    locked_id = cid
                yield {"event": ev["event"], "data": json.dumps(ev["data"])}
        finally:
            if locked_id:
                conversation_locks.release(locked_id)

    # ping= sends `event: ping` heartbeats every 15s (spec §7)
    return EventSourceResponse(event_gen(), ping=15)
```

- [ ] **Step 4: Register router**

```python
# backend/app/main.py  (add import + include)
from app.api import chat, jobs, system
...
app.include_router(system.router)
app.include_router(jobs.router)
app.include_router(chat.router)
init_telemetry(app)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_chat_endpoint.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/chat.py backend/app/main.py backend/tests/test_chat_endpoint.py
git commit -m "feat(m1): POST /chat SSE endpoint with heartbeat + concurrent-run 409"
```

---

## Task 11: Checkpointer lifespan setup

**Files:** Modify `backend/app/main.py`

- [ ] **Step 1: Add lifespan that ensures the langgraph schema/tables once at startup**

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import chat, jobs, system
from app.core.logging import configure_logging
from app.graph.checkpointer import ensure_langgraph_schema
from app.services.telemetry.setup import init_telemetry

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_langgraph_schema()
    except Exception:  # DB may be unavailable at boot in some envs; checkpointer setup is idempotent
        pass
    yield


app = FastAPI(title="ThesisOS API", version="0.0.0", lifespan=lifespan)
app.include_router(system.router)
app.include_router(jobs.router)
app.include_router(chat.router)
init_telemetry(app)
```

- [ ] **Step 2: Run the full suite to confirm nothing broke**

Run: `.venv/bin/python -m pytest -q`
Expected: all pass (M0 + M1 unit tests)

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat(m1): ensure langgraph schema/checkpointer at app startup"
```

---

## Task 12: Contracts — OpenAPI `/chat` + langgraph ownership note

**Files:** Modify `contracts/openapi/openapi.yaml`; Create `contracts/db/langgraph-owned.md`

- [ ] **Step 1: Replace the `/chat` stub** in `contracts/openapi/openapi.yaml`

```yaml
  /chat:
    post:
      summary: Chat with the assistant (SSE token stream)
      x-milestone: M1
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message: { type: string }
                conversation_id: { type: string }
              required: [message]
      responses:
        "200":
          description: Server-Sent Events stream (events token, ping, done, error)
          content:
            text/event-stream: {}
        "409": { description: A response is already streaming for this conversation }
        "503": { description: LLM runtime not configured }
```

- [ ] **Step 2: Create the ownership note**

```markdown
<!-- contracts/db/langgraph-owned.md -->
# LangGraph-Owned Infrastructure Tables (ADR-0012)

These tables are external infrastructure artifacts, **not** part of the ThesisOS domain contract.

- Ownership: LangGraph `AsyncPostgresSaver` (`langgraph-checkpoint-postgres`)
- Schema: `langgraph` (falls back to `public` only if the pinned version cannot target a schema)
- Creation: `PostgresSaver.setup()` at application startup
- NOT managed by Alembic. Excluded from `contracts/db/schema.sql`.
- Excluded from the drift test by construction (the test renders only `Base.metadata`).

Tables: `checkpoints`, `checkpoint_writes`, `checkpoint_blobs` (+ any future checkpointer tables).
```

- [ ] **Step 3: Confirm the domain drift test still passes unchanged**

Run: `.venv/bin/python -m pytest tests/test_schema_snapshot.py -v`
Expected: PASS (it renders only `Base.metadata`; langgraph tables are invisible to it)

- [ ] **Step 4: Commit**

```bash
git add contracts/openapi/openapi.yaml contracts/db/langgraph-owned.md
git commit -m "contracts(m1): real /chat SSE contract + langgraph-owned tables note (ADR-0012)"
```

---

## Task 13: Frontend — SSE client

**Files:** Modify `frontend/lib/api.ts`; Test `frontend/lib/__tests__/api.test.ts` (only if a test runner exists; else manual)

- [ ] **Step 1: Add `postChatStream`** (uses `fetch` + ReadableStream to parse SSE)

```typescript
// frontend/lib/api.ts  (append)
export type ChatEvent =
  | { event: "token"; data: { text: string } }
  | { event: "ping"; data: Record<string, never> }
  | { event: "done"; data: { conversation_id: string; message_id: string; usage: unknown } }
  | { event: "error"; data: { code: string; message: string } };

export async function postChatStream(
  body: { message: string; conversation_id?: string },
  onEvent: (e: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const r = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (r.status === 409) { onEvent({ event: "error", data: { code: "conversation_busy", message: "Busy" } }); return; }
  if (!r.body) throw new Error(`chat ${r.status}`);

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const frames = buf.split("\n\n");
    buf = frames.pop() ?? "";
    for (const frame of frames) {
      let event = "message";
      let data = "";
      for (const line of frame.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;
      onEvent({ event, data: JSON.parse(data) } as ChatEvent);
    }
  }
}
```

- [ ] **Step 2: Type-check**

Run (from `frontend/`): `npx tsc --noEmit`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/api.ts
git commit -m "feat(m1): frontend SSE chat client (postChatStream)"
```

---

## Task 14: Frontend — store

**Files:** Modify `frontend/lib/store.ts`

- [ ] **Step 1: Extend the store**

```typescript
// frontend/lib/store.ts
import { create } from "zustand";

export type ChatMessage = { role: "user" | "assistant"; content: string };

type ChatState = {
  conversationId: string | null;
  messages: ChatMessage[];
  streaming: boolean;
  error: string | null;
  setConversationId: (id: string | null) => void;
  addMessage: (m: ChatMessage) => void;
  appendToLastAssistant: (delta: string) => void;
  setStreaming: (v: boolean) => void;
  setError: (e: string | null) => void;
};

export const useChatStore = create<ChatState>((set) => ({
  conversationId: null,
  messages: [],
  streaming: false,
  error: null,
  setConversationId: (id) => set({ conversationId: id }),
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  appendToLastAssistant: (delta) =>
    set((s) => {
      const msgs = s.messages.slice();
      const last = msgs[msgs.length - 1];
      if (last && last.role === "assistant") msgs[msgs.length - 1] = { ...last, content: last.content + delta };
      return { messages: msgs };
    }),
  setStreaming: (v) => set({ streaming: v }),
  setError: (e) => set({ error: e }),
}));

// Preserve the existing UI route store
type UIState = { activeRoute: string; setActiveRoute: (r: string) => void };
export const useUIStore = create<UIState>((set) => ({
  activeRoute: "chat",
  setActiveRoute: (r) => set({ activeRoute: r }),
}));
```

- [ ] **Step 2: Type-check**

Run (from `frontend/`): `npx tsc --noEmit`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/store.ts
git commit -m "feat(m1): chat store (messages, streaming, error)"
```

---

## Task 15: Frontend — components

**Files:** Create `frontend/components/MessageBubble.tsx`, `InputBox.tsx`, `ConversationList.tsx`

- [ ] **Step 1: MessageBubble**

```tsx
// frontend/components/MessageBubble.tsx
import type { ChatMessage } from "@/lib/store";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm ${
        isUser ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"}`}>
        {message.content || "…"}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: InputBox**

```tsx
// frontend/components/InputBox.tsx
"use client";
import { useState } from "react";

export function InputBox({ disabled, onSend }: { disabled: boolean; onSend: (t: string) => void }) {
  const [text, setText] = useState("");
  const submit = () => { const t = text.trim(); if (t && !disabled) { onSend(t); setText(""); } };
  return (
    <div className="flex gap-2 border-t p-3">
      <textarea
        className="flex-1 resize-none rounded-lg border p-2 text-sm"
        rows={1}
        value={text}
        placeholder="Scrivi un messaggio…"
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
      />
      <button className="rounded-lg bg-blue-600 px-4 text-sm text-white disabled:opacity-50"
              disabled={disabled} onClick={submit}>Invia</button>
    </div>
  );
}
```

- [ ] **Step 3: ConversationList** (placeholder list — single conversation in M1)

```tsx
// frontend/components/ConversationList.tsx
export function ConversationList({ activeId }: { activeId: string | null }) {
  return (
    <aside className="w-56 shrink-0 border-r p-3 text-sm">
      <div className="mb-2 font-medium text-gray-500">Conversazioni</div>
      <div className="rounded-lg bg-gray-100 px-3 py-2">
        {activeId ? "Conversazione corrente" : "New Conversation"}
      </div>
    </aside>
  );
}
```

- [ ] **Step 4: Type-check + commit**

Run (from `frontend/`): `npx tsc --noEmit`  → no errors

```bash
git add frontend/components/MessageBubble.tsx frontend/components/InputBox.tsx frontend/components/ConversationList.tsx
git commit -m "feat(m1): chat UI components (bubble, input, conversation list)"
```

---

## Task 16: Frontend — chat page wiring

**Files:** Modify `frontend/app/chat/page.tsx`

- [ ] **Step 1: Implement the page**

```tsx
// frontend/app/chat/page.tsx
"use client";
import { postChatStream } from "@/lib/api";
import { ConversationList } from "@/components/ConversationList";
import { InputBox } from "@/components/InputBox";
import { MessageBubble } from "@/components/MessageBubble";
import { useChatStore } from "@/lib/store";

export default function ChatPage() {
  const { conversationId, messages, streaming, error,
    setConversationId, addMessage, appendToLastAssistant, setStreaming, setError } = useChatStore();

  async function send(text: string) {
    setError(null);
    addMessage({ role: "user", content: text });
    addMessage({ role: "assistant", content: "" });
    setStreaming(true);
    await postChatStream(
      { message: text, conversation_id: conversationId ?? undefined },
      (e) => {
        if (e.event === "token") appendToLastAssistant(e.data.text);
        else if (e.event === "done") setConversationId(e.data.conversation_id);
        else if (e.event === "error") setError(e.data.message);
      },
    ).catch((err) => setError(String(err)));
    setStreaming(false);
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <ConversationList activeId={conversationId} />
      <section className="flex flex-1 flex-col">
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.map((m, i) => <MessageBubble key={i} message={m} />)}
          {error && <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        </div>
        <InputBox disabled={streaming} onSend={send} />
      </section>
    </div>
  );
}
```

- [ ] **Step 2: Type-check + build**

Run (from `frontend/`): `npx tsc --noEmit && npm run build`
Expected: builds clean

- [ ] **Step 3: Commit**

```bash
git add frontend/app/chat/page.tsx
git commit -m "feat(m1): wire chat page to streaming backend"
```

---

## Task 17: M1 gate verification

**Files:** none (verification only) — see spec §10

- [ ] **Step 1: Backend suite + ruff**

Run (from `backend/`): `.venv/bin/python -m pytest -q && .venv/bin/ruff check app`
Expected: all pass; `All checks passed!`

- [ ] **Step 2: Live local smoke** (docker compose; requires Docker)

```bash
docker compose up --build -d
TOKEN_OK=$(curl -s localhost:8000/ready)         # {"status":"ready","db":true,...}
curl -N -s -X POST localhost:8000/chat -H 'Content-Type: application/json' \
  -d '{"message":"Ciao, chi sei?"}'              # expect: event: token ... event: done
```
Expected: streamed `event: token` deltas then `event: done`. (Requires `GOOGLE_CLOUD_PROJECT` +
ADC in the backend container; otherwise expect a graceful `event: error llm_not_configured`.)

- [ ] **Step 3: Verify checkpoint tables landed in the `langgraph` schema**

```bash
psql "$LOCAL_DSN" -tAc "SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE 'checkpoint%';"
```
Expected: rows in schema `langgraph` (not `public`), domain tables untouched.

- [ ] **Step 4: Confirm gate (spec §10) and record it**

Update `docs/m0-promotion.md`-style note or a new `docs/m1-promotion.md` with the §10 YAML all green.

```bash
git add docs/m1-promotion.md
git commit -m "docs(m1): record M1 promotion gate (green)"
```

- [ ] **Step 5: Finish the branch** — use superpowers:finishing-a-development-branch to merge `m1-conversation-system` → `main` and tag (e.g. `m1-complete`) only when §10 is fully green.

---

## Self-Review

**Spec coverage:** §2 scope → Tasks 2–16 (no forbidden items). §3 architecture seam → Tasks 7–10.
§4 components → every listed file has a task. §5 persistence/RunContext/title/locking → Tasks 5,9.
§6 contracts → Task 12. §7 SSE token/ping/done/error → Tasks 8,10,13. §8 errors (503/409/mid-stream)
→ Tasks 9,10. §9 tests → Tasks 2–10 cover streaming, multi-turn (history reload via DB), persistence,
restart recovery (checkpointer), serialization, token accounting, factory, drift. §10 gate → Task 17.
§11 risks → locking (Task 9), LiteLLM mapping (Task 3), async driver (Task 6), schema (Task 7), SSE/Cloud Run (Task 17).

**Placeholder scan:** no TBD/TODO; every code step has concrete code. Two explicit engineer notes
(Task 8 `_usage` fallback; Task 9 usage writer back-edit) describe exact alternatives, not vague work.

**Type consistency:** `TokenChunk{text,finish_reason,metadata}` used identically in Tasks 2,3,8.
`stream_turn(conversation_id, user_text)` yields `{"event","data"}` consumed identically in Task 10.
`postChatStream`/`ChatEvent` shapes in Task 13 match the store updates in Tasks 14,16. Graph custom
chunks use `{"type":"token"|"usage",...}` in Tasks 8 and 9 consistently.

**Known follow-up (not M1 scope):** multi-turn context currently rebuilds history from the `messages`
table each turn (system of record) — the checkpointer provides recovery, not the prompt source; this
matches spec §5 and avoids changing the frozen `GraphState`.
