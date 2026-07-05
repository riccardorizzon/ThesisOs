# Relatrice Rules

Regole operative estratte dalla **prima revisione PDF** (27-05-2026) e validate
dall'utente il 2026-06-30 (`post-migrazione: R1–R5 ok`).

Fonte annotazioni: `04_KNOWLEDGE/Relatrice/` (PDF + scansioni + trascrizioni proposta).
In caso di conflitto con suggerimenti generici dell'agente, **vince la relatrice**
(solo per indicazioni **validate** qui sotto).

---

## Stato

| Elemento | Stato |
|----------|-------|
| Trascrizioni proposta | ✅ Completate |
| Validazione pattern R1–R5 | ✅ **Congelato** 2026-06-30 |
| Voci granulari P1–P4 | ⏳ Opzionali — vedi `Relatrice/transcription/VALIDATION.md` |

---

## R1 — Citazioni e nomi propri

- **Prima occorrenza** di un autore: **nome completo + cognome** (es. Bernd Löbach, Josef Albers).
- **Occorrenze successive:** solo cognome (autore-data nel corpo, vedi UNI-01).
- **Stilisti, artisti, figure storiche:** nome completo quando opportuno (es. Cristóbal Balenciaga).
- Correggere varianti errate segnalate (Joseph → Josef Albers; Gilles → Gillo Dorfles).

---

## R2 — Attribuzione testo proprio vs fonte

- Distinguere sempre **testo originale** da contenuti **derivati da fonti**.
- Se un'affermazione non è dell'autrice della tesi, va **attribuita** con citazione autore-data.
- Pattern ricorrenti della relatrice: «è tuo questo testo? Se no, cita!»; «questa parte è tua?»;
  «non è una tua appropriazione di [Autore]?».
- Intuizioni valide dell'autrice: esplicitare che sono **interpretazione propria**, non teoria dell'autore citato.

---

## R3 — Struttura del paragrafo

- **Un concetto per paragrafo** quando possibile; evitare paragrafi che accorpano teorie diverse.
- Integrare citazioni **autore-data nel corpo**: `(Autore, anno)` — **nessuna nota a piè di pagina** (UNI-01).
- Separare approcci distinti (es. estetica relazionale, semiotica) in paragrafi autonomi.

---

## R4 — Prudenza argomentativa

- Evitare **affermazioni assolute o categoriche** non dimostrate.
- Preferire formulazioni prudenti, supportate da fonti o esplicitamente marcate come interpretazione.
- Chiedersi: «si riesce a provare questo?» prima di enunciati generali.

---

## R5 — Lessico e preferenze puntuali

- Rispettare **preferenze lessicali** espresse dalla relatrice e mantenerle **coerenti** in tutta la tesi.
- Esempi validati: «silenzioso / meno valorizzato» preferito a «invisibile / sottovalutato»;
  evitare «contraddittorio» se sconsigliato (relatrice: «eviterei!») → preferire «organico» se appropriato al contesto.
- Non generalizzare una correzione puntuale in regola assoluta senza conferma.

---

## Modello di riferimento (PDF revisione)

La prima correzione resta il modello per:

- Densità del testo e lunghezza paragrafi
- Bilanciamento descrizione / analisi
- Tipo di correzioni ricorrenti (oltre a R1–R5)

---

## Workflow obbligatorio (materiale relatrice)

1. Analizzare **tutto** il materiale prima di modificare il testo.
2. Produrre: certezze | dubbi interpretativi | conflitti con regole progetto.
3. **Domande in un solo batch** — poi attendere.
4. **Nessuna ipotesi** su annotazioni ambigue o illeggibili.
5. Piano modifiche solo dopo risposta utente.

Vedi anche `02_METHOD/Review-Protocol.md`, `Revision-Workflow.md`, REV-001–REV-006 in `Decisions.md`.

---

## Preferenze note (da chat — coerenti con revisione)

- Interpretazione **conservativa** delle indicazioni.
- Attenzione a non «teorizzare troppo» sul caso STIGMATA rispetto al filone accademico richiesto.
- Spiegare **come** si analizza (metodo STIGMATA), non solo **cosa** — vedi STIGMATA framework.

---

## Integrazione ThesisOS

- Documenti relatrice → M3 con tag `relatrice`, alta priorità retrieval in route `writer` quando si revisiona.
- Decisioni R1–R5 → `memories` kind `decision`, slug `relatrice-r1` … `relatrice-r5` (promosso Fase B).
