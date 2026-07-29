# ThesisOS — Demo Handout (1 pagina)

**Prodotto:** workspace AI per tesi accademica (fonti, chat RAG, scrittura per capitolo, review, export).  
**Versione:** Beta `v2.0.0-rc.2` · workspace `thesis-agent`

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

1. **Single-user** — nessun multi-tenant; adatto a demo e uso personale.  
2. **Corpus-bound** — le risposte AI usano solo documenti indicizzati; niente web live.  
3. **Tunnel pubblico fragile** — URL Cloudflare può cambiare; per demo stabile usare localhost o VM dedicata.  
4. **Originali file** — molti PDF storici non sono su disco; RAG funziona da chunk Postgres. Re-upload solo se serve download/re-parse.

## Gate tecnico (operatori)

```bash
make ops-check          # health + LLM + export 422 + audit
bash bin/demo-cleanup.sh --dry-run   # stato dati pre-demo
```

## Contatto / repo

Documentazione: `README.md`, onboarding RC: `.asep/reports/RC-BETA-ONBOARDING.md`
