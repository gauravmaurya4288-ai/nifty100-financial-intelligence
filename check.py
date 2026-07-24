import sqlite3
from src.api.config import DB_PATH

conn = sqlite3.connect(DB_PATH)

rows = conn.execute("""
SELECT company_id, company_name
FROM companies
LIMIT 10
""").fetchall()

for row in rows:
    print(row)

conn.close()