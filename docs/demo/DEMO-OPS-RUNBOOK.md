# Demo Ops Runbook — Wave 3 (non fallire mid-demo)

> **Obiettivo:** riaccendere lo stack, recuperare da imprevisti, e presentare senza panico.  
> **Durata:** 5–10 min prima della demo · 2 min se qualcosa cade durante.

## Prima della demo (checklist 5 min)

```bash
cd "/home/ricky/agent thesis"

# 1. Gate completo (Wave 1 + 2 + 3)
make demo-gate

# 2. Backup di sicurezza (consigliato)
make demo-backup

# 3. (Opzionale) URL pubblico per audience remota
cat /tmp/thesisos-beta-public.env 2>/dev/null || bash bin/beta-public-open.sh
```

**Atteso:** tutti i gate PASS; backup in `/tmp/thesisos-pre-demo-*.sql`.

---

## Dopo reboot VM o crash Docker

```bash
cd "/home/ricky/agent thesis"
make up
# attendi ~30s
make ops-check          # health + LLM + export 422
make demo-wave2-check   # dati demo intatti
```

Se `ops-check` fallisce su LLM → verifica `backend/.env` e `GOOGLE_CLOUD_PROJECT` nel container.

---

## Dopo `git pull` o merge che tocca `backend/`

```bash
make deploy-backend     # rebuild + ops-check automatico
make demo-gate          # verifica dati demo
```

**Non usare** `docker compose down -v` — distrugge `pgdata` e `document_data`.

---

## Tunnel Cloudflare caduto (demo pubblica)

```bash
# Riusa URL precedente se possibile
BETA_PUBLIC_URL=https://YOUR-OLD.trycloudflare.com bash bin/beta-public-open.sh

# Oppure genera nuovo URL
bash bin/beta-public-open.sh
cat /tmp/thesisos-beta-public.env
```

Poi verifica: `curl -sf "$(grep PUBLIC_URL /tmp/thesisos-beta-public.env | cut -d= -f2)/health"`

Per demo locale: usa `http://localhost:3000` — nessun tunnel necessario.

---

## Ripristino DB da backup

Solo se cleanup o errore ha corrotto i dati demo:

```bash
# ATTENZIONE: sovrascrive il DB corrente
BACKUP=/tmp/thesisos-pre-demo-20260729.sql   # usa il tuo file
docker compose stop backend
docker compose exec -T db psql -U thesisos -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='thesisos' AND pid <> pg_backend_pid();"
docker compose exec -T db dropdb -U thesisos thesisos --if-exists
docker compose exec -T db createdb -U thesisos thesisos
docker compose exec -T db psql -U thesisos -d thesisos < "$BACKUP"
docker compose start backend
make demo-gate
```

---

## Durante la demo — cosa fare se…

| Problema | Azione rapida |
|----------|---------------|
| Pagina bianca | `docker compose ps` → `make up` se down |
| Chat non risponde | `make ops-check` → se LLM fail, riavvia backend |
| Export 500 | Verifica `project_id=thesis-agent` in UI |
| Tunnel 502 | `bash bin/beta-public-open.sh` → condividi nuovo URL |
| Fonti vuote | **Non** re-upload in live — usa corpus già indexed (15 doc) |

---

## Docling / PDF — defer (OK per questa demo)

La demo usa **15 documenti markdown già indexed** (6 core + 9 corpus).  
**Non serve** abilitare Docling finché non carichi nuovi PDF complessi.

Verifica: `SELECT COUNT(*) FROM documents WHERE status='failed';` → deve essere **0**.

---

## Riferimenti

| Risorsa | Path |
|---------|------|
| Script demo 15 min | `docs/demo/DEMO-SCRIPT.md` |
| Handout limitazioni | `docs/demo/DEMO-HANDOUT.md` |
| Piano dati Wave 1–2 | `docs/demo/DATA-CLEANUP-PLAN.md` |
| Ops dettagliato | `docs/superpowers/plans/2026-07-29-ops-perfection-priorities.md` |
| Gate automatizzati | `make demo-gate`, `make demo-wave3-check`, `make demo-wave4-check` |
| Crescita Wave 4 | `docs/demo/DEMO-GROWTH-PLAN.md`, `docs/demo/DEMO-DEPLOY-GCP.md` |
