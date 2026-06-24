from fastapi import FastAPI

from app.api import chat, jobs, system
from app.core.logging import configure_logging
from app.services.telemetry.setup import init_telemetry

configure_logging()
app = FastAPI(title="ThesisOS API", version="0.0.0")
app.include_router(system.router)
app.include_router(jobs.router)
app.include_router(chat.router)
init_telemetry(app)
