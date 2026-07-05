"""Tests for read-only corpus picker helpers (PX2-EWO-004)."""

from app.graph.corpus_query import (
    EXCLUDED_SOURCE_IDS,
    is_excluded_source_id,
    list_corpus_for_picker,
)


def test_list_corpus_for_picker_omits_excluded_by_default():
    entries = list_corpus_for_picker()
    ids = {e["id"] for e in entries}
    assert "barthes-mythologies" not in ids
    assert "benjamin-opera-arte" in ids


def test_list_corpus_for_picker_search_by_author():
    entries = list_corpus_for_picker("Benjamin")
    assert len(entries) == 1
    assert entries[0]["id"] == "benjamin-opera-arte"


def test_is_excluded_source_id():
    assert is_excluded_source_id("barthes-mythologies")
    assert not is_excluded_source_id("benjamin-opera-arte")
    assert "barthes-mythologies" in EXCLUDED_SOURCE_IDS
