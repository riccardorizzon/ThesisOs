"""Plugin Registry — register and resolve runtime plugins by interface (MB2 §8)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from builder_engine.rules import ActionDescriptor

SUPPORTED_PLUGIN_API_VERSION = 1

INTERFACE_METHODS: dict[str, tuple[str, ...]] = {
    "scheduler": ("claim", "release", "build_manifest"),
    "merge": ("eligible", "execute", "report"),
    "integration": ("start", "run_checks", "report"),
    "qualification": ("spawn", "collect_evidence", "report"),
    "notification": ("notify",),
    "metrics": ("record",),
}


class PluginRegistryError(ValueError):
    """Invalid registry operation."""


class PluginVersionMismatchError(PluginRegistryError):
    """INV-R-15: API version mismatch fails closed at registration."""


class PluginInterfaceError(PluginRegistryError):
    """Registered instance does not satisfy the declared interface."""


@dataclass(frozen=True)
class PluginRegistration:
    plugin_id: str
    api_version: int
    interface: str
    factory: Callable[..., Any]


class PluginRegistry:
    """Register plugins by interface; resolve from Rule Engine action descriptors."""

    def __init__(self) -> None:
        self._plugins: dict[str, PluginRegistration] = {}

    def register(
        self,
        plugin_id: str,
        api_version: int,
        interface: str,
        factory: Callable[..., Any],
    ) -> None:
        """Register a plugin factory. Fails closed on version or interface mismatch."""
        if api_version != SUPPORTED_PLUGIN_API_VERSION:
            raise PluginVersionMismatchError(
                f"plugin {plugin_id!r}: api_version {api_version} "
                f"!= supported {SUPPORTED_PLUGIN_API_VERSION}"
            )
        if interface not in INTERFACE_METHODS:
            raise PluginInterfaceError(f"unknown interface: {interface!r}")
        if plugin_id in self._plugins:
            raise PluginRegistryError(f"plugin already registered: {plugin_id!r}")

        probe = factory()
        _validate_interface(probe, interface)

        self._plugins[plugin_id] = PluginRegistration(
            plugin_id=plugin_id,
            api_version=api_version,
            interface=interface,
            factory=factory,
        )

    def resolve(self, action: ActionDescriptor) -> Any:
        """Resolve action.plugin to a registered plugin instance."""
        reg = self._plugins.get(action.plugin)
        if reg is None:
            raise KeyError(f"no plugin registered for action plugin={action.plugin!r}")
        instance = reg.factory(**action.params) if action.params else reg.factory()
        _validate_interface(instance, reg.interface)
        return instance

    def is_registered(self, plugin_id: str) -> bool:
        return plugin_id in self._plugins


def _validate_interface(instance: Any, interface: str) -> None:
    required = INTERFACE_METHODS[interface]
    missing = [name for name in required if not callable(getattr(instance, name, None))]
    if missing:
        raise PluginInterfaceError(
            f"instance for interface {interface!r} missing methods: {', '.join(missing)}"
        )
