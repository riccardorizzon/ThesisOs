# Engineering Supervisor

> **Orchestrator state machine — does not implement.** The Supervisor is the Project
> Manager of an Engineering Program. Builder agents execute; the Supervisor transitions
> through **states**, reads **QC Certificates** (does not re-run checks), applies
> **Auto Approval Policy** and **Termination Policy**, and spawns WorkOrders.

| Policy | Path |
|--------|------|
| Auto-approval | `docs/auto-approval-policy.md` |
| Termination | `docs/termination-policy.md` |
| QC (certificate issuer) | `.asep/governance/quality-controller.md` |
| Certificate format | `.asep/governance/qc-certificate-template.md` |

---

## Platform position

```text
ASEP
  ↓
Engineering Supervisor    ← this document
  ↓
Quality Controller        (certificate only)
  ↓
Engineering Program
  ↓
Engineering State Machine
  ↓
Capability Graph
  ↓
WorkOrders (EWO / QWO)
  ↓
Runtime
  ↓
Product (e.g. ThesisOS)
```

The Supervisor is **program-agnostic** — same state machine governs migration track,
Runtime Platform milestones, or future document-engineering programs.

---

## State machine

```text
                    ┌──────────┐
                    │   IDLE   │
                    └────┬─────┘
                         │ start / resume
                         ▼
                    ┌──────────┐
              ┌────│ OBSERVE  │◄────────────────┐
              │    └────┬─────┘                 │
              │         │                       │
              │         ▼                       │
              │    ┌──────────┐                 │
              │    │   PLAN   │                 │
              │    └────┬─────┘                 │
              │         │                       │
              │         ▼                       │
              │    ┌──────────┐  invoke QC     │
              │    │    QC    │  (read cert)   │
              │    └────┬─────┘                 │
              │         │                       │
         STOP │    ┌────┴─────┐                 │
              │    │          │                 │
              │  FAIL       PASS + policy       │
              │    │          │                 │
              │    ▼          ▼                 │
              │ ┌──────────┐ ┌──────────┐     │
              │ │   WAIT   │ │ EXECUTE  │     │
              │ └────┬─────┘ └────┬─────┘     │
              │      │            │           │
              │      │            ▼           │
              │      │       ┌──────────┐    │
              │      │       │  VERIFY  │    │
              │      │       └────┬─────┘    │
              │      │            │         │
              │      │            ▼         │
              │      │       ┌──────────┐    │
              │      │       │  REPORT  │    │
              │      │       └────┬─────┘    │
              │      │            │         │
              │      │     termination?      │
              │      │            │         │
              │      └────────────┼─────────┘
              │                   │
              └───────────────────┘
                         (next iteration)
```

### State definitions

| State | Action | Exit |
|-------|--------|------|
| **IDLE** | No active session | Operator `ASEP: continua` → OBSERVE |
| **OBSERVE** | Read HEAD, graph, reports, certificates, `/health` | → PLAN or WAIT (termination) |
| **PLAN** | Select next WorkOrder; verify proposal exists | → QC |
| **QC** | **Read** QC Certificate (request issuance if missing/stale); **do not re-run checks** | → EXECUTE or WAIT |
| **EXECUTE** | Delegate to builder (EWO script / QWO run) | → VERIFY |
| **VERIFY** | Coherence audit, coverage delta, lifecycle rules | → REPORT |
| **REPORT** | Write `.asep/reports/*`, update graph, append WO-TRACE | → OBSERVE or WAIT |
| **WAIT** | Human Review; session halted | Operator clears → OBSERVE |

---

## QC state (critical)

In **QC** state the Supervisor:

1. Checks certificate exists for current `repository.head` + proposal id  
2. If missing/stale → **invoke QC agent once** to issue certificate  
3. **Reads** `checks.verdict`, `readiness.pending_ewo`, `readiness.open_stop`  
4. Applies `auto-approval-policy.md` + `termination-policy.md`  
5. Transitions to EXECUTE or WAIT  

The Supervisor **never** duplicates the checklist. Disagreement with certificate → WAIT
(human), not silent re-check.

---

## Decision table

| Situation | Next state |
|-----------|------------|
| Certificate FAIL | WAIT (T1) |
| `pending_ewo` ≠ none | WAIT (T9) |
| `open_stop` ≠ none | WAIT (T10) |
| QWO + proposal not approved | WAIT |
| Termination policy trigger | WAIT |
| Certificate PASS + policy match | EXECUTE |
| Operator explicit approval | EXECUTE (Level 1 override) |
| QWO → PARTIAL | REPORT → WAIT (human acceptance) |
| QWO → PASS | REPORT → OBSERVE (lifecycle update) |
| Session max iterations | WAIT (T-max-iter) |
| Oscillation detected | WAIT (T-oscillation) |

---

## Termination hooks (in OBSERVE and REPORT)

Before leaving REPORT → OBSERVE, evaluate `docs/termination-policy.md`:

- Coverage regression (T8)  
- No progress streak (T-no-progress)  
- QWO/EWO oscillation (T-oscillation)  
- Max iterations (T-max-iter)  

If triggered → **WAIT** with termination report; do not PLAN next WorkOrder.

---

## Responsibilities

| Does | Does not |
|------|----------|
| Transition state machine | Write application code |
| Read QC certificates | Re-run QC checklist |
| Apply policy + termination | Issue QC certificates |
| Spawn executors | Auto-accept PARTIAL |
| Detect no-progress loops | Override certificate FAIL |

---

## Status block

```text
Supervisor State: IDLE | OBSERVE | PLAN | QC | EXECUTE | VERIFY | REPORT | WAIT
Certificate: <path> | missing | stale
Certificate Verdict: PASS | FAIL | —
Policy Level: 1 | 2 | 3
Auto-Authorized: yes | no
Termination: none | T<n> — <reason>
Next WorkOrder: <id> | none (halted)
Human Required: yes | no
```

---

## ASEP skill mapping

`.cursor/skills/asep/SKILL.md` may implement Supervisor states on `ASEP: continua`:

- **Supervisor pass** (`readonly: true`) — OBSERVE → PLAN → QC → authorize  
- **Executor pass** — EXECUTE → VERIFY → REPORT  

Long autonomous sessions: enforce termination policy every REPORT transition.
