"""Writer capability + node tests (M6.1, ADR-0031).

Covers: capability → DraftResult, adapter mapping to writer.json state only,
empty_context / generation_failed, citation discipline, swappability, isolation.
"""

from __future__ import annotations

import ast
from pathlib import Path

from app.graph import writer as writer_mod
from app.graph.orchestration import writer_prompt as writer_prompt_mod
from app.graph.writer import (
    LLMWriter,
    WriterGenerationError,
    make_writer_node,
)
from app.llm.base import TokenChunk
from app.schemas import draft as draft_mod
from app.schemas.draft import DraftResult, WriterBrief
from app.schemas.graph_state import CitationRef, GraphState, Message, Plan, RetrievedChunk


class FakeStreamLLM:
    """Minimal streaming LLM seam: astream yields the given tokens."""

    def __init__(self, tokens, *, usage=None, fail=False):
        self._tokens = tokens
        self._usage = usage
        self._fail = fail

    async def astream(self, messages, *, model=None, params=None):
        if self._fail:
            raise RuntimeError("llm down")
        for tok in self._tokens:
            yield TokenChunk(text=tok)
        if self._usage:
            yield TokenChunk(text="", metadata={"usage": self._usage})

    async def generate(self, *a, **k):
        return ""

    async def embed(self, *a, **k):
        return []

    async def vision(self, *a, **k):
        return ""


class FakeWriter:
    """An alternate WriterCapability implementation (swappability)."""

    def __init__(self, result: DraftResult):
        self._result = result
        self.calls = 0

    async def write_grounded(self, brief, *, emit=None):
        self.calls += 1
        return self._result


class FailingWriter:
    async def write_grounded(self, brief, *, emit=None):
        raise WriterGenerationError("boom")


def _chunk(chunk_id="c1", document_id="d1", page_from=3):
    return RetrievedChunk(
        chunk_id=chunk_id,
        score=0.9,
        content="grounding text",
        document_id=document_id,
        document_title="Doc",
        page_from=page_from,
    )


def _state(*, context=None, plan_steps=("Write the intro",)):
    return GraphState(
        messages=[Message(role="user", content="Draft the introduction chapter")],
        plan=Plan(steps=list(plan_steps)),
        retrieved_context=list(context or []),
    )


# --- capability -------------------------------------------------------------

async def test_llm_writer_produces_draft_result():
    writer = LLMWriter(FakeStreamLLM(["Intro ", "prose."], usage={"total_tokens": 12}))
    brief = WriterBrief(
        plan=Plan(steps=["Write the intro"]),
        retrieved_context=[_chunk()],
        messages=[Message(role="user", content="Draft it")],
    )
    result = await writer.write_grounded(brief)
    assert isinstance(result, DraftResult)
    assert result.draft == "Intro prose."
    # citations are derived from (⊆) the retrieved sources
    assert [c.source_id for c in result.citations] == ["d1"]
    assert result.metrics["source_count"] == 1
    assert result.metrics["usage"] == {"total_tokens": 12}


async def test_llm_writer_streams_tokens_via_emit():
    seen: list[dict] = []
    writer = LLMWriter(FakeStreamLLM(["a", "b"]))
    brief = WriterBrief(retrieved_context=[_chunk()], messages=[Message(role="user", content="x")])
    await writer.write_grounded(brief, emit=seen.append)
    assert [c["text"] for c in seen if c["type"] == "token"] == ["a", "b"]


async def test_llm_writer_wraps_generation_error():
    writer = LLMWriter(FakeStreamLLM([], fail=True))
    brief = WriterBrief(retrieved_context=[_chunk()], messages=[Message(role="user", content="x")])
    try:
        await writer.write_grounded(brief)
    except WriterGenerationError:
        return
    raise AssertionError("expected WriterGenerationError")


# --- node adapter -----------------------------------------------------------

async def test_node_maps_draft_result_to_writer_json_state_only():
    node = make_writer_node(LLMWriter(FakeStreamLLM(["Hello ", "world"])))
    out = await node(_state(context=[_chunk()]))
    assert out["draft"] == "Hello world"
    assert out["messages"][-1].role == "assistant"
    assert out["messages"][-1].content == "Hello world"
    assert [c.source_id for c in out["citations"]] == ["d1"]
    # DraftResult.metadata/reasoning/metrics MUST NOT leak into GraphState
    assert set(out.keys()) == {"messages", "draft", "citations", "errors"}


async def test_node_empty_context_best_effort_draft_no_citations():
    node = make_writer_node(LLMWriter(FakeStreamLLM(["Ungrounded draft"])))
    out = await node(_state(context=[]))
    assert out["draft"] == "Ungrounded draft"
    assert out["citations"] == []
    assert any(e.message == "empty_context" for e in out["errors"])


async def test_node_generation_failed_finalizes_without_draft():
    node = make_writer_node(FailingWriter())
    out = await node(_state(context=[_chunk()]))
    assert "draft" not in out
    assert any(e.message == "generation_failed" for e in out["errors"])


async def test_node_citation_discipline_drops_invented_source():
    invented = DraftResult(
        draft="text",
        citations=[CitationRef(source_id="d1"), CitationRef(source_id="HALLUCINATED")],
    )
    node = make_writer_node(FakeWriter(invented))
    out = await node(_state(context=[_chunk()]))
    assert [c.source_id for c in out["citations"]] == ["d1"]


async def test_node_swappable_capability():
    fake = FakeWriter(DraftResult(draft="from fake writer"))
    node = make_writer_node(fake)
    out = await node(_state(context=[_chunk()]))
    assert fake.calls == 1
    assert out["draft"] == "from fake writer"


# --- isolation / purity (ADR-0031 §3, Constitution C3) ----------------------

def _imported_modules(path: str) -> set[str]:
    tree = ast.parse(Path(path).read_text())
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(n.name for n in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    return mods


def test_writer_modules_are_pure():
    forbidden_prefixes = ("app.db", "app.runtime", "app.services", "app.llm.factory", "langgraph")
    for module in (writer_mod, writer_prompt_mod, draft_mod):
        for imported in _imported_modules(module.__file__):
            assert not any(
                imported == p or imported.startswith(p + ".") or imported == p
                for p in forbidden_prefixes
            ), f"{module.__name__} imports forbidden {imported}"
