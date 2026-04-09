from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analytics import router as analytics_router
from app.api.routes.cards import router as cards_router
from app.api.routes.compare import router as compare_router
from app.api.routes.upload import router as upload_router
from app.core.config import settings
from app.core.database import ping_database

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title="MTR Cards Analytics API",
    version="1.0.0",
    description=(
        "API for importing BRIF MTR cards, filtering them by characteristics, "
        "and exporting comparison results."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(cards_router)
app.include_router(compare_router)
app.include_router(analytics_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    database_status = "ok" if ping_database() else "unavailable"
    return {
        "status": "ok",
        "database": database_status,
        "environment": settings.environment,
    }
