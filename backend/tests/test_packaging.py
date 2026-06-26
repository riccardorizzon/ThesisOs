"""Packaging regression guard (M4 recovery, bug-2/3).

The runtime must not depend on packages installed by hand in the container: the
backend image must install the parser extra and package the event catalog.
"""

from __future__ import annotations

from pathlib import Path

_DOCKERFILE = Path(__file__).resolve().parents[2] / "docker" / "backend.Dockerfile"


def test_backend_image_installs_parsers_extra():
    text = _DOCKERFILE.read_text(encoding="utf-8")
    assert "[parsers]" in text, "backend image must install .[parsers] (docling + pymupdf)"


def test_backend_image_packages_contracts():
    text = _DOCKERFILE.read_text(encoding="utf-8")
    assert "COPY contracts/" in text, "event catalog (contracts/) must be in the image"
