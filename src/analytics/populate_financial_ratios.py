import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import sqlite3
import pandas as pd
import numpy as np

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion,
    capital_allocation_pattern
)

from src.analytics.historical_cagr import (
    calculate_company_cagr
)

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

print("=" * 70)
print("Loading Source Tables")
print("=" * 70)

profit = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

balance = pd.read_sql(
    "SELECT * FROM balance_sheet",
    conn
)

cash = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

market = pd.read_sql(
    "SELECT * FROM market_cap",
    conn
)

analysis = pd.read_sql(
    "SELECT * FROM analysis",
    conn
)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)

print("Profit :", profit.shape)
print("Balance:", balance.shape)
print("Cash :", cash.shape)
print("Market :", market.shape)
print("Analysis :", analysis.shape)
print("Companies :", companies.shape)
print("Sectors :", sectors.shape)

print("\n" + "=" * 70)
print("Preparing Historical CAGR")
print("=" * 70)

# ---------------------------------------------------
# Historical CAGR Calculation
# ---------------------------------------------------

profit_cagr = profit[
    [
        "company_id",
        "year",
        "sales",
        "net_profit",
        "eps"
    ]
].copy()

cagr_df = calculate_company_cagr(profit_cagr)

print("Historical CAGR Rows :", len(cagr_df))

# ---------------------------------------------------
# Merge Financial Tables
# ---------------------------------------------------

print("\n" + "=" * 70)
print("Merging Tables")
print("=" * 70)

df = (
    profit
    .merge(
        balance,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_bal")
    )
    .merge(
        cash,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_cash")
    )
    .merge(
        market,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_market")
    )
    .merge(
        cagr_df,
        on=["company_id", "year"],
        how="left"
    )
    .merge(
        analysis,
        on="company_id",
        how="left",
        suffixes=("", "_analysis")
    )
    .merge(
        companies,
        on="company_id",
        how="left",
        suffixes=("", "_company")
    )
    .merge(
        sectors,
        on="company_id",
        how="left",
        suffixes=("", "_sector")
    )
)

print("Merged Shape :", df.shape)

# ---------------------------------------------------
# Replace Missing Numeric Values
# ---------------------------------------------------

numeric_columns = df.select_dtypes(
    include=["number"]
).columns

df[numeric_columns] = df[numeric_columns].fillna(0)

# ---------------------------------------------------
# Remove Duplicate Company-Year Rows
# ---------------------------------------------------

df = df.drop_duplicates(
    subset=["company_id", "year"]
)

print("After Removing Duplicates :", len(df))

# ---------------------------------------------------
# Remove Non-Annual Records
# ---------------------------------------------------

df = df[
    ~df["year"].astype(str).str.contains(
        "TTM|9m|15",
        case=False,
        na=False
    )
].copy()

print("Annual Records :", len(df))

# ---------------------------------------------------
# Sort Data
# ---------------------------------------------------

df = df.sort_values(
    [
        "company_id",
        "year"
    ]
).reset_index(drop=True)

print(df.head())

# ---------------------------------------------------
# Prepare Output
# ---------------------------------------------------

rows = []

print("\nReady for KPI Calculation...")
print("=" * 70)

print("\n" + "=" * 70)
print("Calculating Financial Ratios")
print("=" * 70)

