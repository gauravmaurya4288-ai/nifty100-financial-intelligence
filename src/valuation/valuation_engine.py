import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB = BASE_DIR / "db" / "nifty100.db"

OUTPUT = BASE_DIR / "output"

OUTPUT.mkdir(exist_ok=True)



conn = sqlite3.connect(DB)

financial = pd.read_sql(

    "SELECT * FROM financial_ratios",

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

print("Financial Ratios :", financial.shape)
print("Companies        :", companies.shape)
print("Sectors          :", sectors.shape)

financial = financial.sort_values("year")

latest = (

    financial

    .groupby("company_id")

    .tail(1)

    .reset_index(drop=True)

)

print("\nPreparing Latest Financial Records...\n")

print("Latest Records :", latest.shape)

valuation = (

    latest

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

valuation = valuation[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "free_cash_flow_cr",
        "year"
    ]
]

print("\n" + "=" * 80)
print("Missing Values")
print("=" * 80)

print(valuation.isna().sum())

print("\nMerged Shape :", valuation.shape)

print("\nValuation Dataset\n")

print(valuation.head())

# =============================================================================
# CLEAN DATA
# =============================================================================

valuation["market_cap_crore"] = valuation["market_cap_crore"].fillna(0)
valuation["free_cash_flow_cr"] = valuation["free_cash_flow_cr"].fillna(0)
valuation["pe_ratio"] = valuation["pe_ratio"].fillna(0)
valuation["pb_ratio"] = valuation["pb_ratio"].fillna(0)
valuation["ev_ebitda"] = valuation["ev_ebitda"].fillna(0)

valuation["broad_sector"] = valuation["broad_sector"].fillna("Unknown")

print("\nCalculating FCF Yield...")

valuation["fcf_yield_pct"] = np.where(
    valuation["market_cap_crore"] > 0,
    (valuation["free_cash_flow_cr"] / valuation["market_cap_crore"]) * 100,
    np.nan
)

print(
    valuation[
        [
            "company_id",
            "free_cash_flow_cr",
            "market_cap_crore",
            "fcf_yield_pct"
        ]
    ].head()
)

print("\nCalculating Sector Median PE...")

sector_pe = (
    valuation
    .groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_pe.rename(
    columns={
        "pe_ratio": "sector_median_pe"
    },
    inplace=True
)

print(sector_pe)

valuation = valuation.merge(
    sector_pe,
    on="broad_sector",
    how="left"
)

print("\nCalculating PE vs Sector Median...")

valuation["pe_vs_sector_pct"] = np.where(
    valuation["sector_median_pe"] > 0,
    (valuation["pe_ratio"] / valuation["sector_median_pe"]) * 100,
    np.nan
)

print("\nValuation Metrics")

print(
    valuation[
        [
            "company_id",
            "broad_sector",
            "pe_ratio",
            "sector_median_pe",
            "pe_vs_sector_pct",
            "fcf_yield_pct"
        ]
    ].head(10)
)
# =============================================================================
# APPLY VALUATION FLAGS
# =============================================================================

print("\nApplying Valuation Flags...")


def valuation_flag(row):

    pe = row["pe_ratio"]
    median = row["sector_median_pe"]

    if pd.isna(median) or median <= 0:
        return "Unknown"

    elif pe < median * 0.70:
        return "Discount"

    elif pe > median * 1.50:
        return "Caution"

    else:
        return "Fair"


# ----------------------------------------------------
# CREATE FLAG COLUMN
# ----------------------------------------------------

valuation["flag"] = valuation.apply(
    valuation_flag,
    axis=1
)

print("\n" + "=" * 80)
print("VALUATION FLAG SUMMARY")
print("=" * 80)

print(valuation["flag"].value_counts())


print("\nTop Valuation Records")
print("\nColumns in valuation:")
print(valuation.columns.tolist())

# =============================================================================
# CREATE SUMMARY DATAFRAME
# =============================================================================

summary = valuation[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "fcf_yield_pct",
        "sector_median_pe",
        "pe_vs_sector_pct",
        "flag",
    ]
].copy()

summary.rename(
    columns={
        "broad_sector": "sector",
        "pe_ratio": "pe",
        "pb_ratio": "pb",
    },
    inplace=True,
)

# =============================================================================
# GENERATE VALUATION SUMMARY
# =============================================================================

def generate_valuation_summary():
    """
    Return the valuation summary DataFrame.
    """
    return summary.copy()


# =============================================================================
# EXPORT REPORTS
# =============================================================================

def export_reports(summary_df):
    """
    Export valuation reports to Excel and CSV.
    """

    excel_file = OUTPUT / "valuation_summary.xlsx"

    summary_df.to_excel(
        excel_file,
        index=False
    )

    print(f"\nExcel Generated : {excel_file}")

    flags = summary_df[
        summary_df["flag"].isin(
            ["Discount", "Caution"]
        )
    ].copy()

    csv_file = OUTPUT / "valuation_flags.csv"

    flags.to_csv(
        csv_file,
        index=False
    )

    print(f"CSV Generated   : {csv_file}")

    print("\n" + "=" * 80)
    print("DAY 26 COMPLETED")
    print("=" * 80)

    print("\nTotal Companies :", len(summary_df))
    print("Flagged Companies :", len(flags))

    print("\nFlag Distribution")
    print(summary_df["flag"].value_counts())

    print("\nReports Location")
    print(OUTPUT)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    export_reports(summary)

conn.close()