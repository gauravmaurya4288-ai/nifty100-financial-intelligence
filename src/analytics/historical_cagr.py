import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import sqlite3
import pandas as pd

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)


def prepare_year(df):
    """
    Extract 4-digit year from strings like:
    Mar 2018
    Dec 2012
    Mar-18
    """

    df = df.copy()

    # Extract 4-digit year
    df["year_num"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})", expand=False)
    )

    # Remove invalid rows
    df = df[df["year_num"].notna()].copy()

    # Convert to integer
    df["year_num"] = df["year_num"].astype(int)

    return df


def calculate_company_cagr(df):
    """
    Calculates 5-Year Revenue, PAT and EPS CAGR
    for every company.
    """

    df = prepare_year(df)

    df = df.sort_values(
        ["company_id", "year_num"]
    )

    output = []

    for company, group in df.groupby("company_id"):

        group = group.sort_values("year_num")

        group = group.reset_index(drop=True)

        for i in range(len(group)):

            row = group.iloc[i]

            revenue = None
            pat = None
            eps = None

            revenue_flag = "INSUFFICIENT"
            pat_flag = "INSUFFICIENT"
            eps_flag = "INSUFFICIENT"

            previous = group[
                group["year_num"]
                == row["year_num"] - 5
            ]

            if not previous.empty:

                previous = previous.iloc[0]

                revenue, revenue_flag = revenue_cagr(

                    previous["sales"],

                    row["sales"],

                    5

                )

                pat, pat_flag = pat_cagr(

                    previous["net_profit"],

                    row["net_profit"],

                    5

                )

                eps, eps_flag = eps_cagr(

                    previous["eps"],

                    row["eps"],

                    5

                )

            output.append({

                "company_id":
                    row["company_id"],

                "year":
                    row["year"],

                "revenue_cagr_5yr":
                    revenue,

                "revenue_flag":
                    revenue_flag,

                "pat_cagr_5yr":
                    pat,

                "pat_flag":
                    pat_flag,

                "eps_cagr_5yr":
                    eps,

                "eps_flag":
                    eps_flag

            })

    return pd.DataFrame(output)


if __name__ == "__main__":

    import sqlite3

    conn = sqlite3.connect(
        "db/nifty100.db"
    )

    profit = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            net_profit,
            eps
        FROM profit_loss
        """,
        conn
    )

    result = calculate_company_cagr(
        profit
    )

    print(result.head())

    print()

    print("Rows :", len(result))

    conn.close()


import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql(
    "SELECT DISTINCT year FROM profit_loss",
    conn
)

print(df)

conn.close()