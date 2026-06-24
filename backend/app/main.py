import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import chat, jobs, memory, system
from app.core.logging import configure_logging
from app.graph.checkpointer import ensure_langgraph_schema
from app.services.telemetry.setup import init_telemetry

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_langgraph_schema()
    except Exception:  # DB may be unavailable at boot in some envs; checkpointer setup is idempotent
        logging.getLogger("app.main").warning(
            "ensure_langgraph_schema failed at startup; checkpointer setup will retry lazily", exc_info=True
        )
    yield


app = FastAPI(title="ThesisOS API", version="0.0.0", lifespan=lifespan)
app.include_router(system.router)
app.include_router(jobs.router)
app.include_router(chat.router)
app.include_router(memory.router)
init_telemetry(app)
