# Stop Report Template

> **Mandatory** when the Engineering Supervisor enters **WAIT** state.
> Path: `.asep/reports/stop-<YYYYMMDD-HHMMSS>.md` or `stop-<trigger-id>-<WorkOrder>.md`

---

## Example

```markdown
# Stop Report

**Date:** 2026-06-30T15:00:00Z  
**Supervisor State:** WAIT  
**Automation Level:** 2  
**Session:** ASEP continua — thesis-agent-migration

---

## Reason

Human approval required for new QWO proposal (first C.n on capability).

## Termination Rule

T2 — Human gate (new OR-4 proposal)

## Current Capability

| Field | Value |
|-------|-------|
| **Capability** | `or-4-rules` |
| **Lifecycle** | `specified` |
| **Status** | `planned` |

## Last Completed WorkOrder

| Field | Value |
|-------|-------|
| **WorkOrder** | C.3-R2 |
| **Type** | QWO |
| **Verdict** | PASS |
| **Report** | `.asep/reports/C.3-R2.md` |

## QC Certificate (last valid)

`.asep/certificates/C.3-R2-20260630.yaml` — PASS

## Evidence

- `or-3-corpus` → **qualified**
- OR-4 blocked until C.4 proposal approved

## Recommended Action

Review and approve `.asep/proposals/C.4-or-4-constraint-compliance.md`, or reply `C.4: approved`.

## Next Eligible WorkOrder

C.4 proposal → C.4-R1 QWO (after human approval)

## WO-TRACE

```text
C.3-R2 PASS → or-3 qualified → STOP (T2: new proposal gate)
```
```

---

## Required fields

| Field | Description |
|-------|-------------|
| **Reason** | Plain-language why Supervisor halted |
| **Termination Rule** | T1…T12, T-oscillation, T-no-progress, T2 human gate, … |
| **Current Capability** | Graph node + lifecycle + status |
| **Last Completed WO** | Last successful or attempted WorkOrder |
| **QC Certificate** | Path to certificate used before STOP (if any) |
| **Recommended Action** | What operator should do |
| **Next Eligible WorkOrder** | First WO after human clears STOP |

On **WAIT**, write Stop Report per `.asep/governance/stop-report-template.md` →
`.asep/reports/stop-<timestamp>.md` before ending session.
