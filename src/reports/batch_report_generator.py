"""
=====================================================
Nifty100 Financial Intelligence
Batch Portfolio Report Generator
Sprint 5 - Day 34
=====================================================
"""

# =====================================================
# IMPORTS
# =====================================================

import sqlite3
from pathlib import Path

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# =====================================================
# PROJECT PATHS
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

REPORT_DIR = OUTPUT_DIR / "portfolio_reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():
    """Return SQLite connection."""
    return sqlite3.connect(DB_PATH)

# =====================================================
# LOAD PROJECT DATA
# =====================================================

def load_data():

    conn = get_connection()

    # ----------------------------
    # SQLite Tables
    # ----------------------------

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    financial_ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn
    )

    conn.close()

    # ----------------------------
    # AI Generated Files
    # ----------------------------

    analysis = pd.read_csv(
        OUTPUT_DIR / "analysis_parsed.csv"
    )

    cashflow = pd.read_excel(
        OUTPUT_DIR / "cashflow_intelligence.xlsx"
    )

    capital = pd.read_excel(
        OUTPUT_DIR / "capital_allocation_report.xlsx"
    )

    return {

        "companies": companies,

        "financial_ratios": financial_ratios,

        "sectors": sectors,

        "analysis": analysis,

        "cashflow": cashflow,

        "capital": capital,

    }

# =====================================================
# PREVIEW DATA
# =====================================================

def preview_data():

    data = load_data()

    print("=" * 70)
    print("Batch Portfolio Report Generator")
    print("=" * 70)

    for name, df in data.items():

        print(f"{name:<20} {len(df):>6} rows")

# =====================================================
# DATA VALIDATION
# =====================================================

def validate_data():

    data = load_data()

    print("\n" + "=" * 70)
    print("DATA VALIDATION")
    print("=" * 70)

    # -------------------------------------------------
    # Dataset Information
    # -------------------------------------------------

    for name, df in data.items():

        print(f"\n{name.upper()}")

        print("-" * 40)

        print(f"Rows    : {len(df)}")
        print(f"Columns : {len(df.columns)}")

    # -------------------------------------------------
    # Required Tables
    # -------------------------------------------------

    required = [
        "companies",
        "financial_ratios",
        "sectors",
        "analysis",
        "cashflow",
        "capital",
    ]

    print("\n" + "=" * 70)
    print("REQUIRED DATASETS")
    print("=" * 70)

    for table in required:

        if table in data:

            print(f"✓ {table}")

        else:

            print(f"✗ {table} NOT FOUND")

    # -------------------------------------------------
    # Company Count Validation
    # -------------------------------------------------

    print("\n" + "=" * 70)
    print("COMPANY COUNTS")
    print("=" * 70)

    datasets = {

        "Companies":
            data["companies"]["company_id"].nunique(),

        "Sectors":
            data["sectors"]["company_id"].nunique(),

        "Cashflow":
            data["cashflow"]["company_id"].nunique(),

        "Capital":
            data["capital"]["company_id"].nunique(),

        "Analysis":
            data["analysis"]["company_id"].nunique(),

    }

    for name, count in datasets.items():

        print(f"{name:<15}: {count}")

    # -------------------------------------------------
    # Duplicate Company IDs
    # -------------------------------------------------

    print("\n" + "=" * 70)
    print("DUPLICATE COMPANY IDS")
    print("=" * 70)

    for name in ["companies", "sectors"]:

        duplicates = data[name]["company_id"].duplicated().sum()

        print(f"{name:<15}: {duplicates}")

    # -------------------------------------------------
    # Missing Values
    # -------------------------------------------------

    print("\n" + "=" * 70)
    print("MISSING VALUES")
    print("=" * 70)

    for name, df in data.items():

        missing = df.isna().sum().sum()

        print(f"{name:<15}: {missing}")

    # -------------------------------------------------
    # Sector Coverage
    # -------------------------------------------------

    print("\n" + "=" * 70)
    print("SECTOR COVERAGE")
    print("=" * 70)

    print(data["sectors"]["broad_sector"].value_counts())

    # -------------------------------------------------
    # Sample Records
    # -------------------------------------------------

    print("\n" + "=" * 70)
    print("COMPANY PREVIEW")
    print("=" * 70)

    preview = (
        data["companies"]
        .merge(
            data["sectors"],
            on="company_id",
            how="left"
        )
    )

    print(
        preview[
            [
                "company_id",
                "company_name",
                "broad_sector",
                "sub_sector",
            ]
        ].head()
    )

    print("\nValidation Completed Successfully.\n")


