# 04_KNOWLEDGE — Import da Kimi

**Solo questo** va recuperato dalla piattaforma Kimi Claw. Tutto il comportamento
dell'agente è già in `01_SYSTEM/` … `03_PROJECT/` (estratta dalla chat).

## Cosa NON importare da Kimi

- Prompt iniziali o aggiornati
- System prompt / memory della piattaforma
- Istruzioni, workflow, regole (già documentate qui)

## Struttura cartelle

```text
04_KNOWLEDGE/
├── Books/          # Tutti i libri PDF
├── Papers/         # Articoli
├── University/     # Guida tesi, regolamenti, template
├── Relatrice/      # PDF corretti, revisioni, annotazioni
├── References/     # Documenti di supporto
├── Images/         # Immagini generali
├── STIGMATA/       # Foto, pattern, sketch, render, materiali progetto
└── Bibliography/   # PDF bibliografici aggiuntivi
```

## Checklist export Kimi

- [ ] `Books/` — PDF completi, nomi file leggibili (Autore_Anno_Titolo.pdf)
- [ ] `Papers/` — articoli citati o candidati
- [ ] `University/` — guida redazione, regolamento, template
- [ ] `Relatrice/` — prima correzione + successive revisioni
- [ ] `References/` — slide, dispense, supporto
- [ ] `Images/` — figure non STIGMATA
- [ ] `STIGMATA/` — tutto il materiale di processo creativo
- [ ] `Bibliography/` — PDF non classificati altrove

## Dopo l'import (ThesisOS)

1. **M3 Document ingest** — upload con metadata:
   - `category`: books | papers | university | relatrice | references | images | stigmata | bibliography
2. **M4 Retrieval** — filtri per categoria in `writer` / `grounded_chat` routes.
3. Aggiornare `03_PROJECT/Bibliography.md` con path document_id.
4. Compilare `University-Rules.md` e `Relatrice-Rules.md` dai PDF importati.

## Capitoli congelati (opzionale)

I file `chapters/ch01/`, `ch02/` dal workspace Kimi **non** vanno in `04_KNOWLEDGE/`
— importarli come capitoli ThesisOS (M6 `ChapterService`) o in `03_PROJECT/` come
markdown se preferisci mirror testuale.

## Dimensioni e naming

- Evitare duplicati: un PDF per edizione; note edizione in bibliografia.
- STIGMATA: sottocartelle opzionali `foto/`, `sketch/`, `pattern/`, `render/`.
- Non committare file enormi senza policy LFS se necessario.
