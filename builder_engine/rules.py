"""Runtime Rule Engine — declarative packs, deterministic guard evaluation (MB2 §7)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from builder_engine.events import BuildEvent, EventHandler
from builder_engine.yaml_loader import load_simple_yaml, parse_value

logger = logging.getLogger(__name__)

SUPPORTED_SCHEMA_VERSION = 1
FORBIDDEN_GUARD_PREFIXES = ("qc_", "termination_", "adr_", "constitution_")


class RulePackError(ValueError):
    """Invalid rule pack schema or governance guard keys."""


class GovernanceGuardError(RulePackError):
    """Rule pack contains forbidden governance guard keys (INV-R-07)."""


@dataclass(frozen=True)
class ActionDescriptor:
    plugin: str
    params: dict[str, Any]
    rule_id: str
    matched_event_id: str


@dataclass(frozen=True)
class NoMatch:
    event_type: str
    program_id: str


@dataclass(frozen=True)
class Rule:
    id: str
    priority: int
    on: str
    when: dict[str, Any]
    action_plugin: str
    action_params: dict[str, Any]


@dataclass(frozen=True)
class RulePack:
    schema_version: int
    program_id: str
    rules: tuple[Rule, ...]


def _event_id(event: BuildEvent) -> str:
    cycle = event.cycle_id or ""
    return f"{event.type}@{event.timestamp}@{cycle}"


def _forbidden_guard_keys(when: dict[str, Any]) -> list[str]:
    return [
        key
        for key in when
        if any(key.startswith(prefix) for prefix in FORBIDDEN_GUARD_PREFIXES)
    ]


def _parse_rule(raw: dict[str, Any]) -> Rule:
    rule_id = raw.get("id")
    if not rule_id:
        raise RulePackError("rule missing required field: id")
    on = raw.get("on")
    if not on:
        raise RulePackError(f"rule {rule_id!r} missing required field: on")
    action = raw.get("action")
    if not isinstance(action, dict):
        raise RulePackError(f"rule {rule_id!r} missing required field: action")
    plugin = action.get("plugin")
    if not plugin:
        raise RulePackError(f"rule {rule_id!r} action missing plugin")
    when = dict(raw.get("when") or {})
    forbidden = _forbidden_guard_keys(when)
    if forbidden:
        raise GovernanceGuardError(
            f"rule {rule_id!r} contains forbidden governance guard keys: {forbidden}"
        )
    priority = raw.get("priority")
    if priority is None:
        raise RulePackError(f"rule {rule_id!r} missing required field: priority")
    return Rule(
        id=str(rule_id),
        priority=int(priority),
        on=str(on),
        when=when,
        action_plugin=str(plugin),
        action_params=dict(action.get("params") or {}),
    )


def _parse_inline_mapping(raw: str) -> dict[str, Any]:
    inner = raw.strip()
    if inner in ("{}", ""):
        return {}
    if not (inner.startswith("{") and inner.endswith("}")):
        return {}
    body = inner[1:-1].strip()
    if not body:
        return {}
    result: dict[str, Any] = {}
    for part in body.split(","):
        if ":" not in part:
            continue
        key, val = part.split(":", 1)
        result[key.strip()] = parse_value(val.strip())
    return result


def _parse_rules_section(text: str) -> list[dict[str, Any]]:
    """Line parser for indented rules list entries (§7.2)."""
    lines = text.splitlines()
    start = next(
        (idx for idx, line in enumerate(lines) if line.strip().startswith("rules:")),
        None,
    )
    if start is None:
        return []

    section_indent = len(lines[start]) - len(lines[start].lstrip())
    rules: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    when_data: dict[str, Any] = {}
    action_data: dict[str, Any] = {}
    block: str | None = None

    def flush() -> None:
        nonlocal current, when_data, action_data, block
        if not current:
            return
        if when_data:
            current["when"] = when_data
        if action_data:
            current["action"] = action_data
        rules.append(current)
        current = None
        when_data = {}
        action_data = {}
        block = None

    for line in lines[start + 1 :]:
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= section_indent and not line.lstrip().startswith("- "):
            break
        stripped = line.strip()
        if stripped.startswith("- id:"):
            flush()
            current = {"id": stripped.split(":", 1)[1].strip()}
            continue
        if current is None:
            continue
        if stripped.startswith("priority:"):
            current["priority"] = int(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("on:"):
            current["on"] = stripped.split(":", 1)[1].strip()
        elif stripped == "when:":
            block = "when"
        elif stripped == "action:":
            block = "action"
        elif block == "when" and ":" in stripped:
            key, val = stripped.split(":", 1)
            when_data[key.strip()] = parse_value(val.strip())
        elif block == "action":
            if stripped.startswith("plugin:"):
                action_data["plugin"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("params:"):
                action_data["params"] = _parse_inline_mapping(stripped.split(":", 1)[1])
            elif ":" in stripped:
                key, val = stripped.split(":", 1)
                params = action_data.setdefault("params", {})
                if isinstance(params, dict):
                    params[key.strip()] = parse_value(val.strip())

    flush()
    return rules


def load_rule_pack(path: Path) -> RulePack:
    """Load and validate a §7.2 rule pack from YAML."""
    if not path.is_file():
        raise RulePackError(f"rule pack not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
        data = load_simple_yaml(text)
    except Exception as exc:
        raise RulePackError(f"failed to parse rule pack {path}: {exc}") from exc

    schema_version = data.get("schema_version")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise RulePackError(
            f"unsupported schema_version {schema_version!r}; expected {SUPPORTED_SCHEMA_VERSION}"
        )
    program_id = data.get("program_id")
    if not program_id:
        raise RulePackError("rule pack missing required field: program_id")

    raw_rules = _parse_rules_section(text)
    if not raw_rules:
        fallback = data.get("rules")
        if isinstance(fallback, list):
            raw_rules = [item for item in fallback if isinstance(item, dict)]
    if not raw_rules:
        raise RulePackError("rule pack missing non-empty rules list")

    rules = tuple(_parse_rule(item) for item in raw_rules)
    if not rules:
        raise RulePackError("rule pack contains no valid rules")

    return RulePack(
        schema_version=int(schema_version),
        program_id=str(program_id),
        rules=rules,
    )


def _guards_pass(when: dict[str, Any], context: dict[str, Any]) -> bool:
    for key, expected in when.items():
        if key not in context or context[key] != expected:
            return False
    return True


class RuleEngine:
    """Evaluate declarative rule packs — no Governance policy evaluation (INV-R-07)."""

    def __init__(
        self,
        packs: list[RulePack] | None = None,
        *,
        checkpoint: dict[str, Any] | None = None,
    ) -> None:
        self._packs = list(packs or [])
        self._checkpoint = dict(checkpoint or {})

    @classmethod
    def from_pack_paths(
        cls,
        paths: list[Path],
        *,
        checkpoint: dict[str, Any] | None = None,
    ) -> RuleEngine:
        return cls([load_rule_pack(path) for path in paths], checkpoint=checkpoint)

    @classmethod
    def from_fixtures_dir(
        cls,
        fixtures_dir: Path,
        program_id: str,
        *,
        checkpoint: dict[str, Any] | None = None,
    ) -> RuleEngine:
        packs: list[RulePack] = []
        for path in sorted(fixtures_dir.glob("*_rules.yaml")):
            pack = load_rule_pack(path)
            if pack.program_id in (program_id, "*"):
                packs.append(pack)
        return cls(packs, checkpoint=checkpoint)

    def add_pack(self, pack: RulePack) -> None:
        self._packs.append(pack)

    def set_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        self._checkpoint = dict(checkpoint)

    def rules_for_program(self, program_id: str) -> tuple[Rule, ...]:
        matched = [p for p in self._packs if p.program_id in (program_id, "*")]
        ordered = sorted(
            (rule for pack in matched for rule in pack.rules),
            key=lambda r: (r.priority, r.id),
        )
        return tuple(ordered)

    def evaluate(
        self,
        event: BuildEvent,
        checkpoint: dict[str, Any] | None = None,
    ) -> ActionDescriptor | NoMatch:
        context = {**self._checkpoint, **(checkpoint or {}), **event.payload}
        for rule in self.rules_for_program(event.program_id):
            if rule.on != event.type:
                continue
            if not _guards_pass(rule.when, context):
                continue
            return ActionDescriptor(
                plugin=rule.action_plugin,
                params=dict(rule.action_params),
                rule_id=rule.id,
                matched_event_id=_event_id(event),
            )
        return NoMatch(event_type=event.type, program_id=event.program_id)

    def as_subscriber(
        self,
        checkpoint: dict[str, Any] | None = None,
    ) -> EventHandler:
        snap = dict(checkpoint if checkpoint is not None else self._checkpoint)

        def handler(event: BuildEvent) -> None:
            result = self.evaluate(event, snap)
            if isinstance(result, NoMatch):
                logger.debug(
                    "no rule match for event %s program_id=%s",
                    event.type,
                    event.program_id,
                )

        return handler

    def register(self, bus: Any, checkpoint: dict[str, Any] | None = None) -> None:
        """Register as BuildEventBus subscriber."""
        bus.subscribe(self.as_subscriber(checkpoint))
