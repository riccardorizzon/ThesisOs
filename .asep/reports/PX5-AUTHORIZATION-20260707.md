# Architect Authorization — PX-5 Research (Wave B)

Program: thesisos-product-v2  
Milestone: PX-5 — Research  
Role: engineering  
Status: **AUTHORIZED**  
Authorized EWO: **PX5-EWO-002**  
Pre-flight: **PASS**  
Operator command: `AUTHORIZE PX-5 when PX-3 conformance gate satisfied`  
Timestamp: 2026-07-07

---

## PX-3 conformance gate

| Gate | Result |
|------|--------|
| MB2-CONFORMANCE-ASSESSMENT | ✓ PASS |
| Architect ratification | ✓ `.asep/reports/PX3-ARCHITECT-RATIFICATION-MB2-CONFORMANCE-ASSESSMENT-20260705.md` |
| Completion certificate | ✓ `.asep/certificates/PX3-CONFORMANCE-COMPLETE-20260706.yaml` |
| Program graph PX-3 status | ✓ `complete` |
| N-class blockers | ✓ 0 |

**Gate verdict: SATISFIED** — PX-5 authorization unblocked.

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| Program graph | ✓ `.asep/programs/thesisos-product-v2.yaml` |
| PX-4 promoted | ✓ `px4-complete` @ `d5206a0f` |
| PX5-EWO-001 (Wave A spec) | ✓ PASS |
| Product spec | ✓ `docs/product/specs/px5-research-experience-v1.md` |
| UI spec | ✓ `design-system/thesisos/px5-research-experience-ui-spec.md` |
| Wave A backlog | ✓ `.asep/reports/PX5-WAVE-A-BACKLOG.md` |
| Proposal PX5-EWO-002 | ✓ `.asep/proposals/PX5-EWO-002-research-hub-scaffolding.md` |
| `make ci` | ✓ green @ `d5206a0f` |
| Repository | ✓ dirty governance sync (waived by explicit AUTHORIZE) |
| First executable EWO | ✓ PX5-EWO-002 |

---

## Scope boundary

Wave B entry — **Research hub + route scaffolding** only. Does **not** authorize:

- Full canvas viewport / node layer (PX5-EWO-003+)
- Discovery API or saved views persistence
- MB2 runtime / SoR / Constitution modifications
- px-exec Runtime Engineering
- PX-6 Polish

---

## Authorized EWO

| Field | Value |
|-------|-------|
| **Id** | PX5-EWO-002 |
| **Title** | Research hub + route scaffolding |
| **Category** | Infrastructure |
| **Layer** | Business (Product Plane) |
| **Proposal** | `.asep/proposals/PX5-EWO-002-research-hub-scaffolding.md` |
| **Depends on** | PX5-EWO-001 PASS |

### Deliverables (in scope)

- `/research` hub with canvas + guided mode cards
- `/research/canvas` route stub wired
- `/research/guided` stub (PX-3.10 placeholder)
- `/research/[conceptId]` redirect → `/research/canvas?focus=`
- `ModuleStub` replaced on research routes
- Route registry + tests updated

---

## WO-TRACE

```text
PX-3 COMPLETE (conformance gate) → PX-4 PROMOTED
  → PX5-EWO-001 PASS (Wave A spec)
  → AUTHORIZE PX-5 Wave B → PX5-EWO-002 (authorized)
  → Canvas implementation (PX5-EWO-003+ — future wave)
```

---

## Recommended next action

Execute **PX5-EWO-002**, then spawn Wave C backlog (canvas viewport + node layer).
