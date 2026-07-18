"""
Sprint 5 - Day 29

Financial Metrics Parser
"""

import re
import sqlite3
from pathlib import Path

import pandas as pd

# =====================================================
# PROJECT PATHS
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# =====================================================
# DATABASE
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# =====================================================
# LOAD DATA
# =====================================================

def load_analysis():

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM analysis",
        conn
    )

    conn.close()

    print("=" * 60)
    print("Analysis Table Loaded")
    print("=" * 60)

    print(f"Rows : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print()

    print(df.head())

    return df

# =====================================================
# PARSE METRIC
# =====================================================

def parse_metric(text):

    if pd.isna(text):
        return None

    text = str(text).strip()

    if text == "":
        return None

    pattern = (
    r"(TTM|Last Year|1 Year|3 Years|5 Years|10 Years)"
    r"\s*:?\s*"
    r"(-?\d+\.?\d*)%?"
    )

    match = re.search(pattern, text)

    if match:

        period = match.group(1)

        value = float(match.group(2))

        return {

            "period": period,

            "value": value

        }

    return None

# =====================================================
# PARSE COMPANY
# =====================================================

def parse_company(row):

    metrics = {

        "Sales Growth": row["compounded_sales_growth"],

        "Profit Growth": row["compounded_profit_growth"],

        "Stock CAGR": row["stock_price_cagr"],

        "ROE": row["roe"]

    }

    rows = []

    for metric_name, raw_value in metrics.items():

        parsed = parse_metric(raw_value)

        if parsed is None:
            continue

        rows.append({
            "company_id": row["company_id"],
            "metric": metric_name,
            "period": parsed["period"],
            "value": parsed["value"],
            "raw_value": raw_value
        })

    return rows

# =====================================================
# PARSE ENTIRE TABLE
# =====================================================

def parse_all(df):

    print("\n" + "=" * 60)
    print("Parsing Financial Metrics...")
    print("=" * 60)

    parsed_rows = []

    for _, row in df.iterrows():

        parsed_rows.extend(
            parse_company(row)
        )

    parsed_df = pd.DataFrame(parsed_rows)

    print(f"\nTotal Parsed Records : {len(parsed_df)}")

    return parsed_df


# =====================================================
# VALIDATION
# =====================================================

def validate_data(df):

    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    print(df["company_id"].value_counts())

    print(f"Total Records      : {len(df)}")

    print(f"Companies          : {df['company_id'].nunique()}")

    print(f"Metrics            : {df['metric'].nunique()}")

    print(f"Missing Values     : {df.isna().sum().sum()}")

    print("\nRecords per Metric:")

    print(df["metric"].value_counts())

    return df


# =====================================================
# EXPORT
# =====================================================

def export_data(df):

    output_file = OUTPUT_DIR / "analysis_parsed.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("Export Complete")
    print("=" * 60)

    print(f"Saved to : {output_file}")

    return output_file

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    analysis = load_analysis()

    parsed = parse_all(analysis)

    validate_data(parsed)

    export_data(parsed)