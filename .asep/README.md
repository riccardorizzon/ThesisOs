# .asep — ASEP operational templates

Operational templates the **ASEP skill** (`.cursor/skills/asep/SKILL.md`) uses to run a
milestone end to end from a one-line request (e.g. `ASEP: implementa M5.4B`).

This folder holds **process templates only**. Governance lives at its canonical source —
do not duplicate it here:

| Artifact | Source of truth |
|----------|-----------------|
| Runtime Constitution (C1–C8) | `docs/runtime-constitution.md` |
| Architecture Decision Checklist | `docs/architecture-decision-checklist.md` |
| Runtime Contract | `docs/runtime-contract.md` |
| Layer rules / Event model | `decisions/ADR-0030-agent-runtime-layer-boundaries.md` |
| Plans / milestone scope | `plans/*.md` |

## Templates

| File | Used for |
|------|----------|
| `work-order-template.md` | Internal Work Order the skill builds before executing |
| `review-template.md` | ADC review record (Constitution C7 order) |
| `report-template.md` | Milestone status report |
| `promotion-template.md` | Promotion doc for `*.N` freeze milestones |
