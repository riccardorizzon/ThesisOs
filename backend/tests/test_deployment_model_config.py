from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
TERRAFORM_DIR = REPO_ROOT / "infra" / "terraform"


def _variable_default(variable_name: str) -> str:
    variables = (TERRAFORM_DIR / "variables.tf").read_text()
    match = re.search(
        rf'variable "{re.escape(variable_name)}" \{{.*?default\s*=\s*"([^"]+)"',
        variables,
        re.DOTALL,
    )
    assert match is not None, f"Terraform variable {variable_name!r} needs a string default"
    return match.group(1)


def _cloud_run_env_value(env_name: str) -> str:
    cloud_run = (TERRAFORM_DIR / "cloudrun.tf").read_text()
    match = re.search(
        rf'env \{{\s*name\s*=\s*"{re.escape(env_name)}"\s*value\s*=\s*([^\s]+)\s*\}}',
        cloud_run,
    )
    assert match is not None, f"Cloud Run environment variable {env_name!r} is missing"
    return match.group(1)


def _example_env() -> dict[str, str]:
    return {
        key: value
        for line in (REPO_ROOT / ".env.example").read_text().splitlines()
        if line and not line.startswith("#")
        for key, value in [line.split("=", 1)]
    }


def test_deployment_uses_approved_gemini_model_tiers():
    assert _variable_default("vertex_location") == "global"
    assert _variable_default("gemini_model") == "gemini-3.6-flash"
    assert _variable_default("gemini_orchestration_model") == "gemini-3.5-flash-lite"

    assert _cloud_run_env_value("VERTEX_LOCATION") == "var.vertex_location"
    assert _cloud_run_env_value("GEMINI_MODEL") == "var.gemini_model"
    assert (
        _cloud_run_env_value("GEMINI_ORCHESTRATION_MODEL")
        == "var.gemini_orchestration_model"
    )

    example = _example_env()
    assert example["VERTEX_LOCATION"] == "global"
    assert example["GEMINI_MODEL"] == "gemini-3.6-flash"
    assert example["GEMINI_ORCHESTRATION_MODEL"] == "gemini-3.5-flash-lite"
