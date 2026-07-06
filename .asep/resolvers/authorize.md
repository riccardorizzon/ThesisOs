# Architect Authorization Resolver

The **Architect API** — a stable, high-level operator surface. One command replaces
long briefing prompts. History lives in rules and docs; the first message is an
**authorization**, not a recap.

**Future:** Engineering Runtime will execute this resolver automatically. Today the
ASEP skill and agent interpret it. The interface does not change — only the executor.

---

## Command syntax

All forms are equivalent (case-insensitive):

```text
AUTHORIZE PX-3
AUTHORIZE PROGRAM PX-3
ASEP: AUTHORIZE PX-3
# ARCHITECT AUTHORIZATION … Program: PX-3 …   (structured block — same intent)
```

Optional milestone alias map:

| Token | Program | Graph |
|-------|---------|-------|
| `PX-1` … `PX-6` | `.asep/programs/thesisos-product-v2.yaml` | `.asep/capabilities/thesisos-product-v2.yaml` |
| `thesis-agent`, `OR`, `E2E` | `.asep/programs/thesis-agent-migration.yaml` | `.asep/capabilities/thesis-agent-migration.yaml` |
| `runtime-platform`, `M5` | plans + `.asep/capabilities/runtime-platform.yaml` | runtime track |

Emit before proceeding:

```text
intent: authorize
program: PX-3 (thesisos-product-v2)
role: conformance | engineering
```

---

## Resolution pipeline

```text
1. Parse program token
2. Load Program Graph + Capability Graph
3. Pre-flight validation          → STOP on fail
4. Select first executable EWO    → STOP if none
5. Record authorization receipt   → .asep/reports/<PROGRAM>-AUTHORIZATION-<date>.md
6. Enter develop pipeline         → work-order → execute → qualify → report
7. Conformance programs only      → enable px3-conformance-program rule; log I/S/A/N
```

**Never auto-authorize** a blocked milestone without this command. An `AUTHORIZE`
message from the operator **is** explicit Architect authorization — it supersedes
`excluded_until_gate_3_amendment` and similar program-level blocks.

---

## Pre-flight validation (mandatory)

Run before selecting an EWO. On any ✗ → STOP with Stop Report; do not implement.

### All programs

| Check | Verification |
|-------|--------------|
| Platform contract | Proposal includes `platform_contract` YAML per `.asep/templates/platform-contract-block.md`; B/C must cite `hypothesis_id`, `success_metric`, `exit_id` from `docs/platform-justification.md` |
| Program exists | `.asep/programs/*.yaml` loads; milestone defined |
| Prior milestone | Every `depends_on` milestone is `complete` / `qualified` / `frozen` |
| Repository | `git status` clean (or operator waived); branch identified |
| Regression baseline | `make ci` green on HEAD *(or document blocker in STOP)* |
| Live stack | `/health` → 200 when product EWO requires it |

### Conformance programs (`program_role: conformance`)

Additional checks — PX-3 is the reference instance:

| Check | Verification |
|-------|--------------|
| SoR frozen | `.asep/certificates/MB2-SOR-20260705.yaml` exists |
| SoR revision | Program `runtime_contract.sor_revision` matches SoR header |
| Compatibility policy | `.asep/governance/sor-compatibility-policy.md` loaded |
| Engineering Runtime | **NOT authorized** — no `builder_engine/` MB2 implementation |
| Conformance log | `.asep/reports/PX3-CONFORMANCE-LOG.md` exists or create header |
| Product-only scope | Allowed paths per program `constraints.allowed_paths` |

### Engineering programs (PX-1, PX-2 pattern)

| Check | Verification |
|-------|--------------|
| Execution authorization | `docs/product/EXECUTION-AUTHORIZATION*.md` covers milestone, **or** this `AUTHORIZE` command |
| Architect Program Review | Required review doc PASS when program yaml references it |
| Parallel program | Load `px*-parallel.yaml` + dispatch doc when EWO has `wave` |

Emit summary:

```text
Pre-flight: PASS | STOP
  ✓ PX-2 frozen @ 2026-07-05
  ✓ SoR revision 2026-07-05
  ✓ make ci green
  ✗ /health unreachable → STOP
```

---

## Select first executable EWO

From program `workorder_backlog`:

1. Filter: `milestone` matches authorized program token
2. Filter: `status` ∉ `{implemented, qualified, cancelled}`
3. Sort: dependency order (`depends_on` satisfied first)
4. Pick first node whose every `depends_on` EWO is `implemented` or `qualified`
5. Load matching `.asep/proposals/<EWO-id>-*.md`

If backlog empty or all blocked → STOP: *"No executable EWO — spawn proposals first."*

For PX-3 at program start: if backlog is registered, select first EWO with satisfied
dependencies (typically `PX3-EWO-001`). If backlog empty → STOP with recommended action:
draft Wave A from `.asep/reports/PX3-WAVE-A-BACKLOG.md`.

---

## Authorization receipt

Write `.asep/reports/<PROGRAM>-AUTHORIZATION-<YYYYMMDD>.md`:

```text
# Architect Authorization — <PROGRAM>

Program: <id>
Milestone: <PX-n>
Role: engineering | conformance
Status: AUTHORIZED
Authorized EWO: <first EWO id> (or NONE — backlog pending)
Pre-flight: PASS | STOP
SoR revision: <if conformance>
Operator command: <verbatim>
Timestamp: <ISO date>
```

Do **not** edit Governance, SoR, or program yaml lifecycle fields unless the
operator explicitly requests a state sync after PASS pre-flight.

---

## Develop constraints by role

### Conformance (`PX-3+` under SoR)

Enable `.cursor/rules/px3-conformance-program.mdc`.

| Do | Do not |
|----|--------|
| Implement product code only | Modify Governance |
| Treat SoR as normative, read-only | Modify SoR |
| Record deviations I/S/A/N in Conformance Log | Implement Engineering Runtime |
| Stop only on N-class blockers | Redesign architecture |

Then follow `.asep/pipeline/executor.md` scoped to the authorized EWO.

### Engineering (`PX-1`, `PX-2`, migration OR/E2E)

Follow standard ASEP develop pipeline. QC + auto-approval policy apply per
`.asep/governance/engineering-supervisor.md`.

---

## Status block (mandatory end)

```text
Authorization Status: AUTHORIZED | STOP
Program: <id> / <milestone>
Pre-flight: PASS | STOP
Authorized EWO: <id> | none
Repository Status: <branch> @ <sha>
Conformance Log: <path> (if conformance)
Recommended Next Action: <execute EWO | fix pre-flight | spawn backlog>
```
