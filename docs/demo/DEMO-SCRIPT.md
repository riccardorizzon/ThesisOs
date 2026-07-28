# Demo Script — ThesisOS (10–15 min)

> **Audience:** relatrice, beta tester, demo live.  
> **Workspace:** `thesis-agent` (Default Thesis).  
> **Prerequisiti:** `make up`, `make ops-check` PASS, Vertex configurato.

## URL e setup (2 min)

1. Apri l’istanza beta (tunnel Cloudflare — può cambiare dopo reboot):

   ```bash
   cat /tmp/thesisos-beta-public.env 2>/dev/null || bash bin/beta-public-open.sh
   ```

   Esempio storico: `https://indexes-ghz-joan-stronger.trycloudflare.com`

2. Verifica gate ops locale (sul VM):

   ```bash
   make ops-check
   ```

3. **Messaggio di apertura (30 s):**  
   «ThesisOS è un workspace unico per tesi: fonti indicizzate, chat con RAG sul corpus, scrittura per capitolo con AI ancorata alle fonti, review delle proposte e export. Non è un chatbot generico: ogni risposta può citare chunk del corpus caricato.»

---

## 1. Fonti — corpus curato (3 min)

**Route:** `/sources`

| Cosa mostrare | Perché |
|---------------|--------|
| 6 documenti core (Outline-Master, Stigmata-Framework, Core-Theory-Map, Sennett, Benjamin, Guida) | SoR della tesi — re-seed con `make seed-curated-sources` |
| Bibliografia catalogo (Flow, Mythologies, Sex and Suits, …) | Voci senza upload = metadati; con link = documento indicizzato |
| Stato `indexed` | Parsing + chunk + embedding completati |

**Script:**  
«Qui vivono le fonti della tesi. I markdown core definiscono struttura (Outline), framework (STIGMATA) e mappa teorica. Sennett e Benjamin alimentano il capitolo metodologico. L’indicizzazione crea chunk searchable — il RAG legge Postgres, non i file su disco.»

**Non aprire:** documenti di test (`a`, `emb`, `round`, dogfood M4/M5…) — vanno rimossi con Wave 1 cleanup.

---

## 2. Chat — RAG ancorato (4 min)

**Route:** `/ai`  
**Azione:** crea conversazione **«Demo — STIGMATA e Sennett»** (non riusare `__companion_open__` o thread `ping`).

### Prompt 1 — framework

```text
Cos'è STIGMATA nel mio corpus? Riassumi in 5 bullet usando solo le fonti caricate.
```

**Atteso:** riferimenti a Stigmata-Framework / Outline; tono accademico; citazioni o menzione chunk.

### Prompt 2 — autore specifico

```text
Secondo Sennett, cosa distingue la pratica manuale (craftsmanship) dal lavoro astratto? Una risposta, due paragrafi.
```

**Atteso:** contenuto grounded su Sennett_The-Craftsman; niente allucinazioni su autori non presenti.

### Prompt 3 — controllo qualità

```text
Quali autori del corpus NON hai usato in questa risposta e perché?
```

**Script di chiusura sezione:**  
«La chat non sostituisce la lettura: propone sintesi e collegamenti. Le limitazioni (no web live, qualità dipende dal corpus) le vediamo alla fine.»

---

## 3. Scrittura — capitolo vetrina (4 min)

**Route:** `/writing`

| Capitolo demo | ID | Parole |
|---------------|-----|--------|
| **Cap. 3 — Progettazione metodologica** | `503c33f5-a3d8-40ee-adc0-3ff067747a17` | ~3662 |

**Flusso:**

1. Apri il capitolo (status `review`).
2. Mostra outline / contenuto esistente (sezioni §2.x collegate).
3. Nel pannello AI grounded, chiedi:

   ```text
   Aggiungi un paragrafo di transizione tra §2.3 e §2.4 che richiami Benjamin (aura) e Sennett (pratica), tono accademico italiano.
   ```

4. Accetta o modifica la proposta inline.

**Script:**  
«La scrittura è per capitolo. L’AI vede il testo del capitolo + retrieval sul corpus — non inventa bibliografia. Lo status `review` segnala bozze da validare prima dell’export.»

**Capitoli di supporto (se c’è tempo):** §2.1 ricerca (`90237cb8…`), §1.3 processo creativo (`135afba6…`).

---

## 4. Review ed export (2 min)

**Route:** `/review` → poi menu export in `/writing`

1. Mostra una proposta pendente (se esiste) o spiega il flusso accept → chapter.
2. Export: seleziona **project_id** `thesis-agent` e capitolo/i desiderati.

**Nota tecnica (per audience tecnica):**  
`POST /export` senza `project_id` → **422** (contratto multi-thesis). Verificato da `make ops-check`.

---

## 5. Limitazioni oneste (1 min)

Leggi o consegna [`DEMO-HANDOUT.md`](./DEMO-HANDOUT.md). Punti chiave:

- Beta single-user; tunnel pubblico instabile.
- RAG = corpus caricato; niente ricerca web.
- Molti originali PDF non su disco (era `/tmp`); chunk in DB sufficienti per chat/scrittura.
- Manoscritto in nav ma non nel README — Wave 2.
- Titoli capitoli ancora con prefisso `[kimi-claw-2026-06]` — Wave 2 rename.

---

## Checklist pre-demo (5 min prima)

- [ ] `make ops-check` PASS
- [ ] `bash bin/demo-cleanup.sh --dry-run` — verificare conteggi attesi (~15 doc, ~25 capitoli)
- [ ] (Opzionale) `bash bin/demo-cleanup.sh --apply` eseguito e verificato
- [ ] Nuova conversazione demo creata; thread `ping`/`test` non mostrati
- [ ] Cap. 3 apre senza errori
- [ ] Backup DB se si applica cleanup su produzione: `docker compose exec db pg_dump -U thesisos thesisos > /tmp/thesisos-pre-demo.sql`

## Checklist post-demo

- [ ] Annotare domande / bug in issue o `.asep/reports/`
- [ ] Se il tunnel è caduto: `bash bin/beta-public-open.sh`

## Riferimenti

- Piano pulizia dati: [`DATA-CLEANUP-PLAN.md`](./DATA-CLEANUP-PLAN.md)
- Ops runbook: [`docs/superpowers/plans/2026-07-29-ops-perfection-priorities.md`](../superpowers/plans/2026-07-29-ops-perfection-priorities.md)
- Seed corpus: `make seed-curated-sources`
