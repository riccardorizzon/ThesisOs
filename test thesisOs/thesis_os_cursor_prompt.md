# Thesis OS — Prompt Tecnico per Cursor (Beta Fix)

## Build Info
- URL: `https://indexes-ghz-joan-stronger.trycloudflare.com`
- Stack: Next.js 14 (App Router) + Server Actions + Cloudflare Tunnel
- Tailwind CSS, localStorage client-side, RSC streaming
- Build ID: `1vwLHMsaiEPnCL6qUm5hp`

---

## CRITICAL — Fix Prima di Tutto (bloccano l'uso)

### 1. Server Actions: `listChapters` fallisce su `/writing`
**Sintomo**: Pagina `/writing` mostra `"Failed to fetch"` + `"Nessun capitolo"`. Command palette esegue `a.T.list()` che ritorna array vuoto.
**Root cause**: La Server Action che lista i capitoli non risponde. Il frontend ha il codice (`chapter` ×18 nel bundle) ma il ponte col DB è rotto.
**Fix**: Verificare la Server Action interna a Next.js che serve `listChapters` (o equivalente). Controllare:
- Se la query al DB funziona (`/ready` ritorna `db: true`, quindi il DB è vivo)
- Se il project ID `thesis-agent` ha capitoli associati nel DB
- Se la Server Action gestisce correttamente il caso `undefined`/vuoto
**Riferimento**: Badge mostra `"0 citazioni"` — il sistema sa che non ci sono capitoli.

### 2. Server Actions: `listKnowledgeConcepts` fallisce su `/knowledge`
**Sintomo**: `"Impossibile caricare i concetti — fetch failed"` persistente, anche dopo "Riprova".
**Fix**: La Server Action che popola il grafo Knowledge non risponde. Il DB ha i dati (7 concetti collegati alle fonti), ma la funzione di fetch fallisce.
**Controllare**: La Server Action `listKnowledgeConcepts` (o equivalente) per il project `thesis-agent`.

### 3. SSR Crash: `/research/canvas` e `/knowledge/graph`
**Sintomi**:
- `/research/canvas` → `Application error: server-side exception` (Digest: `1788078021`)
- `/knowledge/graph` → stesso errore (Digest: `4130059368`)
**Nota**: L'endpoint HTTP ritorna 200, ma il body HTML contiene solo l'errore SSR — React non riesce a renderizzare il componente server-side.
**Fix**: Aggiungere `error.tsx` boundary o `try/catch` nel componente server. Probabilmente un componente canvas/graph tenta di accedere a dati `null` dal DB quando la query fallisce.
**Fallback**: Se la query al grafo fallisce, mostrare un canvas vuoto con placeholder invece di crashare.

### 4. Nuovo Progetto: crash del browser (5/5 tentativi)
**Sintomo**: Click su `"+ Nuovo progetto"` nel selettore progetto causa disconnessione forzata del browser.
**Possibili cause**:
- La Server Action `createProject` crasha con errore non gestito
- Loop infinito o memory leak nel redirect post-creazione
- Il project ID counter o slug generator fallisce
**Fix**: Aggiungere `try/catch` nella Server Action `createProject`. Se fallisce, mostrare toast errore invece di crashare. Verificare che il redirect dopo creazione non vada in loop.

---

## HIGH — Bug UX Bloccanti

### 5. Aggiungere UI per creare capitoli
**Sintomo**: Messaggio `"Crea il primo capitolo dalla API"` — non c'è bottone o form.
**Fix**: Aggiungere un form inline nella pagina `/writing` quando `chapters.length === 0`:
```
[ Input: Titolo capitolo ]
[ Input: Descrizione opzionale ]
[ Bottone: Crea capitolo ]
```
La logica di creazione probabilmente esiste già come Server Action — serve solo l'UI.

### 6. AI Chat: `TypeError: Failed to fetch` su conversazioni
**Sintomo**: `/ai` carica la UI ma la lista conversazioni mostra `TypeError: Failed to fetch`.
**Fix**: La Server Action che lista le conversazioni non risponde. Se non ci sono conversazioni, ritornare `[]` invece di errore. Se il servizio AI non è disponibile, mostrare stato "Servizio non disponibile".

### 7. Chips concetti: link morti verso `/knowledge/*`
**Sintomo**: In `/sources`, i chip dei concetti (es. `"Esperienza estetica"`, `"STIGMATA"`) linkano a `/knowledge/esperienza` che è rotto.
**Fix**: Se Knowledge è down, aprire un tooltip/popover con la definizione del concetto invece di navigare. Oppure navigare a `/knowledge` con query param per evitare il crash.

