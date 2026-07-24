import subprocess
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "reset-demo-thesis.py"
)


def test_reset_demo_command_rejects_non_demo_project():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-id",
            "thesis-agent",
            "--confirm",
            "thesis-agent",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "only demo-thesis" in result.stderr


def test_reset_demo_command_requires_exact_confirmation():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-id",
            "demo-thesis",
            "--confirm",
            "wrong",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "confirmation" in result.stderr
