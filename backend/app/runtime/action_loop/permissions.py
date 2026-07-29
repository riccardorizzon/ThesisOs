from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from app.runtime.action_loop.risk import RiskClass


class Mode(str, Enum):
    INTERACTIVE = "interactive"


@dataclass(frozen=True)
class Decision:
    allowed: bool
    needs_user: bool


class PermissionEngine:
    def __init__(self, *, workspace_root: Path, mode: Mode = Mode.INTERACTIVE) -> None:
        self._workspace_root = workspace_root
        self._mode = mode

    def check(self, tool_name: str, arguments: dict, risk: RiskClass) -> Decision:
        del tool_name, arguments  # reserved for future policy hooks
        if risk is RiskClass.READ and self._mode is Mode.INTERACTIVE:
            return Decision(allowed=True, needs_user=False)
        return Decision(allowed=False, needs_user=True)
