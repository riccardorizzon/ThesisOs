from builder_memory.context_builder.builder import BuildContextRequest, ContextBuilder
from builder_memory.indexer.indexer import CorpusIndexer
from builder_memory.rankers.base import normalize_scores


def test_assembly_non_authoritative_header(mini_repo):
    CorpusIndexer(mini_repo).index()
    result = ContextBuilder(mini_repo).build(
        BuildContextRequest(task="Verify GraphState contract", agent_role="architect")
    )
    assert "NON-AUTHORITATIVE" in result.context.prompt_block
    assert "Source:" in result.context.prompt_block
    assert "Your task" in result.context.prompt_block


def test_token_budget_respected(mini_repo):
    CorpusIndexer(mini_repo).index()
    result = ContextBuilder(mini_repo).build(
        BuildContextRequest(task="x" * 100, token_budget=500)
    )
    assert result.context.token_estimate <= 600


def test_provenance_fields(mini_repo):
    CorpusIndexer(mini_repo).index()
    result = ContextBuilder(mini_repo).build(
        BuildContextRequest(task="GraphState frozen", agent_role="architect")
    )
    assert result.context.provenance
    first = result.context.provenance[0]
    assert first.path
    assert 0.0 <= first.score <= 1.0
    assert first.source_type
    d = first.to_dict()
    assert set(d.keys()) == {"path", "score", "source_type"}


def test_normalize_scores():
    assert normalize_scores([1.0, 2.0, 3.0]) == [0.0, 0.5, 1.0]
    assert normalize_scores([5.0, 5.0]) == [1.0, 1.0]
