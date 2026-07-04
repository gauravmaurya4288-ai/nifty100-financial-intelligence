import sqlite3
import pandas as pd
import yaml

DB_PATH = "db/nifty100.db"
CONFIG_PATH = "config/screener_config.yaml"

with open(CONFIG_PATH, "r") as file:
    config = yaml.safe_load(file)

    conn = sqlite3.connect(DB_PATH)

    financial = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

market = pd.read_sql(
    "SELECT * FROM market_cap",
    conn
)

sector = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)

df = (
    financial
    .merge(
        market,
        on=["company_id","year"],
        how="left"
    )
    .merge(
        sector,
        on="company_id",
        how="left"
    )
)

df["composite_quality_score"] = (

    df["return_on_equity_pct"].fillna(0)

    +

    df["net_profit_margin_pct"].fillna(0)

    +

    df["revenue_cagr_5yr"].fillna(0)

) / 3


financial_sector = [

    "Banks",

    "Financial Services",

    "Insurance",

    "NBFC"

]

df = df[
    df.return_on_equity_pct >= config["roe_min"]
]

mask = (

    (df.broad_sector.isin(financial_sector))

    |

    (df.debt_to_equity <= config["de_max"])

)

df = df[mask]

df = df[
    df.free_cash_flow_cr >= config["fcf_min"]
]


df = df[
    df.revenue_cagr_5yr >=
    config["revenue_cagr_5yr_min"]
]

df = df[
    df.operating_profit_margin_pct >=
    config["opm_min"]
]

df = df[
    df.pe_ratio <=
    config["pe_max"]
]

df = df[
    df.pb_ratio <=
    config["pb_max"]
]

df = df[
    df.dividend_yield_pct >=
    config["dividend_yield_min"]
]

df["interest_coverage"] = (
    df["interest_coverage"]
    .fillna(float("inf"))
)

df = df[
    df.interest_coverage >=
    config["interest_coverage_min"]
]

df = df[
    df.market_cap_crore >=
    config["market_cap_min"]
]

df = df[
    df.asset_turnover >=
    config["asset_turnover_min"]
]


profit = pd.read_sql(
    "SELECT company_id,year,sales,net_profit FROM profit_loss",
    conn
)

df = df.merge(
    profit,
    on=["company_id","year"],
    how="left"
)

df = df[
    df.sales >= config["sales_min"]
]

df = df[
    df.net_profit >= config["net_profit_min"]
]

df = df.sort_values(
    "composite_quality_score",
    ascending=False
)

print("="*70)

print("Financial Screener")

print("="*70)

print(df.head(20))

print()

print("Companies Found :",len(df))

conn.close()
