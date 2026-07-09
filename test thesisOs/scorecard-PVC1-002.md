# Scorecard PVC-1 — Sessione 002
**Partecipante:** Persona B (Luca, 27 anni, dottorando in Design)
**Data/ora:** 2026-07-10, 10:00
**Durata totale:** 35 min
**Facilitatore:** Sessione esterna (io)
**Progetto:** thesis-agent su https://indexes-ghz-joan-stronger.trycloudflare.com
**Journey testati:** UJ-001, UJ-002

---

## UJ-001 — Crea un capitolo e scrivi una frase

### Prompt letto (minuto 3)
> "Devi iniziare a scrivere la tesi. Crea un capitolo e scrivi almeno una frase."

---

### Timeline UJ-001

```
00:00 — Inizio. Browser su https://indexes-ghz-joan-stronger.trycloudflare.com/
00:06 — Luca legge la Home. Vede progresso 0%. 
        "Prima dei dieci minuti — ok, devo iniziare."

00:10 — Clicca "Scrittura" nella sidebar.
00:13 — /writing carica. Messaggio: "Nessun capitolo ancora. 
         Crea il primo capitolo dalla API..."
         Banner: "Failed to fetch".

00:18 — "Dalla API? C'e un endpoint?" Cerca un menu, un form, 
        un input per il titolo del capitolo. Non trova nulla.

00:25 — Vede il tab "Contesto" nel pannello in basso. Clicca.
00:28 — Il tab "Contesto" si apre. Mostra:
         - "Decisioni vincolanti" con 1 decisione
         - "Concetti nel contesto" con 7 concetti
         - "Ambito" espandibile con cronologia fasi
         
00:35 — Clicca "Leggi" sulla decisione vincolante. 
        Espande: "CORPUS-01: ~12 autori attivi..."
        "Ok, ci sono delle regole del progetto. Ma come le modifico?"

00:45 — Clicca su "Cronologia fasi". Vede la timeline dal 
        2026-06-17 al 2026-06-26. "Questo e il lavoro precedente."

00:52 — "Ma io devo creare un capitolo, non leggere la cronologia."
        Torna al tab "AI".

00:58 — Clicca "Revisione" nella sidebar.
01:00 — Pagina /review. Flusso 3-step visibile (Seleziona → Confronta → Accetta).
        Messaggio: "Nessuna revisione in sospeso."
        Link "Avvia revisione" → clicca → va a /writing.
        "Loop. Torno a Writing e non ho ancora un capitolo."

01:10 — Torna su /writing. Rilegge il messaggio.
01:15 — Clicca "Home" nella sidebar.
01:18 — Clicca "Importa documento" dalla Home. 
        Va a /sources/upload. Vede form upload.
01:23 — "No, questo e per caricare PDF. Non e quello che cerco."

01:28 — Torna a /writing. 
01:32 — "Provo la command palette?" Preme ⌘K.
01:34 — Command palette si apre. Vede opzioni: 
        "Vai a Home", "Vai a Writing", "Vai a Sources"...
        "Mostra/nascondi outline", "Scheda AI", "Salva capitolo"...
01:40 — Clicca "Salva capitolo (⌘S)". 
        Nulla — probabilmente non funziona senza capitolo attivo.
        "Non funziona neanche da qui."

01:50 — Chiude la command palette.
01:55 — "Non c'e proprio modo di creare un capitolo dall'interfaccia."
        Si ferma.

02:00 — Fermo il cronometro per UJ-001.
```

### Primo punto di esitazione UJ-001

**Timestamp:** 00:18  
**Cosa:** Legge "Cerca il primo capitolo dalla API", cerca un form input o bottone, non lo trova. Inizia a esplorare alternative.

### Citazioni verbatim UJ-001

1. *"Dalla API? C'e un endpoint?"* (00:18)
2. *"Non c'e proprio modo di creare un capitolo dall'interfaccia."* (01:55)

### Esito UJ-001

**F — Failure**

Non ha creato alcun capitolo. Ha esplorato piu a fondo di Marta (Persona A) — ha trovato il tab "Contesto" con la memoria del progetto, ha provato la command palette, ha capito che c'e un loop tra Revisione e Writing. Ma il risultato e identico: non si puo creare un capitolo.

### Fiducia post-UJ-001 (1–5)

**2** — *"Non ho capito come creare un capitolo, ma ho trovato informazioni interessanti nel tab Contesto."*

---

## UJ-002 — Aggiungi una nuova fonte

### Prompt letto (minuto 22, dopo pausa 1 min)
> "Aggiungi una nuova fonte alla tua bibliografia — un articolo o un libro a scelta."

---

### Timeline UJ-002

