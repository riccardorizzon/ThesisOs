# Quality Controller (QC)

> **Certificate issuer only — does not decide.** The QC runs read-only checks and emits
> a **QC Certificate**. It does **not** authorize execution, advance lifecycle, or
> apply auto-approval policy.
>
> **Supervisor** reads the certificate and decides (with policy).  
> **Policy:** `docs/auto-approval-policy.md`  
> **Certificate format:** `.asep/governance/qc-certificate-template.md`

---

## Role boundary

| QC does | QC does not |
|---------|-------------|
| Run checklist | Spawn WorkOrders |
| Record PASS/FAIL per check | Auto-approve |
| Capture repository + GT hashes | Override termination policy |
| Emit certificate artifact | Accept QWO PARTIAL |
| Flag `pending_ewo`, `open_stop` | Implement EWO/QWO |

Think **CI pipeline job**: produces attestation; merge gate is elsewhere.

---

## Issuance flow

```text
Supervisor → PLAN (selects WorkOrder)
        ↓
QC runs checklist (read-only)
        ↓
QC writes certificate → .asep/certificates/<id>-<ts>.yaml
        ↓
Supervisor reads certificate (QC state — no re-run of checks)
        ↓
Supervisor + Policy → PROCEED | STOP
```

---

## Checklist (run in order)

### A — Platform invariants (when WO touches `backend/`, `frontend/`, `builder_engine/`)

| # | Check | Source |
|---|-------|--------|
| A1 | No Constitution C1–C8 violation in proposed scope | `docs/runtime-constitution.md` |
| A2 | Layer declared if touching `backend/app/` | ADR-0030 §4 |
| A3 | No Business-layer forbidden imports in proposed diff | ADR-0030 §2 |
| A4 | Runtime Contract extension points respected | `docs/runtime-contract.md` |
| A5 | ADC checklist applicable items addressed | `docs/architecture-decision-checklist.md` |

Skip A* for migration-track-only WOs that touch only runtime promotion via HTTP scripts.

### B — Engineering Program

| # | Check | Source |
|---|-------|--------|
| B1 | WorkOrder type declared (EWO \| QWO) | Proposal header |
| B2 | EWO category declared (Alignment, Promotion, …) | Proposal |
| B3 | Capability node exists in graph | `.asep/capabilities/*.yaml` |
| B4 | Prerequisites satisfied (`depends_on`, prior EWO implemented) | Capability graph |
| B5 | QWO: no mutation constraint stated and enforceable | Qualification Contract |
| B6 | Spawn rule: EWO only after FAIL/PARTIAL report | Prior `.asep/reports/C.*.md` |
| B7 | **No pending EWO** on capability chain | Graph lifecycle ≠ `implemented` for blocking EWO |
| B8 | **No open STOP** | `blocked_by`, unresolved PARTIAL/FAIL disposition |

### C — Ground Truth immutability

| # | Check | Method |
|---|-------|--------|
| C1 | Proposal commits to **no GT edit** | Scope section |
| C2 | WO script/proposal does not write `03_PROJECT/` masters | Static review |
| C3 | No new rows in `Decisions.md` | Diff / scope |
| C4 | No thesis chapter content edits | Scope |

### D — Decision log coherence

| # | Check | Source |
|---|-------|--------|
| D1 | CORPUS / METH / UNI / REL decisions unchanged | `Decisions.md` |
| D2 | M2 memory PATCH (if any) is structural alignment only | EWO scope |
| D3 | No new methodological decision | Proposal out-of-scope |

### E — Pre-flight (live stack WOs)

| # | Check | Source |
|---|-------|--------|
| E1 | `/health` OK | HTTP pre-flight |
| E2 | Prior report exists for spawn chain | `.asep/reports/` |
| E3 | Run id convention respected | Proposal |

### F — QWO-specific (when `workorder_type: QWO`)

| # | Check | Requirement |
|---|-------|-------------|
| F1 | **Proposal status = approved** | Proposal header or operator record |
| F2 | **Capability lifecycle ≥ approved** | Graph (not `draft` / bare `specified` without approval) |
| F3 | **Ground Truth unchanged** | Hash match vs last certified baseline |
| F4 | **No pending EWO** | B7 |
| F5 | **No open STOP** | B8 |
| F6 | Checks B1–E3 **PASS** | Composite |

All F* must pass for QWO certificate to show `readiness.qwo_auto_auth_ready: true`.

### G — Ground Truth hash (certificate binding)

Compute `sha256` over concatenated frozen files (or use repo `checksums` if present):

- `knowledge/thesis-agent/03_PROJECT/Bibliography-Master.md`
- `knowledge/thesis-agent/03_PROJECT/Core-Theory-Map.md`
- `knowledge/thesis-agent/03_PROJECT/Decisions.md`
- Plus capability-specific masters listed in proposal Ground Truth table

Record in certificate `ground_truth.hash`.

---

## Certificate verdict

| `checks.verdict` | Meaning |
|------------------|---------|
| **PASS** | All applicable checks passed |
| **FAIL** | One or more blockers — list in `checks.blockers[]` |

Certificate **never** contains `authorized: true`. Use `policy_evaluation.auto_approval_eligible`
as optional **hint** only; Supervisor confirms against policy + termination policy.

---

## On FAIL

Write certificate with `verdict: FAIL` and blockers. Supervisor → STOP (T1). Do not execute.

---

## Storage

```text
.asep/certificates/<WorkOrder-id>-<YYYYMMDD-HHMMSS>.yaml
```

Reference certificate path in WorkOrder report header. Do not overwrite; re-run QC for new certificate.
