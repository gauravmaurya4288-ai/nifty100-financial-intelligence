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
        fr.company_id,
        c.company_name,
        s.broad_sector,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.operating_profit_margin_pct,
        fr.pe_ratio,
        fr.pb_ratio,
        fr.dividend_yield_pct,
        fr.interest_coverage,
        fr.composite_quality_score
    FROM financial_ratios fr
    LEFT JOIN companies c
        ON fr.company_id = c.company_id
    LEFT JOIN sectors s
        ON fr.company_id = s.company_id
    WHERE fr.year LIKE '%2024%'
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM profit_loss WHERE company_id=?",
        conn,
        params=(ticker,)
    )

    conn.close()

    return df

    @st.cache_data(ttl=600)
    def get_pros_cons(ticker):

        conn = get_connection()

        query = """
        SELECT *
        FROM pros_cons
        WHERE company_id = ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=(ticker,)
        )

        conn.close()

        return df
    
    from utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_pros_cons,
)
    

@st.cache_data(ttl=600)
def get_peer_groups():
    conn = get_connection()

    query = """
    SELECT DISTINCT peer_group_name
    FROM peer_groups
    ORDER BY peer_group_name
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def get_peer_companies(group):

    conn = get_connection()

    query = f"""
    SELECT
        p.company_id,
        c.company_name,
        p.peer_group_name,
        p.is_benchmark
    FROM peer_groups p
    LEFT JOIN companies c
        ON p.company_id=c.company_id
    WHERE p.peer_group_name='{group}'
    ORDER BY c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_peer_metrics(group):

    conn = get_connection()

    query=f"""
    SELECT
        p.company_id,
        c.company_name,
        p.peer_group_name,
        p.is_benchmark,

        r.return_on_equity_pct,
        r.return_on_capital_employed_pct,
        r.net_profit_margin_pct,
        r.debt_to_equity,
        r.free_cash_flow_cr,
        r.revenue_cagr_5yr,
        r.pat_cagr_5yr,
        r.composite_quality_score

    FROM peer_groups p

    LEFT JOIN financial_ratios r
        ON p.company_id=r.company_id

    LEFT JOIN companies c
        ON c.company_id=p.company_id

    WHERE p.peer_group_name='{group}'
    """

    df=pd.read_sql(query,conn)

    conn.close()

    return df
# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    print(get_companies().head())

    print(get_ratios().head())

    print("DB Utility Ready")