"""
cashflow_kpis.py
---------------------------------
Cash Flow Intelligence Module

Sprint 5 - Day 31

Calculates:

• Free Cash Flow
• CFO Quality
• CapEx Intensity
• FCF Conversion
• Capital Allocation Pattern
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    """Return SQLite connection."""
    return sqlite3.connect(DB_PATH)


# ==========================================================
# LOAD DATA
# ==========================================================

def load_data():
    """
    Load all required tables.

    Returns
    -------
    dict
        Dictionary containing DataFrames.
    """

    conn = get_connection()

    data = {
        "companies": pd.read_sql(
            "SELECT * FROM companies",
            conn,
        ),

        "cash_flow": pd.read_sql(
            "SELECT * FROM cash_flow",
            conn,
        ),

        "profit_loss": pd.read_sql(
            "SELECT * FROM profit_loss",
            conn,
        ),

        "balance_sheet": pd.read_sql(
            "SELECT * FROM balance_sheet",
            conn,
        ),

        "financial_ratios": pd.read_sql(
            "SELECT * FROM financial_ratios",
            conn,
        ),

        "sectors": pd.read_sql(
            "SELECT * FROM sectors",
            conn,
        ),
    }

    conn.close()

    return data


# ==========================================================
# FREE CASH FLOW
# ==========================================================

def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow
    """

    if pd.isna(operating_activity) or pd.isna(investing_activity):
        return np.nan

    return operating_activity + investing_activity


# ==========================================================
# CFO QUALITY SCORE
# ==========================================================

def cfo_quality_score(cfo, pat):
    """
    CFO/PAT Ratio Classification

    Returns
    -------
    High Quality
    Moderate
    Accrual Risk
    """

    if pat is None or pat == 0 or pd.isna(pat):
        return None

    ratio = cfo / pat

    if ratio > 1:
        return "High Quality"

    elif ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


# ==========================================================
# CAPEX INTENSITY
# ==========================================================

def capex_intensity(investing_activity, sales):
    """
    Returns
    -------
    (percentage, label)
    """

    if sales is None or sales == 0 or pd.isna(sales):
        return (np.nan, None)

    if investing_activity is None or pd.isna(investing_activity):
        return (np.nan, None)

    intensity = abs(investing_activity) / sales * 100

    if intensity < 3:
        label = "Asset Light"

    elif intensity <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(intensity, 2), label


# ==========================================================
# FCF CONVERSION
# ==========================================================

def fcf_conversion(fcf, operating_profit):
    """
    FCF Conversion (%)
    """

    if operating_profit is None or operating_profit == 0:
        return np.nan

    return round((fcf / operating_profit) * 100, 2)


# ==========================================================
# CAPITAL ALLOCATION PATTERN
# ==========================================================

def capital_allocation_pattern(cfo, cfi, cff, quality=""):
    """
    Classify capital allocation pattern
    """

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):

        if quality == "High Quality":
            return "Shareholder Returns"

        return "Reinvestor"

    elif signs == ("+", "+", "-"):
        return "Liquidating Assets"

    elif signs == ("-", "+", "+"):
        return "Distress Signal"

    elif signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    elif signs == ("+", "+", "+"):
        return "Cash Accumulator"

    elif signs == ("-", "-", "-"):
        return "Pre-Revenue"

    elif signs == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"


# ==========================================================
# CAGR CALCULATION
# ==========================================================

def calculate_cagr(start_value, end_value, years):
    """
    Calculate CAGR.

    Returns
    -------
    float
    """

    if (
        start_value is None
        or end_value is None
        or start_value <= 0
        or end_value <= 0
        or years <= 0
    ):
        return np.nan

    return ((end_value / start_value) ** (1 / years) - 1) * 100

# ==========================================================
# FCF CAGR (5 YEARS)
# ==========================================================

