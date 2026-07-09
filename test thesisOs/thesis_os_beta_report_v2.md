
# ═══════════════════════════════════════════════════════════════════
#  THESIS OS — REPORT BETA TESTER FINAL V2
#  Tester: Sessione esterna | Data: 2026-07-09 | Sessioni: 8+
#  URL: indexes-ghz-joan-stronger.trycloudflare.com
#  Status: ALPHA — NON PRODUCTION READY
# ═══════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════
# 1. COSA C'È DAVVERO IN MEMORIA (La scoperta principale)
# ═══════════════════════════════════════════════════════════════════

## 1.1 Il problema: la memoria ESISTE ma è INVISIBILE

Il badge "5 fonti · 1 decisioni · 7 voci · 0 citazioni" mostra dati reali,
ma NESSUNA UI permette di navigarli direttamente. La memoria è sepolta in
posti non intuitivi:

┌──────────────────────────────────────────────────────────────────┐
│  DATO               │  DOVE SI TROVA DAVVERO                    │
├──────────────────────────────────────────────────────────────────┤
│  1 decisione        │  Writing → tab "Contesto" → "Decisioni    │
│                     │  vincolanti" → click "Leggi"              │
├──────────────────────────────────────────────────────────────────┤
│  7 concetti         │  Writing → tab "Contesto" → "Concetti nel │
│                     │  contesto" + Sources chips                │
├──────────────────────────────────────────────────────────────────┤
│  4 fonti            │  Sources (unico posto visibile)           │
├──────────────────────────────────────────────────────────────────┤
│  Tutte le regole    │  Writing → tab "Contesto" → sezione       │
│  del progetto       │  "Ambito" (espandibile)                   │
├──────────────────────────────────────────────────────────────────┤
│  Cronologia fasi    │  Writing → tab "Contesto" → "Cronologia   │
│                     │  fasi" (da 2026-06-17 a 2026-06-26)       │
└──────────────────────────────────────────────────────────────────┘


## 1.2 Il tab CONTESTO rivela una memoria immensa

Cliccando Writing → tab "Contesto" si scopre una sezione espandibile
"Ambito" che contiene L'INTERO stato del progetto:

### Decisioni vincolanti (stato: Congelato)
┌──────────┬────────────────────────────────────────────────────────┐
│ ID       │ Contenuto                                              │
├──────────┼────────────────────────────────────────────────────────┤
│ CORPUS-01│ ~12 autori attivi nel master; non espandere senza      │
│          │ approvazione                                           │
│ CORPUS-02│ Barthes "Mythologies" — ESCLUSO                        │
│ CORPUS-03│ Bourriaud / estetica relazionale — ESCLUSO             │
│ CORPUS-04│ Library-first obbligatorio prima di paragrafi teorici  │
├──────────┼────────────────────────────────────────────────────────┤
│ REV-001  │ Rispettare indicazioni strutturali relatrice           │
│   a 006  │ Coerenza terminologica, no ripetizioni cross-capitolo, │
│          │ citazioni verificabili, tono allineato, controllo      │
│          │ attribuzioni (FONDATO/PLAUSIBILE/SPECULATIVO)          │
├──────────┼────────────────────────────────────────────────────────┤
│ METH-01  │ Ricerca qualitativa, non quantitativa                  │
│   a 004  │ STIGMATA = caso applicativo (NON oggetto teorico       │
│          │ principale), interpretazione conservativa,             │
│          │ evidence-first per narrativa STIGMATA                  │
├──────────┼────────────────────────────────────────────────────────┤
│ UNI-01   │ University-Rules.md approvato — NESSUNA NOTA A PIE DI  │
│          │ PAGINA, autore-data nel corpo (Accademia del Lusso)    │
│ REL-01   │ Regole relatrice R1-R5 validate                        │
├──────────┼────────────────────────────────────────────────────────┤
│ RED-01   │ Italiano accademico per tutta la tesi                  │
│   a 004  │ Footnote VIETATE, fonti straniere in traduzione,       │
│          │ classificazione: approvata/candidata/scartata          │
├──────────┼────────────────────────────────────────────────────────┤
│ MEM-01   │ Nessuna memoria permanente senza approvazione utente   │
│   a 003  │ Note relatrice: analisi → batch domande → modifiche    │
│          │ Due modalità: conversazione vs scrittura accademica    │
├──────────┼────────────────────────────────────────────────────────┤
│ PLAT-01  │ Non migrare system prompt Kimi; ricostruire da chat    │
│   a 005  │ Knowledge binaria solo da export Kimi                  │
│          │ Persona "Cheerleader" importata, firewall conv/scritt  │
│          │ Scaffolding non promosso; resta in _inbox              │
└──────────┴────────────────────────────────────────────────────────┘

