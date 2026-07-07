# Architect Authorization — PX-6 Polish

Program: thesisos-product-v2  
Milestone: **PX-6 — Polish**  
Role: engineering  
Status: **AUTHORIZED** (milestone)  
Authorized EWO: **NONE** — backlog pending  
Pre-flight: **PASS**  
Operator command: `ASEP: AUTHORIZE PX-6`  
Timestamp: 2026-07-07

---

## Resolution

```text
intent: authorize
program: PX-6 (thesisos-product-v2)
role: engineering
```

Architect authorization **supersedes** `excluded_until_gate_3_amendment` on capability
`px-6-polish` and `milestones_planned_blocked: [PX-6]`. Milestone PX-6 is authorized
for **planning and proposal work** only until the first executable EWO is registered.

**Develop pipeline: STOP** — no executable EWO in program backlog.

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Program graph | ✓ `.asep/programs/thesisos-product-v2.yaml` |
| PX-5 promoted | ✓ `px5-complete` — certificate `.asep/certificates/PX5-PROMOTION-20260707.yaml` |
| QWO-PX5-001 | ✓ PASS — `.asep/reports/QWO-PX5-001.md` |
| PX5-INTEGRATION-E | ✓ PASS — `.asep/reports/PX5-INTEGRATION-E.md` |
| Prior milestone `depends_on` | ✓ PX-5 complete / promoted |
| `make ci` | ✓ green @ `81b92d9d` |
| Repository | ✓ clean on `main` |
| Execution authorization | ✓ waived by explicit `AUTHORIZE PX-6` |
| Product spec (PX-6) | ✗ not drafted |
| Wave backlog | ✗ none |
| EWO proposals | ✗ none (`.asep/proposals/PX6-EWO-*.md`) |
| `px6_workorder_backlog` | ✗ not registered in program yaml |
| First executable EWO | ✗ **none** |

**Pre-flight verdict: PASS** (milestone authorization)  
**Develop gate: STOP** (no executable EWO)

---

## PX-6 scope (from product baseline)

Per `docs/product/specs/thesisos-product-ux-v1.md` §10 and deferred items across
PX-2…PX-5 specs:

| Capability | Source |
|------------|--------|
| Citation validator (W-06 mitigation) | px2 §29, px3 §24, product §12 |
| Export / print (bibliography) | px5 §15, px3 §24 |
| Multi-project switch | px2 §8, px5 §15 |
| Performance polish | product §10 |
| Settings depth | product §10 |
| Typography polish (custom fonts) | `design-system/thesisos/MASTER.md` |
| Outline drag reorder | px2 §12 |

---

## Scope boundary

**Authorized now:**

- Draft PX-6 product spec (`docs/product/specs/px6-polish-experience-v1.md`)
- Draft UI spec (`design-system/thesisos/px6-polish-experience-ui-spec.md`)
- Define Wave A backlog (`.asep/reports/PX6-WAVE-A-BACKLOG.md`)
- File first EWO proposal (`PX6-EWO-001`)

**NOT authorized:**

- Product code changes (no EWO selected)
- MB2 runtime / SoR / Constitution edits
- px-exec Runtime Engineering
- Product v2.0 completion / final QWO until PX-6 EWOs complete

---

## WO-TRACE

```text
PX-5 PROMOTED (px5-complete) @ 2026-07-07
  → AUTHORIZE PX-6 (milestone)
  → STOP — spawn PX6-WAVE-A-BACKLOG + PX6-EWO-001 proposal
  → Re-AUTHORIZE or ASEP: develop PX6-EWO-001 when registered
```

---

## Recommended next action

1. Draft **PX6-WAVE-A-BACKLOG.md** following PX-5 Wave A pattern.
2. Ratify **px6-polish-experience-v1.md** product spec (Wave A / PX6-EWO-001).
3. Register `px6_workorder_backlog` in `.asep/programs/thesisos-product-v2.yaml`.
4. Resume with `ASEP: develop PX6-EWO-001` or `AUTHORIZE PX-6 EWO-001`.
