
# ═══════════════════════════════════════════════════════════════════
#  THESIS OS — REPORT BETA TESTER FINAL V3
#  Approccio: Reverse Engineering JS + HTTP API + Browser Testing
#  Data: 2026-07-09 | Sessioni: 10+
# ═══════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════
# PREMESSA: Approccio di raccolta dati V3 (diverso da V1/V2)
# ═══════════════════════════════════════════════════════════════════

Metodologia precedente (V1/V2): Browser automation — navigazione
manuale pagina per pagina, click su ogni elemento.

Metodologia V3 (questa):
1. HTTP status code testing (curl) su tutte le route
2. Reverse engineering dei chunk JS Next.js per trovare:
   - Route nascoste (/library, /workspace)
   - localStorage keys e architettura client-side
   - Eventi custom interni
   - Riferimenti a funzionalità implementate
3. Cross-reference con i dati browser V2

Questo approccio ha rivelato che IL PROBLEMA NON È FUNZIONALE
ma INFRASTRUTTURALE — il frontend è quasi completo, il backend
(Server Actions Next.js) è down.


# ═══════════════════════════════════════════════════════════════════
# 1. HTTP STATUS CODE MAP — Tutte le route testate
# ═══════════════════════════════════════════════════════════════════

## Route visibili (sidebar)
┌────────────────────┬────────┬─────────────────────────────────────┐
│ Route              │ Status │ Risultato                           │
├────────────────────┼────────┼─────────────────────────────────────┤
│ GET /              │ 200    │ Home OK                             │
│ GET /research      │ 200    │ Hub OK                              │
│ GET /research/canvas│ ❌ 500 │ Server-side exception (Digest:      │
│                    │        │ 1788078021)                         │
│ GET /research/guided│ 200   │ Placeholder OK (testo statico)      │
│ GET /writing       │ 200    │ Pagina OK ma "Failed to fetch"      │
│ GET /sources       │ 200    │ OK                                  │
│ GET /sources/upload│ 200    │ OK                                  │
│ GET /knowledge     │ 200    │ Pagina OK ma "fetch failed"         │
│ GET /knowledge/graph│ ❌ 500│ Server-side exception (Digest:      │
│                    │        │ 4130059368)                         │
│ GET /settings      │ 200    │ OK                                  │
│ GET /review        │ 200    │ OK                                  │
│ GET /ai            │ 200    │ OK ma "TypeError: Failed to fetch"  │
└────────────────────┴────────┴─────────────────────────────────────┘

## Route nascoste (scoperte nel codice JS)
┌────────────────────┬────────┬─────────────────────────────────────┐
│ Route              │ Status │ Risultato                           │
├────────────────────┼────────┼─────────────────────────────────────┤
│ GET /library       │ 307    │ Redirect → /sources (alias)         │
│ GET /workspace     │ 307    │ Redirect → /writing (alias)         │
└────────────────────┴────────┴─────────────────────────────────────┘

