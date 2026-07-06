from __future__ import annotations

from pathlib import Path

from builder_engine.classification_registry import validate_classification_registry


def test_classification_registry_passes_on_repo():
    errors = validate_classification_registry(Path(__file__).resolve().parents[2])
    assert errors == [], "\n".join(errors)
