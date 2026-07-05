"""Retriever exclusion-aware and corpus-list merge tests."""

from __future__ import annotations

from app.graph.corpus_query import is_corpus_list_query
from app.graph.retriever import _merge_results
from app.schemas.retrieval import SearchResultItem


def _item(cid: str, content: str, title: str = "Doc") -> SearchResultItem:
    return SearchResultItem(
        chunk_id=cid,
        document_id="d",
        chunk_hash="h",
        score=0.5,
        content=content,
        document_title=title,
    )


def test_is_corpus_list_query_for_or3_prompt():
    assert is_corpus_list_query(
        "Elenca gli autori del corpus attivo. Indica cosa è escluso."
    )


def test_merge_results_prefers_extras_first():
    primary = [_item("a", "outline")]
    exclusion = [_item("b", "ESCLUSO dal corpus")]
    bibliography = [_item("c", "FONDAMENTALE Löbach", "Bibliography-Master")]
    merged = _merge_results(primary, exclusion, bibliography, limit=10)
    assert [m.chunk_id for m in merged] == ["b", "c", "a"]


def test_merge_results_deduplicates_across_layers():
    primary = [_item("a", "outline")]
    extra = [_item("a", "duplicate")]
    merged = _merge_results(primary, extra, limit=10)
    assert [m.chunk_id for m in merged] == ["a"]
