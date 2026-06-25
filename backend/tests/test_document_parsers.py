import pytest

from app.services.document.exceptions import (
    ParseError,
    ParserUnavailableError,
    UnsupportedFormatError,
)
from app.services.document.parsers import parse_document
from app.services.document.parsers.base import ParsedChunk, ParseResult


class FakeParser:
    def __init__(self, name, *, result=None, error=None):
        self.name = name
        self._result = result
        self._error = error
        self.calls = []

    def parse(self, data, source_type):
        self.calls.append(source_type)
        if self._error is not None:
            raise self._error
        return self._result


def _result(name, n=1):
    return ParseResult(parser=name, chunks=[ParsedChunk(content=f"c{i}") for i in range(n)])


def test_pdf_docling_success_skips_fallback():
    primary = FakeParser("docling", result=_result("docling", 2))
    fallback = FakeParser("pymupdf", result=_result("pymupdf", 1))
    res = parse_document("pdf", b"x", primary=primary, fallback=fallback)
    assert res.parser == "docling"
    assert len(res.chunks) == 2
    assert fallback.calls == []


def test_pdf_docling_failure_uses_fallback():
    primary = FakeParser("docling", error=ParseError("boom"))
    fallback = FakeParser("pymupdf", result=_result("pymupdf", 3))
    res = parse_document("pdf", b"x", primary=primary, fallback=fallback)
    assert res.parser == "pymupdf"
    assert len(res.chunks) == 3


def test_pdf_docling_empty_uses_fallback():
    primary = FakeParser("docling", result=ParseResult(parser="docling", chunks=[]))
    fallback = FakeParser("pymupdf", result=_result("pymupdf", 1))
    res = parse_document("pdf", b"x", primary=primary, fallback=fallback)
    assert res.parser == "pymupdf"


def test_pdf_docling_unavailable_uses_fallback():
    primary = FakeParser("docling", error=ParserUnavailableError("docling"))
    fallback = FakeParser("pymupdf", result=_result("pymupdf", 1))
    res = parse_document("pdf", b"x", primary=primary, fallback=fallback)
    assert res.parser == "pymupdf"


def test_docx_has_no_fallback_on_failure():
    primary = FakeParser("docling", error=ParseError("boom"))
    fallback = FakeParser("pymupdf", result=_result("pymupdf", 1))
    with pytest.raises(ParseError):
        parse_document("docx", b"x", primary=primary, fallback=fallback)
    assert fallback.calls == []


def test_docx_empty_raises_parse_error():
    primary = FakeParser("docling", result=ParseResult(parser="docling", chunks=[]))
    with pytest.raises(ParseError):
        parse_document("docx", b"x", primary=primary)


def test_epub_docling_only_success():
    primary = FakeParser("docling", result=_result("docling", 1))
    res = parse_document("epub", b"x", primary=primary)
    assert res.parser == "docling"


def test_unsupported_format_rejected():
    with pytest.raises(UnsupportedFormatError):
        parse_document("txt", b"x", primary=FakeParser("docling"))