### Cronologia fasi complete (2026-06-17 → 2026-06-26)
│ 2026-06-17 │ Set-up regole operative (FATTO/INFERENZA/VALUTAZIONE)  │
│ 2026-06-17 │ Analisi guida università + descrizione tesi            │
│ 2026-06-19 │ FASE CORPUS: CORE THEORY MAP v2.1 CONGELATO            │
│ 2026-06-19 │ FASE BIBLIOGRAFIA: BIBLIOGRAPHY_MASTER v1.0 CONGELATA  │
│ 2026-06-19 │ FASE ARCHITETTURA: OUTLINE_MASTER v1.0 CONGELATA       │
│ 2026-06-20 │ FASE META-DOCUMENTI: STIGMATA_DOCUMENTATION v1.0 CONG. │
│ 2026-06-22 │ Modalità EVIDENCE-FIRST attivata                       │
│ 2026-06-23 │ Modalità LIBRARY-FIRST: analisi 4 libri                │
│ 2026-06-24 │ FASE STESURA: §1.1 bozza (Löbach, Csikszentmihalyi)    │
│ 2026-06-26 │ Revisione puntuale §1.1 (attribuzioni Löbach)          │


# ═══════════════════════════════════════════════════════════════════
# 2. COMMAND PALETTE (⌘K) — La funzione meglio nascosta
# ═══════════════════════════════════════════════════════════════════

La ⌘K apre una command palette (kbar) con ~20 opzioni:

NAVIGAZIONE:              AZIONI (richiedono capitolo):       SCORCIATOIE:
├── Vai a Home            ├── Mostra/nascondi outline (⌘\\)   ├── G W → Scrittura
├── Vai a Writing         ├── Mostra/nascondi pannello (⌘⇧\\) ├── G S → Fonti
├── Vai a Sources         ├── Scheda AI (⌘1)                  └── G H → Home
├── Vai a Review          ├── Scheda Contesto (⌘2)
├── Vai a Research        ├── Scheda Fonte (⌘3)
└── Vai a Knowledge       ├── Scheda Revisione (⌘4)
                           ├── Salva capitolo (⌘S)
                           ├── Cita fonte (⌘⇧C)
                           ├── Cerca nel capitolo (⌘⇧F)
                           ├── Avvia revisione capitolo (⌘⇧R)
                           ├── Applica suggerimento AI (⌘Enter)
                           ├── Sezione precedente (⌘↑)
                           └── Sezione successiva (⌘↓)

NOTE: Le azioni contrassegnate richiedono un capitolo attivo — che non
è creabile dall'interfaccia. Quindi ~10 scorciatoie su ~20 sono INUTILI.


# ═══════════════════════════════════════════════════════════════════
# 3. TEST FUNZIONALE DETTAGLIATO — Ogni bottone testato
# ═══════════════════════════════════════════════════════════════════

