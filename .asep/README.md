# .asep — ASEP engineering pipeline

The brain of the ASEP skill. The skill (`.cursor/skills/asep/SKILL.md`) is just the
**director**; all logic lives here as small, single-responsibility files it reads.

## Pipeline

```text
ASEP request
   → resolvers/intent.md        (develop | review | design | qualify | promote | status)
   → resolvers/capability.md    (request → Capability Graph node + prerequisites)
   → governance/manifest.yaml   (load Constitution, ADRs, Runtime Contract, ADC, plan)
   → templates/work-order-template.md   (build Work Order internally)
   → pipeline/executor.md       (Observe→Analyze→Strategy→Execute→Verify→Commit→Report)
   → pipeline/qualification.md  (gates; STOP on red)
   → pipeline/promotion.md      (freeze/tag, on demand)
```

## Layout

| Path | Responsibility |
|------|----------------|
| `resolvers/intent.md` | deduce intent from natural language (no commands) |
| `resolvers/capability.md` | map request → Capability Graph node + prerequisite check |
| `capabilities/runtime-platform.yaml` | **Capability Graph** (deps, requires, baseline, tests) |
| `governance/manifest.yaml` | ordered governance load (pointers only) |
| `pipeline/executor.md` | ASEP cycle + hard architectural rules |
| `pipeline/qualification.md` | gate order + STOP discipline |
| `pipeline/promotion.md` | promotion + freeze/tag |
| `templates/` | work-order, review, report, promotion skeletons |
| `reports/` | per-phase reports (where the last run left off) |

## Source of truth

Governance is **not** duplicated here — only referenced:

| Artifact | Source |
|----------|--------|
| Runtime Constitution (C1–C8) | `docs/runtime-constitution.md` |
| Layer rules / event model | `decisions/ADR-0030-agent-runtime-layer-boundaries.md` |
| Runtime Contract | `docs/runtime-contract.md` |
| Architecture Decision Checklist | `docs/architecture-decision-checklist.md` |
| Milestone scope | `plans/*.md` (authoritative) |
