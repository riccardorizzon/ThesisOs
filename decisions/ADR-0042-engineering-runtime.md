# ADR-0042: Engineering Runtime — Governance / Runtime Split

- **Status:** Accepted (design freeze — 2026-07-05)
- **Plane:** Platform (Build Control Plane + Engineering Runtime)
- **Supersedes:** Nothing — extends ADR-0026, ADR-0023, ADR-0025, ADR-0028
- **Authority chain:** `docs/superpowers/specs/mb2-engineering-runtime-spec.md` (SoR — normative Runtime contract), `docs/platform/runtime-model-v2.md` (L3 dynamics map), `.asep/programs/px-exec.yaml` (delivery program)
- **Context:**

  Era I (Execution Foundation) is **demonstrated**, not documented-only. PX-1 and PX-2
  validated in production the full outer loop:

  ```text
  Program → EWO → Wave → Parallel dispatch → Integration → QWO → Freeze
  ```

  The Engineering Supervisor operates as a **state machine** with explicit `WAIT` —
  it does not proceed without policy clearance. ThesisOS PX-2 is **qualified and frozen**,
  providing a stable product baseline.

  The gap is architectural, not procedural: governance and execution still share an
  **operator surface** (`orchestrate-builders` skill, manual dispatch/merge/sync).
  Era II requires a **Runtime Layer** that executes reactively under Governance —
  not an monolithic "Execution Orchestrator" that absorbs both roles.

  `docs/platform/runtime-model.md` (v1, frozen 2026-06-25) defines the canonical
  10-phase cycle. This ADR freezes the **structural decisions** for v2: two-layer
  platform, event-driven reactions, plugin engines, projection-only observability.

- **Decision:**

  ### 1. Two-layer ASEP Platform

  ```text
  ASEP Platform
  │
  ├── Governance Layer          (what is permitted)
  │     Program, Capability Graph, ADR, Constitution
  │     Engineering Supervisor, QC Certificates, QWO contracts
  │     Auto-approval + termination policies
  │
  └── Runtime Layer             (how work executes)
        Event Bus, Rule Engine, Job Queue
        Scheduler, Dependency Engine
        Plugin Registry (Merge, Integration, Qualification, …)
        State Writer, Projection API
  ```

  **Hard boundary:** Governance **never** dispatches agents, merges worktrees, or
  spawns QWO runs directly. Runtime **never** overrides Constitution, ADR, or QC
  verdicts. Runtime may **escalate** to Supervisor (`WAIT`); Supervisor may
  **delegate** execution scope to Runtime (`APPROVED`).

  ### 2. Event-driven execution (not rigid pipeline)

  Cross-cutting workflow steps are **reactions**, not sequential function calls:

  ```text
  Event → Runtime → Rule Engine → Action (plugin)
  ```

  Examples (declarative rules, not hard-coded order):

  | Event | Rule guard | Action |
  |-------|------------|--------|
  | `EwoCompleted` | all dependencies satisfied | schedule merge |
  | `MergeCompleted` | CI passed | integration review |
  | `IntegrationPassed` | coverage OK | spawn QWO |
  | `QwoPassed` | milestone criteria met | escalate to Supervisor for freeze |

  The 10-phase cycle in `runtime-model.md` remains the **semantic processor**;
  v2 implements it through events and rules, not a single orchestrator class.

  ### 3. Program Graph vs Execution Graph

  | Graph | Source | Mutability |
  |-------|--------|------------|
  | **Program Graph** | `.asep/programs/*.yaml`, `.asep/proposals/*`, capability graph | Governance — human/Architect |
  | **Execution Graph** | Derived from Program Graph + current runtime state | Runtime — recomputed on events |

  Program Graph declares intent (waves, EWO deps, merge order, integration gates).
  Execution Graph is the **ready set + critical path** the Runtime schedules.
  No Runtime action may invent nodes not traceable to Program Graph.

  ### 4. Execution State Model

  Two composed state machines (see `runtime-model-v2.md` §4):

  1. **Supervisor FSM** — `IDLE → OBSERVE → … → WAIT | EXECUTE` (Governance)
  2. **Job FSM** — `CREATED → READY → RUNNING → VALIDATING → MERGED → QUALIFIED` (Runtime)

  EWO instances are **jobs** in the Runtime queue. Supervisor transitions gate
  *authorization*; Job FSM tracks *execution*.

  ### 5. Plugin Architecture

  Runtime engines are **plugins** registered behind stable interfaces:

  ```text
  Runtime Core
    ├── Rule Engine
    ├── Plugin Registry
    └── Scheduler
          ├── SchedulerPlugin
          ├── MergePlugin
          ├── IntegrationPlugin
          ├── QualificationPlugin
          ├── NotificationPlugin
          └── MetricsPlugin
  ```

  Adding a capability (e.g. automatic QWO trigger) registers a plugin + rules —
  **no core modification**. Plugins live in `builder_engine/` sidecars or future
  `engineering_runtime/` packages; **must not** import `backend.app`.

  ### 6. Projection-only observability

  Dashboard, CLI (`builder-engine status`), and reports consume a **derived state
  document** — they do not compute workflow logic.

  ```yaml
  # Example projection — not authoritative source of truth
  wave_b: { status: running }
  qwo: { status: locked }
  ```

  Authoritative state: event log + atomic state writer. Projections are rebuildable.

  ### 7. Agent Provider abstraction (Phase 4 — specified, not implemented)

  Runtime dispatches through `AgentProvider` interface. Cursor Task is the first
  adapter. ASEP MUST NOT hard-code a single vendor in Runtime core.

  ### 8. Delivery binding

  | Artifact | Role |
  |----------|------|
  | `docs/superpowers/specs/mb2-engineering-runtime-spec.md` | **Specification of Record (SoR)** — normative Runtime contract |
  | `docs/platform/runtime-model-v2.md` | L3 dynamics map — Program/Execution Graph, events, projection |
  | `.asep/programs/px-exec.yaml` | Platform Engineering Program — phased delivery |
  | MB2 platform milestone | Implementation gate after SoR freeze |
  | PX-3 | First **product** program designed **after** v2 model exists (may execute before Runtime code) |

  **Implementation freeze:** No Runtime code (event bus wiring, queue, plugins) until
  MB2 SoR is frozen and Reference Implementation traces to SoR §14. PX-EXEC Phase 1
  specification phase is **complete**; implementation follows MB2-Q gate passage.

