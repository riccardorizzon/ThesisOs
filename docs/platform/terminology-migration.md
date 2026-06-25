# ASEP Terminology Migration

- **Authority:** ADR-0026 (frozen 2026-06-25)
- **Purpose:** Track legacy → official vocabulary and incremental doc updates without rewriting frozen spec semantics.

## Supersession map

| Legacy term | Official term | Notes |
|-------------|---------------|-------|
| Agent OS | **ASEP** (Adaptive Software Engineering Platform) | Whole repository ecosystem: product + build + contracts + knowledge |
| BuilderOS | **Build Control Plane** + **Engineering Runtime** | Control plane = planning, observation, policy; runtime = `builder_engine/` |
| builder_engine alone = "the OS" | **Engineering Runtime** | One component; not the whole platform |
| M-milestone only roadmap | **Product Track** within ASEP | M0–M18; ThesisOS user-facing capabilities |
| MB-milestone only roadmap | **Platform Track** within ASEP | MB1–MBn; control + runtime intelligence |
| Cursor orchestrator skill | **Operator surface** (on Build Control Plane) | `.cursor/skills/orchestrate-builders/` |
| Cursor Task agents | **Execution workers** | Non-deterministic implementers invoked by runtime/control plane |
| ThesisOS runtime | **Product Plane** | `backend/app/`, `frontend/`, M-series |
| `WorkflowRuntime` (class) | **`EngineeringRuntime`** | ADR-0028: it runs a *cycle*, not a workflow; rename deferred to MB2 branch |

## Planes and runtimes (quick reference)

| Term | Lives in (examples) |
|------|---------------------|
| **Product Plane** | `backend/app/`, `frontend/`, M-series milestones |
| **Build Control Plane** | `plans/builder/`, `decisions/`, `knowledge/`, orchestrate-builders skill |
| **Engineering Runtime** | `builder_engine/` |
| **Execution workers** | Cursor Task agents, human operators |

## Migration status checklist

Update incrementally when touching a file; add supersession header notes rather than destructive rewrites of frozen/historical content.

| Location | Status | Notes |
|----------|--------|-------|
| `decisions/ADR-0026-platform-model-terminology.md` | ✅ Canonical | Source of truth |
| `docs/platform/era-model.md` | ✅ Updated | References ADR-0026 |
| `docs/platform/runtime-model.md` | ✅ Canonical | Engineering Runtime model |
| `docs/platform/global-state-machine.md` | ✅ Canonical | L2 GSM |
| `docs/platform/behavioral-semantics.md` | ✅ Canonical | BS — why objects collaborate (ADR-0029) |
| `docs/platform/DR-001-constitutional-review.md` | ✅ Approved | Constitutional design review |
| `docs/platform/engineering-traceability-matrix.md` | ✅ v1.1 | Vision → Observability → Tests |
| `docs/platform/terminology-migration.md` | ✅ This doc | Living checklist |
| `decisions/ADR-0023-build-workflow-engine.md` | ✅ Header note | Historical Context preserved |
| `decisions/ADR-0019-builder-memory-boundaries.md` | ✅ Context line | Legacy tagged inline |
| `.cursor/skills/orchestrate-builders/SKILL.md` | ✅ Quick Ref + Architecture | ASEP operator surface terms |
| `knowledge/project/roadmap.md` | ✅ Product Track note; M4 promoted | |
| `knowledge/development/builder-memory.md` | ✅ Terminology header | |
| `docs/superpowers/specs/builder-memory-integration-design.md` | ✅ Scope header | Frozen body/diagrams preserved |
| `docs/superpowers/specs/2026-06-25-thesisos-mb1-workflow-engine-design.md` | 🟡 Partial | Has ADR-0026 supersession note; diagram labels legacy |
| `docs/research/builder-memory-framework-analysis.md` | ⬜ Pending | BuilderOS references remain |
| `knowledge/context/current-state.md` | ✅ Updated | Era II constitution L0–L3 |
| `docs/architecture.md` | ⬜ Pending | Review on next edit |
| `WorkflowRuntime` → `EngineeringRuntime` (code) | ⬜ Pending | `builder_engine/runtime.py`, `cli.py`, tests, `runtime-model.md` refs — do on MB2 branch (ADR-0028) |
| Code comments (`builder_engine/`, `builder_memory/`) | ⬜ Pending | Grep when editing modules |

## Grep hygiene

When editing any doc under `docs/` or `decisions/`:

```bash
rg -n 'Agent OS|BuilderOS|Builder OS' docs/ decisions/
```

Prefer:

1. **Header supersession note** referencing ADR-0026 §9 for frozen specs and ADRs.
2. **High-visibility sections** (Scope, Architecture, Quick Reference) — use official terms.
3. **Preserve** historical Context/Decision prose and frozen diagram labels unless Architect re-freeze.

## Related

- ADR-0023 — Engineering Runtime boundaries (unchanged by terminology)
- ADR-0025 — Packet execution state machine
- `docs/platform/era-model.md` — Era I–IV maturity model
