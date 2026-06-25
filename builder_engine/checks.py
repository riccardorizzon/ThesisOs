"""CheckRunner — execute named validation stages and packet checks."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

# Named stages mirror repo root Makefile (MB1 spec §7).
STAGE_COMMANDS: dict[str, str] = {
    "lint": "make lint",
    "typecheck": "make typecheck",
    "unit": "make unit",
    "unit-frontend": "make unit-frontend",
    "unit-builder-engine": "make unit-builder-engine",
    "drift": "make drift",
    "scope": "make scope",
    "isolation": "make isolation",
    "ci": "make ci",
    "embed": "cd backend && .venv/bin/python -m pytest -q tests/test_retrieval_service.py tests/test_retrieval_migration.py",
    "search-smoke": "cd backend && .venv/bin/python -m pytest -q tests/test_search_api.py tests/test_retriever_node.py",
}


@dataclass(frozen=True)
class CheckResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


def run_shell(command: str, repo_root: Path, *, timeout: int = 600) -> CheckResult:
    proc = subprocess.run(
        command,
        shell=True,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return CheckResult(
        command=command,
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def run_stage(stage: str, repo_root: Path) -> CheckResult:
    if stage not in STAGE_COMMANDS:
        return CheckResult(
            command=stage,
            exit_code=127,
            stdout="",
            stderr=f"unknown stage: {stage}",
        )
    return run_shell(STAGE_COMMANDS[stage], repo_root)


def run_packet_checks(checks: tuple[str, ...], repo_root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for check in checks:
        cmd = STAGE_COMMANDS.get(check, check)
        results.append(run_shell(cmd, repo_root))
    return results