- **Invariants:**

  - **INV-RT-1:** Runtime MUST NOT import `backend.app` or mutate Product Plane on behalf of end users (ADR-0023).
  - **INV-RT-2:** Governance policies MUST NOT be evaluated inside Runtime plugins — only Runtime rules + L1 invariants.
  - **INV-RT-3:** Every Runtime transition MUST emit a typed event; no silent state mutation.
  - **INV-RT-4:** Observability surfaces MUST be projections — no duplicated decision logic in UI/CLI.
  - **INV-RT-5:** Execution Graph nodes MUST trace to Program Graph declarations.
  - **INV-RT-6:** Supervisor `WAIT` MUST halt autonomous progression until operator or policy clears.

- **Compliance checklist:**

  - [ ] **C1:** New Runtime module lives in sidecar, not `backend/app/`
  - [ ] **C2:** Event type added to catalog before handler registered
  - [ ] **C3:** Plugin implements interface from registry — no ad-hoc imports in core
  - [ ] **C4:** Dashboard/CLI reads projection path only
  - [ ] **C5:** MB2 implementation spec traces each feature to v2 model section

- **Violation examples:**

  - Runtime auto-merges without `MergeCompleted` event + rule match → INV-RT-3
  - Dashboard computes ready-set independently of Runtime → INV-RT-4
  - Scheduler spawns EWO not in Program Graph → INV-RT-5
  - Runtime skips Supervisor on QWO failure → INV-RT-6

- **Consequences:**

  - **Positive:** ASEP becomes a reusable engineering platform; ThesisOS is the first validated consumer, not the only possible one.
  - **Positive:** PX-3+ product programs can declare Runtime-aware wave/integration contracts before code exists.
  - **Cost:** Short-term manual operator surface remains until MB2 Phase 1 ships.
  - **Cost:** Two policy domains (Governance vs Runtime rules) require clear documentation — see v2 model §5.

- **References:**

  - ADR-0026 Platform Model & Terminology
  - ADR-0023 Build Workflow Engine
  - ADR-0025 Builder Execution State Machine
  - ADR-0028 Engineering Meta-Model
  - ADR-0006 Event-Driven Architecture
  - `docs/platform/era-model.md` — Era II target
  - `docs/platform/runtime-model.md` — v1 cycle (still valid semantics)
  - `docs/superpowers/specs/mb2-engineering-runtime-spec.md` — MB2 SoR
  - `docs/platform/runtime-model-v2.md` — v2 structural model
  - `.asep/programs/px-exec.yaml`
  - `.asep/governance/engineering-supervisor.md`
  - `builder_engine/` — Era I partial Runtime
