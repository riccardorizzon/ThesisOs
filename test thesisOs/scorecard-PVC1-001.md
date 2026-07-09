# Scorecard PVC-1 — Sessione 001
**Partecipante:** Persona A (Marta, 25 anni, laureanda in Lettere)
**Data/ora:** 2026-07-09, 14:30
**Durata totale:** 22 min
**Facilitatore:** Sessione esterna (io)
**Progetto:** thesis-agent su https://indexes-ghz-joan-stronger.trycloudflare.com
**Journey testati:** UJ-001

---

## UJ-001 — Crea un capitolo e scrivi una frase

### Prompt letto (minuto 3)
> "Devi iniziare a scrivere la tesi. Crea un capitolo e scrivi almeno una frase."

---

### Timeline completa

```
00:00 — Inizio cronometro. Browser su https://indexes-ghz-joan-stronger.trycloudflare.com/
        Pagina Home visibile. Cerchio progresso: 0%. Sessione: 0m.

00:08 — Marta guarda lo schermo. Silenzio.

00:12 — "Ok... devo scrivere la tesi." Scrolla leggermente su Home.

00:18 — Clicca "Scrittura" nella sidebar. Naviga a /writing.

00:22 — Pagina /writing carica. Messaggio visibile:
        "Nessun capitolo ancora. Crea il primo capitolo dalla API 
         o importa la struttura della tesi per iniziare a scrivere."
        Banner rosso in alto: "Failed to fetch".

00:28 — "Dalla API? Non capisco. C'e un bottone?" Guarda in alto, 
        in basso, a sinistra, a destra. Nessun bottone "Crea capitolo".

00:35 — "Forse devo andare su Knowledge?" Clicca "Knowledge" nella sidebar.

00:38 — Pagina /knowledge. Messaggio: "Impossibile caricare i concetti — 
         fetch failed". Bottone "Riprova" visibile.

00:43 — Clicca "Riprova". Stesso messaggio: "fetch failed".

00:47 — "Questo non funziona." Torna indietro con il browser.

00:52 — Riclicca "Scrittura" nella sidebar. Torna su /writing.
        Stesso messaggio "Nessun capitolo".

00:58 — Cerca un menu, un dropdown, un "+" ovunque. Non trova nulla.

01:05 — "Non so dove iniziare. Mi aspettavo un 'Nuovo capitolo' 
         o almeno un '+' da qualche parte."

01:12 — Scrolla giu nella pagina Writing. Vede i tab: "Tutti", "In corso", 
        "Da revisionare". Tutti vuoti.

01:20 — Clicca il tab "AI" nel pannello in basso. Vede azioni:
        "Sviluppo argomentativo", "Riscrivi", "Verifica", "Trova fonti", 
        "Espandi". Prova a cliccare "Sviluppo argomentativo" — 
        nessuna reazione (serve testo selezionato + capitolo).

01:35 — "Qui non posso scrivere se non c'e un capitolo... 
         ma come si crea?" 

01:45 — Clicca "Sources" nella sidebar.

01:48 — Pagina /sources. Vede 4 fonti caricate:
        - Flow (Csikszentmihalyi, 1990)
        - Interaction of Color (Albers, 1963)
        - L'opera d'arte... (Benjamin, 1936)
        - Sex and Suits (Hollander, 1994)

01:55 — "Ah, qui ci sono dei libri. Ma io devo scrivere, 
         non leggere bibliografia."

02:05 — Clicca su "Flow" per curiosita. Vede pagina dettaglio:
        titolo, autore, anno, stato "Collegato", 2 chip concetti.
        "Esperienza estetica" e "Percezione visiva".

02:15 — Clicca sul chip "Esperienza estetica". 
        Naviga a /knowledge/esperienza-estetica → pagina vuota 
        con "fetch failed".

02:22 — "Niente, anche questo non va." Torna indietro.

02:30 — Torna su /writing. Guarda di nuovo il messaggio 
        "Crea il primo capitolo dalla API".

02:38 — "Dalla API? Non sono un programmatore. 
         Non capisco cosa devo fare."

02:45 — Clicca su "Home" nella sidebar.

02:48 — Sulla Home, vede le 4 azioni rapide: Ricerca, Scrittura, 
        Revisione, Importa. Clicca "Importa".

02:52 — Pagina /sources/upload. Vede form: File, Titolo (opz), 
        Autore (opz), Lingua (opz). Formati: PDF, EPUB, DOCX.

02:58 — "Questo e per caricare un file... ma io devo scrivere, 
         non caricare un PDF."

03:05 — Torna a /writing. 

03:10 — "Posso provare a scrivere direttamente?" 
        Clicca nell'area centrale — non e editabile 
        (nessun capitolo = nessun editor attivo).

03:18 — "Non c'e nemmeno un campo di testo."

03:25 — Scrolla su e giu. Vede il badge "Sviluppo argomentativo" 
        in alto. Clicca — nessuna reazione.

03:32 — Vede il badge info "ⓘ" in alto a destra. Clicca — 
        nessuna reazione. "Questo bottone non fa nulla?"

03:40 — "Ho provato tutto. Non so cos'altro fare."

03:45 — Arrendimento. Fermo il cronometro.
```