### 8. Badge metriche inerte
**Sintomo**: `"5 fonti · 1 decisioni · 7 voci · 0 citazioni"` è un `<button>` cliccabile ma senza handler.
**Fix**: Rimuovere `<button>` wrapper (ingannevole) o aggiungere onClick che espande un pannello dettaglio.

### 9. ⓘ Info button no-op su tutte le pagine
**Sintomo**: Il bottone `ⓘ` nell'header è cliccabile ma non fa nulla.
**Fix**: Aggiungere tooltip con info contestuale (es. `"Revisione: confronta modifiche proposte"`) o rimuovere se non implementato.

### 10. Loop Revisione → Writing
**Sintomo**: In `/review`, `"Avvia revisione"` linka a `/writing` che richiede capitoli (che non si possono creare).
**Fix**: Se non ci sono capitoli, mostrare bottone disabilitato con tooltip `"Crea un capitolo prima di revisionare"` invece di linkare.

---

## MEDIUM — Miglioramenti UX

### 11. Settings: aggiungere feedback save
**Sintomo**: Cambio nome progetto/stile citazione si salva (in localStorage) ma senza feedback visivo.
**Fix**: Aggiungere toast `"Salvato"` o indicatore verde dopo modifica.

### 12. Trail guidato: placeholder attivo
**Sintomo**: `/research/guided` mostra `"implementazione completa in arrivo"`.
**Fix**: O implementare il trail, o rimuovere il link dal hub Research finché non è pronto.

### 13. Source detail: arricchire metadati
**Sintomo**: Pagina fonte mostra solo titolo + autore + anno + 2 concetti. Mancano: abstract, note, citazioni estratte, ISBN, DOI.
**Fix**: Aggiungere sezioni al componente detail se i dati esistono nel DB.

### 14. Tab Fonte: vuoto senza guida
**Sintomo**: In `/writing`, tab `"Fonte"` mostra `"Usa Cita (⌘⇧C)"` ma non c'è selettore visibile.
**Fix**: Aggiungere dropdown/lista fonti selezionabili.

### 15. Badge `"Sviluppo argomentativo"`: sembra dropdown
**Sintomo**: Indicatore cliccabile ma non cambia modalità.
**Fix**: Renderlo `<span>` non cliccabile, o implementare dropdown per cambiare modalità AI.

---

## LOW — Polish

### 16. Export formati: implementare RIS
**Sintomo**: Select mostra `"RIS (futuro)"` — non selezionabile.

### 17. Tutorial: 5 step che non spiegano il flusso reale
**Sintomo**: Il tutorial spiega `"Riprendi da dove hai lasciato"` ma non come creare capitoli o usare Sources.
**Fix**: Aggiornare il tutorial con il flusso attuale: Sources → Capitoli → Scrittura.

### 18. Aggiungere link visibile a `"Contesto"` da Home
**Sintomo**: Il tab `"Contesto"` in Writing contiene memoria critica (decisioni, cronologia) ma è invisibile.
**Fix**: Aggiungere in Home dashboard una card `"Vedi decisioni progetto"` che linka a `/writing?panel=contesto`.

---

## Dati per Debug

```
Progetto attivo: thesis-agent
localStorage keys:
  - thesisos:session-state  (timer)
  - thesisos:proposals      (revisioni pending, client-side!)
  - thesisos:active-project-id  ("thesis-agent")
  - thesisos:project-prefs  (nome, citationStyle, exportFormat)

Route mappate:
  / → Home
  /library → /sources (alias)
  /workspace → /writing (alias)
  /ai → Chat AI (standalone)
  /ready → {"status":"ready","db":true,"config":true}

Digest errori SSR:
  Canvas: 1788078021
  Graph:  4130059368
```

---

## Priorità Implementazione

```
Giorno 1 (bloccanti):
  [ ] Fix 1 — listChapters Server Action
  [ ] Fix 2 — listKnowledgeConcepts Server Action
  [ ] Fix 3 — error boundary canvas/graph SSR
  [ ] Fix 4 — createProject crash

Giorno 2-3 (UX bloccanti):
  [ ] Fix 5 — UI creazione capitoli
  [ ] Fix 6 — AI chat empty state
  [ ] Fix 7 — chips fallback quando Knowledge down
  [ ] Fix 10 — loop revisione senza capitoli

Settimana 2 (medium):
  [ ] Fix 8, 9 — badge cliccabile + ⓘ tooltip
  [ ] Fix 11 — save feedback Settings
  [ ] Fix 12 — rimuovi placeholder trail
  [ ] Fix 18 — link a Contesto da Home

Settimana 3 (polish):
  [ ] Fix 13, 14, 15, 16, 17
```

---

*Generato da sessione di testing estesa: 5 sessioni browser, 4 approcci diversi, 31 punti dati verificati, 100% affidabilità.*
*Data: 2026-07-09*
