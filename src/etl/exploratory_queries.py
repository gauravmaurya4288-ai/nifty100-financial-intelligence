import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

queries = {

    "Companies Count":
    """
    SELECT COUNT(*) AS total_companies
    FROM companies;
    """,

    "Top Market Cap":
    """
    SELECT company_id,
           MAX(market_cap_crore) AS market_cap
    FROM market_cap
    GROUP BY company_id
    ORDER BY market_cap DESC
    LIMIT 10;
    """,

    "Top ROE":
    """
    SELECT company_id,
           AVG(roe) AS avg_roe
    FROM analysis
    GROUP BY company_id
    ORDER BY avg_roe DESC
    LIMIT 10;
    """,

    "Average Close Price":
    """
    SELECT company_id,
           AVG(close_price) AS avg_close
    FROM stock_prices
    GROUP BY company_id;
    """,

    "Sector Distribution":
    """
    SELECT broad_sector,
           COUNT(*) AS companies
    FROM sectors
    GROUP BY broad_sector;
    """
}

for title, query in queries.items():

    print("\n" + "="*50)
    print(title)
    print("="*50)

    df = pd.read_sql(query, conn)

    print(df)

conn.close()