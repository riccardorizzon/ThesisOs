from builder_memory.config import kind_for_path, should_index


def test_allowlist_includes_adr():
    assert should_index("decisions/ADR-0001-contract-first.md")


def test_denylist_excludes_backend():
    assert not should_index("backend/app/main.py")


def test_kind_adr():
    assert kind_for_path("decisions/ADR-0019-builder-memory-boundaries.md") == "adr"


def test_kind_state():
    assert kind_for_path("plans/builder/STATE.yaml") == "state"
