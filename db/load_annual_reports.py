import sqlite3
import pandas as pd

DB = "db/nifty100.db"

conn = sqlite3.connect(DB)

companies = pd.read_sql(
    """
    SELECT company_id, company_name
    FROM companies
    """,
    conn
)

years = [
    "2024",
    "2023",
    "2022",
    "2021",
    "2020"
]

rows = []

for _, row in companies.iterrows():

    for year in years:

        rows.append({

            "company_id": row["company_id"],

            "company_name": row["company_name"],

            "year": year,

            "report_url": "",

            "status": "Unavailable"

        })

reports = pd.DataFrame(rows)

reports.to_sql(
    "annual_reports",
    conn,
    if_exists="append",
    index=False
)

conn.commit()

print("=" * 60)
print("Annual Reports Loaded")
print("=" * 60)
print("Rows Inserted :", len(reports))
print(reports.head())

conn.close()