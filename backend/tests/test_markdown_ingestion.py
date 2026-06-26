"""Markdown / plain-text ingestion regression tests (M4 recovery, P4)."""

from __future__ import annotations

import pytest

from app.schemas.document import VALID_SOURCE_TYPES, infer_source_type
from app.services.document.exceptions import ParseError
from app.services.document.parsers import parse_document
from app.services.document.parsers.markdown_parser import MarkdownParser


def test_extensions_map_to_markdown_and_text():
    assert infer_source_type("notes.md") == "markdown"
    assert infer_source_type("a.markdown") == "markdown"
    assert infer_source_type("plain.txt") == "text"
    assert {"markdown", "text"} <= VALID_SOURCE_TYPES


def test_markdown_parser_splits_on_headings():
    data = b"# Title\n\nIntro body.\n\n## Section\n\nMore body."
    result = MarkdownParser().parse(data, "markdown")
    assert result.parser == "markdown"
    assert result.chunks
    sections = {c.section_path for c in result.chunks}
    assert {"Title", "Section"} & sections
    joined = " ".join(c.content for c in result.chunks)
    assert "Intro body" in joined and "More body" in joined


def test_text_parser_windows_plain_text():
    result = MarkdownParser().parse(b"just some plain text content", "text")
    assert result.parser == "markdown"
    assert result.chunks and "plain text" in result.chunks[0].content


def test_empty_markdown_raises_parse_error():
    with pytest.raises(ParseError):
        MarkdownParser().parse(b"   \n  ", "markdown")


def test_parse_document_routes_markdown_without_docling():
    result = parse_document("markdown", b"# H\n\nbody")
    assert result.parser == "markdown"
    assert result.chunks
