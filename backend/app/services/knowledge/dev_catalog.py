"""Dev/test catalog gate — M7.1 stub removal."""

from __future__ import annotations

import os


def dev_catalog_enabled() -> bool:
    """Legacy CONCEPT_CATALOG / picker list only when explicitly enabled (tests)."""
    return os.environ.get("THESISOS_DEV_CATALOG", "").lower() in ("1", "true", "yes")
