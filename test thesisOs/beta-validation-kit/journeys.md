# User Journeys — PVC-1

Leggi al partecipante **solo** il testo in * corsivo* sotto "Prompt utente".  
Il resto è per il facilitatore.

Ordine consigliato: UJ-001 → UJ-002 → UJ-003 → … (north star per prima).

---

## UJ-001 — First Chapter Creation ⭐ North star

**Domanda:** Riesco a creare il mio primo capitolo e iniziare a scrivere?

| | |
|---|---|
| **Partenza** | Home `/` — progetto `thesis-agent` già selezionato |
| **Prompt utente** | *"Devi iniziare a scrivere la tesi. Crea un capitolo e scrivi almeno una frase."* |
| **Successo** | Capitolo creato **dall'UI** + testo visibile nell'editor |
| **Parziale** | Trova un capitolo esistente ma non ne crea uno nuovo |
| **Fallimento** | Non capisce come procedere; chiede aiuto; legge messaggio "dalla API" |

**Osserva:** Naviga verso Writing da solo? Cerca un bottone "Crea"? Usa ⌘K?

**Ex-bug:** C5 — **non dire al partecipante**

---

## UJ-002 — Upload a source

**Domanda:** Riesco a caricare o aggiungere una fonte bibliografica?

| | |
|---|---|
| **Partenza** | Home `/` |
| **Prompt utente** | *"Aggiungi una nuova fonte alla tua bibliografia — un articolo o un libro a scelta."* |
| **Successo** | Fonte visibile in Sources dopo l'operazione |
| **Parziale** | Trova upload ma non completa; o aggiunge metadata senza file |
| **Fallimento** | Non trova dove caricare fonti |

**Osserva:** Va su Sources? Trova `/sources/upload`? Capisce il form?

---

## UJ-003 — Find a concept in Knowledge

**Domanda:** Capisco cos'è Knowledge e riesco a trovare un concetto?

| | |
|---|---|
| **Partenza** | Home `/` |
| **Prompt utente** | *"Trova il concetto 'Aura' (o un concetto legato alla tua ricerca) e leggine la descrizione."* |
| **Successo** | Apre scheda concetto con titolo e descrizione |
| **Parziale** | Vede la lista concetti ma non apre il dettaglio |
| **Fallimento** | Pagina errore; "fetch failed"; non capisce cos'è Knowledge |

**Osserva:** Capisce la differenza Knowledge vs Sources?

---

## UJ-004 — Open the research canvas

**Domanda:** Riesco ad aprire la mappa concettuale (canvas)?

| | |
|---|---|
| **Partenza** | Home `/` |
| **Prompt utente** | *"Apri la mappa visuale della tua ricerca — il canvas dove vedi i concetti collegati."* |
| **Successo** | Canvas visibile, navigabile (pan/zoom o nodi visibili) |
| **Parziale** | Trova la pagina ma canvas vuoto o non interagisce |
| **Fallimento** | Errore server; pagina bianca; non trova il canvas |

**Percorso tipico:** Research → Canvas, oppure link da Knowledge.

---

## UJ-005 — Explore the knowledge graph

**Domanda:** Riesco a esplorare il grafo delle relazioni tra concetti?

| | |
|---|---|
| **Partenza** | `/knowledge` (dopo UJ-003, o direttamente) |
| **Prompt utente** | *"Mostra come sono collegati tra loro almeno due concetti — apri il grafo."* |
| **Successo** | Grafo visuale con nodi/archi |
| **Parziale** | Pagina carica ma grafo vuoto o illeggibile |
| **Fallimento** | Crash; errore digest; non trova il link "Grafo" |

---

## UJ-006 — Start an AI conversation

**Domanda:** Riesco ad avviare o riprendere una chat con l'assistente AI?

| | |
|---|---|
| **Partenza** | Home `/` |
| **Prompt utente** | *"Chiedi all'assistente AI un consiglio su come strutturare il primo capitolo."* |
| **Successo** | Messaggio inviato + risposta visibile (o conversazione esistente aperta) |
| **Parziale** | Vede UI chat ma invio fallisce |
| **Fallimento** | "Failed to fetch"; pagina vuota; non trova AI |

**Osserva:** Sidebar → AI? ⌘K?

---

## UJ-007 — Start a revision

**Domanda:** Riesco ad avviare una revisione del testo?

| | |
|---|---|
| **Partenza** | Home `/` |
| **Prompt utente** | *"Fai revisionare un capitolo — avvia una revisione e capisci cosa propone il sistema."* |
| **Successo** | Flusso revisione avviato con proposta o feedback visibile |
| **Parziale** | Arriva su Revisione ma non completa; loop verso Writing |
| **Fallimento** | Non trova Revisione; bloccato su "serve un capitolo" |

**Osserva:** Capisce il legame Revisione ↔ Writing?

---

## UJ-008 — Find project memory and decisions

**Domanda:** Capisco dove sono le decisioni e la memoria del progetto?

| | |
|---|---|
| **Partenza** | Home `/` — **senza** dire dove guardare |
| **Prompt utente** | *"Il sistema dice che c'è '1 decisione' nel progetto. Trovala e leggila."* |
| **Successo** | Legge almeno una decisione vincolante |
| **Parziale** | Trova qualcosa in Contesto ma non la decisione specifica |
| **Fallimento** | Clicca badge inerte; non trova Contesto; si arrende |

**Osserva:** Badge header cliccato? Tab Contesto in Writing?

---

## UJ-009 — Create a new project

**Domanda:** Riesco a creare un nuovo progetto?

| | |
|---|---|
| **Partenza** | Home `/` |
| **Prompt utente** | *"Crea un nuovo progetto chiamato 'Test PVC' per una tesi di prova."* |
| **Successo** | Nuovo progetto selezionato e UI coerente |
| **Parziale** | Form trovato ma errore gestito (banner) |
| **Fallimento** | Crash browser; impossibile procedere |

**Nota facilitatore:** se crash, interrompi scenario e segna Fallimento — riprendi dopo refresh.

---

## UJ-010 — Navigate the app confidently

**Domanda:** Dopo 30 minuti, so dove andare per le attività principali?

| | |
|---|---|
| **Partenza** | Fine sessione (debrief) |
| **Prompt utente** | *"Senza cliccare: dove andresti per (a) scrivere, (b) le fonti, (c) i concetti, (d) l'AI?"* |
| **Successo** | 4/4 risposte corrette |
| **Parziale** | 2–3 corrette |
| **Fallimento** | 0–1 corrette; esprime confusione generale |

**Metrica:** Fiducia navigazione (1–5) — sempre in debrief.

---

## Riepilogo priorità prodotto

| Priorità | Journey | Perché |
|----------|---------|--------|
| P0 | UJ-001 | Senza capitolo, nessun flusso writing/revisione |
| P0 | UJ-008 | Memoria esiste ma invisibile — scoperta chiave beta V2 |
| P1 | UJ-002, UJ-003 | Corpus e knowledge sono il cuore del prodotto |
| P1 | UJ-007 | Revisione è value prop distintivo |
| P2 | UJ-004, UJ-005, UJ-006 | Research e AI — importanti ma dopo il core |
| P2 | UJ-009 | Edge case multi-progetto |
