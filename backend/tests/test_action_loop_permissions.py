from pathlib import Path

from app.runtime.action_loop.permissions import PermissionEngine
from app.runtime.action_loop.risk import classify


def test_interactive_allows_read():
    engine = PermissionEngine(workspace_root=Path("/tmp"))
    d = engine.check("search_corpus", {"query": "craft"}, classify("search_corpus"))
    assert d.allowed is True
    assert d.needs_user is False
