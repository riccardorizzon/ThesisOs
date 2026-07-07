"""PX6 bibliography export tests."""

from app.services.sources.bibliography import export_bibliography_bibtex


def test_export_bibtex_contains_approved_sources():
    out = export_bibliography_bibtex("thesis-agent")
    assert "@book{" in out
    assert "Benjamin" in out
    assert "Hollander" in out
    assert "Barthes" not in out  # esclusa
