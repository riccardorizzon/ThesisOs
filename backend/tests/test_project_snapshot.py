import pytest

from app.db import models
from app.services.project_snapshot import (
    ProjectSnapshotNotFoundError,
    snapshot_project,
)


async def test_project_snapshot_is_deterministic_and_isolated(db_session):
    protected = models.Project(
        id="snapshot-protected",
        display_name="Protected",
        kind="owned",
    )
    other = models.Project(
        id="snapshot-other",
        display_name="Other",
        kind="owned",
    )
    chapter = models.Chapter(
        project_id=protected.id,
        title="Capitolo",
        content_md="Testo stabile",
    )
    db_session.add_all([protected, other, chapter])
    await db_session.commit()

    first = await snapshot_project(db_session, protected.id)
    repeated = await snapshot_project(db_session, protected.id)
    assert first == repeated

    db_session.add(
        models.Chapter(
            project_id=other.id,
            title="Altro capitolo",
            content_md="Non deve influire",
        )
    )
    await db_session.commit()
    after_other_change = await snapshot_project(db_session, protected.id)
    assert after_other_change["overall_sha256"] == first["overall_sha256"]

    chapter.content_md = "Testo modificato"
    await db_session.commit()
    after_protected_change = await snapshot_project(db_session, protected.id)
    assert after_protected_change["overall_sha256"] != first["overall_sha256"]
    assert after_protected_change["aggregates"]["chapters"]["count"] == 1


async def test_project_snapshot_rejects_unknown_project(db_session):
    with pytest.raises(ProjectSnapshotNotFoundError):
        await snapshot_project(db_session, "missing-project")
