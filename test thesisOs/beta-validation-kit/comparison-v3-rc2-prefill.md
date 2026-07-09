# Confronto Beta V3 → RC-2 — ipotesi di partenza

> **Solo per il facilitatore.**  
> Le colonne "Beta V3" derivano dai report beta storici (tunnel).  
> Le colonne "RC-2 ipotesi" derivano da validazione automated Docker — **da confermare con utenti reali in PVC-1**.

Non è un verdetto. È l'ipotesi da testare.

---

## Perché questo documento esiste

RC-2 ha dimostrato che **il software è migliorato**.  
PVC-1 deve dimostrare se **l'esperienza** è migliorata.

---

## Task Success Rate — ipotesi

| Journey | Beta V3 (storico) | RC-2 ipotesi (automated) | Cosa cambia | Cosa NON cambia |
|---------|-------------------|--------------------------|-------------|-----------------|
| **UJ-001** ⭐ | **~0%** — messaggio "dalla API", no UI | **~0–20%** — capitoli esistono in DB ma no form creazione | Writing carica se capitoli già presenti | **Creazione capitolo ancora assente** |
| UJ-002 | **~70%** — Sources funzionava | **~85%** | Lista fonti stabile | Detail fonte ancora scarso |
| UJ-003 | **~0%** — fetch failed | **~80%** | 7 concetti visibili | Discoverability "cos'è Knowledge" |
| UJ-004 | **~0%** — SSR 500 | **~60%** | HTTP 200, route raggiungibile | Utilità canvas non validata umanamente |
| UJ-005 | **~0%** — SSR 500 | **~60%** | HTTP 200 | Leggibilità grafo non validata |
| UJ-006 | **~0%** — TypeError fetch | **~50%** | API conversazioni OK su Docker | Invio messaggio / risposta AI non testato |
| UJ-007 | **~10%** — loop revisione→writing | **~10%** | Errori più visibili (AP-002) | **Dipende da UJ-001** |
| UJ-008 | **~15%** — memoria nascosta in Contesto | **~15%** | Dati ancora in tab Contesto | Badge ancora inerti (G2) |
| UJ-009 | **~0%** — crash browser | **~30%** | Degraded banner vs crash | Creazione progetto non verificata |
| UJ-010 | **~25%** | **~40%** | Più route funzionanti | IA navigazione non ridisegnata |

**Ipotesi media E2E:** Beta V3 ~15% → RC-2 ~35–40% (**technical lift**) — ma **UJ-001 potrebbe restare ~0%**.

---

## La scoperta che PVC-1 deve confermare o smentire

```
Miglioramento tecnico  ≠  Miglioramento percepito
```

**Ipotesi da falsificare** (non da validare):

> UJ-001 è il punto di blocco dominante.

Se Task Success Rate aggregato sale ma **un altro pattern** emerge (es. "non so da dove iniziare" prima di Writing), il backlog prodotto segue **quel** pattern — non C5 o Recovery Sprint 3 per default.

---

## Mapping storico (solo facilitatore — non mostrare al partecipante)

| Journey | Ex-bug ID | Tema beta |
|---------|-----------|-----------|
| UJ-001 | C5 | Writing bloccato |
| UJ-002 | — | Sources OK in V3 |
| UJ-003 | C1, M5 | Knowledge down / link morti |
| UJ-004 | C2 | Canvas crash |
| UJ-005 | C3 | Graph crash |
| UJ-006 | C4 | AI fetch |
| UJ-007 | G4, G8 | Revisione loop |
| UJ-008 | G1, G2 | Memoria invisibile |
| UJ-009 | C7 | Nuovo progetto crash |
| UJ-010 | G3, navigazione | ⓘ no-op, confusione |

---

## Differenza ambiente (importante)

| | Beta V3 | RC-2 PVC-1 |
|---|---------|------------|
| Deploy | Cloudflare tunnel | Docker localhost |
| SSR API | Rotto (AP-001) | Riparato |
| Client fetch pubblico | Possibile fail (AP-004) | N/A in Docker |

Per confronto equo, **PVC-1 su Docker** misura il delta post-Recovery.  
Un secondo giro su tunnel misurerebbe AP-004 separatamente.

---

## Dopo PVC-1: come leggere i risultati

| Esito | Interpretazione | Azione |
|-------|-----------------|--------|
| UJ-001 ↑ significativo | UX fix + technical fix insieme | Design first chapter flow |
| UJ-001 flat, UJ-003/004 ↑ | Technical recovery OK, UX gap | Product Discovery su onboarding |
| Tutti flat | Problema non era stability | Ripensare value prop / IA |
| UJ-008 flat | Memoria ancora invisibile | UJ-008 → prossimo north star dopo UJ-001 |
