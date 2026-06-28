"""Evaluate Policies — declarative rules after Observe (MB2 D2)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from builder_engine.observe import ObservedSnapshot
from builder_engine.paths import find_repo_root
from builder_engine.yaml_loader import load_simple_yaml

PolicyOutcome = Literal["allow", "block", "escalate"]


@dataclass(frozen=True)
class PolicyViolation:
    rule_id: str
    message: str
    action: PolicyOutcome


@dataclass(frozen=True)
class PolicyDecision:
    outcome: PolicyOutcome
    violations: tuple[PolicyViolation, ...]
    warnings: tuple[str, ...]


def default_policies_path(repo_root: Path) -> Path:
    return repo_root / "plans" / "builder" / "policies.yaml"


def _resolve_outcome(violations: list[PolicyViolation]) -> PolicyOutcome:
    if any(v.action == "block" for v in violations):
        return "block"
    if any(v.action == "escalate" for v in violations):
        return "escalate"
    return "allow"


class PolicyEngine:
    """Evaluate tunable policies — does not replace L1 invariants (ADR-0028)."""

    def __init__(
        self,
        repo_root: Path,
        policies_path: Path | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.policies_path = (policies_path or default_policies_path(self.repo_root)).resolve()
        self._policies = self._load_policies()

    def _load_policies(self) -> dict:
        if not self.policies_path.is_file():
            return {}
        try:
            return load_simple_yaml(self.policies_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"_load_error": str(exc)}

    def evaluate(self, snapshot: ObservedSnapshot) -> PolicyDecision:
        violations: list[PolicyViolation] = []
        warnings: list[str] = list(snapshot.validation_warnings)

        load_error = self._policies.get("_load_error")
        if load_error:
            violations.append(
                PolicyViolation(
                    rule_id="policies.load",
                    message=f"failed to load policies.yaml: {load_error}",
                    action="block",
                )
            )

        if not snapshot.validation_ok:
            violations.append(
                PolicyViolation(
                    rule_id="invariant.graph_invalid",
                    message="graph validation failed — fix lint-graph errors before schedule",
                    action="block",
                )
            )
            for err in snapshot.validation_errors:
                violations.append(
                    PolicyViolation(
                        rule_id="invariant.graph_invalid",
                        message=err,
                        action="block",
                    )
                )

        if snapshot.blockers:
            violations.append(
                PolicyViolation(
                    rule_id="workflow.open_blockers",
                    message=f"{len(snapshot.blockers)} open blocker(s) in STATE",
                    action="block",
                )
            )

        self._builtin_packet_rules(snapshot, violations)
        self._yaml_rules(snapshot, violations)

        outcome = _resolve_outcome(violations)
        return PolicyDecision(
            outcome=outcome,
            violations=tuple(violations),
            warnings=tuple(warnings),
        )

    def _builtin_packet_rules(
        self,
        snapshot: ObservedSnapshot,
        violations: list[PolicyViolation],
    ) -> None:
        """Built-in policy hints (§8.8 — stricter than validate_graph warnings)."""
        for pkt in snapshot.packets:
            if not pkt.checks and pkt.agent_type == "implementer":
                if pkt.status == "ready" and pkt.wave == snapshot.wave:
                    violations.append(
                        PolicyViolation(
                            rule_id="packet.implementer_requires_checks",
                            message=(
                                f"{pkt.id}: ready implementer at wave {snapshot.wave} "
                                "must declare checks before dispatch (§8.8)"
                            ),
                            action="block",
                        )
                    )
                elif pkt.status == "in_progress":
                    violations.append(
                        PolicyViolation(
                            rule_id="packet.in_progress_requires_checks",
                            message=f"{pkt.id}: in_progress without checks — add before sync",
                            action="escalate",
                        )
                    )

    def _yaml_rules(
        self,
        snapshot: ObservedSnapshot,
        violations: list[PolicyViolation],
    ) -> None:
        require_files = self._policies.get("require_files") or {}
        if isinstance(require_files, dict):
            for rule_id, rule in require_files.items():
                if not isinstance(rule, dict):
                    continue
                self._apply_require_file(rule_id, rule, violations)
        elif isinstance(require_files, list):
            for rule in require_files:
                if isinstance(rule, dict):
                    self._apply_require_file(str(rule.get("id") or "require_files"), rule, violations)

        rules = self._policies.get("rules") or {}
        if isinstance(rules, dict):
            for rule_id, rule in rules.items():
                if isinstance(rule, dict):
                    self._apply_conditional_rule(rule_id, rule, snapshot, violations)
        elif isinstance(rules, list):
            for rule in rules:
                if isinstance(rule, dict):
                    self._apply_conditional_rule(str(rule.get("id") or "rule"), rule, snapshot, violations)

    def _apply_require_file(
        self,
        rule_id: str,
        rule: dict,
        violations: list[PolicyViolation],
    ) -> None:
        rel_path = rule.get("path")
        if not rel_path:
            return
        action: PolicyOutcome = str(rule.get("action") or "block")  # type: ignore[assignment]
        if action not in ("allow", "block", "escalate"):
            action = "block"
        target = self.repo_root / str(rel_path)
        if not target.is_file():
            violations.append(
                PolicyViolation(
                    rule_id=rule_id,
                    message=str(rule.get("message") or f"required file missing: {rel_path}"),
                    action=action,
                )
            )

    def _apply_conditional_rule(
        self,
        rule_id: str,
        rule: dict,
        snapshot: ObservedSnapshot,
        violations: list[PolicyViolation],
    ) -> None:
        action: PolicyOutcome = str(rule.get("action") or "escalate")  # type: ignore[assignment]
        if action not in ("allow", "block", "escalate"):
            action = "escalate"
        when = rule.get("when") or {}
        if not isinstance(when, dict):
            return
        epic_status = when.get("epic_status")
        if epic_status and snapshot.epic_status != epic_status:
            return
        epic_prefix = when.get("epic_prefix")
        if epic_prefix and not snapshot.epic.startswith(str(epic_prefix)):
            return
        min_wave = when.get("min_wave")
        if min_wave is not None and snapshot.wave < int(min_wave):
            return
        violations.append(
            PolicyViolation(
                rule_id=rule_id,
                message=str(rule.get("message") or f"policy rule {rule_id} matched"),
                action=action,
            )
        )


def evaluate_policies(
    snapshot: ObservedSnapshot,
    repo_root: Path | None = None,
    policies_path: Path | None = None,
) -> PolicyDecision:
    """Convenience: evaluate with default repo root from snapshot state path."""
    root = repo_root
    if root is None:
        state_parent = Path(snapshot.state_path).resolve().parent.parent.parent
        try:
            root = find_repo_root(state_parent)
        except FileNotFoundError:
            root = state_parent
    return PolicyEngine(root, policies_path).evaluate(snapshot)