# =====================================================
# BUILD PORTFOLIO DATASET
# =====================================================

def build_portfolio_dataset():

    data = load_data()

    print("\n" + "=" * 70)
    print("BUILDING PORTFOLIO DATASET")
    print("=" * 70)

    # -------------------------------------------------
    # Load Tables
    # -------------------------------------------------

    companies = data["companies"].copy()
    sectors = data["sectors"].copy()
    financial_ratios = data["financial_ratios"].copy()
    cashflow = data["cashflow"].copy()
    capital = data["capital"].copy()

    # -------------------------------------------------
    # Latest Financial Ratios
    # -------------------------------------------------

    financial_ratios = (
        financial_ratios
        .sort_values("year")
        .groupby("company_id", as_index=False)
        .tail(1)
    )

    # -------------------------------------------------
    # AI Analysis Metrics
    # -------------------------------------------------

    analysis = (
        data["analysis"]
        .pivot_table(
            index="company_id",
            columns="metric",
            values="value",
            aggfunc="first"
        )
        .reset_index()
    )

    # -------------------------------------------------
    # Remove Duplicate Columns
    # -------------------------------------------------

    duplicate_columns = [
        "company_name",
        "company_logo",
        "ticker",
        "website",
        "broad_sector",
        "sub_sector",
        "market_cap_category",
        "index_weight_pct",
    ]

    for df in [financial_ratios, cashflow, capital, analysis]:

        cols = [
            c for c in duplicate_columns
            if c in df.columns
        ]

        if cols:
            df.drop(columns=cols, inplace=True)

    # -------------------------------------------------
    # Merge Everything
    # -------------------------------------------------

    dataset = (
        companies
        .merge(
            sectors,
            on="company_id",
            how="left"
        )
        .merge(
            financial_ratios,
            on="company_id",
            how="left",
            suffixes=("", "_ratio")
        )
        .merge(
            cashflow,
            on="company_id",
            how="left",
            suffixes=("", "_cashflow")
        )
        .merge(
            capital,
            on="company_id",
            how="left",
            suffixes=("", "_capital")
        )
        .merge(
            analysis,
            on="company_id",
            how="left"
        )
    )

    # -------------------------------------------------
    # Remove Duplicate Columns
    # -------------------------------------------------

    dataset = dataset.loc[:, ~dataset.columns.duplicated()]

    # -------------------------------------------------
    # Clean Company Name
    # -------------------------------------------------

    if "company_name" in dataset.columns:

        dataset["company_name"] = (
            dataset["company_name"]
            .astype(str)
            .str.replace("\n", "", regex=False)
            .str.strip()
        )

    # -------------------------------------------------
    # Convert Numeric Columns
    # -------------------------------------------------

    numeric_columns = [

        "roe_percentage",
        "roce_percentage",
        "market_cap_crore",
        "enterprise_value_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "capital_score",
        "index_weight_pct",
        "Profit Growth",
        "Sales Growth",
        "ROE",
        "Stock CAGR"

    ]

    for col in numeric_columns:

        if col in dataset.columns:

            dataset[col] = pd.to_numeric(
                dataset[col],
                errors="coerce"
            )

    # -------------------------------------------------
    # Sort Dataset
    # -------------------------------------------------

    if "market_cap_crore" in dataset.columns:

        dataset = dataset.sort_values(
            "market_cap_crore",
            ascending=False
        )

    dataset.reset_index(
        drop=True,
        inplace=True
    )

    # -------------------------------------------------
    # Dataset Summary
    # -------------------------------------------------

    print(f"\nCompanies : {len(dataset)}")
    print(f"Columns   : {len(dataset.columns)}")

    print("\nBroad Sector Distribution")

    print(
        dataset["broad_sector"]
        .value_counts()
    )

    print("\nPreview")

    preview_columns = [

        "company_id",
        "company_name",
        "broad_sector",
        "sub_sector",
        "market_cap_category",
        "market_cap_crore",
        "roe_percentage",
        "roce_percentage",
        "pe_ratio",
        "capital_score"

    ]

    preview_columns = [
        col for col in preview_columns
        if col in dataset.columns
    ]

    print(
        dataset[preview_columns].head()
    )

    return dataset

