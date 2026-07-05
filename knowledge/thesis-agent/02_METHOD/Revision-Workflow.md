# Revision Workflow

Pipeline operativa per passare da bozza a paragrafo congelato.

## Stati di un paragrafo

```text
IDEA → AUDIT FONTI → OUTLINE → BOZZA → PRONTO PER REVISIONE → [feedback] →
  → MODIFICA → PRONTO PER REVISIONE → … → CONGELATO
```

## REV-006 (dettaglio)

### Controllo attribuzioni

Per ogni frase che attribuisce un'idea a un autore:

1. Indicare fonte (opera, pagina o sezione se possibile).
2. Verificare che il testo della fonte supporti l'attribuzione (FONDATO) o
   dichiarare PLAUSIBILE/SPECULATIVO.
3. Se l'idea è tua applicazione alla tesi, non attribuirla all'autore (parte B).

### Separazione A / B

- **Blocco A:** "Secondo X, …" — solo contenuto ascrivibile a X.
- **Blocco B:** "Nel contesto della presente tesi / STIGMATA, …" — applicazione.

In revisione, evidenziare eventuale contaminazione A←→B.

### Livelli epistemici nel testo

| Livello | Nel testo definitivo |
|---------|----------------------|
| FONDATO | Affermazione diretta con citazione |
| PLAUSIBILE | Formulazioni cautious ("si può leggere", "suggerisce") |
| SPECULATIVO | Solo in bozza o con esplicita etichetta ipotesi — non in congelato |

## Workflow paragrafo teorico (es. §3.1 Albers)

1. **Library-first** su Albers (+ eventuali secondarie nel master).
2. Outline allineato a `OUTLINE_MASTER` e `CORE THEORY MAP`.
3. Stesura con A/B e citazioni.
4. Auto-check REV-006.
5. Consegna: **PRONTO PER REVISIONE** + eventuali domande batch.
6. Attendere utente/relatrice.
7. Congelare → aggiornare `Thesis-State.md`.

## Workflow paragrafo STIGMATA

1. Inventario evidenze nella cartella STIGMATA.
2. Mappa fasi processo ↔ file.
3. Stesura evidence-first.
4. Collegamento esplicito al framework teorico (parte B).
5. Stessi stati e REV-006 dove si citano autori.

## Prima correzione relatrice come modello

Usare il primo PDF corretto in `04_KNOWLEDGE/Relatrice/` come riferimento per:

- Lunghezza paragrafi e densità citazioni.
- Tono (più descrittivo vs più analitico).
- Tipo di correzioni ricorrenti (da annotare in `Relatrice-Rules.md`).

## Integrazione con ThesisOS M6

- Bozza: output `writer` route → `draft` in GraphState (ephemeral).
- Salvataggio: `ChapterService` → `chapters` + versioni.
- Congelamento operativo: metadata capitolo (es. `status: frozen`) — da definire in
  implementazione; fino ad allora tracciato in `Thesis-State.md`.
