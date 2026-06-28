# MB2 Phase 2 Gate — Evaluate Policies (D2)

- **Date:** 2026-06-28
- **Scope:** MB2 deliverable D2 only (`policy.py`, `policies.yaml`, CLI `policy`, tests)
- **Spec:** `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` §3 D2
- **Prerequisite:** Phase 1 (D1 Observe) — `docs/mb2-phase1-gate.md`

## Evidence

| Check | Status | Command |
|-------|--------|---------|
| policy unit tests | green | `make unit-builder-engine` |
| policies.yaml loads | green | `builder-engine policy --repo-root . --json` |
| implementer without checks blocks | green | `test_policy.py::test_ready_implementer_without_checks_blocks` |
| invariants not overridden | green | policy references snapshot validation; L1 in validate_graph |
| read-only policy eval | green | no STATE mutation in `policy.py` |
| isolation | green | `make isolation` |

## Promotion

```yaml
policy_unit: green
policies_yaml_loads: green
unit_builder_engine: green
observe_cli: green
policy_cli: green
```

**Phase 2 closed:** 2026-06-28. Phase 3 (Extended Plan D3) not started.

## CLI

```bash
builder-engine observe --repo-root . --json
builder-engine policy --repo-root . --json
```