for _, row in df.iterrows():

    try:

        # --------------------------------------------------
        # Profitability Ratios
        # --------------------------------------------------

        npm = net_profit_margin(
            row["net_profit"],
            row["sales"]
        )

        opm = operating_profit_margin(
            row["operating_profit"],
            row["sales"]
        )

        roe = return_on_equity(
            row["net_profit"],
            row["equity_capital"],
            row["reserves"]
        )

        roce = return_on_capital_employed(
            row["operating_profit"],
            row["equity_capital"],
            row["reserves"],
            row["borrowings"]
        )

        roa = return_on_assets(
            row["net_profit"],
            row["total_assets"]
        )

        # --------------------------------------------------
        # Leverage
        # --------------------------------------------------

        de = debt_to_equity(
            row["borrowings"],
            row["equity_capital"],
            row["reserves"]
        )

        leverage = high_leverage_flag(
            de,
            row.get("broad_sector", "")
        )

        icr = interest_coverage_ratio(
            row["operating_profit"],
            row["other_income"],
            row["interest"]
        )

        icr_text = icr_label(icr)

        icr_warn = icr_warning(icr)

        debt = net_debt(
            row["borrowings"],
            row["investments"]
        )

        turnover = asset_turnover(
            row["sales"],
            row["total_assets"]
        )

        # --------------------------------------------------
        # Cash Flow KPIs
        # --------------------------------------------------

        fcf = free_cash_flow(
            row["operating_activity"],
            row["investing_activity"]
        )

        cfo_score = cfo_quality_score(
            row["operating_activity"],
            row["net_profit"]
        )

        capex_pct, capex_label = capex_intensity(
            row["investing_activity"],
            row["sales"]
        )

        fcf_conversion_rate = fcf_conversion(
            fcf,
            row["operating_profit"]
        )

        allocation = capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        )

        # --------------------------------------------------
        # CAGR
        # --------------------------------------------------

        revenue_cagr3 = None
        revenue_cagr5 = row.get("revenue_cagr_5yr", None)
        revenue_cagr10 = None

        pat_cagr3 = None
        pat_cagr5 = row.get("pat_cagr_5yr", None)
        pat_cagr10 = None

        eps_cagr3 = None
        eps_cagr5 = row.get("eps_cagr_5yr", None)
        eps_cagr10 = None

        revenue_flag = row.get(
            "revenue_flag",
            None
        )

        pat_flag = row.get(
            "pat_flag",
            None
        )

        eps_flag = row.get(
            "eps_flag",
            None
        )

        # --------------------------------------------------
        # Composite Score
        # --------------------------------------------------

        score = (
            (0 if roe is None else roe) * 0.35
            +
            (0 if npm is None else npm) * 0.20
            +
            (0 if turnover is None else turnover) * 10 * 0.10
            +
            (0 if revenue_cagr5 is None else revenue_cagr5) * 0.15
            +
            (0 if pat_cagr5 is None else pat_cagr5) * 0.10
            +
            (0 if de is None else max(0, 10 - de)) * 2
        )

        score = round(score, 2)

        # --------------------------------------------------
        # Store Row
        # --------------------------------------------------

        rows.append({

            "company_id": row["company_id"],
            "year": row["year"],

            "net_profit_margin_pct": npm,
            "operating_profit_margin_pct": opm,
            "return_on_equity_pct": roe,
            "return_on_capital_employed_pct": roce,
            "return_on_assets_pct": roa,

            "debt_to_equity": de,
            "high_leverage_flag": leverage,

            "interest_coverage": icr,
            "icr_label": icr_text,
            "icr_warning": icr_warn,

            "net_debt": debt,
            "asset_turnover": turnover,

            "free_cash_flow_cr": fcf,
            "cfo_quality_score": cfo_score,

            "capex_intensity_pct": capex_pct,
            "capex_category": capex_label,

            "fcf_conversion_pct": fcf_conversion_rate,
            "capital_allocation_pattern": allocation,

            "earnings_per_share": row["eps"],

            "book_value_per_share":
                row["equity_capital"] + row["reserves"],

            "dividend_payout_ratio_pct":
                row["dividend_payout"],

            "total_debt_cr":
                row["borrowings"],

            "cash_from_operations_cr":
                row["operating_activity"],

            "revenue_cagr_3yr": revenue_cagr3,
            "revenue_cagr_5yr": revenue_cagr5,
            "revenue_cagr_10yr": revenue_cagr10,

            "pat_cagr_3yr": pat_cagr3,
            "pat_cagr_5yr": pat_cagr5,
            "pat_cagr_10yr": pat_cagr10,

            "eps_cagr_3yr": eps_cagr3,
            "eps_cagr_5yr": eps_cagr5,
            "eps_cagr_10yr": eps_cagr10,

            "revenue_cagr_flag": revenue_flag,
            "pat_cagr_flag": pat_flag,
            "eps_cagr_flag": eps_flag,

            "composite_quality_score": score

        })

    except Exception as e:

        print(
            f"Error : {row['company_id']} | {row['year']}"
        )

        print(e)

print("\nRows Generated :", len(rows))

print("\n" + "=" * 70)
print("Creating Financial Ratios DataFrame")
print("=" * 70)

# --------------------------------------------------
# Convert rows into DataFrame
# --------------------------------------------------

financial = pd.DataFrame(rows)

print("Rows :", len(financial))
print("Columns :", len(financial.columns))

print(financial.head())

# --------------------------------------------------
# Ensure all required columns exist
# --------------------------------------------------

required_columns = [

    "company_id",
    "year",

    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "return_on_assets_pct",

    "debt_to_equity",
    "high_leverage_flag",

    "interest_coverage",
    "icr_label",
    "icr_warning",

    "net_debt",
    "asset_turnover",

    "free_cash_flow_cr",
    "cfo_quality_score",

    "capex_intensity_pct",
    "capex_category",

    "fcf_conversion_pct",
    "capital_allocation_pattern",

    "earnings_per_share",
    "book_value_per_share",
    "dividend_payout_ratio_pct",

    "total_debt_cr",
    "cash_from_operations_cr",

    "revenue_cagr_3yr",
    "revenue_cagr_5yr",
    "revenue_cagr_10yr",

    "pat_cagr_3yr",
    "pat_cagr_5yr",
    "pat_cagr_10yr",

    "eps_cagr_3yr",
    "eps_cagr_5yr",
    "eps_cagr_10yr",

    "revenue_cagr_flag",
    "pat_cagr_flag",
    "eps_cagr_flag",

    "composite_quality_score"

]

for column in required_columns:

    if column not in financial.columns:

        financial[column] = None

financial = financial[required_columns]

# --------------------------------------------------
# Replace NaN values
# --------------------------------------------------

financial = financial.replace(
    [np.inf, -np.inf],
    np.nan
)

# Optional: keep NULLs in SQLite
# financial = financial.fillna(0)

print("\nFinal DataFrame Shape :", financial.shape)

print("\nFinal Columns")

print(financial.columns.tolist())

print("\nSample Data")

print(financial.head())

print("\n" + "=" * 70)
print("Writing to SQLite")
print("=" * 70)

# --------------------------------------------------
# Remove old data
# --------------------------------------------------

cursor = conn.cursor()

cursor.execute("DELETE FROM financial_ratios")

conn.commit()

# --------------------------------------------------
# Insert new data
# --------------------------------------------------

financial.to_sql(
    "financial_ratios",
    conn,
    if_exists="append",
    index=False
)

conn.commit()

print("Financial Ratios inserted successfully.")

# --------------------------------------------------
# Verify row count
# --------------------------------------------------

count = pd.read_sql(
    """
    SELECT COUNT(*) AS total_rows
    FROM financial_ratios
    """,
    conn
)

print("\nRows inserted:")

print(count)

# --------------------------------------------------
# Verify columns
# --------------------------------------------------

sample = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    LIMIT 5
    """,
    conn
)

print("\nSample Data")

print(sample)

conn.close()

print("\n" + "=" * 70)
print("Financial Ratio Population Completed Successfully")
print("=" * 70)

