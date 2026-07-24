"""
Main FastAPI application.
"""

import time
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import (
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
    ALLOWED_ORIGINS,
)

from .middleware import log_requests

from .routers import (
    health,
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

START_TIME = time.time()

# -------------------------------------------------------
# CORS
# -------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Request Logging
# -------------------------------------------------------

@app.middleware("http")
async def logging_middleware(request, call_next):
    return await log_requests(request, call_next)


# -------------------------------------------------------
# Routers
# -------------------------------------------------------

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

app.include_router(
    companies.router,
    prefix="/api/v1/companies",
    tags=["Companies"],
)

app.include_router(
    screener.router,
    prefix="/api/v1/screener",
    tags=["Screener"],
)

app.include_router(
    sectors.router,
    prefix="/api/v1/sectors",
    tags=["Sectors"],
)

app.include_router(
    peers.router,
    prefix="/api/v1/peers",
    tags=["Peers"],
)

app.include_router(
    valuation.router,
    prefix="/api/v1/valuation",
    tags=["Valuation"],
)

app.include_router(
    portfolio.router,
    prefix="/api/v1/portfolio",
    tags=["Portfolio"],
)

app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"],
)


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint.
    """
    return {
        "application": API_TITLE,
        "version": API_VERSION,
        "status": "running",
    }