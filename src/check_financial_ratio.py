import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print("=" * 50)
print("Financial Ratios Table")
print("=" * 50)

print(df.head())

print("\nRows :", len(df))

print("\nColumns")

print(df.columns.tolist())

conn.close()