# =====================================================
# SECTOR SUMMARY REPORT
# =====================================================

def sector_summary(portfolio):

    print("\n" + "=" * 70)
    print("SECTOR SUMMARY REPORT")
    print("=" * 70)

    report = (
        portfolio
        .groupby("broad_sector")
        .agg(
            Companies=("company_id", "count"),
            Avg_MarketCap=("market_cap_crore", "mean"),
            Avg_ROE=("roe_percentage", "mean"),
            Avg_ROCE=("roce_percentage", "mean"),
            Avg_PE=("pe_ratio", "mean"),
            Avg_PB=("pb_ratio", "mean"),
            Avg_EV_EBITDA=("ev_ebitda", "mean"),
            Avg_CapitalScore=("capital_score", "mean"),
            Avg_IndexWeight=("index_weight_pct", "mean"),
        )
        .round(2)
        .reset_index()
    )

    report = report.sort_values(
        "Avg_MarketCap",
        ascending=False
    )

    report.rename(
        columns={
            "broad_sector": "Sector"
        },
        inplace=True
    )

    print(report)

    output_file = REPORT_DIR / "sector_summary.csv"

    report.to_csv(
        output_file,
        index=False
    )

    print(f"\nSaved : {output_file}")

    return report

# =====================================================
# COMPANY RANKINGS
# =====================================================

def company_rankings(portfolio):

    print("\n" + "=" * 70)
    print("COMPANY RANKINGS")
    print("=" * 70)

    rankings = {

        "Top_Market_Cap":
            portfolio.nlargest(
                10,
                "market_cap_crore"
            ),

        "Top_ROE":
            portfolio.nlargest(
                10,
                "roe_percentage"
            ),

        "Top_ROCE":
            portfolio.nlargest(
                10,
                "roce_percentage"
            ),

        "Top_Capital_Score":
            portfolio.nlargest(
                10,
                "capital_score"
            ),

        "Top_Profit_Growth":
            portfolio.nlargest(
                10,
                "Profit Growth"
            ),

        "Top_Sales_Growth":
            portfolio.nlargest(
                10,
                "Sales Growth"
            ),

        "Top_Stock_CAGR":
            portfolio.nlargest(
                10,
                "Stock CAGR"
            )

    }

    for report_name, df in rankings.items():

        print("\n" + "-" * 70)
        print(report_name.replace("_", " "))
        print("-" * 70)

        display_columns = [

            "company_name",
            "broad_sector",
            "market_cap_crore",
            "roe_percentage",
            "roce_percentage",
            "capital_score",
            "Profit Growth",
            "Sales Growth",
            "Stock CAGR"

        ]

        display_columns = [
            col for col in display_columns
            if col in df.columns
        ]

        print(df[display_columns])

        output_file = (
            REPORT_DIR /
            f"{report_name.lower()}.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(f"\nSaved : {output_file}")

    return rankings

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    preview_data()

    validate_data()

    portfolio = build_portfolio_dataset()

    sector_report = sector_summary(portfolio)
    
    rankings = company_rankings(portfolio)