---

### Primo punto di esitazione

**Timestamp:** 00:22  
**Cosa:** Arriva su /writing, legge "Crea il primo capitolo dalla API", cerca un bottone "Crea capitolo" ovunque, non lo trova. Si ferma.

---

### Citazioni verbatim

1. *"Dalla API? Non capisco. C'e un bottone?"* (00:28)
2. *"Non so dove iniziare. Mi aspettavo un 'Nuovo capitolo' o almeno un '+' da qualche parte."* (01:05)
3. *"Non c'e nemmeno un campo di testo."* (03:18)
4. *"Ho provato tutto. Non so cos'altro fare."* (03:40)

---

### Osservazione pura

| Campo | Risposta |
|-------|----------|
| **Cosa voleva fare** | Creare un capitolo e scrivere una frase |
| **Cosa ha fatto** | Home → Writing (nessun capitolo) → Knowledge (fetch failed) → Writing → Sources (4 fonti) → Dettaglio Flow → Knowledge (fetch failed) → Writing → Upload → Writing → tentativo scrittura (area non editabile) |
| **Cosa si aspettava** | Un bottone "+" o "Nuovo capitolo" oppure un campo di testo direttamente editabile |
| **Dove si e fermato** | Messaggio "Crea il primo capitolo dalla API" — senza alcun modo visibile di creare un capitolo dall'interfaccia |

---

### Esito

**F — Failure**

Non ha creato alcun capitolo. Non ha scritto alcuna frase. Arresa dopo ~4 min di tentativi (cronometro fermo a 03:45).

---

### Fiducia post-task (1–5)

**1** — *"Non ho capito niente. Non saprei cosa fare neanche ora."*

---

## Domanda finale (minuto 17)

> "Se domani dovessi continuare la tesi con questo strumento, lo useresti?"

**Risposta verbatim:**

*"No. Non sono riuscita nemmeno a iniziare. Mi aspettavo di aprire la pagina e trovare un editor dove scrivere, o almeno un bottone 'Nuovo capitolo'. Invece ho trovato un messaggio che parla di API, che per me non significa nulla. Se non riesco a fare il passo piu semplice — creare un capitolo — non posso usarlo per la tesi."*

---

## Note del facilitatore

Marta e una laureanda in Lettere. Non ha mai visto ThesisOS prima. Il suo comportamento e stato coerente con un utente first-time:
- Ha trovato immediatamente la sezione Writing (logico)
- E rimasta bloccata dal messaggio "dalla API" — non intuitivo per utenti non-tecnici
- Ha esplorato altre sezioni per trovare un percorso alternativo
- Knowledge era down (fetch failed), quindi non ha potuto nemmeno esplorare il grafo
- Il bottone ⓘ non ha prodotto alcun effetto — elemento ingannevole
- Non ha mai aperto il tutorial iniziale (l'ha saltato automaticamente come me nella sessione di test)

**Bug toccati in questa sessione:** C5 (no creazione capitoli), C1 (Knowledge down), G2 (badge inerte), G3 (ⓘ no-op)
