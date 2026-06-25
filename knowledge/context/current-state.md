# Current State

> Snapshot as of **2026-06-25**. Branch: `main`.

## Where are we?

**Constitution complete. Architect sign-off recorded. MB2 rebase is next. No code yet.**

```text
Engineering Constitution   L0 + L1 + BS + L2 + L3   ✅ frozen, signed
DR-001 + ETM v1.1          ✅ Architect approved
L2.1 micro-patch           ✅ applied
Next                       MB2 spec rebase → sign-off → L4
```

## Constitution stack (ADR-0029)

```text
L0  Meta Model           who exists
L1  Invariants            laws
BS  Behavioral Semantics  why objects collaborate
L2  Global State Machine  valid transitions (L2.1)
L3  Runtime Cycle         when transitions run
```

**Center of gravity:** rules + state + semantics — not agents. Workers implement behaviors.

## Authorized pipeline

```text
✅ GSM → DR-001 → ETM → L2.1 → Behavioral Semantics → Architect sign-off
🔴 MB2 rebase (ETM §3 — total traceability)
🔴 Architect sign-off rebased MB2
⏸️ L4 implementation (blocked until rebased MB2 sign-off)
```

## What is next?

1. **Rebase MB2 spec** — every deliverable fills ETM columns (Vision → … → Tests)
2. **Architect sign-off** on rebased MB2
3. **L4** per `plans/l2-global-state-machine-plan.md`

Product M5 remains orthogonal (Critic §12 pending).

See `context/next-actions.md`.
