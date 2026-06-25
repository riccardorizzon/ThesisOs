"""Chunk identity + sizing helpers (M3, spec §5).

`chunk_hash` is the stable content key M4 (embeddings/retrieval) will reuse, so
re-parse of unchanged content does not force re-embedding. No vectors here.
"""

from __future__ import annotations

import hashlib

CHARS_PER_TOKEN = 4
DEFAULT_WINDOW_TOKENS = 512
DEFAULT_OVERLAP_TOKENS = 64


def normalize_content(content: str) -> str:
    """Normalization applied before hashing (spec §5.2)."""
    return content.strip().replace("\r\n", "\n")


def compute_chunk_hash(document_id: str, chunk_index: int, content: str) -> str:
    """SHA-256 over ``{document_id}:{chunk_index}:{normalized}`` (spec §5.2)."""
    normalized = normalize_content(content)
    payload = f"{document_id}:{chunk_index}:{normalized}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def estimate_tokens(text: str) -> int:
    """Cheap token estimate (chars/4); replaced by tiktoken later if needed."""
    return max(1, len(text) // CHARS_PER_TOKEN)


def sliding_window_chunks(
    text: str,
    *,
    window_tokens: int = DEFAULT_WINDOW_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[str]:
    """Fixed-size windowed chunking with overlap — the PyMuPDF fallback path (§5.1).

    Operates on characters using the token≈chars/4 estimate. Empty windows are
    skipped (spec §5.1: never insert zero-length chunks).
    """
    text = text.strip()
    if not text:
        return []
    window = max(1, window_tokens * CHARS_PER_TOKEN)
    overlap = max(0, min(overlap_tokens * CHARS_PER_TOKEN, window - 1))
    step = max(1, window - overlap)

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        piece = text[start : start + window].strip()
        if piece:
            chunks.append(piece)
        if start + window >= n:
            break
        start += step
    return chunks
