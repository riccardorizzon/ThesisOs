"""PX6 bibliography export tests (M7 P-BIBTEX-DB — DB-backed)."""

from __future__ import annotations

import pytest

from app.services.sources.bibliography import export_bibliography_bibtex
from tests.test_sources_db import PROJECT, _insert_seed_sources


@pytest.mark.asyncio
async def test_export_bibtex_contains_approved_sources(db_session):
    await _insert_seed_sources(db_session)
    await db_session.commit()

    out = await export_bibliography_bibtex(PROJECT)
    assert "@book{" in out
    assert "Benjamin" in out
    assert "Hollander" in out
    assert "Barthes" not in out  # esclusa