def calculate_fcf_cagr(fcf_values):
    """
    Calculate 5-Year CAGR of Free Cash Flow.

    Parameters
    ----------
    fcf_values : list or Series
        Ordered oldest -> newest

    Returns
    -------
    float
        CAGR %
    """

    fcf_values = pd.Series(fcf_values).dropna()

    if len(fcf_values) < 2:
        return np.nan

    start = fcf_values.iloc[0]
    end = fcf_values.iloc[-1]

    years = len(fcf_values) - 1

    return calculate_cagr(start, end, years)


# ==========================================================
# AVERAGE CFO QUALITY SCORE
# ==========================================================

def calculate_cfo_quality(cfo_series, pat_series):
    """
    Calculate average CFO/PAT ratio over 5 years.

    Returns
    -------
    average_ratio
    quality_label
    """

    ratios = []

    for cfo, pat in zip(cfo_series, pat_series):

        if pd.isna(cfo):
            continue

        if pd.isna(pat):
            continue

        if pat == 0:
            continue

        ratios.append(cfo / pat)

    if len(ratios) == 0:
        return np.nan, "Unknown"

    avg_ratio = np.mean(ratios)

    if avg_ratio > 1:
        label = "High Quality"

    elif avg_ratio >= 0.5:
        label = "Moderate"

    else:
        label = "Accrual Risk"

    return round(avg_ratio, 2), label


# ==========================================================
# DISTRESS SIGNAL
# ==========================================================

def detect_distress(latest_cfo, latest_cff):
    """
    Distress Signal

    CFO < 0
    AND
    CFF > 0
    """

    if pd.isna(latest_cfo):
        return False

    if pd.isna(latest_cff):
        return False

    return latest_cfo < 0 and latest_cff > 0


# ==========================================================
# DELEVERAGING
# ==========================================================

def detect_deleveraging(cff_latest,
                        borrowings_latest,
                        borrowings_previous):
    """
    Detect active debt repayment.

    Conditions

    CFF < 0

    AND

    Borrowings decreasing
    """

    if pd.isna(cff_latest):
        return False

    if pd.isna(borrowings_latest):
        return False

    if pd.isna(borrowings_previous):
        return False

    return (
        cff_latest < 0
        and
        borrowings_latest < borrowings_previous
    )


# ==========================================================
# CAPITAL ALLOCATION LABEL
# ==========================================================

def capital_allocation_label(pattern):
    """
    Friendly label used in reports.
    """

    mapping = {

        "Shareholder Returns":
            "Excellent",

        "Reinvestor":
            "Growth Focused",

        "Growth Funded by Debt":
            "Aggressive",

        "Cash Accumulator":
            "Conservative",

        "Liquidating Assets":
            "Restructuring",

        "Distress Signal":
            "High Risk",

        "Mixed":
            "Balanced",

        "Pre-Revenue":
            "Early Stage",

        "Unknown":
            "Unknown",
    }

    return mapping.get(pattern, "Unknown")


# ==========================================================
# BUILD COMPANY CASHFLOW KPIs
# ==========================================================

def build_company_cashflow_metrics(company_df):
    """
    Build cash-flow KPIs for a single company.

    Parameters
    ----------
    company_df : DataFrame
        Sorted by year

    Returns
    -------
    dict
    """

    company_df = company_df.sort_values("year")

    company_df["fcf"] = company_df.apply(
        lambda row: free_cash_flow(
            row["operating_activity"],
            row["investing_activity"],
        ),
        axis=1,
    )

    latest = company_df.iloc[-1]

    avg_ratio, quality = calculate_cfo_quality(
        company_df["operating_activity"],
        company_df["net_profit"],
    )

    capex_pct, capex_label = capex_intensity(
        latest["investing_activity"],
        latest["sales"],
    )

    pattern = capital_allocation_pattern(
        latest["operating_activity"],
        latest["investing_activity"],
        latest["financing_activity"],
        quality,
    )

    metrics = {

        "cfo_quality_score": avg_ratio,

        "cfo_quality_label": quality,

        "capex_intensity_pct": capex_pct,

        "capex_label": capex_label,

        "fcf_cagr_5yr":
            calculate_fcf_cagr(company_df["fcf"]),

        "fcf_conversion_pct":
            fcf_conversion(
                latest["fcf"],
                latest["operating_profit"],
            ),

        "distress_flag":
            detect_distress(
                latest["operating_activity"],
                latest["financing_activity"],
            ),

        "deleveraging_flag":
            detect_deleveraging(
                latest["financing_activity"],
                latest["borrowings"],
                company_df.iloc[-2]["borrowings"]
                if len(company_df) > 1
                else np.nan,
            ),

        "capital_allocation_pattern":
            pattern,

        "capital_allocation_label":
            capital_allocation_label(pattern),
    }

    return metrics


