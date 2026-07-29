"""Unit tests for manuscript export ordering."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.chapter.manuscript_order import (
    manuscript_export_order,
    parse_manuscript_title,
    render_manuscript_markdown,
)


@dataclass
class FakeChapter:
    id: str
    title: str
    order_index: int
    word_count: int = 0
    content_md: str | None = None


def test_parse_chapter_and_section_titles():
    assert parse_manuscript_title("Cap. 3 — Metodo").kind == "chapter"
    assert parse_manuscript_title("§1.2 Flow").kind == "section"
    assert parse_manuscript_title("Introduzione").kind == "other"


def test_manuscript_export_order_cap_section_then_others():
    chapters = [
        FakeChapter(id="free", title="Introduzione", order_index=40, content_md="free"),
        FakeChapter(id="s31", title="§3.1 Palette", order_index=31, content_md="s"),
        FakeChapter(id="c3", title="Cap. 3 — Progettazione", order_index=7, content_md="c"),
        FakeChapter(id="s36", title="§3.6 Sintesi", order_index=36, content_md="s6"),
    ]
    ordered = manuscript_export_order(chapters)
    assert [c.id for c in ordered] == ["c3", "s31", "s36", "free"]


def test_render_manuscript_markdown_empty():
    assert render_manuscript_markdown([]) == "# Manoscritto\n"


def test_render_manuscript_markdown_concatenates():
    md = render_manuscript_markdown(
        [
            FakeChapter(
                id="c1",
                title="Cap. 1 — Intro",
                order_index=0,
                content_md="Hello",
            ),
            FakeChapter(
                id="s11",
                title="§1.1 Contesto",
                order_index=1,
                content_md="World",
            ),
        ]
    )
    assert md.startswith("# Cap. 1 — Intro\n\nHello\n")
    assert "---" in md
    assert "# §1.1 Contesto\n\nWorld\n" in md
