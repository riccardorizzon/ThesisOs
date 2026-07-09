# PVC-1 — Task Success Rate (aggregato)

Compila dopo **≥ 3 sessioni** completate.

---

## Metadati

| Campo | Valore |
|-------|--------|
| **Ciclo** | Product Validation Cycle 1 |
| **Periodo** | |
| **Sessioni completate** | /5 target |
| **Ambiente** | |
| **Compilato da** | |

---

## Come leggere i risultati (dopo ≥ 3 sessioni)

**Non partire da** "quali bug ci sono" (C5, G2, …).

Parti da questa tabella:

| Journey | Success Rate | Tempo medio | Primo punto di esitazione | Pattern osservato |
| ------- | -----------: | ----------: | ------------------------- | ----------------- |
| UJ-001  |            ? |           ? | ?                         | ?                 |
| UJ-002  |            ? |           ? | ?                         | ?                 |
| UJ-003  |            ? |           ? | ?                         | ?                 |

La colonna **Pattern osservato** guida il prossimo ciclo — non l'elenco storico bug.

---

## Matrice priorità (backlog prossimo ciclo)

Costruisci **dopo** tutte le sessioni, aggregando pattern cross-partecipante:

| Pattern | Frequenza | Impatto | Priorità |
| ------- | --------: | ------- | -------- |
| Tutti non trovano come creare un capitolo | 3/3 | Molto alto | P1 |
| Due utenti ignorano Knowledge | 2/3 | Alto | P2 |
| Un utente non vede il badge | 1/3 | Basso | P3 |

Il backlog nasce da **questa matrice**, non da C5/G2/M4.

---

## Dettaglio per journey (compilazione)

**Formula:** `(S + 0.5×P) / (S + P + F) × 100%` — escludi N/T dal denominatore.

| Journey | Task | Successo | Tempo | Tentativi | **Primo esitazione** | Blocco finale | Beta V3 | RC-2 PVC-1 | Δ |
|---------|------|----------|-------|-----------|----------------------|---------------|---------|------------|---|
| **UJ-001** ⭐ | Crea primo capitolo | | | | | |
| UJ-002 | Carica fonte | | | | | |
| UJ-003 | Trova concetto | | | | | |
| UJ-004 | Apri canvas | | | | | |
| UJ-005 | Esplora grafo | | | | | |
| UJ-006 | Chat AI | | | | | |
| UJ-007 | Avvia revisione | | | | | |
| UJ-008 | Trova decisioni | | | | | |
| UJ-009 | Nuovo progetto | | | | | |
| UJ-010 | Navigazione (debrief) | | | | | |
| **Media pesata** | — | | | | | |

**Legenda colonne Beta V3 / RC-2:** percentuale successo (S=100%, P=50%, F=0%) oppure `n/N sessioni`.

---

## Fiducia percepita (media 1–5)

| Journey | Beta V3 | RC-2 PVC-1 | Δ |
|---------|---------|------------|---|
| UJ-001 | | | |
| UJ-002 | | | |
| UJ-003 | | | |
| UJ-004 | | | |
| UJ-005 | | | |
| UJ-006 | | | |
| UJ-007 | | | |
| UJ-008 | | | |
| UJ-009 | | | |
| UJ-010 | | | |
| **Media** | | | |

---

## Top 3 **primi punti di esitazione** (RC-2)

Ranked by frequency — dove iniziano a dubitare, non dove falliscono:

1. 
2. 
3. 

---

## Citazioni utente (verbatim)

| # | Journey | Citazione |
|---|---------|-----------|
| 1 | | |
| 2 | | |
| 3 | | |

---

## Verdetto Product Lead

**Il prodotto è migliorato per l'utente?** ☐ Sì ☐ Parzialmente ☐ No

**Ipotesi UJ-001 falsificata o confermata?** ☐ Confermata ☐ Falsificata ☐ Inconclusa — pattern reale: ___

**Prossimo ciclo (max 3 iniziative da matrice priorità):**

1. 
2. 
3. 

**Recovery Sprint 3 autorizzato?** ☐ No ☐ Sì — solo se: ___

---

## Sessioni incluse

| ID | Data | Partecipante | Scorecard |
|----|------|--------------|-----------|
| PVC1-001 | | | `scorecard-PVC1-001.md` |
| PVC1-002 | | | |
| PVC1-003 | | | |
