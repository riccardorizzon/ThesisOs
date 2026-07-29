# ThesisOS — Demo Handout (1 pagina)

**Prodotto:** workspace AI per tesi accademica (fonti, chat RAG, scrittura per capitolo, review, export).  
**Versione:** Demo-ready `v2.0.0-rc.2` · workspace `thesis-agent`  
**Fase demo:** **CLOSED** 2026-07-29 (Waves 1–4 + ADR-0048) — cohort/GA/M8 deferred

## URL demo

```bash
cat /tmp/thesisos-beta-public.env   # URL tunnel corrente
# oppure: bash bin/beta-public-open.sh
```

## Cosa vedrai (5 superfici)

| Route | Funzione |
|-------|----------|
| `/sources` | Biblioteca + upload → indicizzazione |
| `/ai` | Chat persistente con retrieval sul corpus |
| `/writing` | Capitoli + pannello AI grounded |
| `/review` | Proposte AI → accettazione in capitolo |
| `/manuscript` | Manoscritto — lettura ordinata per capitolo |
| `/knowledge` | Concetti strutturati (STIGMATA, aura, …) |

## Flusso demo consigliato (10 min)

1. **Fonti** — 6 markdown core + bibliografia  
2. **Chat** — «Cos'è STIGMATA?» + domanda su Sennett / craftsmanship  
3. **Scrittura** — Cap. 3 Progettazione metodologica (~3600 parole)  
4. **Export** — capitolo selezionato, project `thesis-agent`

## Limitazioni (beta onesta)

1. **Single-user** — un operatore, N tesi; niente login multi-account (ADR-0048 / M8). Gate opzionale `BETA_ACCESS_TOKEN` + `X-Beta-Token` per tunnel pubblici.  
2. **Corpus-bound** — le risposte AI usano solo documenti indicizzati; niente web live.  
3. **Tunnel pubblico fragile** — URL Cloudflare può cambiare; per demo stabile usare localhost o VM dedicata.  
4. **Citazioni (W-06)** — preferenza author-date `(Autore, anno)` con retry; non garantite al 100%.

## Gate tecnico (operatori)

```bash
make ops-check               # health + LLM + export 422 + audit
make demo-gate               # ops + Wave 1–4 + auth/cohort/citations
make cohort-check            # materiali invito + tracker
make demo-auth-check         # ADR-0048
make demo-citations-check    # preferenza cite + residual W-06
make demo-backup             # snapshot DB prima della demo
bash bin/demo-cleanup.sh --dry-run
```

Runbook ops: [`DEMO-OPS-RUNBOOK.md`](./DEMO-OPS-RUNBOOK.md)  
Crescita Wave 4: [`DEMO-GROWTH-PLAN.md`](./DEMO-GROWTH-PLAN.md)

## Contatto / repo

Documentazione: `README.md`, onboarding RC: `.asep/reports/RC-BETA-ONBOARDING.md`
