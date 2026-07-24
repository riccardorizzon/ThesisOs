# ThesisOS End-to-End Remediation Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute all approved ThesisOS E2E remediations in dependency order and requalify the product without modifying the active thesis.

**Architecture:** Five independently gated waves remove API collisions, restore data integrity, harden academic workflows, polish UX, and perform protected cleanup/requalification. A wave may start only after the prior wave’s focused gate passes.

**Tech Stack:** FastAPI, PostgreSQL/pgvector, Next.js 15, React 19, Vitest, pytest, Docker Compose, Playwright, Vertex AI.

## Global Constraints

- Source design: `docs/superpowers/specs/2026-07-24-thesisos-e2e-remediation-design.md`.
- `thesis-agent` is protected and read-only during destructive tests and cleanup.
- No authentication change.
- Product Plane only; no Engineering Runtime or governance changes.
- TDD red→green→refactor for every production behavior.
- Do not create commits unless explicitly requested.

---

### Task 1: Execute Wave 1 — API and streaming

**Files:**
- Plan: `docs/superpowers/plans/2026-07-24-thesisos-remediation-wave1-api-streaming.md`

**Interfaces:**
- Produces a stable browser `/api` boundary and defensive SSE client used by later waves.

- [ ] **Step 1: Execute every Wave 1 checkbox in order**

Use the exact tests and commands in the Wave 1 plan.

- [ ] **Step 2: Require Wave 1 gate**

Chat reaches `/api/chat`, Writing has no JSON parse banner, and unit/build/browser boundary tests pass.

### Task 2: Execute Wave 2 — data lifecycle

**Files:**
- Plan: `docs/superpowers/plans/2026-07-24-thesisos-remediation-wave2-data-lifecycle.md`

**Interfaces:**
- Consumes the `/api` boundary.
- Produces project/chapter/demo/conversation lifecycle contracts used by cleanup.

- [ ] **Step 1: Execute every Wave 2 checkbox in order**

- [ ] **Step 2: Require Wave 2 gate**

Title regressions, demo idempotency, protected project deletion, conversation lifecycle, isolation, and frontend tests pass.

### Task 3: Execute Wave 3 — academic workflows

**Files:**
- Plan: `docs/superpowers/plans/2026-07-24-thesisos-remediation-wave3-academic-workflows.md`

**Interfaces:**
- Consumes scoped API and lifecycle contracts.
- Produces citation linkage, source promotion, Knowledge Notes, and upload preflight.

- [ ] **Step 1: Execute every Wave 3 checkbox in order**

- [ ] **Step 2: Require Wave 3 gate**

Academic unit/integration tests and ephemeral-project Playwright journey pass.

### Task 4: Execute Wave 4 — UX polish

**Files:**
- Plan: `docs/superpowers/plans/2026-07-24-thesisos-remediation-wave4-ux-polish.md`

**Interfaces:**
- Consumes prior product contracts without changing them.

- [ ] **Step 1: Execute every Wave 4 checkbox in order**

- [ ] **Step 2: Require Wave 4 gate**

Frontend tests/build and UX Playwright checks pass with no technical error copy.

### Task 5: Execute Wave 5 — cleanup and qualification

**Files:**
- Plan: `docs/superpowers/plans/2026-07-24-thesisos-remediation-wave5-cleanup-qualification.md`

**Interfaces:**
- Consumes tested project deletion and demo reset.
- Produces backup, protected snapshots, E2E evidence, and final audit.

- [ ] **Step 1: Execute every Wave 5 checkbox in order**

- [ ] **Step 2: Require final completion evidence**

`make ci`, all Playwright tests, human red-team journey, protected snapshot equality, exact cleanup verification, and goal completion audit all pass.

## Execution rule

Stop immediately on:

- any failing gate;
- any unexpected mutation of `thesis-agent`;
- any protected snapshot mismatch;
- any cross-project result;
- any uncertain cleanup target.

Fix the failing wave, rerun its focused gate, then continue. Never skip ahead to cleanup.
