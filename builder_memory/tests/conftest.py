"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "mini_repo"


@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    """Copy mini fixture repo to a temp directory."""
    import shutil

    dest = tmp_path / "repo"
    shutil.copytree(FIXTURE_ROOT, dest)
    return dest
