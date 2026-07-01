import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql(
    "SELECT * FROM financial_ratios LIMIT 10",
    conn
)

print(df)

count = pd.read_sql(
    "SELECT COUNT(*) AS total_rows FROM financial_ratios",
    conn
)

print("\nTotal Rows:")
print(count)

conn.close()