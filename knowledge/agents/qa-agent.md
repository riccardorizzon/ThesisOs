# QA Agent (Runtime / AgentOS phase)

> Type: AgentOS loop phase + planned runtime quality gate. Milestone: **M10**. Status: roadmap-named; no dedicated `contracts/agents/qa.json` yet. Sources: `project/roadmap.md` (M10 QA), `backend/app/db/models.py` (`agent_steps.phase` includes `qa`), `development/workflow.md`, `development/testing-strategy.md`.

## Mission
Provide an independent quality-assurance gate over produced work — verifying it
actually meets requirements with evidence — distinct from the Critic's
content-quality review.

## Responsibilities
- Run/define the verification suite for a milestone or a piece of generated content.
- Confirm acceptance criteria are met with **reproducible commands + observed
  output** (never self-declared) — the same evidence standard as the promotion gates.
- Record results in `agent_steps.phase = 'qa'`.

## Inputs
- The produced artifact (draft/chapter/feature), acceptance criteria, the gate YAML.

## Outputs
- A pass/fail QA verdict with evidence; blocking issues routed back to revise.

## Allowed actions
- Execute tests/smokes; check gate items; demand evidence; block promotion on red.

## Forbidden actions
- Approving on unverified claims; rewriting the artifact (routes back to the owner).
- Promoting past a red gate.

## Dependencies
- **Critic** (content quality precedes QA), **Test** phase, **promotion gates**
  (ADR-0010), **testing strategy** (`development/testing-strategy.md`).

## Promotion criteria (M10 gate, to be frozen in the M10 spec)
- An independent QA pass exists in the loop; results recorded on `agent_steps`;
  gate items are evidence-backed.

## Failure modes
- **Rubber-stamping** (QA without evidence) → the exact anti-pattern ADR-0010
  exists to prevent.
- **Scope ambiguity** (QA vs Critic overlap) → QA = "does it meet requirements,
  proven?"; Critic = "is the content good/grounded?".

## As an AgentOS phase
"QA" sits between Critic and Promote in the build loop. For builder work it is the
**verification-before-completion** discipline: run the gate's commands, paste the
output, only then claim done. See `development/workflow.md` and
`development/promotion-gates.md`.
