"""Validate platform_contract classification passes against the ASEP registry.

Governance-only — must not be imported by backend.app (INV-B9).
First consumer: ``make validate-platform-classification`` (CI).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from builder_engine.paths import find_repo_root

REGISTRY_REL = Path(".asep/registry/platform-classification.yaml")
PROPOSALS_DIR = Path(".asep/proposals")
WORKORDER_RE = re.compile(
    r"^#\s+Engineering WorkOrder Proposal\s+—\s+(.+?)\s*$",
    re.MULTILINE,
)
YAML_BLOCK_RE = re.compile(r"```yaml\s*\nplatform_contract:\s*\n(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class ProposalContract:
    path: Path
    workorder_id: str
    classification_pass: str | None
    classification_mode: str | None
    classification_registry: str | None


def _parse_contract_block(block: str) -> dict[str, str | None]:
    fields: dict[str, str | None] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val in ("", "null"):
            fields[key] = None
        else:
            fields[key] = val
    return fields


def load_registry(root: Path | None = None) -> dict:
    base = root or find_repo_root()
    path = base / REGISTRY_REL
    if not path.is_file():
        raise FileNotFoundError(f"registry not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _proposal_path_for_workorder(base: Path, workorder_id: str) -> Path | None:
    matches = sorted(base.glob(f"{workorder_id}*.md"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        return None
    # Prefer exact prefix match without ambiguity
    exact = [m for m in matches if m.stem == workorder_id or m.stem.startswith(workorder_id + "-")]
    return exact[0] if len(exact) == 1 else matches[0]


def scan_proposals(root: Path | None = None) -> list[ProposalContract]:
    base = root or find_repo_root()
    proposals_dir = base / PROPOSALS_DIR
    out: list[ProposalContract] = []
    for path in sorted(proposals_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        wo_match = WORKORDER_RE.search(text)
        if not wo_match:
            continue
        workorder_id = wo_match.group(1).strip()
        block_match = YAML_BLOCK_RE.search(text)
        if not block_match:
            continue
        fields = _parse_contract_block(block_match.group(1))
        out.append(
            ProposalContract(
                path=path.relative_to(base),
                workorder_id=workorder_id,
                classification_pass=fields.get("classification_pass"),
                classification_mode=fields.get("classification_mode"),
                classification_registry=fields.get("classification_registry"),
            )
        )
    return out


def validate_classification_registry(root: Path | None = None) -> list[str]:
    """Return human-readable violation messages; empty list means PASS."""
    base = root or find_repo_root()
    registry = load_registry(base)
    errors: list[str] = []

    passes = registry.get("passes") or []
    if not isinstance(passes, list):
        return ["registry: passes must be a list"]

    pass_by_id: dict[str, dict] = {}
    scope_to_pass: dict[str, str] = {}
    for entry in passes:
        if not isinstance(entry, dict):
            errors.append("registry: each pass entry must be a mapping")
            continue
        pass_id = entry.get("id")
        if not isinstance(pass_id, str) or not pass_id:
            errors.append("registry: pass missing id")
            continue
        pass_by_id[pass_id] = entry
        scope = entry.get("scope") or []
        if not isinstance(scope, list):
            errors.append(f"registry: pass {pass_id} scope must be a list")
            continue
        for wo in scope:
            if not isinstance(wo, str):
                errors.append(f"registry: pass {pass_id} scope entries must be strings")
                continue
            if wo in scope_to_pass and scope_to_pass[wo] != pass_id:
                errors.append(
                    f"registry: workorder {wo} listed in both {scope_to_pass[wo]} and {pass_id}"
                )
            scope_to_pass[wo] = pass_id
            proposal_path = _proposal_path_for_workorder(base / PROPOSALS_DIR, wo)
            if proposal_path is None:
                errors.append(f"registry: pass {pass_id} scope {wo} — proposal file not found")
            elif not proposal_path.is_file():
                errors.append(f"registry: pass {pass_id} scope {wo} — missing {proposal_path}")

    planned_ids = {
        p.get("id")
        for p in (registry.get("planned") or [])
        if isinstance(p, dict) and isinstance(p.get("id"), str)
    }

    for contract in scan_proposals(base):
        pass_id = contract.classification_pass
        if pass_id is None:
            continue

        if pass_id in planned_ids:
            errors.append(
                f"{contract.path}: classification_pass {pass_id} is planned-only, not executed"
            )
            continue

        if pass_id not in pass_by_id:
            errors.append(
                f"{contract.path}: classification_pass {pass_id!r} not in registry passes"
            )
            continue

        reg_pass = pass_by_id[pass_id]
        scope = reg_pass.get("scope") or []
        if contract.workorder_id not in scope:
            errors.append(
                f"{contract.path}: {contract.workorder_id} has pass {pass_id} "
                f"but is not in registry scope"
            )

        mode = contract.classification_mode
        if mode in ("retrospective", "prospective") and not contract.classification_registry:
            errors.append(
                f"{contract.path}: {mode} classification requires classification_registry"
            )

        expected_registry = str(REGISTRY_REL).replace("\\", "/")
        if contract.classification_registry and contract.classification_registry.replace(
            "\\", "/"
        ) not in (expected_registry, f"./{expected_registry}"):
            errors.append(
                f"{contract.path}: classification_registry must point to {expected_registry}"
            )

    # Registry scope entries must carry matching pass in proposal when block exists
    contracts_by_wo = {c.workorder_id: c for c in scan_proposals(base)}
    for pass_id, entry in pass_by_id.items():
        for wo in entry.get("scope") or []:
            if not isinstance(wo, str):
                continue
            contract = contracts_by_wo.get(wo)
            if contract is None:
                errors.append(f"registry: pass {pass_id} scope {wo} — no platform_contract block")
            elif contract.classification_pass != pass_id:
                errors.append(
                    f"registry: pass {pass_id} scope {wo} — proposal has "
                    f"{contract.classification_pass!r}"
                )

    return errors
