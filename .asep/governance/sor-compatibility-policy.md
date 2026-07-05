# SoR Compatibility Policy

> **Governance policy** — not part of the Runtime SoR. Governs how
> `docs/superpowers/specs/mb2-engineering-runtime-spec.md` may evolve after
> Specification Freeze.

| Policy | Path |
|--------|------|
| SoR (normative) | `docs/superpowers/specs/mb2-engineering-runtime-spec.md` |
| Specification freeze | `.asep/certificates/MB2-SOR-20260705.yaml` |
| ADR | `decisions/ADR-0042-engineering-runtime.md` |

---

## Versioning

- SoR amendments increment **document revision date** and update §14 traceability.
- **Compatible** changes: existing Reference Implementation and Programs continue without migration.
- **Breaking** changes: require new SoR major revision + typically new ADR + re-qualification (MB2-Q*).

Programs declare `runtime_contract.sor_revision` at authorization. A Runtime implementation
declares supported `sor_revision` range in its Qualification Package.

---

## Compatibility matrix

| Change | Backward compatible | Requires ADR | Requires re-qualification |
|--------|---------------------|--------------|---------------------------|
| New optional plugin | Yes | No | Plugin-specific tests only |
| New optional rule guard | Yes | No | MB2-Q-004 if semantics change |
| New projection field (additive) | Yes | No | MB2-Q-015 update |
| New event type (optional handlers) | Usually | Maybe | MB2-Q2 + catalog tests |
| New required event field | No | Yes | MB2-Q2 full |
| New Job FSM state or transition | No | Yes | MB2-Q1, MB2-Q6 |
| Invariant change (INV-R-*) | No | Yes | Full MB2-Q1…Q6 |
| Governance / Runtime boundary change | No | Yes | Full MB2-Q + Supervisor review |
| Plugin API breaking change | No | Maybe | MB2-Q4 + affected plugins |
| Program Graph schema breaking change | No | Yes | PX program amendment |

**Rule of thumb:** If a conformant Reference Implementation from revision *N* could fail
revision *N+1* without code change, the change is **breaking**.

---

## When to amend SoR vs ADR

| Situation | Action |
|-----------|--------|
| Clarification, no semantic change | SoR errata — same revision, traceability note |
| New optional capability | SoR amendment — no ADR if invariants unchanged |
| New invariant or boundary | **New ADR** + SoR amendment |
| Supersede entire Runtime model | New ADR + new SoR major + Architect sign-off |

---

## Program compatibility

A Program authorized against SoR revision **2026-07-05** MAY run on Reference
Implementation supporting that revision or any **backward-compatible** later revision.

If SoR breaking change is required, either:

1. Migrate Program Graph to new schema (new EWO/amendment), or
2. Pin Program to prior SoR revision until migration completes.

PX-3 is the first program under this policy.
