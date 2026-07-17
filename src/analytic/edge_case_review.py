import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

financial = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)

df = (
    financial
    .merge(
        companies,
        on="company_id"
    )
    .merge(
        sectors,
        on="company_id"
    )
)
log = open(
    "output/ratio_edge_cases.log",
    "w",
    encoding="utf-8"
)

for _, row in df.iterrows():

    if pd.isna(row["roce_percentage"]):
        continue

    if pd.isna(row["return_on_equity_pct"]):
        continue

    difference = abs(
        row["return_on_equity_pct"]
        - row["roe_percentage"]
    )

    if difference > 5:

        log.write(
            f"{row.company_id} | ROE Difference = {difference:.2f}%\n"
        )

financial_sector = [
    "Banks",
    "Financial Services",
    "Insurance",
    "NBFC"
]

for _, row in df.iterrows():

    if row["broad_sector"] in financial_sector:

        log.write(
            f"{row.company_id} | Financial Sector | D/E Warning Suppressed\n"
        )


if abs(
    row["roce_percentage"]
    - row["return_on_equity_pct"]
) > 5:

    log.write(
        f"{row.company_id} | ROCE anomaly\n"
    )

if difference > 5:

    category = "Formula Difference"

    log.write(
        f"""
Company : {row.company_id}

Difference : {difference:.2f}

Category : {category}

--------------------------
"""
    )

log.close()

print("ratio_edge_cases.log generated")


import os

print(
    os.path.exists(
        "output/ratio_edge_cases.log"
    )
)