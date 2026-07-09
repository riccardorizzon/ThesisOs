# PVC-1 — Risultati Sessioni Beta Testing
**Progetto:** Thesis OS (https://indexes-ghz-joan-stronger.trycloudflare.com)  
**Data:** 9–11 Luglio 2026  
**Partecipanti:** 3 persone (Marta, Luca, Giulia)  
**Sessioni:** 3 (crescenti: 1 → 2 → 3 journeys)  
**Facilitatore:** Sessione esterna  

---

## Tabella riassuntiva

| Journey | Success Rate | Tempo medio | Primo esitazione | Pattern osservato |
|---------|-------------|-------------|------------------|-------------------|
| **UJ-001** | **0/3 (0%)** | 3 min | "Vede messaggio API, cerca bottone, non lo trova" | **Nessuno trova come creare un capitolo. Messaggio "dalla API" confonde tutti. 3/3 partecipanti hanno esplorato alternative ma sono tornati al blocco iniziale.** |
| **UJ-002** | **0/3 (0%)** | 4 min | "Cerca bottone '+' in Sources, non lo trova" | **2/3 hanno trovato il form upload (via Home→Importa) ma nessuno ha completato. Tutti si aspettavano inserimento manuale (titolo/autore/anno). 1/3 ha causato crash browser su /research/canvas.** |
| **UJ-003** | **0/3 (0%)** | 5 min | "Knowledge fetch failed, prova Riprova, non funziona" | **Knowledge completamente down per tutti. 1/3 ha trovato il chip "Aura" dalla fonte Benjamin ma il link e morto. Trail guidato e placeholder. Mappa concettuale crasha (SSR exception).** |

### Calcolo Success Rate

- **S** = 1 punto | **P** = 0.5 punti | **F** = 0 punti
- UJ-001: F + F + F = 0/3 = **0%**
- UJ-002: F + P + P = 1/3 = **33%** (nessuno ha completato, solo parziali)
- UJ-003: F + — + F = 0/2 = **0%** (Luca non ha fatto UJ-003)

---

## Matrice pattern

| Pattern | Frequenza | Impatto | Priorita |
|---------|-----------|---------|----------|
| **Impossibile creare capitoli** — Nessun bottone/form nell'UI. Messaggio "dalla API" confonde utenti non-tecnici. | **3/3** | **Critico** | **P0** |
| **Knowledge completamente down** — "fetch failed" persistente su tutte le route Knowledge. Concetti non navigabili. | **3/3** | **Critico** | **P0** |
| **Mappa concettuale crasha** — /research/canvas causa SSR exception (Digest: 1788078021). 1/3 ha causato crash browser. | **3/3** (testato da 2, evitato da 1 che sapeva del crash) | **Critico** | **P0** |
| **Aggiunta fonte solo via upload** — Nessun form inserimento manuale. Bottone "+" assente da Sources. | **3/3** | **Alto** | **P1** |
| **Badge metriche inerte** — "5 fonti · 1 decisioni · 7 voci" cliccabile ma senza effetto. | **3/3** | **Medio** | **P2** |
| **ⓘ Info button no-op** — Cliccabile su tutte le pagine, zero effetto. | **3/3** | **Basso** | **P3** |
| **Azioni AI non cliccabili** — Richiedono testo selezionato + capitolo, ma capitolo non creabile. | **2/3** | **Alto** | **P1** |
| **Trail guidato placeholder** — "Implementazione completa in arrivo" — non funzionante. | **1/3** testato | **Medio** | **P2** |
| **Loop Revisione→Writing** — "Avvia revisione" linka a /writing che richiede capitoli. | **1/3** testato | **Medio** | **P2** |
| **Chip concetti → link morti** — Link a /knowledge/* che e down. | **2/3** testato | **Medio** | **P2** |

---

## Sintesi qualitativa

### Il problema #1: non si puo iniziare

Tutti e 3 i partecipanti si sono bloccati sullo stesso punto: **creare un capitolo**. Il messaggio "Crea il primo capitolo dalla API" e:
- **Confusionario** per utenti non-tecnici ("dalla API?" — Marta)
- **Incompleto** perche non spiega come (nessun link, nessun form, nessun bottone)
- **Bloccante** perche senza capitolo non si puo scrivere, non si puo usare l'AI, non si puo revisionare

### Il problema #2: Knowledge e il cuore rotto

Knowledge e down per tutti. Questo ha impattato:
- **UJ-003** direttamente (0% success rate)
- **UJ-001** indirettamente (2/3 hanno provato Knowledge come alternativa)
- Le chips concetti in Sources (link morti)
- Il trail guidato (dipende da Knowledge)

### Il problema #3: assenza di path alternativi

Quando il path principale fallisce (creare capitolo), non ci sono:
- **Fallback UI**: se non puoi creare un capitolo, non c'e nemmeno un editor "bozza" o "note"
- **Errori utili**: "Failed to fetch" non spiega cosa fare
- **Guida contestuale**: il tutorial iniziale (5 step) e saltato automaticamente da tutti e 3

---

## Citazioni rappresentative

> *"Mi aspettavo un 'Nuovo capitolo' o almeno un '+' da qualche parte."*  
> — Marta (Persona A), minuto 01:05

> *"E come avere una macchina senza chiave."*  
> — Luca (Persona B), minuto 32

> *"Sembra promettente ma non va da nessuna parte."*  
> — Giulia (Persona C), minuto 46

---

## Raccomandazioni prioritarie (dal testing utente)

### P0 — Sblocca tutto (fix immediato)

1. **Aggiungere UI creazione capitoli** in `/writing` quando `chapters.length === 0`
   - Form semplice: titolo + descrizione opzionale + bottone "Crea"
   - Sostituire messaggio "dalla API" con questo form
   - Il codice backend probabilmente esiste gia (tab Contesto mostra "§1.1 in bozza")

2. **Fixare Knowledge** — il DB e vivo (`/ready` ritorna `db: true`), la query specifica fallisce

3. **Fixare /research/canvas SSR** — aggiungere error boundary, non crashare il browser

### P1 — Sblocca fonti e AI

4. Aggiungere form inserimento manuale fonte (titolo, autore, anno) — non solo upload PDF
5. Rendere azioni AI fallback quando non c'e capitolo (es: "Devi prima creare un capitolo")

### P2 — Polish UX

6. Rendere badge metriche cliccabile (mostra dettaglio memoria)
7. Fix ⓘ button (tooltip esplicativo)
8. Rimuovere placeholder trail guidato o implementarlo

---

## Allegati

- `scorecard-PVC1-001.md` — Marta (UJ-001)
- `scorecard-PVC1-002.md` — Luca (UJ-001 + UJ-002)
- `scorecard-PVC1-003.md` — Giulia (UJ-001 + UJ-002 + UJ-003)
