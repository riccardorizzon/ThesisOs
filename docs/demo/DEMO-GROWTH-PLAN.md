# Demo Wave 4 — Crescita (post-MVP presentabile)

> **Obiettivo:** passare da «posso presentarlo» a «prodotto in crescita».  
> **Non bloccante** per demo 15 min — complementa Wave 1–3.

## Scope Wave 4

| # | Track | Deliverable | Stato |
|---|-------|-------------|-------|
| 1 | **Research wow** | Canvas live + segmento demo opzionale | `/research/canvas` 200 |
| 2 | **Beta cohort** | Invito + tracker 5–10 tester | `.asep/reports/BETA-COHORT-INVITE.md` |
| 3 | **Deploy GCP** | Runbook Cloud Run (oltre tunnel) | `docs/demo/DEMO-DEPLOY-GCP.md` |
| 4 | **Auth / multi-user** | **Defer M8** — documentato, non implementato | v3 backlog |

## Cosa NON è Wave 4

- Docling / PDF pesanti → resta defer (Wave 3)
- Wave E FTS/research polish → remediation backlog
- ASEP / SoR changes → fuori product plane

## Gate

```bash
make demo-wave4-check   # growth artifacts + research canvas smoke
make demo-gate            # Wave 1–4 completo
```

## Auth — criteri M8 (defer esplicito)

Implementare login/multi-tenant solo quando:

1. Cohort beta richiede isolamento account
2. GA package approvato
3. ADR dedicato (session/JWT, non stub)

Fino ad allora: **single-user** dichiarato in Settings + handout.

## Riferimenti

| Risorsa | Path |
|---------|------|
| Demo script | `docs/demo/DEMO-SCRIPT.md` |
| Ops Wave 3 | `docs/demo/DEMO-OPS-RUNBOOK.md` |
| Cohort tracker | `.asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md` |
| Terraform GCP | `infra/terraform/` |
