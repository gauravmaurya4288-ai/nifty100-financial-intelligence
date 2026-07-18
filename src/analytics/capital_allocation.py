"""
Sprint 5 - Day 32

Capital Allocation Intelligence
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

# =====================================================
# PROJECT PATHS
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
# LOAD TABLES
# =====================================================

def load_data():

    conn = get_connection()

    data = {
        "companies": pd.read_sql(
            "SELECT * FROM companies",
            conn,
        ),

        "cash_flow": pd.read_sql(
            "SELECT * FROM cash_flow",
            conn,
        ),

        "financial_ratios": pd.read_sql(
            "SELECT * FROM financial_ratios",
            conn,
        ),

        "balance_sheet": pd.read_sql(
            "SELECT * FROM balance_sheet",
            conn,
        ),
    }

    conn.close()

    print("=" * 60)
    print("Capital Allocation Data Loaded")
    print("=" * 60)

    for table, df in data.items():
        print(f"{table:<20}: {len(df)} rows")

    return data

# =====================================================
# REINVESTMENT RATIO
# =====================================================

def calculate_reinvestment_ratio(operating_activity, investing_activity):
    """
    Reinvestment Ratio (%)

    Formula:
        |Investing Activity| / Operating Activity × 100
    """

    if (
        pd.isna(operating_activity)
        or pd.isna(investing_activity)
        or operating_activity == 0
    ):
        return np.nan

    ratio = abs(investing_activity) / abs(operating_activity) * 100

    return round(ratio, 2)


# =====================================================
# REINVESTMENT CATEGORY
# =====================================================

def classify_reinvestment(ratio):

    if pd.isna(ratio):
        return "Unknown"

    if ratio < 25:
        return "Low Reinvestment"

    elif ratio < 60:
        return "Balanced"

    elif ratio < 100:
        return "Growth Focused"

    return "Aggressive Expansion"


# =====================================================
# DIVIDEND POLICY
# =====================================================

def classify_dividend_policy(dividend_payout_ratio):

    if pd.isna(dividend_payout_ratio):
        return "Unknown"

    if dividend_payout_ratio == 0:
        return "No Dividend"

    elif dividend_payout_ratio < 20:
        return "Low Dividend"

    elif dividend_payout_ratio < 50:
        return "Moderate Dividend"

    return "High Dividend"


# =====================================================
# CASH UTILIZATION
# =====================================================

def analyze_cash_utilization(cfo, cfi, cff):

    if pd.isna(cfo) or pd.isna(cfi) or pd.isna(cff):
        return "Unknown"

    if cfo > 0 and cfi < 0 and cff < 0:
        return "Healthy Capital Allocation"

    elif cfo > 0 and cfi < 0 and cff > 0:
        return "Expansion Using External Funding"

    elif cfo < 0 and cff > 0:
        return "Financial Stress"

    elif cfo > 0 and cfi > 0:
        return "Asset Monetization"

    return "Mixed"


# =====================================================
# PREVIEW FUNCTIONS
# =====================================================

def preview_metrics():

    print("\n" + "=" * 60)
    print("Sample Capital Allocation Metrics")
    print("=" * 60)

    print(
        "Reinvestment Ratio:",
        calculate_reinvestment_ratio(
            1000,
            -350
        ),
    )

    print(
        "Dividend Policy:",
        classify_dividend_policy(
            35
        ),
    )

    print(
        "Cash Utilization:",
        analyze_cash_utilization(
            1000,
            -350,
            -150
        ),
    )

# =====================================================
# DEBT TREND ANALYSIS
# =====================================================

def analyze_debt_trend(borrowings):

    borrowings = pd.Series(borrowings).dropna()

    if len(borrowings) < 2:
        return "Unknown"

    latest = borrowings.iloc[-1]
    previous = borrowings.iloc[-2]

    if latest < previous:
        return "Deleveraging"

    elif latest > previous:
        return "Increasing Debt"

    return "Stable Debt"


# =====================================================
# LEVERAGE RISK
# =====================================================

def leverage_risk(debt_to_equity):

    if pd.isna(debt_to_equity):
        return "Unknown"

    if debt_to_equity < 0.5:
        return "Low"

    elif debt_to_equity < 1:
        return "Moderate"

    elif debt_to_equity < 2:
        return "High"

    return "Very High"


# =====================================================
# DEBT MANAGEMENT SCORE
# =====================================================

def debt_management_score(debt_trend, leverage):

    score = 0

    if debt_trend == "Deleveraging":
        score += 40

    elif debt_trend == "Stable Debt":
        score += 30

    elif debt_trend == "Increasing Debt":
        score += 15

    if leverage == "Low":
        score += 60

    elif leverage == "Moderate":
        score += 45

    elif leverage == "High":
        score += 25

    elif leverage == "Very High":
        score += 10

    return score


# =====================================================
# PREVIEW DEBT ANALYSIS
# =====================================================

def preview_debt_analysis():

    print("\n" + "=" * 60)
    print("Debt Management Preview")
    print("=" * 60)

    sample_borrowings = [1200, 1100, 980]

    trend = analyze_debt_trend(sample_borrowings)

    leverage = leverage_risk(0.65)

    score = debt_management_score(
        trend,
        leverage
    )

    print("Debt Trend      :", trend)
    print("Leverage Risk   :", leverage)
    print("Debt Score      :", score)

# =====================================================
# CAPITAL ALLOCATION SCORE
# =====================================================

def capital_allocation_score(
    debt_score,
    reinvestment_category,
    dividend_policy,
    cash_utilization,
):

    score = debt_score

    # -------------------------------
    # Reinvestment
    # -------------------------------

    if reinvestment_category == "Balanced":
        score += 20

    elif reinvestment_category == "Growth Focused":
        score += 18

    elif reinvestment_category == "Low Reinvestment":
        score += 10

    elif reinvestment_category == "Aggressive Expansion":
        score += 12

    # -------------------------------
    # Dividend Policy
    # -------------------------------

    if dividend_policy == "Moderate Dividend":
        score += 15

    elif dividend_policy == "High Dividend":
        score += 12

    elif dividend_policy == "Low Dividend":
        score += 8

    # -------------------------------
    # Cash Utilization
    # -------------------------------

    if cash_utilization == "Healthy Capital Allocation":
        score += 20

    elif cash_utilization == "Expansion Using External Funding":
        score += 12

    elif cash_utilization == "Asset Monetization":
        score += 10

    # Keep score between 0 and 100
    score = max(0, min(score, 100))

    return score


# =====================================================
# FINAL RATING
# =====================================================

def capital_rating(score):

    if score >= 85:
        return "Excellent"

    elif score >= 70:
        return "Good"

    elif score >= 55:
        return "Average"

    return "Weak"


# =====================================================
# PREVIEW SCORE
# =====================================================

def preview_final_score():

    print("\n" + "=" * 60)
    print("Capital Allocation Score Preview")
    print("=" * 60)

    debt = debt_management_score(
        "Deleveraging",
        "Moderate"
    )

    score = capital_allocation_score(
        debt,
        "Balanced",
        "Moderate Dividend",
        "Healthy Capital Allocation"
    )

    rating = capital_rating(score)

    print("Capital Allocation Score :", score)
    print("Final Rating             :", rating)

# =====================================================
# BUILD CAPITAL ALLOCATION REPORT
# =====================================================

def build_capital_allocation_report():

    print("\n" + "=" * 60)
    print("Generating Capital Allocation Report...")
    print("=" * 60)

    data = load_data()

    companies = data["companies"]
    cash_flow = data["cash_flow"]
    ratios = data["financial_ratios"]
    balance = data["balance_sheet"]

    # Merge tables
    df = (
        cash_flow
        .merge(
            ratios,
            on=["company_id", "year"],
            how="left"
        )
        .merge(
            balance,
            on=["company_id", "year"],
            how="left"
        )
        .merge(
            companies,
            on="company_id",
            how="left"
        )
    )

    df = df.sort_values(["company_id", "year"])

    report = []

    for company_id, company_df in df.groupby("company_id"):

        latest = company_df.iloc[-1]

        reinvestment = calculate_reinvestment_ratio(
            latest["operating_activity"],
            latest["investing_activity"]
        )

        reinvestment_category = classify_reinvestment(
            reinvestment
        )

        dividend = classify_dividend_policy(
            latest.get("dividend_payout_ratio_pct", np.nan)
        )

        cash_use = analyze_cash_utilization(
            latest["operating_activity"],
            latest["investing_activity"],
            latest["financing_activity"]
        )

        debt_trend = analyze_debt_trend(
            company_df["borrowings"]
        )

        leverage = leverage_risk(
            latest.get("debt_to_equity", np.nan)
        )

        debt_score = debt_management_score(
            debt_trend,
            leverage
        )

        score = capital_allocation_score(
            debt_score,
            reinvestment_category,
            dividend,
            cash_use
        )

        rating = capital_rating(score)

        report.append({

            "company_id": company_id,

            "company_name":
                latest.get("company_name", company_id),

            "year":
                latest["year"],

            "reinvestment_ratio":
                reinvestment,

            "reinvestment_category":
                reinvestment_category,

            "dividend_policy":
                dividend,

            "cash_utilization":
                cash_use,

            "debt_trend":
                debt_trend,

            "leverage":
                leverage,

            "capital_score":
                score,

            "rating":
                rating

        })

    report_df = pd.DataFrame(report)

    print(f"\nCompanies Processed : {len(report_df)}")

    return report_df


# =====================================================
# EXPORT REPORTS
# =====================================================

def export_reports(report_df):

    excel_file = OUTPUT_DIR / "capital_allocation_report.xlsx"
    summary_file = OUTPUT_DIR / "capital_allocation_summary.csv"
    dashboard_file = OUTPUT_DIR / "capital_allocation_dashboard.csv"

    # Full report
    report_df.to_excel(
        excel_file,
        index=False
    )

    # Summary
    summary = (
        report_df.groupby("rating")
        .agg(
            companies=("company_id", "count"),
            average_score=("capital_score", "mean")
        )
        .reset_index()
    )

    summary["average_score"] = summary["average_score"].round(2)

    summary.to_csv(
        summary_file,
        index=False
    )

    # Dashboard dataset
    dashboard_cols = [
        "company_id",
        "company_name",
        "capital_score",
        "rating",
        "reinvestment_ratio",
        "reinvestment_category",
        "dividend_policy",
        "cash_utilization",
        "debt_trend",
        "leverage",
    ]

    report_df[dashboard_cols].to_csv(
        dashboard_file,
        index=False
    )

    print("\n" + "=" * 60)
    print("Capital Allocation Report Generated")
    print("=" * 60)

    print(f"Companies Processed : {len(report_df)}")
    print(f"Average Score       : {report_df['capital_score'].mean():.2f}")

    print("\nRating Distribution:")
    print(report_df["rating"].value_counts())

    print("\nSaved Files:")
    print(excel_file)
    print(summary_file)
    print(dashboard_file)

    return summary

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    if __name__ == "__main__":

        preview_metrics()

    preview_debt_analysis()

    preview_final_score()

    report = build_capital_allocation_report()

    export_reports(report)