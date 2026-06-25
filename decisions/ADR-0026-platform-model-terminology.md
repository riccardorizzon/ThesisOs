# ADR-0026: Platform Model & Terminology

> **Amended by ADR-0028 (2026-06-25):** §8 is refined — invariants are **not** a
> category of policy. Invariants are fail-closed laws (see `docs/platform/invariant-model.md`),
> policies are tunable decisions. The state vocabulary (§6) is given an object model
> in `docs/platform/engineering-meta-model.md`.

- Status: Accepted (frozen 2026-06-25)
- Context: Era I closed with M0–M4 (product) and MB1 Phases 1–2 (build execution engine). Documentation still mixes legacy terms ("Agent OS", "BuilderOS") with newer terms ("workflow execution engine", "Era", "Control Plane"). Without a frozen vocabulary, Era II implementations (MB2+) will fork concepts in code and docs. The project is no longer "a system of agents" — it is a platform whose **Engineering Runtime** executes a repeatable engineering cycle under a **Build Control Plane**.
- Decision:

  ### 1. Official name

  **Adaptive Software Engineering Platform (ASEP)** — the entire repository ecosystem: product runtime, build control plane, sidecar engines, contracts, knowledge, and governance.

  Legacy names **Agent OS** and **BuilderOS** are **deprecated** in new documents. They may appear in historical specs with a `(legacy)` note mapping to ASEP terms below.

  ### 2. Planes and runtimes

  | Term | Definition | Lives in (examples) |
  |------|------------|---------------------|
  | **Product Plane** | End-user ThesisOS capabilities at request time | `backend/app/`, `frontend/`, M-series milestones |
  | **Build Control Plane** | Planning, observation, assignment, policy, promotion of engineering work | `plans/builder/`, `decisions/`, `knowledge/`, `orchestrate-builders` skill, future observability/policy modules |
  | **Engineering Runtime** | Deterministic executor of the engineering cycle (see `docs/platform/runtime-model.md`) | `builder_engine/` today; may split into sidecars later |
  | **Execution workers** | Non-deterministic executors invoked by the runtime | Cursor Task agents, human operators, future automated workers |

  **Hard boundary (unchanged from ADR-0023):** Engineering Runtime and Build Control Plane **must not** import `backend.app` or mutate product runtime on behalf of end users.

  ### 3. Tracks

  | Track | Milestone prefix | Purpose | Gate doc pattern |
  |-------|------------------|---------|------------------|
  | **Product Track** | M0–M18 | Ship user-facing ThesisOS capabilities | `docs/m{n}-promotion.md`, tag `m{n}-complete` |
  | **Platform Track** | MB1–MBn | Evolve ASEP control + runtime intelligence | `docs/mb{n}-promotion.md` or phase gate, tag optional |

  Tracks are **orthogonal**. Product specs freeze before platform phases that depend on their semantics (ADR-0025 §6).

  ### 4. Eras

  Eras describe **platform maturity**, not a single milestone. See `docs/platform/era-model.md`.

  | Era | Name | Status (2026-06-25) |
  |-----|------|---------------------|
  | I | Execution Foundation | ✅ Complete |
  | II | Adaptive Workflow Intelligence | 🟡 Constitution frozen; implementation next |
  | III | Autonomous Engineering | ⬜ |
  | IV | Self-Optimizing Platform | ⬜ |

  ### 5. Global capability lifecycle (mandatory)

  Every new capability — Product **or** Platform — MUST follow:

  ```text
  Vision → Spec → ADR (if decision) → Freeze → Implementation → Gate → Promotion
  ```

  "Freeze" means Architect sign-off on the spec/ADR; no implementation of semantics before freeze (ADR-0001, ADR-0010). MB2+ is not exempt.

  ### 6. State vocabulary

  | Term | Scope | Authority |
  |------|-------|-----------|
  | **Project state** | Era, active tracks, promotion status, strategic objectives | Build Control Plane (future unified model; today: `knowledge/` + gate YAML) |
  | **Workflow state** | Epic, wave, packets, locks, blockers | `plans/builder/STATE.yaml` (filesystem) |
  | **Packet execution state** | CREATED→…→DONE machine | ADR-0025; projected in STATE packet `status` |
  | **Product domain state** | GraphState, documents, memory, … | Product Plane services + contracts |

  Do not conflate these layers. MB2 implements **project + workflow** coordination atop the frozen runtime model — not a fourth ad-hoc state.

  ### 7. Event vocabulary (directional)

  Product events: typed catalog + outbox (ADR-0006) — `DocumentUploaded`, `ChunkCreated`, …

  Build events (Era II+): typed, append-only, consumed by Control Plane and Runtime — e.g. `TaskCompleted`, `ValidationFailed`, `MilestoneFrozen`, `MergeAccepted`, `ReviewRejected`. Producers **publish**; consumers **react**. No direct Control Plane → Runtime procedure chains for cross-cutting concerns (see runtime-model §Publish Events).

  ### 8. Policy vocabulary (directional)

  **Policies** are declarative rules (who may do what, under which state). **Invariants** (MB1 §8) are structural graph checks. Era II introduces a **Policy Engine** that evaluates policies after Observe and before Plan; until then, ADRs + `validate_graph` are the policy stand-in.

  ### 9. Supersession map (legacy → official)

  | Legacy | Official |
  |--------|----------|
  | Agent OS | ASEP (context-dependent: whole platform) |
  | BuilderOS | Build Control Plane + Engineering Runtime |
  | builder_engine alone = "the OS" | Engineering Runtime (one component) |
  | M-milestone only roadmap | Product Track within ASEP |
  | MB-milestone only roadmap | Platform Track within ASEP |

- Consequences: One vocabulary for docs, ADRs, specs, and code comments for Era II+. MB2 implementation becomes translation of frozen models, not reinvention. Cost: historical docs must be updated incrementally; grep for "Agent OS" when touching a file.
- Alternatives considered:
  - Continue informal naming — rejected; already causing Agent OS vs execution engine drift.
  - Rename repository — rejected; ASEP is architectural name, not repo rename.
  - Collapse Product and Platform tracks — rejected; conflates user features with factory intelligence.

- References: ADR-0001, ADR-0010, ADR-0023, ADR-0025; `docs/platform/era-model.md`; `docs/platform/runtime-model.md`.
