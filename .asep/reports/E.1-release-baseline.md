# EWO E.1 — Release Baseline Report

**Date:** 2026-07-01  
**WorkOrder:** E.1 · **Type:** EWO (Release)  
**Capability:** `release-baseline`  
**Release:** **ThesisOS v1.0 Operational**  
**Verdict:** **COMPLETE**

**Operator disposition:** E.1 RELEASE BASELINE AUTHORIZED  
**Preconditions:** OR-1…OR-7 qualified · D.1 E2E PASS

---

## 1. Release scope (executed)

| Item | Artifact | Status |
|------|----------|--------|
| Known limitations | `docs/KNOWN_LIMITATIONS.md` | ✅ Created |
| Release manifest (frozen) | `docs/RELEASE-MANIFEST-v1.0.yaml` | ✅ Created |
| Release notes | `docs/RELEASE-NOTES-v1.0.md` | ✅ Created |
| Operational runbook | `docs/thesisos-operational-runbook.md` | ✅ Created |
| Capability registry freeze | `.asep/capabilities/thesis-agent-migration.yaml` | ✅ Updated |
| Operational log freeze | `operational-readiness-log.md` | ✅ Updated |
| Baseline marker | `knowledge/thesis-agent/RELEASE_BASELINE.md` | ✅ Created |
| Git tag (recommended) | `thesisos-v1.0-operational` | 📋 Documented — apply at commit |

---

## 2. Post-baseline constraints (binding)

```text
No capability, oracle, acceptance criteria, or governance changes
after baseline freeze without new engineering change process.
```

---

## 3. Qualification summary (frozen)

| Gate | Verdict | Lifecycle |
|------|---------|-----------|
| OR-1 … OR-5 | PASS | qualified |
| OR-6 | PASS\* | qualified (W-06 platform limitation) |
| OR-7 | PASS | qualified |
| D.1 E2E | PASS | operational → frozen at E.1 |
| E.1 | COMPLETE | release-baseline frozen |

---

## 4. Known limitations (release definition)

Documented in `docs/KNOWN_LIMITATIONS.md`:

- **W-06** — autore-date / Platform Limitation (C.6-R1→R3 evidence chain)
- Framework vs model responsibility boundary
- Operational assumptions (promoted corpus, frozen decisions, operator gates)

---

## 5. Migration program status

```text
Fase A — Validazione regole              ✅
Fase B — Promozione runtime              ✅
Fase C — OR-1 … OR-7                     ✅
Fase D — E2E                             ✅
Fase E — Release baseline (E.1)          ✅

ThesisOS v1.0 Operational               ACHIEVED
```

Program completion criteria (`.asep/programs/thesis-agent-migration.yaml`): satisfied.

---

## 6. Recommended git operations (operator)

When ready to commit the baseline (not executed automatically):

```bash
git add docs/KNOWN_LIMITATIONS.md docs/RELEASE-*.yaml docs/RELEASE-NOTES-v1.0.md \
        docs/thesisos-operational-runbook.md .asep/reports/E.1-release-baseline.md \
        knowledge/thesis-agent/RELEASE_BASELINE.md
# … plus other E.1-updated files
git commit -m "release: ThesisOS v1.0 Operational baseline (E.1)"
git tag -a thesisos-v1.0-operational -m "ThesisOS v1.0 Operational — OR-1..OR-7 + E2E qualified"
```

---

## 7. Verdict

**E.1 COMPLETE** — Release baseline frozen. ThesisOS **v1.0 Operational**.

No further migration gates. Operational usage per `docs/thesisos-operational-runbook.md`.

---

## WO-TRACE

```text
D.1 E2E PASS → E.1 AUTHORIZED → freeze manifest + KNOWN_LIMITATIONS → v1.0 Operational
```
