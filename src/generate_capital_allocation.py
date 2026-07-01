import sqlite3
import pandas as pd

from src.analytics.cashflow_kpis import (
    cfo_quality_score,
    capital_allocation_pattern
)

conn = sqlite3.connect("db/nifty100.db")

cashflow = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

rows = []

for _, row in cashflow.iterrows():

    quality = cfo_quality_score(
        row["operating_activity"],
        row["net_cash_flow"]
    )

    pattern = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
        quality
    )

    rows.append({
        "company_id": row["company_id"],
        "year": row["year"],
        "cfo_sign": "+" if row["operating_activity"] >= 0 else "-",
        "cfi_sign": "+" if row["investing_activity"] >= 0 else "-",
        "cff_sign": "+" if row["financing_activity"] >= 0 else "-",
        "pattern_label": pattern
    })

pd.DataFrame(rows).to_csv(
    "output/capital_allocation.csv",
    index=False
)

print("capital_allocation.csv generated successfully.")

conn.close()