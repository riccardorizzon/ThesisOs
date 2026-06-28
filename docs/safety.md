# Builder Loop Safety

Denylists, escalation, and auto-merge policy for ASEP / loop engineering.

## Denylist paths (no unattended auto-edit)

- `.env`, `*.pem`, `*credentials*`, `*secret*`
- `infra/terraform/` production modules without explicit epic scope
- `contracts/` — Architect re-freeze only
- `decisions/` — explicit ADR workflow only
- `docs/superpowers/specs/` — frozen specs; documenter packet only

## Auto-merge

- **Never** auto-merge to `main` without integrator pass and green `required_checks`.
- PR babysit loops may comment/suggest only until L2 checklist complete.

## MCP / connectors

- GitHub: read + comment default; write/merge requires human gate.
- No product runtime credentials in builder loops (ADR-0002).

## Escalation triggers

| Signal | Action |
|--------|--------|
| 3 failed fix attempts on same issue | Human triage |
| Merge conflict | Integrator; no auto-resolve |
| `staleness_reasons` from `builder-engine observe` | Block schedule |
| Scope creep outside `owned_files` | REJECT (verifier) |

## Risk paths (human review even if tests pass)

- Auth, payments, IAM, Terraform prod
- Database migrations
- LangGraph topology changes (M5+)

## References

- `loop-budget.md` — caps and kill switch
- ADR-0023 — engine isolation
- `.cursor/agents/loop-verifier.md` — checker agent
