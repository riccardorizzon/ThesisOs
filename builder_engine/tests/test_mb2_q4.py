"""MB2-Q4 — Plugin Registry qualification tests (normative test IDs).

SoR §13.2 MB2-Q4: register/resolve; version mismatch fails closed;
MB2-Q-010…012.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from builder_engine.plugin_registry import (
    PluginInterfaceError,
    PluginRegistry,
    PluginRegistryError,
    PluginVersionMismatchError,
)
from builder_engine.rules import ActionDescriptor

ENGINE_ROOT = Path(__file__).resolve().parents[1]

# Core runtime modules — must not import concrete plugin implementations (INV-R-14).
CORE_RUNTIME_MODULES = (
    "runtime.py",
    "cycle.py",
    "executor.py",
    "rules.py",
    "dependency.py",
    "job_queue.py",
    "projection.py",
    "recovery.py",
    "events.py",
    "program_graph.py",
)

FORBIDDEN_PLUGIN_IMPORTS = (
    "merge_plugin",
    "integration_plugin",
    "qualification_plugin",
    "notification_plugin",
    "metrics_plugin",
)


class _StubMergePlugin:
    def eligible(self, job: object) -> bool:
        return True

    def execute(self, context: dict) -> dict:
        return {"status": "ok", **context}

    def report(self) -> dict:
        return {"plugin": "merge", "status": "ok"}


class _IncompletePlugin:
    def eligible(self, job: object) -> bool:
        return True


def test_mb2_q_010_plugin_registers_by_interface():
    """INV-R-14: plugin registers and resolves by interface (REQ-10)."""
    registry = PluginRegistry()
    stub = _StubMergePlugin()
    registry.register("merge", 1, "merge", lambda: stub)

    descriptor = ActionDescriptor(
        plugin="merge",
        params={},
        rule_id="post-ewo-merge",
        matched_event_id="EwoCompleted@test",
    )
    resolved = registry.resolve(descriptor)

    assert resolved is stub
    assert resolved.eligible("job-1") is True
    assert resolved.execute({"ewo_id": "PX2-EWO-003"})["status"] == "ok"
    assert registry.is_registered("merge")


def test_mb2_q_010_incomplete_interface_rejected_at_register():
    registry = PluginRegistry()
    with pytest.raises(PluginInterfaceError, match="missing methods"):
        registry.register("merge", 1, "merge", lambda: _IncompletePlugin())


def test_mb2_q_011_version_mismatch_rejected():
    """INV-R-15: API version mismatch fails closed at registration."""
    registry = PluginRegistry()
    with pytest.raises(PluginVersionMismatchError, match="api_version 2"):
        registry.register("merge", 2, "merge", lambda: _StubMergePlugin())

    assert not registry.is_registered("merge")

    registry.register("merge", 1, "merge", lambda: _StubMergePlugin())
    with pytest.raises(PluginRegistryError, match="already registered"):
        registry.register("merge", 1, "merge", lambda: _StubMergePlugin())


def test_mb2_q_012_core_has_no_direct_plugin_imports():
    """INV-R-14: core runtime modules must not import plugin implementations."""
    for module_name in CORE_RUNTIME_MODULES:
        source_path = ENGINE_ROOT / module_name
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _assert_no_forbidden_import(alias.name, module_name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                _assert_no_forbidden_import(module, module_name)
                for alias in node.names:
                    _assert_no_forbidden_import(alias.name, module_name)


def _assert_no_forbidden_import(name: str, module_name: str) -> None:
    lowered = name.lower()
    for forbidden in FORBIDDEN_PLUGIN_IMPORTS:
        assert forbidden not in lowered, (
            f"{module_name} must not import plugin implementation {name!r} — use PluginRegistry"
        )
