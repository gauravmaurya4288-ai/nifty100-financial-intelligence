"""
recommendation.py
-----------------
Generates investment recommendations based on
the company score calculated in company_score.py.
"""

import pandas as pd


# ==========================================================
# Recommendation Logic
# ==========================================================

def get_recommendation(score):
    """
    Generate recommendation based on overall score.
    """

    if pd.isna(score):
        return "Unknown"

    if score >= 85:
        return "🟢 Buy"

    elif score >= 70:
        return "🟡 Hold"

    elif score >= 50:
        return "🟠 Watch"

    else:
        return "🔴 High Risk"
    

# ==========================================================
# Risk Level
# ==========================================================

def get_risk_level(score):
    """
    Calculate investment risk.
    """

    if pd.isna(score):
        return "Unknown"

    if score >= 85:
        return "Low"

    elif score >= 70:
        return "Moderate"

    elif score >= 50:
        return "High"

    else:
        return "Very High"
    

    # ==========================================================
# Recommendation Engine
# ==========================================================

def generate_recommendations(score_df):
    """
    Add recommendation and risk columns to score DataFrame.

    Parameters
    ----------
    score_df : DataFrame

    Returns
    -------
    DataFrame
    """

    df = score_df.copy()

    df["recommendation"] = (
        df["overall_score"]
        .apply(get_recommendation)
    )

    df["risk_level"] = (
        df["overall_score"]
        .apply(get_risk_level)
    )

    return df


if __name__ == "__main__":

    from src.analytics.company_score import (
        generate_company_scorecard
    )

    scores = generate_company_scorecard()

    recommendations = generate_recommendations(scores)

    print("\nTop 10 Recommendations\n")

    print(
        recommendations[
            [
                "rank",
                "company_name",
                "overall_score",
                "grade",
                "recommendation",
                "risk_level"
            ]
        ].head(10)
    )