import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

# ==========================================================
# Database Path
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB = PROJECT_ROOT / "db" / "nifty100.db"

# ==========================================================
# Connection
# ==========================================================

def get_connection():

    return sqlite3.connect(DB)

# ==========================================================
# Companies
# ==========================================================

@st.cache_data(ttl=600)
def get_companies():

    conn = get_connection()

    df = pd.read_sql(

        "SELECT * FROM companies",

        conn

    )

    conn.close()

    return df

# ==========================================================
# Financial Ratios
# ==========================================================

@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):

    conn = get_connection()

    query = "SELECT * FROM financial_ratios"

    conditions = []

    if ticker:

        conditions.append(f"company_id='{ticker}'")

    if year:

        conditions.append(f"year='{year}'")

    if conditions:

        query += " WHERE " + " AND ".join(conditions)

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================================
# Profit & Loss
# ==========================================================

@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = get_connection()

    df = pd.read_sql(

        f"SELECT * FROM profit_loss WHERE company_id='{ticker}'",

        conn

    )

    conn.close()

    return df

# ==========================================================
# Balance Sheet
# ==========================================================

@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = get_connection()

    df = pd.read_sql(

        f"SELECT * FROM balance_sheet WHERE company_id='{ticker}'",

        conn

    )

    conn.close()

    return df

# ==========================================================
# Cash Flow
# ==========================================================

@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = get_connection()

    df = pd.read_sql(

        f"SELECT * FROM cash_flow WHERE company_id='{ticker}'",

        conn

    )

    conn.close()

    return df

# ==========================================================
# Sectors
# ==========================================================

@st.cache_data(ttl=600)
def get_sectors():

    conn = get_connection()

    df = pd.read_sql(

        "SELECT * FROM sectors",

        conn

    )

    conn.close()

    return df

# ==========================================================
# Peer Groups
# ==========================================================

@st.cache_data(ttl=600)
def get_peers(group_name):

    conn = get_connection()

    query = f"""

    SELECT *

    FROM peer_groups

    WHERE peer_group_name='{group_name}'

    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================================
# Valuation
# ==========================================================

@st.cache_data(ttl=600)
def get_valuation(ticker=None):

    conn = get_connection()

    query = "SELECT * FROM financial_ratios"

    if ticker:

        query += f" WHERE company_id='{ticker}'"

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================================
# Latest Financial Data
# ==========================================================

@st.cache_data(ttl=600)
def get_latest_financials():

    conn = get_connection()

    query = """

    SELECT *

    FROM financial_ratios

    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================================
# Peer Percentiles
# ==========================================================

@st.cache_data(ttl=600)
def get_peer_percentiles():

    conn = get_connection()

    df = pd.read_sql(

        "SELECT * FROM peer_percentiles",

        conn

    )

    conn.close()

    return df

# ==========================================================
# Screener Dataset
# ==========================================================

@st.cache_data(ttl=600)
def get_screener_data():

    conn = get_connection()

    query = """

    SELECT

        f.*,

        c.company_name,

        s.broad_sector,

        s.sub_sector

    FROM financial_ratios f

    LEFT JOIN companies c

        ON f.company_id=c.company_id

    LEFT JOIN sectors s

        ON f.company_id=s.company_id

    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    print(get_companies().head())

    print(get_ratios().head())

    print("DB Utility Ready")