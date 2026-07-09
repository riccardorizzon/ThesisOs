# Regole metodologiche — PVC-1

> Aggiunta al Beta Validation Kit. Non sostituisce gli altri documenti.

---

## Disciplina di progetto

**Non modificare ThesisOS finché non hai completato almeno 3 sessioni PVC-1 con utenti reali.**

Il codice è congelato. L'apprendimento avviene osservando le persone.

---

## Falsificare, non validare

PVC-1 **non** serve a confermare che UJ-001 è il problema principale.

Serve a **falsificare** l'ipotesi di partenza:

> *"Gli utenti si bloccano principalmente sulla creazione del primo capitolo (UJ-001)."*

È un'ipotesi ragionevole — resta un'ipotesi.

**Durante le sessioni:** nessuna aspettativa implicita. Potresti scoprire che:

- si bloccano **prima** — non capiscono da dove iniziare;
- ignorano Writing e vanno su Knowledge senza capire cos'è;
- non vedono affatto il percorso verso il capitolo.

Se parti convinto che il problema sia UJ-001, interpreterai tutto attraverso quella lente. **Osserva. Non confermare.**

UJ-001 resta il **primo scenario** (sessione 1) perché è il task più critico per la tesi — non perché sappiamo già dove falliscono.

---

## Regola del facilitatore

Il facilitatore **non può aiutare**.

Può dire **solo**:

> *"Continua come faresti normalmente."*

Se il partecipante chiede:

- *"Dove devo cliccare?"*
- *"Cosa significa Knowledge?"*
- *"Come creo un capitolo?"*

… la risposta è **sempre la stessa**. Nessuna spiegazione, nessun hint, nessun "prova Writing".

Ogni spiegazione falsifica il risultato.

**Eccezione unica:** se il browser crasha o la sessione è tecnicamente impossibile (schermo bianco totale), interrompi lo scenario, annota il fallimento tecnico, riavvia — **senza** spiegare come completare il task.

---

## Think-aloud — prime parole

Chiedi al partecipante di **pensare ad alta voce** durante tutta la sessione.

**Trascrivi letteralmente** frasi come:

- *"Non so dove iniziare."*
- *"Pensavo fosse qui."*
- *"Questo pulsante cosa fa?"*
- *"Mi aspettavo un '+'"*

**Non interpretare.** Non riassumere in bullet "l'utente era confuso". La citazione verbatim è dato di ricerca.

Usa il campo **Timeline esitazione** e **Citazione utente** in `scorecard.md`.

---

## Primo punto di esitazione

Per ogni journey, registra **dove inizia a dubitare** — non solo dove fallisce alla fine.

Esempio UJ-001:

```text
00:00 — prompt dato
00:18 — guarda il menu
00:22 — si ferma
00:35 — legge "Knowledge"
00:41 — torna indietro
01:10 — abbandona
```

Quell'istante iniziale (es. 00:22) vale più del blocco finale.

---

## Osservazione pura — niente soluzioni

**Durante le sessioni non progettare soluzioni.**

Per ogni problema annota **solo**:

| Campo | Domanda |
|-------|---------|
| **Intenzione** | Cosa voleva fare l'utente? |
| **Azione** | Cosa ha fatto realmente? |
| **Aspettativa** | Cosa si aspettava che succedesse? |
| **Stop** | Dove si è fermato? |

Le soluzioni arrivano **dopo** aver analizzato tutte le sessioni insieme — non durante il debrief, non nel commento del facilitatore.

---

## Progressione sessioni (obbligatoria)

**Non** fare tutte e 10 le journey in una sessione.

| Sessione | Journey incluse | Durata indicativa |
|----------|-----------------|-------------------|
| **1** | **Solo UJ-001** | 20–30 min |
| **2** | UJ-001 + UJ-002 | 30–40 min |
| **3** | UJ-001 + UJ-002 + UJ-003 | 40–50 min |
| 4+ | Aggiungi UJ-004, UJ-005, … quando le sessioni 1–3 sono complete | |

**Perché UJ-001 per primo:** se il task fondamentale fallisce al primo minuto, le altre journey hanno poco senso nella stessa sessione — non perché abbiamo già deciso che UJ-001 è *il* problema.

Ripeti UJ-001 in ogni sessione per **consistenza tra partecipanti**, non per validare un'ipotesi.

---

## Domanda finale (una sola)

Non usare il questionario lungo in `scorecard.md` per il debrief. Una domanda:

> **"Se domani dovessi continuare la tesi con questo strumento, lo useresti?"**

Poi **silenzio**. Lascia parlare. Annota la risposta verbatim.

Quella risposta vale più di molte metriche quantitative.

---

## Quando riaprire Cursor (dopo ≥ 3 sessioni)

**Non partire da** "quali bug ci sono".

Compila prima la tabella in `results-template.md` — la colonna **Pattern osservato** guida il prossimo ciclo.

Poi chiedi:

> *"Analizza i risultati di Product Validation Cycle 1 e individua i pattern comuni tra i partecipanti. Raggruppa per user journey, non per componente tecnico. Costruisci la matrice frequenza × impatto. Proponi al massimo tre iniziative di prodotto ordinate per impatto sulla Task Success Rate, senza scrivere codice."*

Cursor torna utile come **analista**, non come implementatore.
