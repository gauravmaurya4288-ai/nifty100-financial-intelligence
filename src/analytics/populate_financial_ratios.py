import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.ratios import *
from src.analytics.cagr import *
from src.analytics.cashflow_kpis import *


import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

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

print("Profit Loss:", profit.shape)
print("Balance Sheet:", balance.shape)
print("Cash Flow:", cash.shape)

df = (
    profit
    .merge(
        balance,
        on=["company_id", "year"]
    )
    .merge(
        cash,
        on=["company_id", "year"]
    )
)

rows = []

for _, row in df.iterrows():

    npm = net_profit_margin(
        row.net_profit,
        row.sales
    )

    opm = operating_profit_margin(
        row.operating_profit,
        row.sales
    )

    roe = return_on_equity(
        row.net_profit,
        row.equity_capital,
        row.reserves
    )

    de = debt_to_equity(
        row.borrowings,
        row.equity_capital,
        row.reserves
    )

    icr = interest_coverage_ratio(
        row.operating_profit,
        row.other_income,
        row.interest
    )

    asset = asset_turnover(
        row.sales,
        row.total_assets
    )

    fcf = free_cash_flow(
        row.operating_activity,
        row.investing_activity
    )

    
    capex, _ = capex_intensity(
    row.investing_activity,
    row.sales
)

        

    rows.append({

        "company_id": row.company_id,
        "year": row.year,

        "net_profit_margin_pct": npm,
        "operating_profit_margin_pct": opm,
        "return_on_equity_pct": roe,

        "debt_to_equity": de,
        "interest_coverage": icr,
        "asset_turnover": asset,

        "free_cash_flow_cr": fcf,
        "capex_cr": capex,

        "earnings_per_share": row.eps,

        "book_value_per_share":
            (row.equity_capital + row.reserves),

        "dividend_payout_ratio_pct":
            row.dividend_payout,

        "total_debt_cr":
            row.borrowings,

        "cash_from_operations_cr":
            row.operating_activity

    })
print("Rows generated:", len(rows))

financial = pd.DataFrame(rows)

financial.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

print(financial.head())

count = pd.read_sql(
    """
    SELECT COUNT(*)
    FROM financial_ratios
    """,
    conn
)

print(count)

