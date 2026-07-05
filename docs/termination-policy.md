# Termination Policy

> **Binding:** Engineering Supervisor must halt autonomous loops when any rule below
> applies — even if auto-approval policy would otherwise allow continuation.
>
> Related: `docs/auto-approval-policy.md`, `.asep/governance/engineering-supervisor.md`

---

## Principle

Autonomous engineering requires **two** stop mechanisms:

1. **Authorization stops** — human gate, QC certificate FAIL, policy STOP triggers  
2. **Progress stops** — the loop no longer advances the program usefully  

A Supervisor that only knows when to proceed is unsafe. It must know **when to stop
because progress has stalled**.

---

## Mandatory STOP (immediate halt)

| # | Trigger | Detection |
|---|---------|-----------|
| T1 | **QC Certificate FAIL** | `checks.verdict: FAIL` on certificate |
| T2 | **Human gate** | Open STOP awaiting operator; explicit `STOP` / `hold` |
| T3 | **New decision required** | Proposal scope adds Decisions.md row or M2 policy |
| T4 | **New capability** | Graph node or WorkOrder outside current program |
| T5 | **Invariant violation** | Constitution, ADR, Runtime Contract, layer rules |
| T6 | **Runtime inconsistent** | `/health` fail; promotion audit regression; index corrupt |
| T7 | **Ground Truth drift** | Hash mismatch vs certificate; uncommitted GT edit |
| T8 | **Coverage regression** | Runtime or Qualification Coverage **decreases** vs prior certified snapshot without documented cause |
| T9 | **Pending EWO** | Capability graph or reports show EWO approved but not `implemented` |
| T10 | **Open STOP record** | `.asep/reports/` or graph `blocked_by` / `status: blocked` unresolved |
| T11 | **QWO disposition open** | PARTIAL/FAIL report without operator acceptance / spawn resolution |
| T12 | **Release / irreversible action** | E.1, baseline freeze, destructive git |

On any T* → Supervisor → **WAIT** (human) or **IDLE**; do not EXECUTE next WorkOrder.

---

## Progress stops (No Progress Detection)

### Oscillation pattern

Detect the loop:

```text
QWO → PARTIAL → EWO → QWO → PARTIAL → EWO → …
```

**Rule:** If the **same capability** completes **≥ 2** consecutive QWO runs with
**PARTIAL** or **FAIL** without an intervening EWO marked `implemented`, → **STOP**
(T-oscillation).

**Rule:** If **≥ 3** consecutive WorkOrders on the same capability produce no lifecycle
advance (`qualified`, `implemented`, or accepted Outer Loop resolution), → **STOP**
(T-stall).

### Coverage stall

If after an implemented EWO the next QWO **Qualification Coverage** is not strictly
greater than the prior QWO on the same capability (and verdict ≠ PASS), → **STOP**
(T-coverage-stall) — alignment may be insufficient or wrong diagnosis.

### Runtime Coverage regression

If **Runtime Coverage** drops between EWO `implemented` and subsequent pre-flight without
a documented rollback EWO, → **STOP** (T8).

---

## Iteration limits (session guards)

Default limits for autonomous sessions (Level 2/3). Operator may tighten; loosening
requires explicit `ASEP: autonomous extended`.

| Guard | Default | Action |
|-------|---------|--------|
| **Max iterations** | 12 WorkOrders per session | STOP (T-max-iter) |
| **Max QWO per capability** | 4 runs (`R1`…`R4`) without PASS | STOP — propose human review |
| **Max EWO chain depth** | 3 EWOs per capability without re-QWO PASS | STOP |
| **Wall clock** | 4 hours autonomous | STOP — report partial progress |
| **No progress window** | Last **N = 3** iterations: no lifecycle advance, no coverage increase | STOP (T-no-progress) |

**Lifecycle advance** counts as: `implemented`, `qualified`, operator **ACCEPTED** on
PARTIAL, or capability `status` change from `blocked` → `ready`.

---

## Supervisor behavior on termination

```text
Detect termination trigger
        ↓
Supervisor → WAIT
        ↓
Write Termination Report (append to session report or .asep/reports/termination-<date>.md)
        ↓
Surface Human Review card:
  - trigger id (T1…T12, T-oscillation, …)
  - evidence (reports, coverage deltas, certificate)
  - recommended operator action
        ↓
Do NOT auto-spawn next WorkOrder
```

---

## Certificate and hash binding

Termination checks use the **QC Certificate** snapshot:

- `repository_hash` — git HEAD at certificate time  
- `ground_truth_hash` — checksum of frozen GT paths (see QC checklist § G)  

If HEAD or GT hash changed since certificate issuance without a new certificate →
**STOP** (T7) before EXECUTE.

---

## Operator resume

After human resolution:

1. Operator clears STOP (acceptance, approval, scope fix)  
2. New **QC Certificate** required before next auto-approved EXECUTE  
3. Supervisor → OBSERVE (fresh iteration)

Explicit operator command (`C.n-Rk: approved`) may resume Level 1; Level 2/3 still
require valid certificate unless operator forces Level 1 for session.

---

## Related artifacts

| Path | Role |
|------|------|
| `docs/auto-approval-policy.md` | Authorization stops |
| `.asep/governance/quality-controller.md` | Certificate issuance |
| `.asep/governance/engineering-supervisor.md` | State machine + termination hooks |
| `.asep/governance/qc-certificate-template.md` | Certificate format |