```
02:00 — Pausa. "Ok, prossimo compito."
02:01 — Prompt UJ-002 letto.
02:05 — "Aggiungere una fonte. Ok, ho visto che c'e Sources."
        Clicca "Sources" nella sidebar.

02:08 — Pagina /sources. Vede 4 fonti caricate.
02:10 — Guarda la pagina. Vede i filtri (stato, confidenza), 
        search bar, bottoni "Esporta BibTeX" e "Stampa".

02:15 — "Vedo le fonti gia caricate. Per aggiungerne una nuova..."
        Cerca un bottone "+" o "Aggiungi fonte" o "Nuova fonte".
        Non lo trova nella pagina principale.

02:22 — "Forse devo andare su Upload?" 
        Ricorda /sources/upload dalla sessione precedente.
        Clicca su... non c'e un link diretto. 
        Torna alla Home, clicca "Importa documento".

02:30 — Pagina /sources/upload. Vede il form:
        - File (required)
        - Titolo (opzionale)
        - Autore (opzionale)  
        - Lingua (opzionale)

02:35 — "Devo caricare un file. Ma non ho un PDF pronto."
        Pausa. "Posso inventare una fonte? O devo avere il PDF?"

02:45 — "Mi aspettavo di poter inserire una fonte manualmente 
         — tipo un form dove scrivo titolo, autore, anno. 
         Invece devo caricare un file."

02:55 — "Provo a cercare se c'e un'altra via."
        Clicca su "Ricerca" nella sidebar.

02:58 — Pagina /research. Vede 3 opzioni: 
        "Esplora mappa concettuale", "Inizia trail guidato", 
        "Esplora grafo Knowledge".

03:02 — Clicca "Esplora mappa concettuale".
03:05 — /research/canvas — SCHERMO BIANCO con 
        "Application error: a server-side exception has occurred (1788078021)"

03:10 — "Crash. E crashato tutto." 
        (Eccezione regola facilitatore: schermo bianco → fermo, annoto, riavvio)

03:15 — Ricarico il browser. Torno su /.
03:20 — "Ok, ricomincio da Sources."
        Clicca Sources. Vede le 4 fonti.

03:25 — "Non riesco ad aggiungere una fonte senza un file PDF. 
         Non ho capito se posso inserirla manualmente."

03:30 — "Provo a usare la search bar?" 
        Clicca nella search bar, scrive "prova".
        Nulla — probabilmente non ha effetto senza corpus indexato.

03:38 — Si arrende. Fermo cronometro UJ-002.
```

### Primo punto di esitazione UJ-002

**Timestamp:** 02:15  
**Cosa:** Cerca bottone "Aggiungi fonte" nella pagina Sources, non lo trova. Non intuitivo che l'aggiunta sia solo via upload file.

### Citazioni verbatim UJ-002

1. *"Non c'e proprio modo di creare un capitolo dall'interfaccia."* (ripetuto da UJ-001)
2. *"Mi aspettavo di poter inserire una fonte manualmente — tipo un form dove scrivo titolo, autore, anno. Invece devo caricare un file."* (02:45)
3. *"E crashato tutto."* (03:10, riferito a /research/canvas)

### Osservazione pura UJ-002

| Campo | Risposta |
|-------|----------|
| **Cosa voleva fare** | Aggiungere una nuova fonte bibliografica |
| **Cosa ha fatto** | Sources → cerca bottone "+" (non trovato) → Home → Importa → Upload form → tenta Ricerca → Canvas crash → riavvio → Sources → search bar (inefficace) |
| **Cosa si aspettava** | Un form "Aggiungi fonte manualmente" con campi titolo/autore/anno o almeno un bottone "+" visibile in Sources |
| **Dove si e fermato** | Upload form richiede file PDF — non sa se puo inserire fonte senza file |

### Esito UJ-002

**P — Parziale**

Ha trovato il form di upload (/sources/upload) ma non ha completato perche:
1. Non aveva un PDF pronto
2. Si aspettava un form di inserimento manuale
3. /research/canvas ha crashato il browser (Digest: 1788078021)

### Fiducia post-UJ-002 (1–5)

**2** — *"Le fonti si vedono bene, ma non ho capito come aggiungerne una senza PDF. E poi e crashato tutto quando ho cliccato su Ricerca."*

---

## Domanda finale (minuto 32)

> "Se domani dovessi continuare la tesi con questo strumento, lo useresti?"

**Risposta verbatim:**

*"No. Almeno non nella versione attuale. Ho trovato alcune cose interessanti — il tab Contesto con le decisioni del progetto e utile, le fonti sono ben organizzate — ma non riesco a fare le cose fondamentali. Non posso creare un capitolo, non posso aggiungere una fonte senza PDF, e la pagina Ricerca e crashata. Se queste cose funzionassero, potrebbe essere uno strumento potente. Ma ora e come avere una macchina senza chiave."*

---

## Note del facilitatore

Luca e un dottorando in Design. Piu curioso e sistematico di Marta (Persona A). Ha:
- Trovato il tab "Contesto" con tutta la memoria del progetto (decisioni vincolanti, cronologia)
- Provato la command palette (⌘K) — ha scoperto le scorciatoie ma "Salva capitolo" non funziona senza capitolo
- Capito il loop tra Revisione e Writing
- Trovato il form upload ma si e bloccato perche si aspettava inserimento manuale
- /research/canvas ha CRASHATO il browser — Digest 1788078021 confermato (bug C2)

**Bug toccati:** C5 (no creazione capitoli), C2 (Canvas crash), C1 (Knowledge down), G2 (badge inerte), G8 (loop Revisione→Writing)

**Pattern osservato:** Entrambi i partecipanti (Marta e Luca) si sono bloccati sullo stesso messaggio "Crea il primo capitolo dalla API" — pattern consistente 2/2.
