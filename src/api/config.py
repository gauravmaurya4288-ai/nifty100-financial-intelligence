"""
Application configuration settings.
"""

from pathlib import Path

# =====================================================
# Project Paths
# =====================================================

CURRENT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = CURRENT_DIR.parents[1]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

REPORTS_DIR = PROJECT_ROOT / "reports"

# Create directories if they do not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# API Settings
# =====================================================

API_TITLE = "Nifty100 Financial Intelligence API"

API_VERSION = "2.1.0"

API_DESCRIPTION = (
    "REST API for the Nifty100 Financial Intelligence Platform"
)

API_PREFIX = "/api/v1"

# =====================================================
# Server Settings
# =====================================================

HOST = "0.0.0.0"

PORT = 8000

DEBUG = True

# =====================================================
# CORS Configuration
# =====================================================

ALLOWED_ORIGINS = [
    "*"
]

ALLOWED_METHODS = [
    "*"
]

ALLOWED_HEADERS = [
    "*"
]

ALLOW_CREDENTIALS = True

# =====================================================
# Database
# =====================================================

DATABASE_URL = f"sqlite:///{DB_PATH}"

# =====================================================
# Application State
# =====================================================

APP_START_TIME = None

# =====================================================
# Pagination Defaults
# =====================================================

DEFAULT_PAGE_SIZE = 25

MAX_PAGE_SIZE = 100

# =====================================================
# Logging
# =====================================================

LOG_LEVEL = "INFO"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)