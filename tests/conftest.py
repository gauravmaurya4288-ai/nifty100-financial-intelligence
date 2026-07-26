"""
Shared pytest fixtures for the Nifty100 Financial Intelligence Platform
"""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.config import DB_PATH

# ==========================================================
# FastAPI Test Client
# ==========================================================

@pytest.fixture(scope="session")
def client():
    """
    Returns a FastAPI TestClient.
    """
    with TestClient(app) as client:
        yield client


# ==========================================================
# Database Connection
# ==========================================================

@pytest.fixture(scope="session")
def db_connection():
    """
    Creates a SQLite connection for the test session.
    """

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    yield conn

    conn.close()


# ==========================================================
# Database Cursor
# ==========================================================

@pytest.fixture(scope="function")
def db_cursor(db_connection):
    """
    Creates a fresh cursor for each test.
    """

    cursor = db_connection.cursor()

    yield cursor

    cursor.close()


# ==========================================================
# Sample Company
# ==========================================================

@pytest.fixture
def sample_company():
    return "TCS"


@pytest.fixture
def invalid_company():
    return "INVALID_COMPANY"


# ==========================================================
# API Endpoints
# ==========================================================

@pytest.fixture
def health_endpoint():
    return "/api/v1/health"


@pytest.fixture
def companies_endpoint():
    return "/api/v1/companies"


@pytest.fixture
def screener_endpoint():
    return "/api/v1/screener"


@pytest.fixture
def sectors_endpoint():
    return "/api/v1/sectors"


@pytest.fixture
def peers_endpoint():
    return "/api/v1/peers"


@pytest.fixture
def valuation_endpoint():
    return "/api/v1/valuation"


@pytest.fixture
def documents_endpoint():
    return "/api/v1/documents"


# ==========================================================
# Expected Database Row Counts
# ==========================================================

@pytest.fixture(scope="session")
def expected_counts():
    """
    Expected number of rows in each database table.
    """

    return {

        "companies": 92,
        "profit_loss": 1276,
        "balance_sheet": 1312,
        "cash_flow": 1187,
        "stock_prices": 5520,
        "market_cap": 552,
             
        "sectors": 92,
        "analysis": 20,
        "peer_groups": 56,
        
        "financial_ratios": 1162,
        
       

    }


# ==========================================================
# Helper Functions
# ==========================================================

def assert_success(response):
    """
    Assert that the API response is successful.
    """

    assert response.status_code == 200

    data = response.json()

    assert data is not None

    return data


def count_rows(cursor, table_name):
    """
    Return number of rows in a database table.
    """

    cursor.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    )

    return cursor.fetchone()[0]


# ==========================================================
# Health Check Helper
# ==========================================================

@pytest.fixture
def health_data(client):

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    return response.json()


# ==========================================================
# Company Helper
# ==========================================================

@pytest.fixture
def company_data(client):

    response = client.get("/api/v1/companies/TCS")

    assert response.status_code == 200

    return response.json()


# ==========================================================
# Screener Helper
# ==========================================================

@pytest.fixture
def screener_data(client):

    response = client.get(
        "/api/v1/screener?min_roe=15"
    )

    assert response.status_code == 200

    return response.json()


# ==========================================================
# Sector Helper
# ==========================================================

@pytest.fixture
def sector_data(client):

    response = client.get("/api/v1/sectors")

    assert response.status_code == 200

    return response.json()


# ==========================================================
# Documents Helper
# ==========================================================

@pytest.fixture
def documents_data(client):

    response = client.get(
        "/api/v1/documents/TCS"
    )

    assert response.status_code == 200

    return response.json()


# ==========================================================
# Valuation Helper
# ==========================================================

@pytest.fixture
def valuation_data(client):

    response = client.get(
        "/api/v1/valuation/TCS"
    )

    assert response.status_code == 200

    return response.json()


# ==========================================================
# Peer Helper
# ==========================================================

@pytest.fixture
def peer_data(client):

    response = client.get(
        "/api/v1/peers/IT"
    )

    assert response.status_code == 200

    return response.json()