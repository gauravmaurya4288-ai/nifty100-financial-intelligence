"""
Health check endpoints.
"""

import time
import sqlite3

from fastapi import APIRouter

from ..config import API_VERSION, DB_PATH
from ..database import execute_scalar

router = APIRouter()

START_TIME = time.time()


@router.get("/health")
def health():
    """
    Returns application health and database statistics.
    """

    tables = [
        "companies",
        "profit_loss",
        "balance_sheet",
        "cash_flow",
        "financial_ratios",
        "stock_prices",
        "market_cap",
        "peer_groups",
        "analysis",
        "sectors",
    ]

    row_counts = {}

    try:

        for table in tables:

            row_counts[table] = execute_scalar(
                f"SELECT COUNT(*) FROM {table}"
            )

        database = "connected"

    except sqlite3.Error:

        database = "disconnected"

        row_counts = {}

    return {
        "status": "ok",
        "database": database,
        "version": API_VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "db_row_counts": row_counts,
    }