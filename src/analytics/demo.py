import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

tables = [
    "companies",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "stock_prices",
    "market_cap",
    "analysis",
    "documents"
]

for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count}")

conn.close()