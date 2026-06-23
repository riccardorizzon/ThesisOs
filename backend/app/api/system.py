from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text

from app.db.session import engine

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    db_ok = True
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    status_code = 200 if db_ok else 503
    body = f'{{"status":"{"ready" if db_ok else "degraded"}","db":{str(db_ok).lower()},"config":true}}'
    return Response(content=body, media_type="application/json", status_code=status_code)


@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
