"""
Application configuration settings.
"""

from pathlib import Path

# -----------------------------------------------------
# Project Paths
# -----------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = CURRENT_DIR.parents[1]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

REPORTS_DIR = PROJECT_ROOT / "reports"

# -----------------------------------------------------
# API Settings
# -----------------------------------------------------

API_TITLE = "Nifty100 Financial Intelligence API"

API_VERSION = "2.1.0"

API_DESCRIPTION = (
    "REST API for Nifty100 Financial Intelligence Platform"
)

# -----------------------------------------------------
# CORS
# -----------------------------------------------------

ALLOWED_ORIGINS = ["*"]

# -----------------------------------------------------
# Application
# -----------------------------------------------------

APP_START_TIME = None