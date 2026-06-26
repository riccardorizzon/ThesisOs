"""Docling parser — primary for PDF/DOCX/EPUB (spec §12).

Docling is imported lazily and written to a temp file because its converter works
on paths. If the library is absent we raise ParserUnavailableError so the package
still imports in environments (e.g. CI) without the heavy dependency installed.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from app.services.document.exceptions import ParseError, ParserUnavailableError
from app.services.document.parsers.base import ParseResult, markdown_to_chunks

_EXT = {"pdf": ".pdf", "docx": ".docx", "epub": ".epub"}


class DoclingParser:
    name = "docling"

    def parse(self, data: bytes, source_type: str) -> ParseResult:
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption
        except ImportError as exc:  # pragma: no cover - env without docling
            raise ParserUnavailableError("docling") from exc

        # M3 defers scanned-PDF OCR; default Docling 2.x OCR init fails in our
        # container (RapidOCR torch.PP-OCRv6.det.small). Born-digital PDFs parse
        # cleanly with OCR off; PyMuPDF remains the PDF fallback on other errors.
        pdf_options = PdfPipelineOptions()
        pdf_options.do_ocr = False
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options)}
        )

        suffix = _EXT.get(source_type, "")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            try:
                result = converter.convert(Path(tmp.name))
                markdown = result.document.export_to_markdown()
            except Exception as exc:  # docling raises a variety of errors
                raise ParseError(f"docling failed for {source_type}: {exc}") from exc

        chunks = markdown_to_chunks(markdown or "")
        return ParseResult(parser=self.name, chunks=chunks)
