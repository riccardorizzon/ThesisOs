# ThesisOS v1.0 Operational — Release Notes

**Release:** `thesisos-v1.0-operational`  
**Date:** 2026-07-01  
**WorkOrder:** E.1 Release Baseline  
**Program:** thesis-agent migration (`kimi-claw-2026-06`)

---

## Summary

ThesisOS v1.0 Operational is a **qualified framework for managing an academic thesis
project** — not a generic chat agent. Knowledge, governance, writing, memory, and
integration have been validated through governed Qualification WorkOrders (OR-1…OR-7)
and a continuous End-to-End session (D.1).

**Migration status:** Kimi Claw export → ThesisOS knowledge base → runtime promotion →
operational qualification **complete**.

---

## What this release is

An **operational specialized framework** characterized by:

- Separation of knowledge, governance, and execution
- Explicit decision lifecycle (Frozen vs open)
- Governed persistent memory (MEMORY UPDATE PROPOSAL; State Atomicity)
- Capability qualification via dedicated QWOs
- Methodological distinction: **Capability Failure vs Platform Limitation**

---

## Qualification matrix

| Gate | Capability | Verdict | Report |
|------|------------|---------|--------|
| OR-1 | Thesis structure | PASS | C.1-R2 |
| OR-2 | STIGMATA framework | PASS | C.2-R2 |
| OR-3 | Corpus utilization | PASS | C.3-R4 |
| OR-4 | Constraint compliance | PASS | C.4-R1 |
| OR-5 | Decision lifecycle | PASS | C.5-R1 |
| OR-6 | Academic production | **PASS\*** | C.6-R3 |
| OR-7 | Memory runtime integrity | PASS | C.7-R1 |
| D.1 | E2E integration | PASS | D.1-E2E |

---

## Known limitation (documented, not hidden)

**W-06 — Platform Limitation:** autore-date citations may not appear on every LLM
generation despite full inference enforcement. OR-6 remains **qualified (PASS\*)**.

See: `docs/KNOWN_LIMITATIONS.md`

---

## Engineering artifacts (EWO)

Runtime alignment delivered via EWO-1…EWO-4A, EWO-7B (production path), EWO-7C
(inference enforcement). Full trace in `.asep/capabilities/thesis-agent-migration.yaml`.

---

## Post-baseline policy

After this freeze:

- No capability, oracle, or governance changes without new WorkOrder + operator auth.
- Known limitations changes require new baseline or explicit engineering program amendment.

---

## Getting started

Operational usage: `docs/thesisos-operational-runbook.md`

Stack: `make up` → `http://localhost:8000` → `/chat` with promoted knowledge.

---

## WO-TRACE

```text
OR-1..OR-7 qualified → D.1 E2E PASS → E.1 freeze → ThesisOS v1.0 Operational
```
