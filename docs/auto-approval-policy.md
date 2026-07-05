# Auto Approval Policy

> **Alias:** `AutoApprovalPolicy.md`  
> **Binding:** `docs/engineering-program.md` § Automation levels  
> **Default mode for this repo:** **Level 2 — Conditional auto-approval** (recommended)

Human-governed engineering does not require a human at every keystroke. It requires a
human at every **irreversible or high-risk decision**. This policy defines when an
agent may proceed without explicit operator approval, and when it must **STOP**.

---

## Principle

```text
Automate the process.
Do not automate accountability.
```

**Approval (`approved`)** is a control gate, not a technical step. Removing it entirely
converts ASEP from human-governed engineering into an autonomous agent. This policy
preserves governance while allowing long autonomous runs on low-risk, repetitive work.

---

## Three automation levels

| Level | Name | Human gate | Use when |
|-------|------|------------|----------|
| **1** | Auto-loop with human gate | Every proposal + every Outer Loop verdict | Maximum caution; new programs |
| **2** | Conditional auto-approval | **Policy + QC**; human only on STOP triggers | **Recommended default** |
| **3** | Autonomous Engineering Program | QC PASS → auto-approve; human on QC FAIL | Mature program, stable invariants |

This repository operates at **Level 2** unless the operator explicitly selects Level 1
or Level 3 for a session.

---

## Level 2 — Conditional auto-approval (recommended)

```text
Engineering Proposal
        ↓
Quality Controller → QC Certificate (attestation only)
        ↓
Engineering Supervisor reads certificate
        ↓
Auto Approval Policy + Termination Policy
        ↓
   ┌────┴────┐
   │         │
 eligible   STOP → WAIT → Human Review
   ↓
Execute → Validate → Report
   ↓
Next WorkOrder (loop) — unless Termination Policy halts
```

### Auto-approve IF (all must hold)

```text
WorkOrder category ∈ { Alignment, Promotion, Runtime sync }
AND proposal scope matches an existing capability node
AND no new Decisions.md entries
AND no Ground Truth content edits (03_PROJECT masters, Decisions, frozen rules)
AND no Constitution / ADR / Runtime Contract changes
AND no architectural or layer-boundary change (ADR-0030)
AND no new capability node in capability graph
AND no new EWO category or template pattern
AND spawn rule satisfied (QWO FAIL/PARTIAL → EWO only with prior report evidence)
```

### Auto-approve — operation matrix

| Operation | Auto (L2) | Notes |
|-----------|-----------|-------|
| **Alignment EWO** execute | ✅ | EWO-1/2/3 pattern: GT → runtime surfaces only |
| **Promotion** ingest (scripted) | ✅ | Idempotent promotion scripts; log + report |
| **Runtime sync** / coherence audit | ✅ | Verify-only + smoke retrieval |
| **QWO execution** (run test) | ✅ *conditional* | See **QWO auto-authorization** below — all clauses required |
| **Report** generation | ✅ | `.asep/reports/*`, log updates |
| **Lifecycle update** from verdict | ✅ | Only when verdict is unambiguous **PASS** or EWO **implemented** |
| **Capability Coverage** snapshot | ✅ | Observability; does not replace QWO verdict |
| **Pre-flight audit** | ✅ | Repository → Runtime → Coverage |
| **re-QWO** after implemented EWO | ✅ *conditional* | Same as QWO auto-authorization |

### QWO execution — auto-authorization (Level 2)

QWO **run** is auto-authorizable **only if all** hold (certificate must attest each):

```text
Proposal status = approved
AND capability lifecycle ≥ approved (already specified and proposal-approved)
AND Ground Truth unchanged (hash match on certificate)
AND QC Certificate checks.verdict = PASS
AND readiness.pending_ewo = none
AND readiness.open_stop = none
AND no unresolved QWO PARTIAL/FAIL disposition on same capability
AND termination policy allows continuation (no oscillation / max-iter / coverage regression)
```

If **any** pending EWO or open STOP exists on the capability chain → **Supervisor WAIT**
— no automatic QWO, even if other checks pass.

**QWO disposition** (accept PARTIAL, override FAIL) remains **human** — never auto.

### STOP — human required (never auto-approve)

| Trigger | Why |
|---------|-----|
| **New capability** or graph node | Scope expansion |
| **New decision** in `Decisions.md` or M2 memory | Domain policy change |
| **Ground Truth edit** | Frozen blueprint change |
| **Constitution / ADR / Runtime Contract** edit | Platform invariant change |
| **Architectural change** | Layer, event model, new subsystem |
| **New template or WO pattern** | Process change |
| **QWO PARTIAL / FAIL disposition** | Outer Loop — accept/reject/spawn EWO |
| **New program** or completion criteria change | META / roadmap |
| **Release baseline (E.1)** | Irreversible freeze |
| **QC Certificate FAIL** | Any invariant check red — Supervisor WAIT (T1) |
| **Pending EWO** | T9 — no QWO auto-auth until EWO `implemented` |
| **Open STOP** | T10 — blocked capability, unresolved disposition |