# ==========================================================
# CASH FLOW INTELLIGENCE ENGINE
# ==========================================================

def generate_cashflow_intelligence():
    """
    Generate Cash Flow Intelligence Report
    """

    print("=" * 60)
    print("Generating Cash Flow Intelligence Report...")
    print("=" * 60)

    data = load_data()

    companies = data["companies"]
    cash_flow = data["cash_flow"]
    profit_loss = data["profit_loss"]
    balance_sheet = data["balance_sheet"]
    sectors = data["sectors"]

    # -------------------------------------------------------
    # Merge datasets
    # -------------------------------------------------------

    df = (
        cash_flow
        .merge(
            profit_loss,
            on=["company_id", "year"],
            how="left",
            suffixes=("", "_pl")
        )
        .merge(
            balance_sheet,
            on=["company_id", "year"],
            how="left"
        )
        .merge(
            companies,
            on="company_id",
            how="left"
        )
        .merge(
            sectors,
            on="company_id",
            how="left"
        )
    )

    df = df.sort_values(
        ["company_id", "year"]
    )

    intelligence = []

    distress_alerts = []

    # -------------------------------------------------------
    # Process company-wise
    # -------------------------------------------------------

    for company_id, company_df in df.groupby("company_id"):

        try:

            metrics = build_company_cashflow_metrics(company_df)

            latest = company_df.sort_values(
                "year"
            ).iloc[-1]

            row = {

                "company_id":
                    company_id,

                "company_name":
                    latest.get("company_name", ""),

                "ticker":
                    latest.get("ticker", ""),

                "sector":
                    latest.get("sector", ""),

                **metrics
            }

            intelligence.append(row)

            if metrics["distress_flag"]:

                distress_alerts.append({

                    "company_id":
                        company_id,

                    "company_name":
                        latest.get("company_name", ""),

                    "ticker":
                        latest.get("ticker", ""),

                    "cfo":
                        latest["operating_activity"],

                    "cff":
                        latest["financing_activity"],

                    "latest_net_profit":
                        latest["net_profit"]
                })

        except Exception as e:

            print(f"Skipped {company_id}: {e}")

    # -------------------------------------------------------
    # Convert to DataFrame
    # -------------------------------------------------------

    intelligence_df = pd.DataFrame(intelligence)

    distress_df = pd.DataFrame(distress_alerts)

    # -------------------------------------------------------
    # Export Reports
    # -------------------------------------------------------

    intelligence_file = (
        OUTPUT_DIR /
        "cashflow_intelligence.xlsx"
    )

    distress_file = (
        OUTPUT_DIR /
        "distress_alerts.csv"
    )

    intelligence_df.to_excel(
        intelligence_file,
        index=False
    )

    distress_df.to_csv(
        distress_file,
        index=False
    )

    # -------------------------------------------------------
    # Summary
    # -------------------------------------------------------

    print()

    print("Cash Flow Intelligence Generated")

    print(
        f"Companies Processed : "
        f"{len(intelligence_df)}"
    )

    print(
        f"Distress Alerts     : "
        f"{len(distress_df)}"
    )

    print()

    print(
        f"Saved : {intelligence_file}"
    )

    print(
        f"Saved : {distress_file}"
    )

    print("=" * 60)

    return intelligence_df


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    generate_cashflow_intelligence()