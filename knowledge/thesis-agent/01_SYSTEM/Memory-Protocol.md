# Memory Protocol

## Regola fondamentale

**Nessuna scrittura in memoria permanente senza approvazione esplicita dell'utente.**

In ThesisOS questo corrisponde a: non creare/aggiornare record `memories` di tipo
`editable`, `thesis`, `decision` senza conferma — allineato ad ADR-0015 (ownership).

## MEMORY UPDATE PROPOSAL

Quando emerge una regola, decisione o fatto da rendere duraturo, proporre:

```text
MEMORY UPDATE PROPOSAL
──────────────────────
Tipo:        [regola | decisione | preferenza relatrice | stato progetto | altro]
Destinazione:[Permanent.md | Decisions.md | Thesis-State.md | editable DB]
Contenuto:   [testo esatto proposto]
Motivazione: [perché ora, da quale fonte/chat]
Azione:      [aggiungi | modifica | rimuovi]
──────────────────────
Approvare? (sì/no/modifica)
```

Solo dopo **sì** (o testo modificato dall'utente) si aggiorna il file o si promuove
in ThesisOS.

## Cosa va in memoria permanente

- Regole REV approvate dalla relatrice o dall'utente.
- Stato "congelato" di paragrafi e versioni master (THEORY MAP, OUTLINE, …).
- Classificazione fonti (approvata / scartata) con motivazione.
- Preferenze redazionali confermate (footnote, citazioni, struttura capitoli).
- Terminologia fissata (`03_PROJECT/Terminology.md`).

## Cosa NON va in permanente

- Bozze in revisione.
- Ipotesi interpretative su note della relatrice.
- Contenuto estratto da una sola lettura non verificata.
- Output di audit non approvati dall'utente.

## Memoria temporanea

`05_MEMORY/Temporary.md` — contesto di sessione: paragrafo in corso, domande aperte,
audit parziali. Si può svuotare a fine sessione o dopo promozione in permanente.

## Changelog

Ogni modifica approvata a permanente o decisioni va riga in `05_MEMORY/Changelog.md`:

```text
YYYY-MM-DD | file | azione | sintesi
```

## Mapping ThesisOS (M2)

| File / concetto | `memories.kind` | `key` suggerita |
|-----------------|-----------------|-----------------|
| Regole sempre attive | `editable` | `editable` |
| Scope tesi, outline summary | `thesis` | `thesis` |
| Scelte esplicite (corpus, REV) | `decision` | slug es. `rev-006` |
| Preferenze utente | `user` | `user` |
| Concetti / schede autore | `concept` | slug autore |
| Note su singola fonte | `citation` | slug fonte |

**Injection in chat (M2):** sempre `editable`; `thesis` e `user` se `pinned=true`.
Le `decision` non vanno iniettate automaticamente — si richiamano quando rilevanti.

## Memoria estratta da Kimi (NON importare)

Non recuperare da Kimi: system prompt, memory file, istruzioni interne della
piattaforma. Il comportamento è già in `01_SYSTEM/` e `02_METHOD/`.
