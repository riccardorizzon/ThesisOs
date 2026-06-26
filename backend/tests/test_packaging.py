"""Packaging regression guard (M4 recovery, bug-2/3).

The runtime must not depend on packages installed by hand in the container: the
backend image must install the parser extra and package the event catalog.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _find_dockerfile() -> Path | None:
    """Walk up from this test file until docker/backend.Dockerfile is found."""
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "docker" / "backend.Dockerfile"
        if candidate.is_file():
            return candidate
    return None


_DOCKERFILE = _find_dockerfile()


@pytest.mark.skipif(_DOCKERFILE is None, reason="docker/backend.Dockerfile not visible from test cwd")
def test_backend_image_installs_parsers_extra():
    text = _DOCKERFILE.read_text(encoding="utf-8")
    assert "[parsers]" in text, "backend image must install .[parsers] (docling + pymupdf)"


@pytest.mark.skipif(_DOCKERFILE is None, reason="docker/backend.Dockerfile not visible from test cwd")
def test_backend_image_packages_contracts():
    text = _DOCKERFILE.read_text(encoding="utf-8")
    assert "COPY contracts/" in text, "event catalog (contracts/) must be in the image"
