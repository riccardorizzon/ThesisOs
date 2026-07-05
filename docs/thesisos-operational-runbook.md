# ThesisOS Operational Runbook — v1.0

> **Audience:** operator (thesis author) using ThesisOS after migration baseline.  
> **Prerequisite:** v1.0 Operational release (`docs/RELEASE-MANIFEST-v1.0.yaml`).

This is **not** the Kimi migration runbook (`docs/kimi-to-thesisos-migration-runbook.md`).
It describes day-to-day use of a **qualified** ThesisOS instance.

---

## 1. Start the stack

```bash
make up          # db + backend + frontend
curl localhost:8000/health   # expect {"status":"ok"}
```

Frontend chat UI or API `POST /chat` with `Accept: text/event-stream`.

---

## 2. What ThesisOS guarantees (v1.0)

| Area | Qualified by | Operator expectation |
|------|--------------|-------------------|
| Structure / outline | OR-1 | Agent knows 6-chapter GT |
| STIGMATA / evidence | OR-2 | FONDATO/PLAUSIBILE discipline |
| Corpus / exclusions | OR-3 | Active authors only; CORPUS-02/03 respected |
| Uni + relatrice rules | OR-4 | Norms embedded when asked |
| Decisions | OR-5 | Frozen vs open; no silent reopen |
| Writing | OR-6 PASS\* | Academic paragraph; see W-06 limitation |
| Memory / state | OR-7 | Session closure proposals; no auto permanent write |
| Integration | E2E | Continuous session coherence |

**Not guaranteed:** deterministic author-date on every generation — see
`docs/KNOWN_LIMITATIONS.md` (W-06).

---

## 3. Typical session flow

```text
1. Research / read corpus source     (library-first, OR-3)
2. Draft paragraph                   (OR-6 modes; REV-006, A/B)
3. Review with relatrice rules       (OR-4)
4. Close session                     (OR-7)
   ├── MEMORY UPDATE PROPOSAL (if needed)
   ├── Thesis-State delta (proposal)
   ├── Changelog row (proposal)
   └── Bibliography candidata (if new source)
5. Operator approves proposals       (sì/no/modifica)
6. Only then persist to Permanent / M2
```

**State Atomicity:** never accept partial state — Thesis-State + Changelog + manifest
must stay coherent (OR-7 M-09).

---

## 4. MEMORY UPDATE protocol

Format: `knowledge/thesis-agent/01_SYSTEM/Memory-Protocol.md`

- Agent **proposes** — never writes permanent memory without your **sì**.
- Frozen decisions and master artifacts require explicit trigger to change.

---

## 5. Decision lifecycle

- **Congelato / Frozen** — do not reopen without trigger (CORPUS, OUTLINE, REV, …).
- **Da decidere** — open backlog in `Decisions.md`.
- Agent must not unilaterally congelare bozze.

---

## 6. Corpus rules

- Write only from **active** corpus (~12 authors in Bibliography-Master).
- **Excluded:** Barthes *Mythologies*, Bourriaud (CORPUS-02/03).
- New sources → **candidata** until you approve promotion.

---

## 7. Writing mode

For academic paragraphs, use explicit cues (see OR-6 canonical prompt in
`.asep/proposals/C.6-or-6-academic-production.md`):

- `scrittura accademica`, REV-006, separazione A/B, firewall persona OFF
- Expect status label: **PRONTO PER REVISIONE**
- Review output for W-06 — add `(Author, YYYY)` manually if model uses `[n]`

---

## 8. Troubleshooting

| Symptom | Likely class | Action |
|---------|--------------|--------|
| Wrong corpus / exclusions | Capability regression | Check M2 `decisions`; report via ASEP |
| Numeric `[n]` only cites | **W-06 Platform Limitation** | Manual fix or model change — not EWO spiral |
| Agent writes permanent without OK | OR-7 regression | Stop; do not approve; file issue |
| Reopens frozen phase | OR-5 regression | Cite Decisions.md; reject suggestion |

---

## 9. Governance references

| Document | Role |
|----------|------|
| `docs/KNOWN_LIMITATIONS.md` | Platform vs framework boundaries |
| `docs/asep-capability-model.md` | PASS*, sub-capabilities |
| `knowledge/thesis-agent/_migration/operational-readiness-log.md` | Qualification audit trail |
| `.asep/capabilities/thesis-agent-migration.yaml` | Capability registry (frozen at E.1) |

---

## 10. Post-baseline changes

Any change to capabilities, oracles, or governance after v1.0 requires a **new
engineering change process** — not ad-hoc prompt edits.

---

*ThesisOS v1.0 Operational — E.1 Release Baseline 2026-07-01*
