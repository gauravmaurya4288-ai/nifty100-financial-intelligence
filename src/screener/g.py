import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("SELECT * FROM financial_ratios LIMIT 5", conn)

profit = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

balance = pd.read_sql(
    "SELECT * FROM balance_sheet",
    conn
)

cash = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

market = pd.read_sql(
    "SELECT * FROM market_cap",
    conn
)

analysis = pd.read_sql(
    "SELECT * FROM analysis",
    conn
)

print(df.columns.tolist())

conn.close()