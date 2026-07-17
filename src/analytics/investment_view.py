import pandas as pd

from src.analytics.company_score import generate_company_scorecard
from src.analytics.recommendation import generate_recommendations

# ==========================================================
# INVESTMENT SUMMARY
# ==========================================================

def generate_investment_view(row):
    """
    Generate investment summary.
    """

    recommendation = row["recommendation"]

    if recommendation == "🟢 Buy":
        return (
            "Strong financial fundamentals with healthy "
            "profitability and attractive valuation. "
            "Suitable for long-term investors."
        )

    elif recommendation == "🟡 Hold":
        return (
            "Stable business with consistent performance. "
            "Current valuation appears reasonable. "
            "Suitable for holding existing investments."
        )

    elif recommendation == "🟠 Watch":
        return (
            "Business fundamentals require monitoring. "
            "Wait for improved financial performance "
            "or better valuation before investing."
        )

    return (
        "High investment risk due to weak financial "
        "performance or expensive valuation."
    )

# ==========================================================
# RISK SUMMARY
# ==========================================================

def generate_risk_summary(row):
    """
    Generate risk summary.
    """

    risk = row["risk_level"]

    if risk == "Low":
        return "Low investment risk with strong financial stability."

    elif risk == "Moderate":
        return "Moderate investment risk. Monitor future performance."

    elif risk == "High":
        return "High investment risk due to weaker fundamentals."

    return "Very high investment risk. Invest cautiously."


# ==========================================================
# OPPORTUNITY SUMMARY
# ==========================================================

def generate_opportunity(row):
    """
    Generate opportunity summary.
    """

    opportunities = []

    if row["flag"] == "Discount":
        opportunities.append(
            "Potential upside due to attractive valuation."
        )

    if row["revenue_cagr_5yr"] >= 15:
        opportunities.append(
            "Strong revenue growth supports future expansion."
        )

    if row["return_on_equity_pct"] >= 20:
        opportunities.append(
            "Efficient capital utilization."
        )

    if len(opportunities) == 0:
        opportunities.append(
            "No major investment opportunities identified."
        )

    return opportunities

def generate_strengths(row):

    strengths = []

    if row["return_on_equity_pct"] >= 20:
        strengths.append("High Return on Equity")

    if row["return_on_capital_employed_pct"] >= 20:
        strengths.append("Strong Capital Efficiency")

    if row["revenue_cagr_5yr"] >= 15:
        strengths.append("Healthy Revenue Growth")

    if row["net_profit_margin_pct"] >= 15:
        strengths.append("Excellent Profit Margin")

    if row["composite_quality_score"] >= 80:
        strengths.append("High Quality Business")

    if row["flag"] == "Discount":
        strengths.append("Trading Below Sector Valuation")

    if not strengths:
        strengths.append("No major financial strengths identified")

    return strengths

def generate_weaknesses(row):

    weaknesses = []

    if row["return_on_equity_pct"] < 10:
        weaknesses.append("Low Return on Equity")

    if row["return_on_capital_employed_pct"] < 10:
        weaknesses.append("Weak Capital Efficiency")

    if row["revenue_cagr_5yr"] < 5:
        weaknesses.append("Slow Revenue Growth")

    if row["net_profit_margin_pct"] < 5:
        weaknesses.append("Low Profit Margin")

    if row["composite_quality_score"] < 60:
        weaknesses.append("Weak Quality Score")

    if row["flag"] == "Caution":
        weaknesses.append("Expensive Compared to Sector")

    if not weaknesses:
        weaknesses.append("No significant weaknesses")

    return weaknesses

def generate_investment_view(row):

    recommendation = row["recommendation"]

    if recommendation == "🟢 Buy":
        return (
            "Strong financial fundamentals with healthy profitability "
            "and attractive valuation. Suitable for long-term investors."
        )

    elif recommendation == "🟡 Hold":
        return (
            "Stable business with consistent performance. "
            "Current valuation appears reasonable."
        )

    elif recommendation == "🟠 Watch":
        return (
            "Business fundamentals require monitoring before investment."
        )

    return (
        "High investment risk due to weak fundamentals."
    )


# ==========================================================
# GENERATE COMPLETE REPORT
# ==========================================================

def generate_investment_report():

    score_df = generate_company_scorecard()

    recommendation_df = generate_recommendations(score_df)

    recommendation_df["strengths"] = recommendation_df.apply(
        generate_strengths,
        axis=1
    )

    recommendation_df["weaknesses"] = recommendation_df.apply(
        generate_weaknesses,
        axis=1
    )

    recommendation_df["investment_view"] = recommendation_df.apply(
        generate_investment_view,
        axis=1
    )

    recommendation_df["risk_summary"] = recommendation_df.apply(
        generate_risk_summary,
        axis=1
    )

    recommendation_df["opportunities"] = recommendation_df.apply(
        generate_opportunity,
        axis=1
    )

    return recommendation_df

# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    report = generate_investment_report()

    company = report.iloc[0]

    print("\n" + "=" * 70)
    print(company["company_name"])
    print("=" * 70)

    print("\nOverall Score :", company["overall_score"])
    print("Grade         :", company["grade"])
    print("Recommendation:", company["recommendation"])
    print("Risk Level    :", company["risk_level"])

    print("\nStrengths")
    for item in company["strengths"]:
        print("✔", item)

    print("\nWeaknesses")
    for item in company["weaknesses"]:
        print("⚠", item)

    print("\nOpportunities")
    for item in company["opportunities"]:
        print("➜", item)

    print("\nInvestment View")
    print(company["investment_view"])

    print("\nRisk Summary")
    print(company["risk_summary"])