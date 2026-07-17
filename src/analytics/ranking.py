"""
==========================================================
DAY 28 - RANKING ENGINE
==========================================================

Provides reusable ranking functions for the dashboard.

Author: Gaurav Maurya
"""

import pandas as pd

from src.analytics.investment_view import generate_investment_report


# ==========================================================
# LOAD REPORT
# ==========================================================

def load_report():
    """
    Load the complete investment report.
    """
    return generate_investment_report()


# ==========================================================
# TOP COMPANIES
# ==========================================================

def top_companies(n=10):

    df = load_report()

    return (
        df.sort_values("overall_score", ascending=False)
          .head(n)
          .reset_index(drop=True)
    )


# ==========================================================
# VALUE PICKS
# ==========================================================

def value_picks(n=10):

    df = load_report()

    value = df[df["flag"] == "Discount"]

    return (
        value.sort_values("overall_score", ascending=False)
             .head(n)
             .reset_index(drop=True)
    )


# ==========================================================
# GROWTH COMPANIES
# ==========================================================

def growth_companies(n=10):

    df = load_report()

    return (
        df.sort_values(
            "revenue_cagr_5yr",
            ascending=False
        )
        .head(n)
        .reset_index(drop=True)
    )


# ==========================================================
# QUALITY COMPANIES
# ==========================================================

def quality_companies(n=10):

    df = load_report()

    return (
        df.sort_values(
            "composite_quality_score",
            ascending=False
        )
        .head(n)
        .reset_index(drop=True)
    )


# ==========================================================
# HIGH ROE
# ==========================================================

def top_roe_companies(n=10):

    df = load_report()

    return (
        df.sort_values(
            "return_on_equity_pct",
            ascending=False
        )
        .head(n)
        .reset_index(drop=True)
    )


# ==========================================================
# SECTOR RANKINGS
# ==========================================================

def sector_rankings():

    df = load_report()

    sector = (
        df.groupby("broad_sector")
          .agg(
              companies=("company_name", "count"),
              avg_score=("overall_score", "mean"),
              avg_roe=("return_on_equity_pct", "mean"),
              avg_growth=("revenue_cagr_5yr", "mean"),
          )
          .round(2)
          .sort_values("avg_score", ascending=False)
          .reset_index()
    )

    return sector


# ==========================================================
# GRADE DISTRIBUTION
# ==========================================================

def grade_distribution():

    df = load_report()

    grades = (
        df["grade"]
        .value_counts()
        .rename_axis("grade")
        .reset_index(name="companies")
    )

    return grades


# ==========================================================
# RECOMMENDATION DISTRIBUTION
# ==========================================================

def recommendation_distribution():

    df = load_report()

    rec = (
        df["recommendation"]
        .value_counts()
        .rename_axis("recommendation")
        .reset_index(name="companies")
    )

    return rec


# ==========================================================
# EXPORT RANKINGS
# ==========================================================

def export_rankings():

    top_companies(100).to_csv(
        "reports/top_companies.csv",
        index=False,
    )

    value_picks(100).to_csv(
        "reports/value_picks.csv",
        index=False,
    )

    growth_companies(100).to_csv(
        "reports/growth_companies.csv",
        index=False,
    )

    quality_companies(100).to_csv(
        "reports/quality_companies.csv",
        index=False,
    )

    sector_rankings().to_csv(
        "reports/sector_rankings.csv",
        index=False,
    )

    grade_distribution().to_csv(
        "reports/grade_distribution.csv",
        index=False,
    )

    recommendation_distribution().to_csv(
        "reports/recommendation_distribution.csv",
        index=False,
    )

    print("\nRanking reports exported successfully.")


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("\nTOP 10 COMPANIES")
    print(
        top_companies()[
            [
                "company_name",
                "overall_score",
                "grade",
                "recommendation",
            ]
        ]
    )

    print("\nTOP VALUE PICKS")
    print(
        value_picks()[
            [
                "company_name",
                "overall_score",
                "flag",
            ]
        ]
    )

    print("\nSECTOR RANKINGS")
    print(sector_rankings())

    print("\nGRADE DISTRIBUTION")
    print(grade_distribution())

    export_rankings()