**QWO discipline:** running a QWO may be auto-authorized under **QWO auto-authorization**
above; **accepting** PARTIAL, overriding FAIL, or non-standard EWO scope always requires
the operator.

---

## Termination Policy

Autonomous loops must halt when progress stalls or guards fire — even if auto-approval
would allow the next step. See `docs/termination-policy.md` (oscillation detection,
max iterations, coverage regression, no-progress window).

---

## Quality Controller — certificate, not decision

The QC **issues a QC Certificate** (`.asep/governance/qc-certificate-template.md`). It
does **not** authorize work. The **Supervisor** reads the certificate and applies this
policy — same separation as CI attestation vs merge gate.

---

## Engineering Supervisor — state machine

The Supervisor implements the state machine in `.asep/governance/engineering-supervisor.md`:

```text
IDLE → OBSERVE → PLAN → QC → EXECUTE → VERIFY → REPORT → (OBSERVE | WAIT)
```

In **QC** state it **reads** the certificate; it does not re-run checks.

---

## Engineering Platform hierarchy

```text
ASEP
  ↓
Engineering Supervisor
  ↓
Quality Controller (certificate)
  ↓
Engineering Program
  ↓
Engineering State Machine
  ↓
Capability Graph
  ↓
WorkOrders
  ↓
Runtime
  ↓
Product under evolution (e.g. ThesisOS)
```

This stack is **program-agnostic** — reusable beyond the thesis-agent migration track.

## Level 3 — Autonomous Engineering Program

Opt-in continuous Supervisor loop (`ASEP: autonomous`). Same certificate + termination
rules as Level 2; difference is Supervisor auto-transitions OBSERVE → … without waiting
for operator text when certificate + policy allow.

On certificate FAIL or termination trigger → **WAIT** + Stop Report.  
Level 3 does **not** bypass human gates on disposition, GT, or architecture.

---

## Audit trail (mandatory for auto-approval)

Every auto-approved action must leave:

| Artifact | Content |
|----------|---------|
| Proposal | Scope + category + preconditions |
| **QC Certificate** | `.asep/certificates/<id>-<ts>.yaml` |
| Policy match | Which rule authorized auto-approve (Supervisor record) |
| Report | Verdict, coverage, WO-TRACE |
| Capability graph | Lifecycle + `qualification_runs[]` |

Auto-approval **never** skips reports or overwrites prior run history.

---

## Migration track — worked examples

| WorkOrder | Auto-approve execute? | Human still required? |
|-----------|----------------------|------------------------|
| EWO-1/2/3 Alignment | ✅ (after QWO gap evidenced) | No — if scope matches policy |
| C.n-Rk QWO run | ✅ *if QWO auto-authorization clauses + certificate* | No — if EWO pending / STOP open |
| C.n-Rk PARTIAL → accept | ❌ | **Yes** — Outer Loop |
| C.n-Rk PASS → `qualified` | ✅ lifecycle update | No |
| C.n-R2 after EWO implemented | ✅ *if no pending EWO / open STOP* | No |
| EWO-4 new scope (normalization Mythologies OCR) | ❌ | **Yes** — new scope decision |
| OR-4 proposal first time | ❌ | **Yes** — new QWO proposal |
| E.1 release | ❌ | **Yes** |

---

## Operator overrides

| Command | Effect |
|---------|--------|
| Explicit `EWO-n: approved` / `C.n-Rk: approved` | Human approval; bypasses auto-approval need |
| `STOP` / `hold` | Force Level 1 for session |
| `ASEP: autonomous` | Opt into Level 3 (QC still required) |
| Decline auto-approve in UI | Revert to Level 1 for that WorkOrder |

Explicit human approval always wins over policy.

---

## Related artifacts

| Path | Role |
|------|------|
| `docs/engineering-program.md` | Program rules, WO types, coverage |
| `.asep/governance/quality-controller.md` | QC checklist (certificate issuer) |
| `.asep/governance/qc-certificate-template.md` | Certificate format |
| `.asep/governance/engineering-supervisor.md` | Supervisor state machine |
| `docs/termination-policy.md` | Mandatory halt + no-progress detection |
| `.asep/proposals/` | Proposals awaiting or recording approval |
| `.asep/reports/` | Evidence + WO-TRACE |
