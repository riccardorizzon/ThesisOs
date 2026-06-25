from builder_memory.indexer.indexer import CorpusIndexer


def test_index_mini_repo(mini_repo):
    stats = CorpusIndexer(mini_repo).index()
    assert stats.file_count >= 3
    assert stats.chunk_count >= 3


def test_incremental_skips(mini_repo):
    indexer = CorpusIndexer(mini_repo)
    first = indexer.index()
    second = indexer.index(incremental=True)
    assert second.skipped >= first.file_count - 1