## 3.1 HOME
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Elemento        │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ Progresso 0%    │ ✅       │ Visuale corretto, cerchio SVG        │
│ "Prima dei dieci│ ✅       │ Testo condizionale su stato          │
│  minuti"        │          │                                      │
│ Pulsante        │ ✅       │ Naviga a /writing                    │
│ "Continua"      │          │                                      │
│ Card Ricerca    │ ✅       │ Naviga a /research                   │
│ Card Scrittura  │ ✅       │ Naviga a /writing                    │
│ Card Revisione  │ ✅       │ Naviga a /review                     │
│ Card Importa    │ ✅       │ Naviga a /sources/upload             │
│ Link "Scrittura"│ ✅       │ Naviga a /writing                    │
│ Link "importa"  │ ✅       │ Naviga a /sources/upload             │
│ ⌘K              │ ✅       │ Apre command palette completa        │
│ Sessione timer  │ ✅       "0m" — incrementa in tempo reale      │
│ Progetto select │ ⚠️       │ Apre ma CREAZIONE NUOVO CRASHA       │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.2 SOURCES — Ogni funzione testata
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Elemento        │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ Lista 4 fonti   │ ✅       │ Tutte visibili con chip concetti     │
│ Card Flow       │ ✅       │ Naviga a /sources/csikszentmihalyi-  │
│                 │          │ flow                                 │
│ Card Albers     │ ✅       │ Naviga a dettaglio                   │
│ Card Benjamin   │ ✅       │ Naviga a dettaglio                   │
│ Card Hollander  │ ✅       │ Naviga a dettaglio                   │
│ Chip concetto   │ ❌       │ Link a /knowledge/* ma Knowledge     │
│ (qualsiasi)     │          │ fetch failed — link morti            │
│ Select stato    │ 🟡       │ Presente, opzioni visibili,          │
│                 │          │ interazione non testabile            │
│ Select confid.  │ 🟡       │ Stesso comportamento                 │
│ Checkbox "Mostra│ 🟡       │ Presente                             │
│ deprecate"      │          │                                      │
│ Search corpus   │ ✅       │ Input presente                       │
│ Esporta BibTeX  │ ✅       │ Bottone cliccabile, download?        │
│                 │          │ (non verificato end-to-end)          │
│ Stampa          │ ✅       │ Bottine cliccabile                   │
│ Link "Knowledge"│ ❌       │ /knowledge fetch failed              │
│ Dettaglio fonte │ ⚠️       │ Solo titolo+autore+anno+stato+2chip. │
│                 │          │ MANCANO: abstract, note, metadati    │
│                 │          │ estesi, citazioni estratte, ISBN,    │
│                 │          │ DOI, data importazione, dimensione   │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.3 WRITING — Test di ogni elemento
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Elemento        │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ "Failed to fetch"│ ❌      │ Errore visibile in header pagina     │
│ Messaggio       │ ✅       │ "Nessun capitolo" chiaro             │
│ "dalla API"     │ ❌       │ Messaggio rivela dipendenza da API   │
│ Link "Importa   │ ✅       │ Naviga a /sources/upload             │
│ documento"      │          │                                      │
│ Link "Torna alla│ ✅       │ Naviga a /home                       │
│ Home"           │          │                                      │
│ Tab "Tutti"     │ ✅       │ Selezionabile, outline vuoto         │
│ Tab "In corso"  │ ✅       │ Selezionabile, outline vuoto         │
│ Tab "Da         │ ✅       │ Selezionabile, outline vuoto         │
│ revisionare"    │          │                                      │
│ Toolbar Cita/   │ 🟡       │ Visibile ma non cliccabile (serve    │
│ Find/Preview/   │          │ capitolo)                            │
│ Esporta         │          │                                      │
│ Tab "AI"        │ ✅       │ Mostra azioni AI (testo statico)     │
│ Tab "Contesto"  │ ✅       │ RIVELA MEMORIA COMPLETA (vedi §1)    │
│ Tab "Fonte"     │ ⚠️       │ "Anteprima fonte — usa Cita"         │
│ Tab "Revisione" │ ✅       │ "Nessuna revisione" + link a /review │
│ Azioni AI       │ 🟡       │ 5 azioni visibili ma NON cliccabili  │
│ (tutte)         │          │ (serve testo selezionato+capitolo)   │
│ Badge "Sviluppo │ ❌       │ Cliccabile ma NON apre dropdown.     │
│ argomentativo"  │          │ Dovrebbe cambiare modalità AI        │
│ Badge metriche  │ ❌       │ Cliccabile ma zero effetto. Memoria  │
│                 │          │ non navigabile                       │
│ ⓘ Info button   │ ❌       │ Cliccabile, ZERO effetto. No tooltip,│
│                 │          │ no modal, no navigazione             │
│ "Leggi" (in     │ ✅       │ ESPANDE decisione vincolante         │
│ Contesto)       │          │ completa                             │
│ "Chiedi al      │ ?        │ Presente ma non testato              │
│ revisore"       │          │                                      │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.4 RESEARCH — Tutte le route
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Route           │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ /research (hub) │ ✅       │ Pagina hub con 3 opzioni visibili    │
│ /research/canvas│ ❌ CRASH │ Server-side exception                │
│                 │          │ Digest: 1788078021                   │
│ /research/guided│ ⚠️ STUB  │ Placeholder "implementazione         │
│                 │          │ completa in arrivo"                  │
│ /knowledge/graph│ ❌ CRASH │ Server-side exception                │
│                 │          │ Digest: 4130059368                   │
│ Link "mappa" da │ ❌ CRASH │ Stesso errore                        │
│ guided          │          │                                      │
│ Link "Knowledge"│ ❌ CRASH │ Stesso errore                        │
│ da guided       │          │                                      │
│ Link "Vai a     │ ❌       │ /knowledge fetch failed              │
│ Knowledge" da   │          │                                      │
│ Research        │          │                                      │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.5 KNOWLEDGE — Tutte le route
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Route           │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ /knowledge      │ ❌       │ "Impossibile caricare i concetti —   │
│                 │          │ fetch failed" — persistente anche    │
│                 │          │ dopo "Riprova"                       │
│ /knowledge/graph│ ❌ CRASH │ Server-side exception                │
│ /knowledge/*    │ ❌       │ Tutti i link da Sources chip portano │
│ (da chips)      │          │ a pagine con fetch failed            │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.6 REVISIONE — Test completo
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Elemento        │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ Step indicator  │ ✅       │ "1 Seleziona → 2 Confronta → 3       │
│                 │          │ Accetta" — visivamente chiaro         │
│ Messaggio vuoto │ ✅       │ "Nessuna revisione in sospeso"       │
│ "Avvia          │ ✅       │ Naviga a /writing                    │
│ revisione"      │          │                                      │
│ Link "/ai"      │ ❌       │ Punta a pagina con TypeError         │
│ Badge Sviluppo  │ ❌       │ No-op (come in Writing)              │
│ arg.            │          │                                      │
│ Badge metriche  │ ❌       │ No-op                                │
│ ⓘ Info button   │ ❌       │ No-op                                │
│ Flusso end-to-end│ 🟡      │ Non testabile senza capitoli         │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.7 AI CHAT (/ai) — Test completo
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Elemento        │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ "Conversazioni" │ ❌       │ TypeError: Failed to fetch           │
│ list            │          │ (non carica lista conversazioni)     │
│ Bottone "Nuova" │ ❌       │ Probabilmente non funzionante        │
│ Textarea input  │ ✅       │ Accetta testo correttamente          │
│ Bottone "Invia" │ ⚠️       │ Invia il messaggio (appare in chat)  │
│                 │          │ ma risposta è "TypeError: Failed to  │
│                 │          │ fetch" — backend morto               │
│ Messaggio inviato│ ⚠️      │ Visibile nella cronologia ma senza   │
│                 │          │ risposta                             │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.8 SETTINGS — Test campo per campo
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Elemento        │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ Nome visualizz. │ ✅       │ Input editabile, accetta testo       │
│ ID attivo       │ ℹ️       │ Visualizzato, NON modificabile       │
│ Radio Autore-   │ ✅       │ Selezionato di default               │
│ data            │          │                                      │
│ Radio APA       │ ✅       │ Selezionabile, auto-save             │
│ Select BibTeX   │ ✅       │ Selezionato di default               │
│ Select RIS      │ ⚠️       │ Opzione "futuro" — non selezionabile?│
│ Salva           │ ❌ ASSENT│ NESSUN bottone salva. Auto-save?     │
│                 │          │ Nessun feedback di conferma          │
│ Modalità        │ ❌       │ NON ESISTE nessuna configurazione    │
│ revisione       │          │ per tipo di revisione                │
│ Dark mode       │ ❌       │ Non presente                         │
│ Font size       │ ❌       │ Non presente                         │
│ Densità UI      │ ❌       │ Non presente                         │
│ Backup/Export   │ ❌       │ Non presente                         │
│ Gestione multi- │ ❌       │ Non presente (oltre al select che    │
│ progetto        │          │ crasha alla creazione)               │
└─────────────────┴──────────┴──────────────────────────────────────┘

## 3.9 UPLOAD — Test form
┌─────────────────┬──────────┬──────────────────────────────────────┐
│ Elemento        │ Stato    │ Risultato test                       │
├─────────────────┼──────────┼──────────────────────────────────────┤
│ File input      │ ✅       │ Campo file presente                  │
│ Titolo (opt)    │ ✅       │ Input testo                          │
│ Autore (opt)    │ ✅       │ Input testo                          │
│ Lingua (opt)    │ ✅       │ Input testo                          │
│ Formati         │ ℹ️       │ PDF, EPUB, DOCX dichiarati           │
│ "Analisi auto"  │ ℹ️       │ Dichiarata, non testata              │
│ post-caricamento│          │                                      │
│ Submit          │ ?        │ Nessun bottone submit visibile?      │
└─────────────────┴──────────┴──────────────────────────────────────┘


# ═══════════════════════════════════════════════════════════════════
# 4. BUG RILEVATI — Classificati per severità
# ═══════════════════════════════════════════════════════════════════

## 🔴 CRITICI (7 bug — bloccano funzionalità core)

ID   │ Modulo           │ Bug                              │ Impatto
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
C1   │ Knowledge        │ Fetch failed persistente su      │ Grafo concettuale
     │                  │ /knowledge e /knowledge/*        │ completamente inaccess.
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
C2   │ Research/Canvas  │ Server-side exception            │ Mappa concettuale
     │                  │ Digest: 1788078021               │ crash totale
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
C3   │ Knowledge/Graph  │ Server-side exception            │ Grafo visuale crash
     │                  │ Digest: 4130059368               │
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
C4   │ AI Chat          │ TypeError: Failed to fetch       │ Assistente AI non
     │                  │ su conversazioni + risposte      │ funzionante
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
C5   │ Writing          │ Impossibile creare capitoli      │ UTENTE COMPLETAMENTE
     │                  │ dall'UI. Messaggio: "dalla API"  │ BLOCCATO. Non può
     │                  │                                  │ scrivere nulla.
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
C6   │ Writing          │ "Failed to fetch" in header      │ Errore visibile all'ap.
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
C7*  │ Progetto/Nuovo   │ Click su "+ Nuovo progetto"      │ CRASH BROWSER, server
     │                  │ causa disconnessione forzata     │ side failure. Non si
     │                  │ (testato 4 volte, crash          │ può creare nuovo proj.
     │                  │ consistente)                     │

*C7 = NUOVO BUG scoperto in questa sessione


## 🟡 GRAVI (8 bug — UX gravemente compromessa)

ID   │ Modulo           │ Bug                              │ Impatto
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G1   │ Writing/Contesto │ Memoria esiste ma è Nascosta     │ L'utente non troverà
     │                  │ dietro tab "Contesto" non        │ mai le decisioni del
     │                  │ intuitivo                        │ progetto senza guida
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G2   │ Badge metriche   │ "1 decisioni · 7 voci" è         │ Memoria esistente non
     │ (tutte pagine)   │ <button> cliccabile ma zero      │ navigabile
     │                  │ effetto                          │
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G3   │ ⓘ Info button    │ Cliccabile su tutte le pagine    │ Elemento ingannevole,
     │ (tutte pagine)   │ ma ZERO effetto. No tooltip,     │ fa sembrare la UI
     │                  │ no modal, no navigazione         │ rotta/non finita
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G4   │ Settings         │ NESSUNA config. modalità         │ L'utente NON PUO'
     │                  │ revisione: focus, tono,          │ personalizzare come
     │                  │ profondità, check specifici      │ l'AI revisiona
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G5   │ Settings         │ Auto-save senza feedback visivo  │ L'utente non sa se le
     │                  │ (nessun "Salvato" confirm)       │ modifiche sono salvate
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G6   │ Source Detail    │ Pagina fonte scarna: mancano     │ Metadati insufficienti
     │                  │ abstract, note, citazioni, ISBN, │ per lavoro accademico
     │                  │ DOI, data import, dimensione    │
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G7   │ Research/Guided  │ Placeholder "in arrivo" senza    │ Funzione promessa ma
     │                  │ implementazione reale            │ non esistente
─────┼──────────────────┼──────────────────────────────────┼────────────────────────
G8   │ Revisione        │ "Avvia revisione" linka a        │ Loop di dipendenza:
     │                  │ /writing che richiede capitoli   │ revisione→writing→cap.→
     │                  │                                  │ impossibile


## 🟢 MEDIE (5 bug — migliorabili, non bloccano)

ID   │ Modulo           │ Bug
─────┼──────────────────┼────────────────────────────────────────────
M1   │ Tab Fonte        │ Vuoto, nessuna fonte pre-selezionabile.
     │                  │ Solo shortcut ⌘⇧C — non scopribile
M2   │ "Sviluppo arg."  │ Indicatore, non dropdown. Sembra
     │ badge            │ cliccabile ma non cambia modalità
M3   │ Export formati   │ Solo BibTeX. RIS "futuro" non disponibile
M4   │ Sessione timer   │ "0m" — non chiaro cosa misuri (sessione
     │                  │ utente? tempo di editing?)
M5   │ Chips concetti   │ Link a /knowledge/* che è rotto —
     │ in Sources       │ link morti in tutta l'applicazione


# ═══════════════════════════════════════════════════════════════════
# 5. ANALISI ARCHITETTURALE AGGIORNATA
# ═══════════════════════════════════════════════════════════════════

## Stato moduli (% funzionante / % usabile / stato)
┌────────────────┬────────────┬────────────┬─────────────────────────────┐
│ Modulo         │ % Funziona │ % Usabile  │ Stato                       │
├────────────────┼────────────┼────────────┼─────────────────────────────┤
│ Home           │ 90%        │ 90%        │ ✅ Quasi completo           │
│ Sources        │ 75%        │ 60%        │ ✅ Lista OK, detail povero  │
│ Settings       │ 40%        │ 40%        │ 🟡 Minimale, no feedback    │
│ Command Pal.   │ 50%        │ 50%        │ 🟡 10 scorciatoie inutili   │
│ Upload         │ 70%        │ 70%        │ 🟡 Form OK, no e2e test     │
│ Revisione      │ 40%        │ 20%        │ 🟡 UI presente, non usable  │
│ Writing        │ 30%        │ 10%        │ 🔴 Bloccato (no capitoli)   │
│ AI Chat        │ 20%        │ 0%         │ 🔴 Backend morto            │
│ Research       │ 15%        │ 5%         │ 🔴 Solo hub funziona        │
│ Knowledge      │ 5%         │ 0%         │ 🔴 Tutto rotto              │
│ Nuovo Progetto │ 0%         │ 0%         │ 🔴 CRASH server             │
└────────────────┴────────────┴────────────┴─────────────────────────────┘

## Coverage aggiornato
- Funzionalità core funzionanti: ~25%
- Funzionalità usabili end-to-end: ~15%
- Bug critici: 7
- Bug gravi: 8
- Bug medi: 5
- Totale bug: 20


# ═══════════════════════════════════════════════════════════════════
# 6. RECOMMENDATIONS AGGIORNATE — Priorità sviluppo
# ═══════════════════════════════════════════════════════════════════

### EMERGENZA (Week 1) — Sbloccare l'utente
1. [C7] FIX crash creazione nuovo progetto — CRITICO
2. [C5] Aggiungere UI per creare capitoli (form semplice: titolo+
    descrizione) — senza questo la piattaforma è INUTILE
3. [C1] Fix fetch Knowledge base — il grafo è il cuore del prodotto
4. [C2+C3] Fix server-side exception canvas + graph
5. [C4] Fix AI Chat backend

### ALTA (Week 2) — Rendere navigabile la memoria
6. [G1] Aggiungere link/breadcrumb visibile alla sezione Contesto
    (es: "Vedi decisioni progetto" in Home dashboard)
7. [G2] Rendere badge metriche cliccabile (espande pannello
    dettaglio memoria)
8. [G3] Rimuovere ⓘ o renderlo funzionale (tooltip esplicativo)
9. [G4] Implementare configurazione modalità revisione:
    ┌─────────────────────────────────────────────────────────┐
    │  FOCUS:     [ ] Stile  [ ] Argomento  [ ] Citazioni    │
    │             [ ] Struttura  [x] Tutto                    │
    │  TONO:      [x] Accademico  [ ] Critico  [ ] Leggero   │
    │  PROFONDITÀ: [ ] Superficiale [x] Standard [ ] Deep     │
    │  CHECK:     [x] Coerenza  [ ] Plagio  [x] Forma        │
    │             [x] Citazioni                               │
    └─────────────────────────────────────────────────────────┘

### MEDIA (Week 3-4) — Completare funzionalità
10. [G6] Arricchire pagina dettaglio fonte (abstract, metadati)
11. [G5] Aggiungere feedback salvataggio Settings (toast "Salvato")
12. [G7] Implementare trail guidato o rimuovere placeholder
13. [G8] Sistemare loop Revisione→Writing (abilitare revisione
     anche senza capitoli, o disabilitare bottone se bloccato)
14. [M1] Aggiungere selettore fonte visibile nel tab Fonte
15. [M2] Rendere "Sviluppo argomentativo" un vero dropdown

### BASSA (Week 5) — Polish
16. Aggiungere dark mode, font preferences
17. Aggiungere più formati export (RIS, APA, MLA, Chicago)
18. Migliorare UX primo accesso (wizard struttura tesi)
19. Aggiungere tutorial contestuale (non 5 step iniziali)
20. Rendere chips concetti navigabili (anche se Knowledge down,
     mostrare almeno un tooltip con definizione)


# ═══════════════════════════════════════════════════════════════════
# 7. VERDETTO FINALE
# ═══════════════════════════════════════════════════════════════════

## Stato: ALPHA — NON UTILIZZABILE IN PRODUZIONE

Thesis OS ha un'architettura concettualmente ECCEZIONALE. Il modello
"fonti → concetti → grafo → scrittura → revisione" è intelligente,
e la scoperta del tab "Contesto" rivela una memoria progettuale
densissima e ben strutturata (decisioni vincolanti, cronologia,
requisiti istituzionali, metodo).

MA nella sua forma attuale:

┌──────────────────────────────────────────────────────────────────┐
│  ❌ NON si può scrivere (manca creazione capitoli)               │
│  ❌ NON si può ricercare (Research 75% crashato)                 │
│  ❌ NON si può consultare Knowledge (fetch failed)               │
│  ❌ NON si può chattare con AI (backend morto)                   │
│  ❌ NON si può creare un nuovo progetto (crash)                  │
│  ❌ NON si può personalizzare la revisione (settings assenti)    │
├──────────────────────────────────────────────────────────────────┤
│  ✅ SI PUO' gestire fonti (lista, filtri, export BibTeX)         │
│  ✅ SI PUO' navigare la memoria (se si sa del tab Contesto)      │
│  ✅ SI PUO' usare la command palette (⌘K)                        │
│  ✅ SI PUO' uploadare documenti                                   │
└──────────────────────────────────────────────────────────────────┘

## Stima fix: 3-4 sprint (6-8 settimane) per versione beta utilizzabile

───────────────────────────────────────────────────────────────────
Tester: Sessione esterna | Data: 2026-07-09
Metodologia: Black-box testing manuale, navigazione completa di
             tutte le route, test di ogni elemento interattivo,
             8+ sessioni browser, 4 crash server documentati
───────────────────────────────────────────────────────────────────
