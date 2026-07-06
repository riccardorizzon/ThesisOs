# MB2 — Engineering Runtime Promotion

**Branch:** `main` · **Promotion baseline:** `dbf5243`  
**Spec:** `docs/superpowers/specs/mb2-engineering-runtime-spec.md` (SoR frozen 2026-07-05)  
**ADR:** ADR-0042 (Engineering Runtime)  
**Program:** `.asep/programs/px-exec.yaml`

## Summary

MB2 closes the **SoR-based Engineering Runtime Reference Implementation** for Era II
Adaptive Workflow Intelligence. The milestone delivers:

- Phase 1 (PX-EXEC-P1): event bus, rule engine, dependency engine, job queue, scheduler, projection
- Phase 2 (PX-EXEC-P2): merge, integration, and qualification plugins
- Qualification gates MB2-Q1…Q6 PASS with documented certificates
- §13.3 golden path replay PASS — live plugin chain evidenced against PX-2 parallel manual audit trail

This promotion is distinct from the prior **Era I MB2 slice** (D1–D10) documented in
`docs/mb2-phase-gate.md` (2026-06-28). That gate closed the Build Control Plane operator
loop; this gate closes the **normative SoR qualification package** per §13.

## Capability map (frozen baselines)

| Capability | Phase | EWO | Evidence |
|------------|-------|-----|----------|
| Event Model & Bus | P1 | EWO-001 | `PX-EXEC-EWO-001-event-model.md` |
| Rule Engine | P1 | EWO-002 | `MB2-Q2-RULE-ENGINE-20260706.md` |
| Dependency Engine | P1 | EWO-003 | `MB2-Q1-RUNTIME-GRAPH-20260706.md` |
| Job Queue | P1 | EWO-004 | `PX-EXEC-EWO-004-job-queue.md` |
| Scheduler | P1 | EWO-005 | `MB2-Q3-SCHEDULER-20260706.md` |
| State Projection | P1 | EWO-006 | `MB2-Q5-PROJECTION-20260706.md` |
| Merge Plugin | P2 | EWO-007 | `PX-EXEC-EWO-007-merge-plugin.md` |
| Integration Plugin | P2 | EWO-008 | `PX-EXEC-EWO-008-integration-plugin.md` |
| Qualification Plugin | P2 | EWO-009 | `PX-EXEC-EWO-009-qualification-plugin.md` |

## Qualification gates (SoR §13.2)

| Gate | Certificate | Verdict |
|------|-------------|---------|
| MB2-Q1 Runtime Graph | `MB2-Q1-20260706.yaml` | PASS |
| MB2-Q2 Rule Engine | `MB2-Q2-20260706.yaml` | PASS |
| MB2-Q3 Scheduler | `MB2-Q3-20260706.yaml` | PASS |
| MB2-Q4 Plugin Registry | `MB2-Q4-20260706.yaml` | PASS |
| MB2-Q5 Projection | `MB2-Q5-20260706.yaml` | PASS |
| MB2-Q6 Recovery | `MB2-Q6-20260706.yaml` | PASS |
| §13.3 Golden Path | `MB2-GOLDEN-PATH-20260706.yaml` | PASS |

## Promotion gates

```yaml
sor_frozen: green                    # MB2-SOR-20260705.yaml
mb2_q1: green
mb2_q2: green
mb2_q3: green
mb2_q4: green
mb2_q5: green
mb2_q6: green
golden_path_13_3: green            # MB2-GOLDEN-PATH-20260706.yaml
phase_1_ewos: green                # EWO-001…006
phase_2_ewos: green                # EWO-007…009
unit_builder_engine: green         # 190 passed @ dbf5243
make_ci: green
unit_m4_recovery: green            # C6 — M4 unchanged
scope_creep: false
documentation: complete
knowledge_updated: true
mb2_complete_tag: pending          # tag withheld — explicit go-ahead required
```

## §13.3 golden path evidence

Reference program: `.asep/programs/px2-parallel.yaml`

```text
wave_a → integration_a → wave_b → integration_b → wave_c → integration_c
  → wave_d → QWO-PX2-001 → qualified
```

Replay orchestrator: `builder_engine/golden_path.py`  
Audit report: `.asep/reports/MB2-GOLDEN-PATH-REPLAY-AUDIT-20260706.md`

## Tag procedure (final step)

All promotion gates are green. Tag withheld for explicit Architect go-ahead:

```bash
git tag -a mb2-complete -m "MB2 Engineering Runtime — SoR qualified + §13.3 PASS" dbf5243
```

## What MB2 explicitly did NOT close

- PX-EXEC-P3 observability (dashboard, metrics, notification plugins)
- PX-EXEC-P4 provider abstraction (AgentProvider, multi-program, full recovery EWO)
- Live git merge subprocess in Runtime (external integrator manifest pattern)
- Live QWO subprocess evidence collection (fixture stub — extension point documented)
- PX-4 product program

Phase 3+ capabilities remain `blocked` / `not_authorized` in `.asep/programs/px-exec.yaml`.

## Operator loop

```bash
builder-engine observe --repo-root .
builder-engine policy --repo-root .
builder-engine plan --repo-root .
make unit-builder-engine
```

## Related documents

| Doc | Role |
|-----|------|
| `docs/mb2-phase-gate.md` | Era I D1–D10 slice (2026-06-28) — superseded for SoR promotion scope |
| `.asep/reports/MB2-PROMOTION-REVIEW-20260706.md` | Pre-§13.3 readiness review |
| `.asep/reports/MB2-PROMOTION-EXECUTION-20260706.md` | Promotion execution report |
