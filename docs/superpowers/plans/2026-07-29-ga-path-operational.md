# Piano operativo — da demo-ready a GA (`v2.0.0`)

> **Contesto:** Demo Waves 1–4 + ADR-0048 = **CLOSED**. Prodotto **presentabile**.  
> **Obiettivo di questo piano:** chiudere il percorso **RC → GA**, non aggiungere feature.  
> **Fuori scope:** M8 (dopo GA). Docling, PX-EXEC, ASEP Core.  
> **Receipt demo:** `.asep/reports/DEMO-PRESENTABILITY-CLOSURE-20260729.md`  
> **Execution 2026-07-29:** `.asep/reports/GA-PATH-EXECUTION-20260729.md` — agent closed automatable steps; P1/AUTHORIZE/tag skipped.

---

## Perché non sei già “chiuso” a livello prodotto

| Livello | Cosa significa | Sei qui? |
|---------|----------------|----------|
| **Demo-ready** | Operatore può presentare; gate automatici verdi | **Sì** |
| **Beta validato** | Persone reali hanno usato il prodotto; feedback triagato | **No** |
| **GA (`v2.0.0`)** | Architetto/Product firmano: “rilasciabile come v2” | **No** |
| **M8** | Nuove feature / multi-user reale | **Dopo GA** |

I gate automatici dicono: *la macchina funziona oggi*.  
Cohort + 7 giorni + package GA dicono: *regge l’uso umano e merita il tag stabile*.

---

## Mappa del percorso

```text
[DONE] PX-1…6 + M7 + rc.2 + demo Waves 1–4 + ADR-0048
              ↓
[P0]  Freeze baseline (merge branch → main / tag tip)
              ↓
[P1]  Cohort umana 5–10 (7–14 giorni calendario)
              ↓
[P2]  Triage feedback (zero v2.0-blocker aperti)
              ↓
[P3]  Stabilità 7 giorni + smoke post-hotfix
              ↓
[P4]  GA Approval Package + AUTHORIZE + tag v2.0.0
              ↓
[P5]  (opzionale) M8 Work Order
```

---

## Perché serve ciascuna cosa

### 1. Freeze baseline (merge `feat/companion-persistence` → `main`)

**Perché:** Il lavoro demo (originali, Sennett boost, citazioni, ADR-0048, closure docs) vive sul branch. GA senza merge firma una baseline **diversa** da quella che hai appena verificato — oppure lascia hardening fuori dal tag.

**Cosa fa:** PR → review → merge → `make demo-gate` + `make beta-validator-rc` su `main`.

**Se salti:** GA su codice vecchio, o tag su branch non ufficiale.

---

### 2. Cohort umana 5–10

**Perché:** Gli agent e `make demo-gate` usano percorsi noti (stesso progetto, stesse query). Gli umani:
- cliccano ordini strani,
- hanno reti/browser diversi,
- trovano UX blocker che lo script non vede,
- validano che le **limitazioni dichiarate** (single-user, W-06, tunnel) siano accettabili.

**Cosa fa:** inviti da `BETA-COHORT-INVITE.md`, onboarding `RC-BETA-ONBOARDING.md`, riga tracker `#1…#10`.

**Se salti:** “Beta” è solo marketing interno; rischio regressione al primo utente vero.

---

### 3. Triage feedback (no `v2.0-blocker`)

**Perché:** Avere tester senza chiudere i ticket è peggio che non testare: sai che è rotto e rilasci lo stesso. Il triage decide:
- **blocker** → hotfix / rc.3 prima di GA,
- **major** → fix o accepted limitation documentata,
- **minor / feature** → backlog M8+.

**Cosa fa:** tabella Feedback in `THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md`.

**Se salti:** GA con debiti nascosti; non puoi rispondere “cosa sapevamo”.

---

### 4. Staging stabile 7 giorni + smoke post-hotfix

**Perché:** Un giorno verde ≠ una settimana. I fallimenti tipici appaiono dopo:
- restart container / tunnel,
- DB backup/restore,
- rate limit LLM,
- memory leak / disco documenti,
- “funzionava venerdì”.

I 7 giorni sono un **filtro temporale**, non una cerimonia. Smoke dopo ogni hotfix evita di “aggiustare A e rompere B” in silenzio.

**Cosa fa:** stack fisso (`main` tip o tag rc.2+), log giornaliero breve, `make ops-check` / `make demo-gate` a cadenza (es. ogni 48h o post-change).

**Se salti:** GA su snapshot fortunato; niente evidenza di stabilità.

---

### 5. GA Approval Package + tag `v2.0.0`

**Perché:** Il tag GA è un **contratto esterno** (repo, stakeholder, “questa è la v2”). Non è un rename di rc.2. Serve un atto esplicito (come i bundle rc.1/rc.2) che elenca:
- baseline SHA,
- gate verdi,
- limitazioni accettate,
- rollback,
- cosa **non** è incluso (M8).

**Cosa fa:** documento tipo `THESISOS-v2.0.0-GA-BUNDLE.md` + certificate + `AUTHORIZE` / approval execution + `git tag -a v2.0.0`.

**Se salti:** confusione eterna tra “demo-ready”, “rc”, e “released”.

---

### 6. M8 (solo dopo)

**Perché:** Multi-user reale e feature nuove cambiano superficie e rischio. Farle prima di GA mescola “stabilizzare v2” con “inventare v3”. ADR-0048 lo dice esplicitamente.

