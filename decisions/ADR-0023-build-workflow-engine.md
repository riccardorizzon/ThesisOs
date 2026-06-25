# ADR-0023: Build Workflow Engine

- Status: Accepted (2026-06-25)
- **Terminology (ADR-0026):** Legacy *Agent OS* / *BuilderOS* in this ADR denote **ASEP** platform components — **Build Control Plane** (planning, observation, policy) + **Engineering Runtime** (`builder_engine/`). See ADR-0026 §9 supersession map. Historical wording below is preserved.
- Context: The build-time Agent OS (BuilderOS) — the Cursor-agent system that *builds* ThesisOS — encodes its **Workflow Engine** and **Scheduler** as prose that an LLM orchestrator follows by hand (`.cursor/skills/orchestrate-builders/SKILL.md`). The only deterministic orchestration code today is `scripts/validate-state.sh` (it checks `file_locks` overlap and that `in_progress`/`done` packets have `done` dependencies — nothing else) plus the `builder_memory/` retrieval sidecar (ADR-0019). The core control decisions — ready-set detection (SKILL §2A), `file_locks` assignment (§2B), wave advancement (§3E), `git merge` (§3C), and execution of packet `required_checks` (§3D) — are all manual LLM steps. There is **no CI test gate**: `infra/ci/cloudbuild.yaml` only builds images and deploys to Cloud Run; no `.github/workflows/`, no pre-commit, no Makefile. The result is non-deterministic and non-repeatable orchestration: the live M1 `plans/builder/STATE.yaml` closed at `wave: 1` although its packets spanned waves 1–3, ran sequentially instead of in parallel worktrees, and left every packet's `checks: []` empty. The "System Architecture Evolution — Adaptive Workflow-Driven Agent OS" brief (2026-06-25) directs us to prefer workflow over prompting, determinism over randomness, state over conversation memory, and to make validation mandatory — while evolving incrementally, reusing the existing implementation, and preserving backward compatibility. A reverse-engineering pass found that ~80% of the brief's target architecture already exists as artifacts; the missing piece is a deterministic engine that *owns the control decisions* the skill currently describes in prose.
- Decision:
  1. **Introduce a deterministic Build Workflow Engine** as a sibling Python sidecar `builder_engine/`, mirroring the install and CLI pattern of `builder_memory/` (editable pip package, `builder` console script, Typer CLI). The engine becomes the deterministic owner of build-orchestration *decisions*: graph validation, ready-set computation, ownership/lock assignment, wave advancement, validation-check execution, and Definition-of-Done enforcement. The orchestrator LLM stops *computing* these and instead *executes the engine's plan*. The one genuinely agentic step — fanning out Cursor Task agents to write code in parallel — remains LLM-driven.
  2. **Filesystem stays authoritative (extends ADR-0019).** The engine *reads* `plans/builder/STATE.yaml`, `plans/builder/packets/*.yaml`, frozen specs, ADRs, and promotion-gate YAML; it *derives* views (ready set, critical path, unified project state) and *validates* invariants; it **never** becomes the source of truth. The existing STATE/packet YAML schema is unchanged, so the current `orchestrate-builders` flow keeps working untouched. Any engine-local scratch state lives in gitignored `.builder-engine/` (run logs only); git history remains the audit log.
  3. **Validation is mandatory and deterministic.** A single runner exposes named stages (`lint`, `format`, `typecheck`, `unit`, `integration`, `drift`, `scope`, `infra`) built from the commands that already exist (`ruff`, `pytest`, `vitest`, `tsc --noEmit`, `next build`, schema drift test, the `NotImplementedError` scope-creep grep, `terraform validate`). No packet may transition to `done`, and no worktree may merge, unless its `required_checks` pass. CI gains a **test stage before deploy**; a pre-commit hook runs the fast stages.
  4. **Runtime isolation (extends ADR-0002, ADR-0019).** `builder_engine/` must not import `backend.app` and must not share tables or services with the ThesisOS runtime (system A). No deployed runtime code path calls the engine. The engine is build-time only.
  5. **Allowed / forbidden operations:**

```yaml
read:
  - plans/builder/STATE.yaml
  - plans/builder/packets/
  - docs/superpowers/specs/
  - decisions/
  - contracts/
  - docs/m*-promotion.md
derive: yes          # ready set, critical path, project-state view (computed, not stored as truth)
validate: yes        # graph invariants, ownership, DoD, gate YAML
write_state: yes     # atomic edits to plans/builder/STATE.yaml status/locks/wave fields ONLY
run_checks: yes      # execute required_checks / validation stages
manage_worktrees: yes
```

```yaml
edit_specs: false        # frozen specs change only via Architect re-freeze
edit_adr: false          # decisions/ change only via explicit Architect action
edit_contracts: false    # contracts/ change require Architect + ADR
generate_code: false     # builders (Cursor Task agents) write code, not the engine
source_of_truth: false   # filesystem + git win on any conflict
runtime_integration: false  # no hooks into /chat, ConversationService, GraphState, MemoryService
become_source_of_truth_db: false  # no DB-backed authoritative state
```

  6. **Governance & scope.** The engine evolves through the same milestone / ADR / freeze discipline as the rest of the system. It is tracked as build-track milestone **MB1** (the first milestone of the **MB-series** = build-time Agent OS milestones, orthogonal to the M-series product milestones M0–M18) with its own frozen design spec at `docs/superpowers/specs/2026-06-25-thesisos-mb1-workflow-engine-design.md`.
  7. **Backward-compatible, phased adoption.** The engine is additive at every step. It rolls out as five independently shippable phases — Phase 0 (deterministic validation pipeline), Phase 1 (graph read-model), Phase 2 (scheduler + sync), Phase 3 (unified project state), Phase 4 (adaptive replanning + debug/governance automation). After each phase the prose `orchestrate-builders` flow still works; the skill is updated to *cite engine commands* rather than re-derive decisions.
- Consequences: Build orchestration becomes repeatable, auditable, and parallel-safe. The "intelligence" moves out of the orchestrator prompt and into the workflow, exactly as the brief intends ("the workflow is the system; the LLMs are execution tools"). Validation can no longer be silently skipped. The cost is maintaining a second build-time sidecar and porting `validate-state.sh` logic into it. Primary risks: (a) **engine/skill divergence** — mitigated by making the skill cite engine commands as the single deterministic authority and adding a check that the skill's documented commands exist; (b) **over-engineering** — mitigated by YAGNI, the same minimalism that kept Builder Memory BM25-only, and strictly phased delivery; (c) **scope creep into the runtime** — mitigated by the runtime-isolation lint (no `backend.app` import) reused from ADR-0019.
- Alternatives considered:
  (a) **Keep prose-only and improve prompts** — rejected: the brief explicitly chooses determinism over prompting, and the prose flow already fails silently (M1 empty `checks`, wave counter wrong).
  (b) **Adopt an external workflow engine** (Temporal, Airflow, Prefect, Dagster, or LangGraph-for-builds) — rejected: heavyweight runtime, wrong abstraction for a single-user filesystem-first build loop, couples the build process to deployed infrastructure, and contradicts the reuse/incremental-evolution mandate (YAGNI).
  (c) **Fold the engine into `builder_memory/`** — rejected: violates single responsibility (memory is *retrieval*; the engine is *control*) and would muddy ADR-0019's clean cache-only boundary.
  (d) **Rewrite orchestration from scratch** — rejected: the brief mandates incremental evolution, maximum reuse, and backward compatibility.
  (e) **Make the engine the source of truth via a database** — rejected: ADR-0019 establishes filesystem authority and git as the audit log; a DB-backed authoritative build state would duplicate and contend with that.
