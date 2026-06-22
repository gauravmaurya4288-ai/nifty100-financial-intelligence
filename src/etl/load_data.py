import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

audit = []


def load_table(df, table_name):

    try:

        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )

        audit.append({
            "table_name": table_name,
            "rows_loaded": len(df),
            "rows_rejected": 0,
            "load_timestamp": datetime.now()
        })

        print(f"{table_name} loaded: {len(df)}")

    except Exception as e:

        audit.append({
            "table_name": table_name,
            "rows_loaded": 0,
            "rows_rejected": len(df),
            "load_timestamp": datetime.now()
        })

        print(f"\nERROR loading {table_name}")
        print(type(e).__name__)
        print(e)


print("Loading source files...")

# =========================
# COMPANIES
# =========================

companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)

companies.rename(
    columns={"id": "company_id"},
    inplace=True
)

load_table(companies, "companies")


# =========================
# PROFIT & LOSS
# =========================

profit_loss = pd.read_excel(
    "data/raw/profitandloss.xlsx",
    header=1
)

profit_loss.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(profit_loss, "profit_loss")


# =========================
# BALANCE SHEET
# =========================

balance_sheet = pd.read_excel(
    "data/raw/balancesheet.xlsx",
    header=1
)

balance_sheet.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(balance_sheet, "balance_sheet")


# =========================
# CASH FLOW
# =========================

cash_flow = pd.read_excel(
    "data/raw/cashflow.xlsx",
    header=1
)

cash_flow.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(cash_flow, "cash_flow")


# =========================
# RATIOS
# =========================

ratios = pd.read_excel(
    "data/raw/financial_ratios.xlsx"
)

ratios.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(ratios, "ratios")


# =========================
# STOCK PRICES
# =========================

stock_prices = pd.read_excel(
    "data/raw/stock_prices.xlsx"
)

stock_prices.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(stock_prices, "stock_prices")


# =========================
# MARKET CAP
# =========================

market_cap = pd.read_excel(
    "data/raw/market_cap.xlsx"
)

market_cap.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(market_cap, "market_cap")


# =========================
# PROS & CONS
# =========================

pros_cons = pd.read_excel(
    "data/raw/prosandcons.xlsx",
    header=1
)

pros_cons.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(pros_cons, "pros_cons")


# =========================
# SECTORS
# =========================

sectors = pd.read_excel(
    "data/raw/sectors.xlsx"
)

sectors.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(sectors, "sectors")


# =========================
# ANALYSIS
# =========================

analysis = pd.read_excel(
    "data/raw/analysis.xlsx",
    header=1
)

analysis.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(analysis, "analysis")


# =========================
# PEER GROUPS
# =========================

peer_groups = pd.read_excel(
    "data/raw/peer_groups.xlsx"
)

peer_groups.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(peer_groups, "peer_groups")


# =========================
# DOCUMENTS
# =========================

documents = pd.read_excel(
    "data/raw/documents.xlsx",
    header=1
)

documents.drop(
    columns=["id"],
    inplace=True,
    errors="ignore"
)

load_table(documents, "documents")


# =========================
# SAVE AUDIT
# =========================

audit_df = pd.DataFrame(audit)

audit_df.to_csv(
    "output/load_audit.csv",
    index=False
)

print("\nLoad Audit Generated")

# FK CHECK

try:

    fk = conn.execute(
        "PRAGMA foreign_key_check;"
    ).fetchall()

    print(
        f"Foreign Key Violations: {len(fk)}"
    )

except Exception:
    pass

conn.close()