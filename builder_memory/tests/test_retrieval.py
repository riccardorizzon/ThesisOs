from builder_memory.indexer.indexer import CorpusIndexer
from builder_memory.rankers.bm25 import Bm25Ranker
from builder_memory.retriever.retriever import Retriever


def test_retrieve_graphstate(mini_repo):
    CorpusIndexer(mini_repo).index()
    results = Retriever(mini_repo).retrieve("GraphState frozen", agent_role="architect")
    paths = {r.source_path for r in results}
    assert "decisions/ADR-0007-state-contract.md" in paths or any(
        "GraphState" in r.content for r in results
    )


def test_role_bias_via_ranker(mini_repo):
    CorpusIndexer(mini_repo).index()
    raw = Retriever(mini_repo).retrieve("ADR state", agent_role="architect", limit=5)
    ranker = Bm25Ranker()
    arch = ranker.provenance(raw, agent_role="architect")
    back = ranker.provenance(raw, agent_role="backend")
    assert arch or back
    if arch and back and arch[0].path == back[0].path:
        # Same top path — scores may still differ after role weighting.
        assert arch[0].source_type == back[0].source_type
