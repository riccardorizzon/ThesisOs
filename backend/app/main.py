import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    chapters,
    chat,
    citations,
    conformance,
    conversations,
    documents,
    export,
    jobs,
    knowledge,
    memory,
    project_registry,
    projects,
    proposals,
    search,
    sources,
    system,
    writing_actions,
)
from app.core.logging import configure_logging
from app.core.config import settings
from app.graph.checkpointer import ensure_langgraph_schema
from app.middleware.beta_access import BetaAccessMiddleware
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
# ADR-0048 — optional; no-op when BETA_ACCESS_TOKEN unset (must be outer-ish for 401)
app.add_middleware(BetaAccessMiddleware)
if settings.app_env == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.include_router(system.router)
app.include_router(jobs.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(memory.router)
app.include_router(documents.router)
app.include_router(export.router)
app.include_router(search.router)
app.include_router(chapters.router)
app.include_router(proposals.router)
app.include_router(project_registry.router)
app.include_router(projects.router)
app.include_router(citations.router)
app.include_router(knowledge.router)
app.include_router(conformance.router)
app.include_router(sources.router)
app.include_router(writing_actions.router)
init_telemetry(app)
