# Demo Wave 4 — Crescita (post-MVP presentabile)

> **Obiettivo:** passare da «posso presentarlo» a «prodotto in crescita».  
> **Non bloccante** per demo 15 min — complementa Wave 1–3.

## Scope Wave 4

| # | Track | Deliverable | Stato |
|---|-------|-------------|-------|
| 1 | **Research wow** | Canvas live + segmento demo opzionale | `/research/canvas` 200 |
| 2 | **Beta cohort** | Invito + tracker 5–10 + operator checklist | `.asep/reports/BETA-COHORT-INVITE.md` · `make cohort-check` |
| 3 | **Deploy GCP** | Runbook Cloud Run (oltre tunnel) | `docs/demo/DEMO-DEPLOY-GCP.md` |
| 4 | **Access control** | ADR-0048 shared beta gate + **multi-user defer M8** | `BETA_ACCESS_TOKEN` / `X-Beta-Token` |
| 5 | **Citations** | Preferenza author-date + enforce retry; residual W-06 | `make demo-citations-check` |

## Cosa NON è Wave 4

- Docling / PDF pesanti → resta defer (Wave 3)
- Wave E FTS/research polish → remediation backlog
- ASEP / SoR changes → fuori product plane
- Login multi-account reale → **M8** (non stub)

## Gate

```bash
make demo-wave4-check        # growth artifacts + research canvas
make cohort-check            # invite pack + tracker + honest limits
make demo-auth-check         # ADR-0048 wiring + live default/token
make demo-citations-check    # prompt wiring + live soft smoke + W-06 docs
make demo-gate               # Wave 1–4 + auth/cohort/citations
```

## Access control (ADR-0048)

| Modalità | Comportamento |
|----------|---------------|
| **Default** | `BETA_ACCESS_TOKEN` vuoto → API aperta (DX locale) |
| **Cohort pubblica** | Token impostato su backend (+ FE/middleware) → header `X-Beta-Token` obbligatorio |
| **M8** | Identity reale (session/JWT/OIDC), isolamento per utente — solo con GA package |

Criteri per aprire M8:

1. Cohort richiede isolamento account
2. GA package approvato
3. Work Order + ADR dedicato (non questo gate)

## Citations — onesto

- Preferenza **author-date** `(Autore, anno)` nei prompt Q&A grounded
- Retry `enforce_citations` su chat grounded
- **W-06:** non garantito al 100% — documentato in handout / Settings

## Riferimenti

| Risorsa | Path |
|---------|------|
| Demo script | `docs/demo/DEMO-SCRIPT.md` |
| Ops Wave 3 | `docs/demo/DEMO-OPS-RUNBOOK.md` |
| Cohort tracker | `.asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md` |
| ADR access | `decisions/ADR-0048-access-control-beta.md` |
| Terraform GCP | `infra/terraform/` |
