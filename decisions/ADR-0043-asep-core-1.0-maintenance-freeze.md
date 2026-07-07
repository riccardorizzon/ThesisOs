# ADR-0043: ASEP Core 1.0 — Maintenance Freeze

- **Status:** Accepted
- **Date:** 2026-07-07
- **Plane:** Platform (Governance — Build Control Plane)
- **Supersedes:** Nothing — crystallizes operating mode from `knowledge/context/next-actions.md`
- **Context:**

  After MB1/MB2 Era I delivery, PX program execution (PX-1…PX-3), architecture review,
  and introduction of `docs/platform-justification.md` plus the classification registry,
  the governance stack reached **sufficient completeness** for daily product engineering.

  Continued ASEP expansion without product dogfood risks a **framework-first loop**:
  governance improves while ThesisOS waits.

  ASEP Core must be distinguished from **PX-EXEC R&D** (Engineering Runtime reference
  implementation), which remains **unproven** at operational scale.

- **Decision:**

  ### 1. Declare ASEP Core 1.0 COMPLETE

  Release: `docs/asep-1.0-release.md`

  ASEP Core 1.0 includes: CI gates, isolation, drift, qualification/STOP discipline,
  platform justification contract, classification registry with CI validation, and
  maintained `builder_engine/` Era I sidecar.

  ### 2. Enter maintenance mode

  ASEP Core changes allowed only for:

  - break/fix (CI, isolation, registry integrity)
  - minimal fix for a **reproducible product milestone block** (all three conditions
    in `next-actions.md` operating mode)
  - explicit Architect authorization

  ### 3. PX-EXEC is R&D — not Core

  `.asep/programs/px-exec.yaml` track status: **R&D frozen** until promotion criteria
  in `docs/asep-1.0-release.md` § PX-EXEC are met.

  No PX-EXEC EWO-002+ without Architect act citing satisfied promotion criterion.

  ### 4. Product runtime exclusion

  Product plane (`backend/app/`, `frontend/`) must **not** read ASEP classification
  registry or depend on governance metadata at runtime. Governance stays above execution.

- **Consequences:**

  - Primary progress metric → ThesisOS user-perceivable capability + dogfood evidence
  - New platform investment requires `platform-justification.md` hypothesis + exit id
  - Routine EWO reports de-emphasized; CI + PR evidence preferred
  - Operator may tag `asep-core-1.0` when checklist in release doc is complete

- **Alternatives considered:**

  - Continue PX-EXEC implementation — rejected until promotion criteria met
  - Declare full MB2/platform “complete” — rejected; only **governance** frozen at 1.0
  - Leave operating mode provisional — rejected; trial period ended with explicit contract
