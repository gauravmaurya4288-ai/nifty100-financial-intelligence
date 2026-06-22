import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print("=" * 50)
print("MANUAL DATA QUALITY REVIEW")
print("=" * 50)

# Random 5 companies

query = """
SELECT company_id, company_name
FROM companies
ORDER BY RANDOM()
LIMIT 5
"""

companies = pd.read_sql(query, conn)

print("\nRandom 5 Companies:")
print(companies)
 

 ## Year Coverage

print("\nYear Coverage")

query = """
SELECT
    company_id,
    COUNT(DISTINCT year) AS years_available
FROM profit_loss
GROUP BY company_id
ORDER BY years_available ASC
"""

coverage = pd.read_sql(query, conn)

print(coverage.head(20))

## Companies with less than 5 Year

query = """
SELECT
    company_id,
    COUNT(DISTINCT year) AS years_available
FROM profit_loss
GROUP BY company_id
HAVING COUNT(DISTINCT year) < 5
"""

few_years = pd.read_sql(query, conn)

print("\nCompanies With <5 Years Data")
print(few_years)

## Row Count

tables = [
    "companies",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "ratios",
    "stock_prices",
    "market_cap",
    "pros_cons",
    "sectors",
    "analysis",
    "peer_groups",
    "documents"
]

print("\nRow Counts")

for table in tables:

    count = pd.read_sql(
        f"SELECT COUNT(*) AS cnt FROM {table}",
        conn
    )

    print(
        f"{table}: {count.iloc[0,0]}"
    )