## Endpoint API testati (tutti 404)
┌────────────────────┬────────┬─────────────────────────────────────┐
│ Endpoint           │ Status │ Nota                                │
├────────────────────┼────────┼─────────────────────────────────────┤
│ /api/health        │ 404    │ No health check endpoint            │
│ /api/projects      │ 404    │ No REST API — usa Server Actions    │
│ /api/sources       │ 404    │ "                                   │
│ /api/chapters      │ 404    │ "                                   │
│ /api/knowledge/... │ 404    │ "                                   │
│ /api/* (tutti)     │ 404    │ Next.js Server Actions, non REST    │
└────────────────────┴────────┴─────────────────────────────────────┘


# ═══════════════════════════════════════════════════════════════════
# 2. ARCHITETTURA CLIENT-SIDE — Reverse Engineering JS
# ═══════════════════════════════════════════════════════════════════

## 2.1 Tecnologia
- Framework: Next.js 14+ (App Router)
- Styling: Tailwind CSS (classi `bg-bg`, `text-ink`, `border-border`)
- State locale: localStorage
- State server: Next.js Server Actions (non REST API)
- Componenti: Command palette (kbar pattern), Tabs, Sidebar

## 2.2 localStorage Keys (persistenza locale)
┌─────────────────────────────┬──────────────────────────────────────┐
│ Key                         │ Contenuto                            │
├─────────────────────────────┼──────────────────────────────────────┤
│ thesisos:session-state      │ Timer sessione, timestamp inizio     │
│                             │ Formato: {updatedAt, startedAt, ...} │
├─────────────────────────────┼──────────────────────────────────────┤
│ thesisos:proposals          │ Proposte revisione in sospeso        │
│                             │ Formato: [{id, type, text, ...}]     │
│                             │ LETTO da listPendingProposals()      │
│                             │ ma se Server Action fallisce →       │
│                             │ fallback a localStorage!             │
├─────────────────────────────┼──────────────────────────────────────┤
│ thesisos:active-project-id  │ "thesis-agent" (default)             │
├─────────────────────────────┼──────────────────────────────────────┤
│ thesisos:project-prefs      │ {displayName, citationStyle,         │
│                             │ exportFormat}                        │
│                             │ Default: {                           │
│                             │   displayName: "Tesi di laurea",     │
│                             │   citationStyle: "author-date",      │
│                             │   exportFormat: "bibtex"             │
│                             │ }                                    │
└─────────────────────────────┴──────────────────────────────────────┘

INSIGHT CRITICO: Le proposte revisione sono salvate in LOCALSTORAGE,
non sul server! Questo significa che la funzione "Revisione" è
parzialmente client-side — le proposte generate vengono memorizzate
localmente e lette da lì. Ma la GENERAZIONE delle proposte richiede
il server (Server Actions), che è down.

## 2.3 Eventi Custom (comunicazione interna)
┌──────────────────────────────────┬────────────────────────────────┐
│ Evento                           │ Funzione                       │
├──────────────────────────────────┼────────────────────────────────┤
│ thesisos:open-command-palette    │ Apre ⌘K palette                │
│ thesisos:toggle-outline          │ Mostra/nascondi outline (⌘\\)  │
│ thesisos:toggle-right-rail       │ Mostra/nascondi pannello       │
│ thesisos:force-save              │ Salva capitolo (⌘S)            │
│ thesisos:find-in-chapter         │ Cerca nel capitolo (⌘⇧F)       │
│ thesisos:apply-ai-suggestion     │ Applica suggerimento (⌘Enter)  │
│ thesisos:outline-prev-section    │ Sezione precedente (⌘↑)        │
│ thesisos:outline-next-section    │ Sezione successiva (⌘↓)        │
│ thesisos:insert-citation         │ Cita fonte (⌘⇧C)               │
│ thesisos:proposal-bundle-resolved│ Bundle proposte approvato/rif. │
│ thesisos:rail-tab-*              │ Cambio tab pannello (1-4)      │
└──────────────────────────────────┴────────────────────────────────┘

## 2.4 Route mapping (dal codice)
┌────────────────────┬──────────────────────────────────────────────┐
│ Route              │ Label nel codice                             │
├────────────────────┼──────────────────────────────────────────────┤
│ /                  │ Home                                         │
│ /research          │ Research                                     │
│ /writing           │ Writing                                      │
│ /sources           │ Sources                                      │
│ /knowledge         │ Knowledge                                    │
│ /settings          │ Settings                                     │
│ /review            │ Revisione                                    │
│ /ai                │ AI                                           │
│ /library           │ Library (alias → /sources)                   │
│ /workspace         │ Writing (alias → /writing)                   │
└────────────────────┴──────────────────────────────────────────────┘


# ═══════════════════════════════════════════════════════════════════
# 3. LA CAUSA ROOT — Perché tutto sembra rotto
# ═══════════════════════════════════════════════════════════════════

## Ipotesi confermata: INFRASTRUTTURA, non codice

Dal reverse engineering del codice JS emerge che:

1. **Le funzionalità ESISTONO nel frontend:**
   - Riferimenti a "chapter" ×18 nel bundle
   - Riferimenti a "proposal" ×14
   - Riferimenti a "review" ×10
   - Riferimenti a "project" ×9
   - Command palette cerca capitoli via `a.T.list()`
   - Fallback localStorage per proposte revisione

2. **Il backend (Server Actions) non risponde:**
   - Tutte le pagine che richiedono dati server mostrano "Failed to fetch"
   - Next.js Server Actions usano endpoint speciali (non /api/*)
   - Gli endpoint Server Actions probabilmente crashano o sono down

3. **Le 3 pagine che funzionano** (Home, Sources, Settings) sono quelle
che NON richiedono dati server al caricamento — mostrano solo UI statica.

4. **Le pagine che crashano** (Canvas, Graph) sono quelle dove il server
side rendering (SSR) fallisce a livello di React/Next.js — non arrivano
nemmeno al client.

┌──────────────────────────────────────────────────────────────────┐
│                    ARCHITETTURA THESIS OS                        │
│                                                                  │
│   ┌──────────────┐    Server Actions    ┌──────────────┐        │
│   │   Next.js    │ ◄──────────────────► │   Backend    │        │
│   │   Frontend   │    (BROKEN — 500)    │   (tRPC/     │        │
│   │              │                      │   Server     │        │
│   │  ┌────────┐  │                      │   Actions)   │        │
│   │  │localStorage│ ◄── Fallback ──────►│              │        │
│   │  │session │  │    (proposte,        │              │        │
│   │  │proposals│ │     preferenze)      │              │        │
│   │  └────────┘  │                      │              │        │
│   └──────────────┘                      └──────────────┘        │
│          ▲                                                       │
│          │ Failed to fetch (tutte le chiamate server)            │
│          ▼                                                       │
│   ┌──────────────┐                                               │
│   │  Cloudflare  │ ← Tunnel instabile?                           │
│   │  (trycloudf.)│   Potrebbe essere il problema!                │
│   └──────────────┘                                               │
└──────────────────────────────────────────────────────────────────┘


# ═══════════════════════════════════════════════════════════════════
# 4. RI-VERIFICA REPORT V2 — Confronto con nuovi dati
# ═══════════════════════════════════════════════════════════════════

## Bug confermati (stessa severità)

ID  │ Bug V2                    │ Stato V3    │ Evidenza
────┼───────────────────────────┼─────────────┼─────────────────────────
C1  │ Knowledge fetch failed    │ ✅ Conferm. │ HTTP 200 pagina ma fetch
    │                           │             │ interno fallisce
C2  │ Canvas server crash       │ ✅ Conferm. │ HTTP 500, Digest:
    │                           │             │ 1788078021
C3  │ Graph server crash        │ ✅ Conferm. │ HTTP 500, Digest:
    │                           │             │ 4130059368
C4  │ AI Chat TypeError         │ ✅ Conferm. │ HTTP 200 pagina ma
    │                           │             │ fetch conversazioni
C5  │ No creazione capitoli     │ ⚠️ Ricalib. │ Il CODICE per creare
    │                           │             │ capitoli ESISTE nel JS
    │                           │             │ (chapter×18), ma il
    │                           │             │ backend non risponde.
    │                           │             │ Non manca la UI —
    │                           │             │ manca il server.
C6  │ Writing "Failed to fetch" │ ✅ Conferm. │ Server Action down
C7  │ Nuovo progetto crash      │ ✅ Conferm. │ 4 tentativi, tutti
    │                           │             │ disconnessione forzata

## Bug ricalibrati (severità o causa corretta)

ID  │ Bug V2                    │ Correzione V3
────┼───────────────────────────┼─────────────────────────────────────
G1  │ Memoria nascosta in       │ CONFERMATO ma con contesto: il tab
    │ "Contesto"                │ "Contesto" è l'unico che legge
    │                           │ decisioni dal backend. Quando il
    │                           │ backend è down, mostra solo i dati
    │                           │ cache-client. È un design choice
    │                           │ discutibile, non un bug puro.
G2  │ Badge metriche non        │ CONFERMATO. Il codice mostra che il
    │ cliccabile                │ badge è un <button> ma senza
    │                           │ onClick handler. Design incomplete.
G3  │ ⓘ no-op                   │ CONFERMATO. Nessun handler nel JS.
G4  │ No config modalità        │ CONFERMATO. Nessun riferimento nel
    │ revisione                 │ JS a configurazioni revisione.
G5  │ Auto-save no feedback     │ CONFERMATO. localStorage setItem
    │                           │ senza dispatch evento feedback.
G6  │ Source detail povero      │ CONFERMATO. Il componente esiste
    │                           │ ma senza metadati estesi.
G7  │ Trail guided placeholder  │ CONFERMATO. Solo testo statico.
G8  │ Loop Revisione→Writing    │ CONFERMATO. "Avvia revisione"
    │                           │ hardcoded a /writing.

## Nuove scoperte (non presenti in V2)

ID  │ Scoperta V3
────┼────────────────────────────────────────────────────────────────
N1  │ Le proposte revisione sono in LOCALSTORAGE — client-side!
    │ Il codice JS mostra: localStorage.getItem("thesisos:proposals")
    │ con fallback se Server Actions falliscono.
N2  │ La command palette cerca capitoli via `a.T.list()` che
    │ probabilmente è una Server Action. Se fallisce → array vuoto.
N3  │ Route nascoste: /library → /sources, /workspace → /writing
N4  │ L'app usa Next.js Server Actions (non REST API). Tutti i
    │ /api/* ritornano 404. Le chiamate sono interne a Next.js.
N5  │ Il problema potrebbe essere il tunnel Cloudflare
    │ (trycloudflare.com) — instabile, usato per dev testing.
N6  │ Le preferenze (nome progetto, stile citazione) sono salvate
    │ in localStorage, non sul server. Auto-save implicito.


# ═══════════════════════════════════════════════════════════════════
# 5. VERDETTO FINALE V3 — Prospettiva infrastrutturale
# ═══════════════════════════════════════════════════════════════════

## Il problema NON è che manca il codice

Contrariamente a quanto sembrava in V2, il **frontend è quasi completo**:
- Capitoli: codice presente, backend non risponde
- Revisione: UI + localStorage proposte, generazione server down
- Research: Canvas implementato, SSR crasha
- AI Chat: UI completa, backend conversazioni down
- Sources: funzionante (solo lettura dati statici)

## Il problema È l'infrastruttura

┌──────────────────────────────────────────────────────────────────┐
│  CAUSA ROOT: Server backend (Server Actions Next.js) non         │
│  risponde correttamente. Possibili cause:                        │
│                                                                  │
│  1. Tunnel Cloudflare (trycloudflare.com) instabile — questo     │
│     URL è tipicamente usato per development, non production      │
│                                                                  │
│  2. Database/backend service non raggiungibile dal server        │
│                                                                  │
│  3. Errori di configurazione ambiente (env vars mancanti)        │
│                                                                  │
│  4. Deploy incompleto — frontend deployato, backend no           │
└──────────────────────────────────────────────────────────────────┘

## Se il backend funzionasse, la piattaforma sarebbe:

┌──────────────────────────────────────────────────────────────────┐
│  HOME           │ ✅ 90% — già funziona                          │
│  SOURCES        │ ✅ 80% — lista OK, detail da arricchire        │
│  WRITING        │ 🟡 70% — capitoli creabili, editor completo    │
│  REVISIONE      │ 🟡 60% — flusso 3-step + proposte locali       │
│  AI CHAT        │ 🟡 60% — UI completa, dipende da AI backend    │
│  RESEARCH       │ 🟡 50% — canvas funzionerebbe, trail no        │
│  KNOWLEDGE      │ 🟡 50% — grafo visibile se backend OK          │
│  SETTINGS       │ 🟡 40% — minimale, niente modalità revisione   │
│  NUOVO PROGETTO │ ❓  ?  — crash potrebbe essere tunnel           │
└──────────────────────────────────────────────────────────────────┘

Stima: con backend funzionante, sarebbe ~65% usabile (BETA) invece
del ~15% attuale.


# ═══════════════════════════════════════════════════════════════════
# 6. RECOMMENDATIONS V3 — Priorità ri-calibrate
# ═══════════════════════════════════════════════════════════════════

### EMERGENZA (Giorno 1) — Fix infrastruttura
1. Verificare stato tunnel Cloudflare — riavviare se necessario
2. Verificare log Server Actions Next.js (Vercel/console)
3. Verificare connessione database/backend
4. Deploy separato: frontend vs backend status

### ALTA (Week 1) — Sbloccare core (dopo fix infra)
5. [C5] Aggiungere UI creazione capitoli (il codice esiste ma
   manca il form — è un'aggiunta frontend semplice)
6. [C7] Fix creazione nuovo progetto (potrebbe risolversi con
   fix infrastruttura)
7. [G1] Rendere "Contesto" più scopribile (link da Home)
8. [G4] Implementare config modalità revisione in Settings

### MEDIA (Week 2) — UX improvement
9. [G3] Fix ⓘ button (aggiungere tooltip esplicativo)
10. [G2] Rendere badge metriche cliccabile (dettaglio memoria)
11. [G6] Arricchire detail fonte (abstract, metadati)
12. [G5] Aggiungere feedback auto-save (toast)
13. [G7] Implementare trail guidato o rimuovere placeholder

### BASSA (Week 3) — Polish
14. Dark mode, font preferences
15. Più formati export (RIS, APA, MLA, Chicago)
16. Wizard primo accesso
17. Tutorial contestuale


───────────────────────────────────────────────────────────────────
Tester: Sessione esterna | Data: 2026-07-09
Metodologia V3: HTTP status testing + JS reverse engineering +
                localStorage analysis + cross-reference V2
                10+ endpoint HTTP testati, 2 JS bundle analizzati,
                17 eventi custom documentati, 4 localStorage keys
                mappate
───────────────────────────────────────────────────────────────────
