# Source Classification

## Tre classi

### Approvate

- In `BIBLIOGRAPHY_MASTER` / corpus attivo (12 autori principali + supporti).
- PDF disponibile in `04_KNOWLEDGE/` (Books, Papers, Bibliography).
- Usabili in stesura e citazione senza caveat.

### Candidate

- Proposte in chat o trovate in ricerca; non ancora validate dall'utente o relatrice.
- Consentito: discussione, audit, confronto in note di lavoro.
- **Vietato:** citare in testo congelato come se approvate.

### Scartate

- Esplicitamente escluse dal corpus (con motivazione in `Decisions.md`).
- Non citare; non riproporre senza nuova discussione.

## Corpus congelato (snapshot chat)

**Esclusi (esempi confermati):**

- Roland Barthes — *Mythologies* (perimetro progetto)
- Nicolas Bourriaud — *Relational Aesthetics* / filone relazionale come pilastro

**Attivi (elenco di lavoro — completare da BIBLIOGRAPHY_MASTER):**

Seivewright, Sennett, Löbach, Albers, Benjamin, Hollander, Csikszentmihalyi, …
(+ altri fino a 12 autori nel master)

## Workflow per nuova fonte

```text
1. Proposta → classe CANDIDATA
2. Audit (rilevanza, capitolo, edizione)
3. Decisione utente/relatrice → APPROVATA o SCARTATA
4. Aggiornamento Bibliography + Changelog
5. Solo allora uso in paragrafo
```

## Fonti istituzionali

| Tipo | Percorso | Priorità |
|------|----------|------------|
| Guida redazione | `04_KNOWLEDGE/University/` | Assoluta per formato |
| Regolamento tesi | `04_KNOWLEDGE/University/` | Assoluta |
| Template Word/LaTeX | `04_KNOWLEDGE/University/` | Formattazione |
| PDF corretti relatrice | `04_KNOWLEDGE/Relatrice/` | Contenuto e stile |

## Fonti non testuali

- Immagini: `04_KNOWLEDGE/Images/`, `STIGMATA/`
- Usare in didascalie e nel testo con riferimento esplicito al materiale archiviato.
- Non inferire date o intenti non documentati.

## Integrazione ThesisOS

- Documenti importati → M3 `documents` con metadata (tipo: book | paper | university |
  relatrice | stigmata | image).
- Retrieval M4: filtrare per classe e cartella logica.
- `memories` kind `citation` per note puntuali su singola fonte (pagine, DOI).
