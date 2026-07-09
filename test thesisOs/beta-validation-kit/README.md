# Beta Validation Kit — Product Validation Cycle 1

> **Ciclo:** Product Validation Cycle 1 (PVC-1)  
> **Non è:** Recovery Sprint 3, engineering, o estensione del Research Engine  
> **Domanda centrale:** *Perché non si capisce?* — non *Perché rompe?*

**Disciplina:** non modificare ThesisOS finché non hai completato **≥ 3 sessioni** con utenti reali.

---

## A cosa serve

Misurare **Task Success Rate** — quanti utenti completano i task fondamentali di ThesisOS, quanto tempo impiegano, dove si bloccano.

Non misura bug Critical/High/Medium. Misura **journeys**.

---

## Chi fa cosa

| Ruolo | Compito |
|-------|---------|
| **Facilitatore** | Prepara l'ambiente, cronometra, osserva senza guidare, compila le schede |
| **Partecipante** | Utente reale o proxy — **non** deve conoscere il codice né i bug ID |
| **Product Lead** | Legge i risultati aggregati e decide il prossimo ciclo (UX, onboarding, feature) |

**Regola del facilitatore:** vedi [`facilitator-rules.md`](facilitator-rules.md) — il facilitatore **non può aiutare**, solo *"Continua come faresti normalmente."*

---

## Ambiente

| Opzione | URL | Quando usarla |
|---------|-----|---------------|
| **Docker (RC-2)** | `http://127.0.0.1:3000` | Confronto diretto post-Recovery — **consigliato per PVC-1** |
| **Tunnel (Beta V3)** | URL Cloudflare del deploy | Solo se serve validare deploy pubblico |

Avvia Docker:

```bash
make up
# oppure: docker compose up -d
```

Verifica rapida: apri `/knowledge` — devono comparire concetti (Aura, Abbigliamento, …).

---

## Materiali nel kit

| File | Contenuto |
|------|-----------|
| [`journeys.md`](journeys.md) | 10 user journey con istruzioni per il facilitatore |
| [`scorecard.md`](scorecard.md) | Scheda vuota — una copia per journey × partecipante |
| [`results-template.md`](results-template.md) | Tabella Task Success Rate + confronto Beta V3 ↔ RC-2 |
| [`comparison-v3-rc2-prefill.md`](comparison-v3-rc2-prefill.md) | Ipotesi di partenza da riempire con dati umani |
| [`facilitator-rules.md`](facilitator-rules.md) | Regole metodologiche — non aiutare, esitazione, progressione sessioni |

---

## Come condurre una sessione

Vedi [`facilitator-rules.md`](facilitator-rules.md) per il dettaglio completo.

**Progressione obbligatoria:**

| Sessione | Journey |
|----------|---------|
| 1 | Solo **UJ-001** |
| 2 | UJ-001 + UJ-002 |
| 3 | UJ-001 + UJ-002 + UJ-003 |
| 4+ | Altre journey quando sessioni 1–3 complete |

Vedi [`facilitator-rules.md`](facilitator-rules.md) — falsificare l'ipotesi UJ-001, non validarla.

**Flusso:**

1. **Briefing (2 min)** — *"Pensa ad alta voce. Continua come faresti normalmente."*
2. **Journey** — compila `scorecard.md` (incluso **primo punto di esitazione** + timeline)
3. **Domanda finale (una sola)** — *"Se domani dovessi continuare la tesi con questo strumento, lo useresti?"* → silenzio → trascrivi verbatim
4. **Aggregazione** — dopo ≥ 3 sessioni, compila `results-template.md`

**Target cohort:** 3–5 partecipanti (minimo 3 per segnale).

---

## Metrica principale

```text
Task Success Rate = (journey completati / journey tentati) × 100%
```

Per journey e in aggregato. Vedi template in `results-template.md`.

---

## North star / ipotesi da falsificare

**UJ-001 — First Chapter Creation** è il primo scenario (sessione 1), non una conclusione anticipata.

Ipotesi da falsificare:

> *"Gli utenti si bloccano principalmente sulla creazione del primo capitolo."*

Potrebbe essere falsa. PVC-1 serve a scoprirlo.

Vedi [`facilitator-rules.md`](facilitator-rules.md) — **osserva, non confermare.**

---

## Cosa NON fare in PVC-1

- Non aprire ticket engineering durante la sessione
- Non citare AP-001, C5, G2, ecc. al partecipante
- Non aggiungere guard, metriche al Research Engine, o documenti ASEP
- Non "aiutare" cliccando al posto dell'utente

---

## Riferimenti baseline (solo facilitatore)

| Baseline | File |
|----------|------|
| Beta V3 | `../thesis_os_beta_report_v3.md` |
| Statistiche beta | `../thesis_os_stats_final.md` |
| RC-2 automated | `../../.asep/reports/THESISOS-RC-2-RECOVERY-VALIDATION.md` |

---

## Prossimo passo dopo PVC-1

1. Compila `results-template.md` con almeno 3 sessioni
2. Confronta Task Success Rate Beta V3 vs RC-2
3. Product Lead decide: UX theme, onboarding, o altro — **non** engineering finché i journey non guidano la priorità
