# Builder Loop State (bridge)

> **Authoritative state:** [`plans/builder/STATE.yaml`](plans/builder/STATE.yaml)
>
> This file exists for loop-engineering tooling compatibility
> ([loop-audit](https://github.com/cobusgreyling/loop-engineering)). Do not
> duplicate packet status here — edit `STATE.yaml` only.

## Project

- **Name:** ThesisOS / ASEP
- **Active epic:** `mb2-adaptive-runtime` (closed 2026-06-28)
- **Gate:** `docs/mb2-phase-gate.md`

## Last run

- **2026-06-28** — MB2 loop complete (D3–D10); 65 engine tests green

## Escalation

- Packet `blocked` → record in `STATE.yaml` `blockers`, orchestrator resolves
- Gate red → no promotion; fix evidence before next wave
- >3 failed auto-fix attempts on same issue → human triage (no unattended retry loop)

## Quick status

```bash
builder-engine observe --repo-root .
builder-engine policy --repo-root .
builder-engine lint-graph --repo-root .
```
