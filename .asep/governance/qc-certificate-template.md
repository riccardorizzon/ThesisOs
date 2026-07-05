# QC Certificate Template

> The Quality Controller **does not decide**. It runs checks and emits this certificate.
> The **Engineering Supervisor** reads the certificate and applies
> `docs/auto-approval-policy.md`. Termination rules: `docs/termination-policy.md`.

Store issued certificates at: `.asep/certificates/<WorkOrder-id>-<timestamp>.yaml`

---

## Example (YAML)

```yaml
# QC Certificate — do not edit after issuance; re-run QC for new certificate
certificate_version: "1.0"
issued_at: "2026-06-30T14:22:00Z"
issued_by: quality-controller
checklist: .asep/governance/quality-controller.md

proposal:
  workorder_id: C.3-R2
  workorder_type: QWO
  capability: or-3-corpus
  proposal_path: .asep/proposals/C.3-or-3-corpus.md
  proposal_status: approved

repository:
  head: "abc123def4567890"
  branch: "main"
  working_tree: clean

ground_truth:
  hash: "sha256:…"   # frozen paths per QC § G
  unchanged: true
  paths:
    - knowledge/thesis-agent/03_PROJECT/Bibliography-Master.md
    - knowledge/thesis-agent/03_PROJECT/Core-Theory-Map.md
    - knowledge/thesis-agent/03_PROJECT/Decisions.md

checks:
  verdict: PASS          # PASS | FAIL — factual only; not authorization
  passed: 18
  failed: 0
  skipped: 2
  blockers: []

readiness:
  capability_lifecycle: approved
  pending_ewo: none      # REQUIRED: none for QWO auto-auth
  open_stop: none        # REQUIRED: none for any auto-auth
  prior_ewo_implemented: EWO-3
  qwo_disposition_resolved: true   # C.3-R1 ACCEPTED

policy_evaluation:
  automation_level: 2
  auto_approval_eligible: yes   # Supervisor/policy fills after reading certificate + policy
  auto_approval_reason: "QWO re-run; proposal approved; EWO-3 implemented; no open STOP"

runtime:
  health: ok
  runtime_coverage: "~100%"

termination:
  iteration_count_session: 7
  no_progress_streak: 0
  oscillation_detected: false
```

---

## Example (human-readable header for reports)

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QC CERTIFICATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Proposal:        C.3-R2 (QWO · or-3-corpus)
Repository:      abc123d @ main (clean)
Ground Truth:    sha256:… (unchanged)
QC Checks:       PASS (18/18 applicable)
Pending EWO:     none
Open STOP:       none
Policy Level:    2
Auto-Eligible:   YES (Supervisor confirmed)
Certificate:     .asep/certificates/C.3-R2-20260630.yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Fields the QC must populate (factual)

| Field | QC sets | Supervisor interprets |
|-------|---------|------------------------|
| `checks.verdict` | PASS / FAIL | FAIL → STOP (T1) |
| `ground_truth.unchanged` | true / false | false → STOP (T7) |
| `readiness.pending_ewo` | id or `none` | not `none` → STOP (T9) |
| `readiness.open_stop` | id or `none` | not `none` → STOP (T10) |
| `policy_evaluation.auto_approval_eligible` | **optional hint** | Supervisor + policy decide |

QC may suggest `auto_approval_eligible: yes` when checks pass, but **authorization**
is never issued by QC alone.

---

## Invalidation

Certificate invalid if:

- `repository.head` ≠ current HEAD  
- `ground_truth.hash` ≠ current GT hash  
- Any check marked stale (proposal edited after issuance)  
- More than 24h elapsed without operator resume (configurable — re-run QC)

Supervisor must request **new certificate** before EXECUTE.
