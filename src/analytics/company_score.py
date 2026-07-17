"""
company_score.py
----------------
Calculates an overall investment score for each company using
financial ratios and valuation engine results.

Output:
    - Overall Score (0-100)
    - Grade
    - Individual metric scores
"""

import pandas as pd

# ==============================
# Scoring Functions
# ==============================

def score_roe(roe):
    """Score Return on Equity (20 Marks)"""
    if pd.isna(roe):
        return 0
    if roe >= 25:
        return 20
    elif roe >= 20:
        return 18
    elif roe >= 15:
        return 15
    elif roe >= 10:
        return 10
    return 5


def score_roce(roce):
    """Score Return on Capital Employed (20 Marks)"""
    if pd.isna(roce):
        return 0
    if roce >= 25:
        return 20
    elif roce >= 20:
        return 18
    elif roce >= 15:
        return 15
    elif roce >= 10:
        return 10
    return 5


def score_growth(cagr):
    """Score Revenue CAGR (15 Marks)"""
    if pd.isna(cagr):
        return 0
    if cagr >= 20:
        return 15
    elif cagr >= 15:
        return 12
    elif cagr >= 10:
        return 10
    elif cagr >= 5:
        return 7
    return 3


def score_margin(margin):
    """Score Net Profit Margin (15 Marks)"""
    if pd.isna(margin):
        return 0
    if margin >= 20:
        return 15
    elif margin >= 15:
        return 12
    elif margin >= 10:
        return 10
    elif margin >= 5:
        return 7
    return 3


def score_quality(score):
    """Score Composite Quality Score (20 Marks)"""
    if pd.isna(score):
        return 0
    if score >= 90:
        return 20
    elif score >= 80:
        return 18
    elif score >= 70:
        return 15
    elif score >= 60:
        return 10
    return 5


def score_valuation(flag):
    """Convert valuation flag to score (10 Marks)"""
    mapping = {
        "Discount": 10,
        "Fair": 8,
        "Caution": 5,
        "Unknown": 6
    }
    return mapping.get(flag, 6)


# ==============================
# Grade Assignment
# ==============================

def assign_grade(score):
    """Assign grade based on overall score."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    return "D"


# ==============================
# Main Scoring Function
# ==============================

def calculate_company_scores(financial_df, valuation_df):
    """
    Calculate company scores by combining financial metrics
    with valuation engine results.

    Parameters
    ----------
    financial_df : DataFrame
        Financial ratios table

    valuation_df : DataFrame
        Output from valuation engine

    Returns
    -------
    DataFrame
    """

    # -------------------------
    # Merge valuation results
    # -------------------------
    df = financial_df.merge(
        valuation_df[["company_id", "flag"]],
        on="company_id",
        how="left"
    )

    df["flag"] = df["flag"].fillna("Unknown")

    # -------------------------
    # Individual Scores
    # -------------------------
    df["roe_score"] = df["return_on_equity_pct"].apply(score_roe)

    df["roce_score"] = df[
        "return_on_capital_employed_pct"
    ].apply(score_roce)

    df["growth_score"] = df[
        "revenue_cagr_5yr"
    ].apply(score_growth)

    df["margin_score"] = df[
        "net_profit_margin_pct"
    ].apply(score_margin)

    df["quality_score"] = df[
        "composite_quality_score"
    ].apply(score_quality)

    df["valuation_score"] = df["flag"].apply(score_valuation)

    # -------------------------
    # Overall Score
    # -------------------------
    df["overall_score"] = (
        df["roe_score"]
        + df["roce_score"]
        + df["growth_score"]
        + df["margin_score"]
        + df["quality_score"]
        + df["valuation_score"]
    )

    # -------------------------
    # Grade
    # -------------------------
    df["grade"] = df["overall_score"].apply(assign_grade)

    return df

import sqlite3
from pathlib import Path

# Import your Day-26 valuation engine
from src.valuation.valuation_engine import generate_valuation_summary


# =====================================================
# Database Connection
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


def get_connection():
    """Create SQLite connection."""
    return sqlite3.connect(DB_PATH)


# =====================================================
# Load Financial Ratios
# =====================================================

def load_financial_ratios():
    """
    Load the latest financial ratios from SQLite.
    """

    conn = get_connection()

    query = """
        SELECT
            fr.company_id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.net_profit_margin_pct,
            fr.revenue_cagr_5yr,
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


# =====================================================
# Generate Company Scorecard
# =====================================================

def generate_company_scorecard():
    """
    Complete scoring pipeline.

    Returns
    -------
    DataFrame
    """

    # Financial data
    financial_df = load_financial_ratios()

    # Day-26 valuation engine
    valuation_df = generate_valuation_summary()

    # Calculate scores
    score_df = calculate_company_scores(
        financial_df,
        valuation_df
    )

    # Highest score first
    score_df = score_df.sort_values(
        "overall_score",
        ascending=False
    ).reset_index(drop=True)

    # Ranking
    score_df["rank"] = score_df.index + 1

    return score_df

import sqlite3
from pathlib import Path

from src.valuation.valuation_engine import generate_valuation_summary


# ==========================================================
# DATABASE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB = BASE_DIR / "db" / "nifty100.db"


def get_connection():
    return sqlite3.connect(DB)


# ==========================================================
# LOAD FINANCIAL DATA
# ==========================================================

def load_financial_ratios():

    conn = get_connection()

    query = """
        SELECT
            fr.company_id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.net_profit_margin_pct,
            fr.revenue_cagr_5yr,
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


# ==========================================================
# GENERATE COMPANY SCORECARD
# ==========================================================

def generate_company_scorecard():

    financial_df = load_financial_ratios()

    valuation_df = generate_valuation_summary()

    score_df = calculate_company_scores(
        financial_df,
        valuation_df
    )

    score_df = score_df.sort_values(
        "overall_score",
        ascending=False
    ).reset_index(drop=True)

    score_df["rank"] = score_df.index + 1

    return score_df


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    df = generate_company_scorecard()

    print(df[
        [
            "rank",
            "company_name",
            "overall_score",
            "grade"
        ]
    ].head(10))