"""
Sprint 5 - Day 30

Auto Pros & Cons Generator
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


# =====================================================
# PATHS
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# =====================================================
# DATABASE
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# =====================================================
# LOAD DATA
# =====================================================

def load_data():

    conn = get_connection()

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    profit_loss = pd.read_sql(
        "SELECT * FROM profit_loss",
        conn
    )

    cash_flow = pd.read_sql(
        "SELECT * FROM cash_flow",
        conn
    )

    balance_sheet = pd.read_sql(
        "SELECT * FROM balance_sheet",
        conn
    )

    conn.close()

    return (
        companies,
        ratios,
        profit_loss,
        cash_flow,
        balance_sheet
    )

# =====================================================
# COMPANY HISTORY
# =====================================================

def get_company_history(
    company_id,
    ratios,
    profit_loss,
    cash_flow,
    balance_sheet,
):

    ratio = (
        ratios[
            ratios.company_id == company_id
        ]
        .sort_values("year")
    )

    pnl = (
        profit_loss[
            profit_loss.company_id == company_id
        ]
        .sort_values("year")
    )

    cf = (
        cash_flow[
            cash_flow.company_id == company_id
        ]
        .sort_values("year")
    )

    bs = (
        balance_sheet[
            balance_sheet.company_id == company_id
        ]
        .sort_values("year")
    )

    return ratio, pnl, cf, bs


# =====================================================
# TREND HELPERS
# =====================================================

def consecutive_positive(series):
    """Count consecutive positive values from the latest year backwards."""

    values = series.fillna(0).to_list()

    count = 0

    for value in reversed(values):
        if value > 0:
            count += 1
        else:
            break

    return count


def consecutive_negative(series):
    """Count consecutive negative values from the latest year backwards."""

    values = series.fillna(0).tolist()

    count = 0

    for value in reversed(values):
        if value < 0:
            count += 1
        else:
            break

    return count


def improving(series, years=3):

    s = series.dropna()

    if len(s) < years:
        return False

    s = s.tail(years).tolist()

    return all(
        s[i] > s[i - 1]
        for i in range(1, len(s))
    )


def declining(series, years=3):

    s = series.dropna()

    if len(s) < years:
        return False

    s = s.tail(years).tolist()

    return all(
        s[i] < s[i - 1]
        for i in range(1, len(s))
    )


# =====================================================
# PRO RULES
# =====================================================

def generate_pros(ratio, pnl, cf, bs):

    pros = []

    latest_ratio = ratio.iloc[-1]
    latest_pnl = pnl.iloc[-1]
    latest_cf = cf.iloc[-1]
    latest_bs = bs.iloc[-1]

    # -------------------------------------------------
    # PRO 1
    # ROE > 20%
    # -------------------------------------------------

    if latest_ratio["return_on_equity_pct"] > 20:

        pros.append({
            "rule_id": "PRO_01",
            "text": "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
            "confidence_pct": 95
        })

    # -------------------------------------------------
    # PRO 2
    # Positive CFO for 5 Years
    # -------------------------------------------------

    if consecutive_positive(
        cf["operating_activity"]
    ) >= 5:

        pros.append({
            "rule_id": "PRO_02",
            "text": "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # PRO 3
    # Debt Free
    # -------------------------------------------------

    if latest_ratio["debt_to_equity"] == 0:

        pros.append({
            "rule_id": "PRO_03",
            "text": "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
            "confidence_pct": 100
        })

    # -------------------------------------------------
    # PRO 4
    # Revenue CAGR
    # -------------------------------------------------

    if latest_ratio["revenue_cagr_5yr"] > 15:

        pros.append({
            "rule_id": "PRO_04",
            "text": "Revenue growing above 15% CAGR over 5 years reflects strong business momentum.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # PRO 5
    # OPM
    # -------------------------------------------------

    if latest_ratio["operating_profit_margin_pct"] > 25:

        pros.append({
            "rule_id": "PRO_05",
            "text": "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
            "confidence_pct": 85
        })

    # -------------------------------------------------
    # PRO 6
    # PAT CAGR
    # -------------------------------------------------

    if latest_ratio["pat_cagr_5yr"] > 20:

        pros.append({
            "rule_id": "PRO_06",
            "text": "Net profit compounding above 20% over 5 years creates significant shareholder value.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # PRO 7
    # Interest Coverage
    # -------------------------------------------------

    if (
        latest_ratio["interest_coverage"] > 10
        or
        latest_ratio["debt_to_equity"] == 0
    ):

        pros.append({
            "rule_id": "PRO_07",
            "text": "Very high interest coverage ratio reflects negligible financial stress from debt servicing.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # PRO 8
    # Dividend
    # -------------------------------------------------

    if (
        latest_ratio["dividend_yield_pct"] > 2
        and
        consecutive_positive(
            cf["operating_activity"]
        ) >= 5
    ):

        pros.append({
            "rule_id": "PRO_08",
            "text": "Consistent dividend yield above 2% backed by positive free cash flow.",
            "confidence_pct": 85
        })

    # -------------------------------------------------
    # PRO 9
    # EPS CAGR
    # -------------------------------------------------

    if latest_ratio["eps_cagr_5yr"] > 15:

        pros.append({
            "rule_id": "PRO_09",
            "text": "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # PRO 10
    # Improving ROE
    # -------------------------------------------------

    if improving(
        ratio["return_on_equity_pct"]
    ):

        pros.append({
            "rule_id": "PRO_10",
            "text": "Return on equity improving for 3 consecutive years shows strengthening business quality.",
            "confidence_pct": 80
        })

    # -------------------------------------------------
    # PRO 11
    # PAT > Revenue CAGR
    # -------------------------------------------------

    if (
        latest_ratio["pat_cagr_5yr"] >
        latest_ratio["revenue_cagr_5yr"]
    ):

        pros.append({
            "rule_id": "PRO_11",
            "text": "Revenue growing slower than profits shows improving operating leverage and scale benefits.",
            "confidence_pct": 80
        })

    # -------------------------------------------------
    # PRO 12
    # Assets Growing + Borrowings Falling
    # -------------------------------------------------

    if (
        improving(bs["total_assets"])
        and
        declining(bs["borrowings"])
    ):

        pros.append({
            "rule_id": "PRO_12",
            "text": "Growing asset base funded by internal accruals reflects self-sustaining growth.",
            "confidence_pct": 85
        })

    return pros

# =====================================================
# CON RULES
# =====================================================

def generate_cons(ratio, pnl, cf, bs):

    cons = []

    latest_ratio = ratio.iloc[-1]
    latest_pnl = pnl.iloc[-1]
    latest_cf = cf.iloc[-1]
    latest_bs = bs.iloc[-1]

    # -------------------------------------------------
    # CON 1
    # High Debt
    # -------------------------------------------------

    if latest_ratio["debt_to_equity"] > 2:

        cons.append({
            "rule_id": "CON_01",
            "text": f"Debt-to-equity ratio of {latest_ratio['debt_to_equity']:.2f} is elevated for a non-financial company and warrants monitoring.",
            "confidence_pct": 95
        })

    # -------------------------------------------------
    # CON 2
    # Negative CFO
    # -------------------------------------------------

    if consecutive_negative(
        cf["operating_activity"]
    ) >= 3:

        cons.append({
            "rule_id": "CON_02",
            "text": "Free cash flow negative for 3 consecutive years raises concern about cash generation quality.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # CON 3
    # OPM Declining
    # -------------------------------------------------

    if declining(
        ratio["operating_profit_margin_pct"]
    ):

        cons.append({
            "rule_id": "CON_03",
            "text": "Operating margins declining for 3 consecutive years suggest pricing or cost pressure.",
            "confidence_pct": 85
        })

    # -------------------------------------------------
    # CON 4
    # Net Loss
    # -------------------------------------------------

    if latest_pnl["net_profit"] < 0:

        cons.append({
            "rule_id": "CON_04",
            "text": "Company reported a net loss in the most recent financial year.",
            "confidence_pct": 100
        })

    # -------------------------------------------------
    # CON 5
    # Revenue Declining
    # -------------------------------------------------

    if declining(
        pnl["sales"]
    ):

        cons.append({
            "rule_id": "CON_05",
            "text": "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss.",
            "confidence_pct": 85
        })

    # -------------------------------------------------
    # CON 6
    # Interest Coverage
    # -------------------------------------------------

    if latest_ratio["interest_coverage"] < 1.5:

        cons.append({
            "rule_id": "CON_06",
            "text": "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations.",
            "confidence_pct": 95
        })

    # -------------------------------------------------
    # CON 7
    # Dividend Payout
    # -------------------------------------------------

    if latest_ratio["dividend_payout_ratio_pct"] > 100:

        cons.append({
            "rule_id": "CON_07",
            "text": "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable.",
            "confidence_pct": 95
        })

    # -------------------------------------------------
    # CON 8
    # Rising Borrowings
    # -------------------------------------------------

    if improving(
        bs["borrowings"]
    ):

        cons.append({
            "rule_id": "CON_08",
            "text": "Rising debt over the past 3 years suggests increasing financial leverage risk.",
            "confidence_pct": 85
        })

    # -------------------------------------------------
    # CON 9
    # EPS Declining
    # -------------------------------------------------

    if declining(
        pnl["eps"]
    ):

        cons.append({
            "rule_id": "CON_09",
            "text": "Earnings per share declining for 3 consecutive years reflects deteriorating profitability.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # CON 10
    # ROCE
    # -------------------------------------------------

    if latest_ratio["return_on_capital_employed_pct"] < 10:

        cons.append({
            "rule_id": "CON_10",
            "text": "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital.",
            "confidence_pct": 85
        })

    # -------------------------------------------------
    # CON 11
    # Net Debt
    # -------------------------------------------------

    if latest_ratio["net_debt"] > (
        latest_pnl["operating_profit"] * 3
    ):

        cons.append({
            "rule_id": "CON_11",
            "text": "Net debt exceeding three times operating profit indicates elevated financial leverage.",
            "confidence_pct": 90
        })

    # -------------------------------------------------
    # CON 12
    # Weak Revenue CAGR
    # -------------------------------------------------

    if latest_ratio["revenue_cagr_5yr"] < 5:

        cons.append({
            "rule_id": "CON_12",
            "text": "Revenue growing below 5% over five years suggests limited business momentum.",
            "confidence_pct": 80
        })

    return cons

# =====================================================
# MAIN ENGINE
# =====================================================

def generate_pros_cons():

    print("=" * 60)
    print("Generating Pros & Cons...")
    print("=" * 60)

    (
        companies,
        ratios,
        profit_loss,
        cash_flow,
        balance_sheet,
    ) = load_data()

    output = []

    # --------------------------------------------------
    # Process Every Company
    # --------------------------------------------------

    for _, company in companies.iterrows():

        company_id = company["company_id"]

        ratio, pnl, cf, bs = get_company_history(
            company_id,
            ratios,
            profit_loss,
            cash_flow,
            balance_sheet,
        )

        # Skip incomplete companies
        if (
            ratio.empty
            or pnl.empty
            or cf.empty
            or bs.empty
        ):
            continue

        pros = generate_pros(
            ratio,
            pnl,
            cf,
            bs,
        )

        cons = generate_cons(
            ratio,
            pnl,
            cf,
            bs,
        )

        # ----------------------------------------------
        # Ensure at least one Pro
        # ----------------------------------------------

        if len(pros) == 0:

            pros.append({

                "rule_id": "DEFAULT_PRO",

                "text":
                "Business demonstrates stable financial performance and is suitable for continued monitoring.",

                "confidence_pct": 60
            })

        # ----------------------------------------------
        # Ensure at least one Con
        # ----------------------------------------------

        if len(cons) == 0:

            cons.append({

                "rule_id": "DEFAULT_CON",

                "text":
                "No significant financial weakness identified, however future performance should continue to be monitored.",

                "confidence_pct": 60
            })

        # ----------------------------------------------
        # Save Pros
        # ----------------------------------------------

        for p in pros:

            output.append({

                "company_id": company_id,

                "company_name": company["company_name"],

                "type": "Pro",

                "rule_id": p["rule_id"],

                "text": p["text"],

                "confidence_pct": p["confidence_pct"]

            })

        # ----------------------------------------------
        # Save Cons
        # ----------------------------------------------

        for c in cons:

            output.append({

                "company_id": company_id,

                "company_name": company["company_name"],

                "type": "Con",

                "rule_id": c["rule_id"],

                "text": c["text"],

                "confidence_pct": c["confidence_pct"]

            })

    # ==================================================
    # CREATE DATAFRAME
    # ==================================================

    result = pd.DataFrame(output)

    # ==================================================
    # VALIDATION
    # ==================================================

    summary = (

        result

        .groupby(["company_id", "type"])

        .size()

        .unstack(fill_value=0)

    )

    missing_pro = 0
    missing_con = 0

    if "Pro" in summary.columns:
        missing_pro = (summary["Pro"] == 0).sum()

    if "Con" in summary.columns:
        missing_con = (summary["Con"] == 0).sum()

    # ==================================================
    # SAVE CSV
    # ==================================================

    output_file = OUTPUT_DIR / "pros_cons_generated.csv"

    result.to_csv(
        output_file,
        index=False
    )

    # ==================================================
    # SUMMARY
    # ==================================================

    print()

    print("=" * 60)

    print("Pros & Cons Generation Complete")

    print("=" * 60)

    print(f"Companies Processed : {companies.shape[0]}")

    print(f"Pros Generated      : {(result['type']=='Pro').sum()}")

    print(f"Cons Generated      : {(result['type']=='Con').sum()}")

    print(f"Missing Pros        : {missing_pro}")

    print(f"Missing Cons        : {missing_con}")

    print()

    print(f"Output Saved : {output_file}")

    print("=" * 60)

    return result


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    generate_pros_cons()