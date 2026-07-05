# .asep — ASEP engineering pipeline

The brain of the ASEP skill. The skill (`.cursor/skills/asep/SKILL.md`) is just the
**director**; all logic lives here as small, single-responsibility files it reads.

## Pipeline

```text
ASEP request
   → resolvers/intent.md        (authorize | develop | review | design | qualify | promote | status)
   → resolvers/authorize.md     (AUTHORIZE PX-n — Architect API; pre-flight → first EWO)
   → Engineering Program        (if thesis-agent/OR/E2E track — see capability resolver)
   → resolvers/capability.md    (request → Capability Graph node + prerequisites)
   → governance/manifest.yaml   (load Constitution, ADRs, Runtime Contract, ADC, plan)
   → governance/quality-controller.md   (issue QC Certificate — does not decide)
   → governance/engineering-supervisor.md   (read certificate; state machine)
   → templates/work-order-template.md   (build Work Order internally)
   → pipeline/executor.md       (Observe→Analyze→Strategy→Execute→Verify→Commit→Report)
   → pipeline/qualification.md  (gates; STOP on red)
   → pipeline/promotion.md      (freeze/tag, on demand)
```

See `docs/engineering-program.md` for **outer loop** (roadmap → spawn WorkOrder) vs
**inner loop** (execute WorkOrder).

## Layout

| Path | Responsibility |
|------|----------------|
| `programs/*.yaml` | **Engineering Program** instances (scope, binding, backlog) |
| `resolvers/intent.md` | deduce intent from natural language or Architect API |
| `resolvers/authorize.md` | **Architect API** — `AUTHORIZE PX-n` → pre-flight → first EWO |
| `resolvers/capability.md` | map request → Capability Graph node + prerequisite check |
| `capabilities/runtime-platform.yaml` | Runtime Platform capability graph |
| `capabilities/thesis-agent-migration.yaml` | Thesis-agent migration OR/E2E graph |
| `governance/manifest.yaml` | ordered governance load (pointers only) |
| `governance/quality-controller.md` | QC checklist — **issues certificate only** |
| `governance/qc-certificate-template.md` | QC Certificate format |
| `governance/engineering-supervisor.md` | state machine (reads certificate) |
| `certificates/` | issued QC Certificates (immutable) |
| `pipeline/executor.md` | ASEP cycle + hard architectural rules |
| `pipeline/qualification.md` | gate order + STOP discipline |
| `pipeline/promotion.md` | promotion + freeze/tag |
| `templates/conformance-ewo-template.md` | **PX-3+ EWO** — SoR `covers` (max 3) + Yes/Observable |
| `reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-FRAMEWORK.md` | Taxonomy ratification (Yes/Observable) |
| `reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-BACKLOG-REVIEW.md` | Backlog review PASS — dispatch authorized |
| `reports/PX3-ARCHITECT-REVIEW-WAVE-B-20260705.md` | Wave B exit review — PASS; Wave C NOT YET AUTHORIZED |
| `reports/PX3-WAVE-B-BACKLOG.md` | Wave B backlog (APPROVED) |
| `proposals/` | QWO/EWO proposals — **authorization required** (human or auto-approval policy) |
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
| Engineering Program model | `docs/engineering-program.md` |
| Thesis-agent migration program | `.asep/programs/thesis-agent-migration.yaml` |
