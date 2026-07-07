"""Export API tests (M7 P-EXPORT-MIN)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.chapter import ChapterCreate
from app.services.chapter import ChapterService

client = TestClient(app)


@pytest.mark.asyncio
async def test_export_chapter_markdown(db_session):
    chapter_svc = ChapterService()
    chapter = await chapter_svc.create(
        ChapterCreate(title="Export me", content_md="# Hello\n\nExported paragraph."),
        session=db_session,
    )
    await db_session.commit()

    res = client.get(f"/export/chapters/{chapter.id}.md")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/markdown")
    assert "attachment" in res.headers.get("content-disposition", "")
    assert "# Hello" in res.text
    assert "Exported paragraph." in res.text


def test_export_chapter_not_found():
    res = client.get("/export/chapters/00000000-0000-0000-0000-000000000000.md")
    assert res.status_code == 404
    body = res.json()
    assert body["code"] == "chapter_not_found"
