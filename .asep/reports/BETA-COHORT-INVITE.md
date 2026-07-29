# Beta Cohort — Invito tester (Wave 4)

> **Status:** **DEFERRED** 2026-07-29 — materials ready; cohort not run  
> **Closure:** `.asep/reports/DEMO-PRESENTABILITY-CLOSURE-20260729.md`  
> **Target:** 5–10 persone · **Tracker:** `.asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md`  
> **Onboarding:** `.asep/reports/RC-BETA-ONBOARDING.md` · **Handout:** `docs/demo/DEMO-HANDOUT.md`

## Messaggio invito (copia-incolla)

```text
Ciao — ti invito a provare ThesisOS beta (workspace AI per tesi).

Cosa fa: fonti indicizzate, chat RAG sul corpus, scrittura per capitolo, export.

Tempo richiesto: 30–45 min, una sessione.

URL: [LOCALE http://localhost:3000 OPPURE tunnel/GCP — vedi sotto]

Prima di iniziare:
1. Apri Home → Writing → Sources
2. Leggi limitazioni beta in Settings
3. Segnala solo bug/regressioni (non feature request)

Feedback (template):
  Surface: (Home | Writing | Sources | Knowledge | Research | Settings)
  Severity: (blocker | major | minor)
  Steps: 1… 2… 3…
  Expected: …
  Actual: …

Grazie!
```

## URL per cohort

| Modalità | Setup | Durata consigliata |
|----------|-------|-------------------|
| **Locale + SSH tunnel** | Cursor Remote-SSH, forward 3000+8000 | Dev / relatrice |
| **Cloudflare tunnel** | `bash bin/beta-public-open.sh` | Demo singola (<24h) |
| **Cloud Run GCP** | `docs/demo/DEMO-DEPLOY-GCP.md` | Cohort multi-giorno |

## Tracker cohort (aggiorna dopo ogni invito)

Vedi tabella **Cohort** in `THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md`:

- `#1` … `#10` — nome, Invited ☑, Onboarded ☑, note sessione

## Checklist operatore (prima di inviare URL)

1. [ ] `make demo-gate` verde sullo stack della cohort
2. [ ] `make cohort-check` PASS
3. [ ] Se URL pubblico (tunnel/GCP): impostare `BETA_ACCESS_TOKEN` su backend **e** FE
   (`X-Beta-Token` via `frontend/middleware.ts` / `NEXT_PUBLIC_BETA_ACCESS_TOKEN`) — ADR-0048
4. [ ] Verificare: senza token → API 401; con token → superfici 200 (`make demo-auth-check` con token esportato)
5. [ ] Handout + Settings «Accesso (beta)» / limitazioni letti almeno una volta
6. [ ] Annotare riga tracker (`#1`…`#10`) con nome + data invito
7. [ ] Dopo sessione: onboarded ☑ + note (blocker / major / minor)

> Non inventare tester umani. Slot vuoti = cohort non ancora attiva — ok per demo operator-only.

## Exit cohort → GA

- [ ] 5–10 righe compilate nel tracker
- [ ] Feedback triage senza blocker aperti
- [ ] `make demo-gate` verde sullo stack usato dalla cohort
- [ ] Decisione M8 solo se serve isolamento account (non prima)