**Se le fai prima:** riallughi la beta; i tester non validano più lo stesso prodotto.

---

## Piano operativo (checklist)

### P0 — Baseline (½–1 giorno)

- [ ] Push commit di closure se non già su remote (`86ad1578`+)
- [ ] Aprire PR `feat/companion-persistence` → `main`
- [ ] CI verde; review layer frontend/backend dove tocca
- [ ] Merge
- [ ] Su `main`: `make demo-gate` + `make beta-validator-rc`
- [ ] Annotare SHA baseline GA-candidate nel tracker beta

**Done when:** hardening demo è su `main` e i gate passano lì.

---

### P1 — Cohort (calendario 7–14 giorni; effort ops ~2–4h setup)

- [ ] Product Lead sceglie 5–10 persone reali (non inventate)
- [ ] Decidere URL: localhost/SSH **oppure** tunnel/GCP con `BETA_ACCESS_TOKEN`
- [ ] `make demo-backup` prima dell’apertura cohort
- [ ] Inviare messaggio da `BETA-COHORT-INVITE.md`
- [ ] Compilare tracker: Invited ☑ per ogni riga
- [ ] Sessione 30–45 min per tester (superfici in `RC-BETA-ONBOARDING.md`)
- [ ] Onboarded ☑ + note sessione

**Done when:** ≥5 onboarded **oppure** disposition scritta “cohort ridotta N=…” firmata Product Lead (minimo onesto: non zero se vuoi GA “beta-validated”).

---

### P2 — Triage (in parallelo a P1; chiusura a fine cohort)

- [ ] Ogni report → riga Feedback (severity / major / minor)
- [ ] Blocker → hotfix su `main`, eventuale `v2.0.0-rc.3`, re-smoke
- [ ] Major → fix o entry in `KNOWN_LIMITATIONS` / handout
- [ ] Feature request → backlog M8 (non in GA)
- [ ] Verdetto: **zero `v2.0-blocker` aperti**

**Done when:** tabella triage senza blocker aperti; disposition su ogni major.

---

### P3 — Stabilità 7 giorni (calendario)

Partenza consigliata: giorno in cui baseline P0 è su `main` (può sovrapporsi a P1).

| Giorno | Azione minima |
|--------|----------------|
| D0 | Gate verdi; annota SHA + URL stack |
| D2 / D4 / D6 | `make ops-check` (o `demo-gate`); nota PASS/FAIL |
| Post-hotfix | smoke obbligatorio prima di ripartire il conteggio “stabile” se il fix è rischioso |
| D7 | Report 7-day: uptime note, incident, hotfix list |

**Done when:** report 7-day allegato al GA bundle (anche breve: ½ pagina).

---

### P4 — GA package (½–1 giorno dopo P1–P3)

- [ ] Redigere `.asep/reports/THESISOS-v2.0.0-GA-BUNDLE.md` (modello: rc.2 M7 bundle)
- [ ] Includere: SHA, gate, cohort summary, 7-day report, limitazioni accettate, rollback
- [ ] Certificate YAML in `.asep/certificates/`
- [ ] Atto Architect / Product: `AUTHORIZE` GA (o blocco approval firmato)
- [ ] `git tag -a v2.0.0 -m "…" <sha>` + push tag
- [ ] Aggiornare README: Beta → GA
- [ ] Chiudere tracker beta come COMPLETE (non solo deferred)

**Done when:** tag `v2.0.0` esiste e punta allo SHA del bundle.

---

### P5 — Solo dopo GA

- [ ] Decidere se aprire M8 (auth multi-user, feature) con Work Order dedicato
- [ ] Non mescolare M8 nel tag GA

---

## Percorsi alternativi (se vuoi accelerare)

| Percorso | Cosa accetti | Cosa rischi |
|----------|--------------|-------------|
| **A — GA stretto (default sopra)** | Tempo + cohort | Basso |
| **B — GA “operator-only”** | Skip cohort; package dichiara *no external beta* | Alto reputazionale; non chiamarlo “beta-validated” |
| **C — Restare demo-ready** | Nessun tag GA; usi rc.2 + closure | Onesto per tesi/demo; non è “prodotto rilasciato” |

**Raccomandazione:** se l’uso è demo/relatrice/uso personale → **C** è già sufficiente.  
Se vuoi dire “ThesisOS v2.0.0 released” → **A**.

---

## Ruoli

| Ruolo | Responsabilità |
|-------|----------------|
| **Operatore / tu** | Stack su, backup, gate, tunnel/token |
| **Product Lead** | Inviti cohort, triage severity, accept limitations |
| **Architect** | AUTHORIZE GA package; no M8 prima |
| **Agent** | Hotfix, bundle draft, smoke — non inventare tester |

---

## Comandi ricorrenti

```bash
make demo-backup
make demo-gate
make beta-validator-rc
make demo-auth-check          # se BETA_ACCESS_TOKEN impostato
# cohort materials
make cohort-check
```

---

## Definition of Done (GA)

- [x] Demo presentability CLOSED  
- [ ] Baseline hardening su `main`  
- [ ] Cohort disposition onesta (≥5 onboarded **o** waiver firmato)  
- [ ] Zero `v2.0-blocker`  
- [ ] 7-day stability report  
- [ ] GA bundle + certificate + tag `v2.0.0`  

Finché uno di questi manca, il prodotto resta **demo-ready / rc**, non **GA**.
