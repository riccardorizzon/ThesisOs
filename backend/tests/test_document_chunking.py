import hashlib

from app.services.document.chunking import (
    compute_chunk_hash,
    estimate_tokens,
    sliding_window_chunks,
)


def test_chunk_hash_matches_spec_formula():
    doc_id, idx, content = "doc-1", 0, " Hello\r\nWorld "
    normalized = content.strip().replace("\r\n", "\n")
    expected = hashlib.sha256(f"{doc_id}:{idx}:{normalized}".encode()).hexdigest()
    assert compute_chunk_hash(doc_id, idx, content) == expected


def test_chunk_hash_stable_across_reparse_same_content():
    assert compute_chunk_hash("d", 2, "same") == compute_chunk_hash("d", 2, "same")


def test_chunk_hash_varies_with_index_and_document():
    base = compute_chunk_hash("d", 0, "x")
    assert compute_chunk_hash("d", 1, "x") != base
    assert compute_chunk_hash("e", 0, "x") != base


def test_chunk_hash_ignores_crlf_and_surrounding_whitespace():
    assert compute_chunk_hash("d", 0, "a\r\nb") == compute_chunk_hash("d", 0, "  a\nb  ")


def test_estimate_tokens():
    assert estimate_tokens("") >= 1
    assert estimate_tokens("a" * 40) == 10


def test_sliding_window_empty_text():
    assert sliding_window_chunks("   ") == []


def test_sliding_window_orders_and_overlaps():
    text = "abcdefghij" * 100  # 1000 chars
    chunks = sliding_window_chunks(text, window_tokens=50, overlap_tokens=10)
    assert len(chunks) > 1
    assert all(c.strip() for c in chunks)
