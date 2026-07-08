import sys
from pathlib import Path
import sqlite3
import pandas as pd

# --------------------------------------------------
# Project Root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# --------------------------------------------------
# Imports
# --------------------------------------------------

from src.screener.presets import (
    quality_compounder,
    value_pick,
    growth_accelerator,
    dividend_champion,
    debt_free_bluechip,
    turnaround_watch,
    summary
)

from src.screener.scoring import calculate_scores
from src.screener.export import export_screener

# --------------------------------------------------
# Database
# --------------------------------------------------

DB = PROJECT_ROOT / "db" / "nifty100.db"

conn = sqlite3.connect(DB)

print("=" * 80)
print("DAY 17 - STOCK SCREENER")
print("=" * 80)

# --------------------------------------------------
# Load Data
# --------------------------------------------------

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print("\nRows Loaded :", len(df))
print("Columns :", len(df.columns))

# --------------------------------------------------
# Calculate Composite Scores
# --------------------------------------------------

print("\nCalculating Composite Scores...")

df = calculate_scores(df)

print("Completed")

print("\nTop Composite Scores")

print(
    df[
        [
            "company_id",
            "year",
            "composite_quality_score"
        ]
    ]
    .sort_values(
        "composite_quality_score",
        ascending=False
    )
    .head(10)
)

# --------------------------------------------------
# Run Presets
# --------------------------------------------------

print("\nRunning Preset Screeners...\n")

quality = quality_compounder(df)

value = value_pick(df)

growth = growth_accelerator(df)

dividend = dividend_champion(df)

bluechip = debt_free_bluechip(df)

turnaround = turnaround_watch(df)

# --------------------------------------------------
# Top 50 Only
# --------------------------------------------------

quality = quality.head(50)

value = value.head(50)

growth = growth.head(50)

dividend = dividend.head(50)

bluechip = bluechip.head(50)

turnaround = turnaround.head(50)

# --------------------------------------------------
# Summary
# --------------------------------------------------

results = {

    "Quality Compounder": quality,

    "Value Pick": value,

    "Growth Accelerator": growth,

    "Dividend Champion": dividend,

    "Debt Free Blue Chip": bluechip,

    "Turnaround Watch": turnaround

}

summary(results)

# --------------------------------------------------
# Export
# --------------------------------------------------

# --------------------------------------------------
# Export Results
# --------------------------------------------------

OUTPUT = PROJECT_ROOT / "output" / "screener_output.xlsx"

print("\nExporting Excel Report...")

export_screener(
    results,
    OUTPUT
)

print("Excel Export Completed")

print()

print("=" * 80)
print("DAY 17 COMPLETED")
print("=" * 80)

print()

print("Output File")
print(OUTPUT)

print()

print("Summary")

print(f"Quality Compounder : {len(quality)}")

print(f"Value Pick         : {len(value)}")

print(f"Growth Accelerator : {len(growth)}")

print(f"Dividend Champion  : {len(dividend)}")

print(f"Debt Free Bluechip : {len(bluechip)}")

print(f"Turnaround Watch   : {len(turnaround)}")

print()

print("Top 5 Companies")

print(

    df[

        [

            "company_id",

            "composite_quality_score"

        ]

    ]

    .sort_values(

        "composite_quality_score",

        ascending=False

    )

    .head()

)

conn.close()