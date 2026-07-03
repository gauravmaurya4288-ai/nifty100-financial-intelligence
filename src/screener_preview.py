import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
company_id,
return_on_equity_pct,
debt_to_equity

FROM financial_ratios

WHERE
return_on_equity_pct > 15
AND debt_to_equity < 1

ORDER BY return_on_equity_pct DESC
"""

df = pd.read_sql(query, conn)

print(df)

print("\nCompanies Found :", len(df))

conn.close()

with open(
    "output/ratio_edge_cases.log",
    encoding="utf8"
) as f:

    print(f.read())