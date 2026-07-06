import sys
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# Project Root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------
# Analytics Modules
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

print("=" * 80)
print("POPULATE FINANCIAL RATIOS")
print("=" * 80)

# ---------------------------------------------------------
# Load Source Tables
# ---------------------------------------------------------

print("\nLoading Source Tables...\n")

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

print("Profit Loss :", profit.shape)
print("Balance Sheet :", balance.shape)
print("Cash Flow :", cash.shape)
print("Market Cap :", market.shape)
print("Analysis :", analysis.shape)
print("Companies :", companies.shape)
print("Sectors :", sectors.shape)

# ---------------------------------------------------------
# Prepare Latest Market Data
# ---------------------------------------------------------

market["year"] = market["year"].astype(int)

market_latest = (

    market

    .sort_values("year")

    .drop_duplicates(

        subset="company_id",

        keep="last"

    )

)

print("\nLatest Market Records")

print(market_latest.head())

# ---------------------------------------------------------
# Historical CAGR
# ---------------------------------------------------------

print("\nPreparing Historical CAGR...\n")

cagr_df = calculate_company_cagr(
    profit.copy()
)

print("Historical CAGR Records :", len(cagr_df))

# ---------------------------------------------------------
# Helper Function
# ---------------------------------------------------------

def annual_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only annual financial statements.
    """

    years = (

        df["year"]

        .astype(str)

        .str.upper()

    )

    mask = (

        ~years.str.contains("TTM")

        &

        ~years.str.contains("9M")

        &

        ~years.str.contains("Q")

    )

    return df.loc[mask].copy()

print("=" * 80)

# ---------------------------------------------------------
# Merge Source Tables
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("MERGING SOURCE TABLES")
print("=" * 80)

df = (

    profit

    .merge(

        balance,

        on=["company_id", "year"],

        how="left"

    )

    .merge(

        cash,

        on=["company_id", "year"],

        how="left"

    )

    .merge(

        cagr_df,

        on=["company_id", "year"],

        how="left"

    )

    .merge(

        analysis,

        on="company_id",

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

    .merge(

        market_latest[

            [

                "company_id",

                "market_cap_crore",

                "enterprise_value_crore",

                "pe_ratio",

                "pb_ratio",

                "ev_ebitda",

                "dividend_yield_pct"

            ]

        ],

        on="company_id",

        how="left"

    )

)

print("\nMerged Shape :", df.shape)

# ---------------------------------------------------------
# Remove Duplicate Records
# ---------------------------------------------------------

df = (

    df

    .drop_duplicates(

        subset=[

            "company_id",

            "year"

        ]

    )

)

print("After Removing Duplicates :", df.shape)

# ---------------------------------------------------------
# Keep Annual Statements Only
# ---------------------------------------------------------

df = annual_records(df)

print("Annual Records :", df.shape)

# ---------------------------------------------------------
# Sort Data
# ---------------------------------------------------------

df = (

    df

    .sort_values(

        [

            "company_id",

            "year"

        ]

    )

    .reset_index(

        drop=True

    )

)

# ---------------------------------------------------------
# Replace Infinite Values
# ---------------------------------------------------------

df = df.replace(

    [

        np.inf,

        -np.inf

    ],

    np.nan

)

# ---------------------------------------------------------
# Verify Important Columns
# ---------------------------------------------------------

print("\nColumns Loaded")

print(df.columns.tolist())

print("\nMarket Data Check")

print(

    df[

        [

            "market_cap_crore",

            "pe_ratio",

            "pb_ratio",

            "ev_ebitda",

            "dividend_yield_pct"

        ]

    ].describe()

)

print("\nSample Records")

print(

    df.head()

)

print("=" * 80)

# ---------------------------------------------------------
# Calculate Financial Ratios
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("CALCULATING FINANCIAL RATIOS")
print("=" * 80)

rows = []

def safe(x):

    if pd.isna(x):
        return 0

    return float(x)

# ---------------------------------------
# Start Processing
# ---------------------------------------


for _, row in df.iterrows():

    try:

        # -------------------------------------------------
        # Profitability
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Leverage
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Cash Flow
        # -------------------------------------------------

        fcf = free_cash_flow(
            row["operating_activity"],
            row["investing_activity"]
        )

        cfo = cfo_quality_score(
            row["operating_activity"],
            row["net_profit"]
        )

        capex_pct, capex_label = capex_intensity(
            row["investing_activity"],
            row["sales"]
        )

        fcf_conv = fcf_conversion(
            fcf,
            row["operating_profit"]
        )

        allocation = capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        )

        # -------------------------------------------------
        # Composite Score
        # -------------------------------------------------

        score = (

            safe(roe) * 0.35 +

            safe(npm) * 0.20 +

            safe(turnover) * 1.00 +

            safe(row.get("revenue_cagr_5yr")) * 0.15 +

            safe(row.get("pat_cagr_5yr")) * 0.10 +

            max(0, 10 - safe(de)) * 2

        )

        score = round(score, 2)
        

        # -------------------------------------------------
        # Store Record
        # -------------------------------------------------

        rows.append({

            "company_id": row["company_id"],
            "year": row["year"],

            # Profitability
            "net_profit_margin_pct": npm,
            "operating_profit_margin_pct": opm,
            "return_on_equity_pct": roe,
            "return_on_capital_employed_pct": roce,
            "return_on_assets_pct": roa,

            # Leverage
            "debt_to_equity": de,
            "high_leverage_flag": leverage,
            "interest_coverage": icr,
            "icr_label": icr_text,
            "icr_warning": icr_warn,
            "net_debt": debt,
            "asset_turnover": turnover,

            # Cash Flow
            "free_cash_flow_cr": fcf,
            "cfo_quality_score": cfo,
            "capex_intensity_pct": capex_pct,
            "capex_category": capex_label,
            "fcf_conversion_pct": fcf_conv,
            "capital_allocation_pattern": allocation,

            # Market Valuation
            "market_cap_crore": row["market_cap_crore"],
            "enterprise_value_crore": row["enterprise_value_crore"],
            "pe_ratio": row["pe_ratio"],
            "pb_ratio": row["pb_ratio"],
            "ev_ebitda": row["ev_ebitda"],
            "dividend_yield_pct": row["dividend_yield_pct"],

            # Financials
            "earnings_per_share": row["eps"],
            "book_value_per_share":
                row["equity_capital"] + row["reserves"],
            "dividend_payout_ratio_pct": row["dividend_payout"],
            "total_debt_cr": row["borrowings"],
            "cash_from_operations_cr": row["operating_activity"],

            # CAGR
            "revenue_cagr_3yr": None,
            "revenue_cagr_5yr": row.get("revenue_cagr_5yr"),
            "revenue_cagr_10yr": None,

            "pat_cagr_3yr": None,
            "pat_cagr_5yr": row.get("pat_cagr_5yr"),
            "pat_cagr_10yr": None,

            "eps_cagr_3yr": None,
            "eps_cagr_5yr": row.get("eps_cagr_5yr"),
            "eps_cagr_10yr": None,

            # Flags
            "revenue_cagr_flag": row.get("revenue_flag"),
            "pat_cagr_flag": row.get("pat_flag"),
            "eps_cagr_flag": row.get("eps_flag"),

            # Composite
            "composite_quality_score": score

        })

    except Exception as e:

        print(
            f"Skipped -> {row['company_id']} | {row['year']}"
        )

        print(e)

print("\nRows Generated :", len(rows))

financial = pd.DataFrame(rows)

print("\nFinancial DataFrame Shape :", financial.shape)

print(financial.head())

print("=" * 80)

# ---------------------------------------------------------
# Final DataFrame
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("FINAL DATAFRAME")
print("=" * 80)

financial = pd.DataFrame(rows)

print("Rows :", len(financial))
print("Columns :", len(financial.columns))

print("\nColumn Names")

print(financial.columns.tolist())

# ---------------------------------------------------------
# Required Column Order
# ---------------------------------------------------------

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

    "market_cap_crore",
    "enterprise_value_crore",

    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
    "dividend_yield_pct",

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

# ---------------------------------------------------------
# Add Missing Columns
# ---------------------------------------------------------

for col in required_columns:

    if col not in financial.columns:

        financial[col] = None

financial = financial[required_columns]

# ---------------------------------------------------------
# Remove Existing Data
# ---------------------------------------------------------

cursor = conn.cursor()

cursor.execute(
    "DELETE FROM financial_ratios"
)

conn.commit()

print("\nOld Records Deleted")

# ---------------------------------------------------------
# Insert New Data
# ---------------------------------------------------------

financial.to_sql(

    "financial_ratios",

    conn,

    if_exists="append",

    index=False

)

print("\nData Inserted Successfully")

# ---------------------------------------------------------
# Verification
# ---------------------------------------------------------

count = pd.read_sql(

    """
    SELECT COUNT(*) AS total_rows
    FROM financial_ratios
    """,

    conn

)

print("\nDatabase Row Count")

print(count)

# ---------------------------------------------------------
# Verify Important Columns
# ---------------------------------------------------------

verification = pd.read_sql(

    """
    SELECT

        COUNT(pe_ratio) AS pe,

        COUNT(pb_ratio) AS pb,

        COUNT(dividend_yield_pct) AS dividend,

        COUNT(revenue_cagr_5yr) AS revenue,

        COUNT(composite_quality_score) AS score

    FROM financial_ratios

    """,

    conn

)

print("\nVerification")

print(verification)

# ---------------------------------------------------------
# Preview
# ---------------------------------------------------------

print("\nSample Data")

print(

    financial.head()

)

# ---------------------------------------------------------
# Save Backup
# ---------------------------------------------------------

financial.to_csv(

    PROJECT_ROOT / "output" / "financial_ratios.csv",

    index=False

)

print("\nCSV Exported")

print(PROJECT_ROOT / "output" / "financial_ratios.csv")

# ---------------------------------------------------------
# Close Database
# ---------------------------------------------------------

conn.close()

print("\n" + "=" * 80)
print("FINANCIAL RATIOS POPULATION COMPLETED")
print("=" * 80)