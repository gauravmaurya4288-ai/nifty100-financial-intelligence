import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.analytics.investment_view import generate_investment_report

from components.header import render_header
from components.footer import render_footer


from components.styles import load_css

load_css()

def render():
    """Portfolio Simulator"""

    st.title("💼 Portfolio Simulator")
    st.caption(
        "Build a virtual investment portfolio and analyse its quality, diversification and risk."
    )

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    try:
        report = generate_investment_report()

    except Exception as e:
        st.error(f"Unable to load portfolio data.\n\n{e}")
        return

    # ==========================================================
    # SIDEBAR
    # ==========================================================

    st.sidebar.subheader("Portfolio Settings")

    companies = sorted(
        report["company_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        companies,
    )

    investment = st.sidebar.number_input(
        "Investment Amount (₹)",
        min_value=10000,
        value=500000,
        step=10000,
    )

    if len(selected_companies) == 0:
        st.info("👈 Select one or more companies from the sidebar.")
        return

    portfolio = report[
        report["company_name"].isin(selected_companies)
    ].copy()

    # ==========================================================
    # KPI CARDS
    # ==========================================================

    portfolio_score = portfolio["overall_score"].mean()

    average_roe = portfolio["return_on_equity_pct"].mean()

    average_growth = portfolio["revenue_cagr_5yr"].mean()

    risk = portfolio["risk_level"].mode().iloc[0]

    buy_percentage = (
        portfolio["recommendation"]
        .eq("🟢 Buy")
        .mean()
        * 100
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Portfolio Score",
        f"{portfolio_score:.1f}",
    )

    c2.metric(
        "Average ROE",
        f"{average_roe:.1f}%",
    )

    c3.metric(
        "Average Growth",
        f"{average_growth:.1f}%",
    )

    c4.metric(
        "Buy %",
        f"{buy_percentage:.0f}%",
    )

    st.success(f"Overall Risk Level : {risk}")

    st.divider()

    # ==========================================================
    # COMPANY TABLE
    # ==========================================================

    st.subheader("Selected Companies")

    st.dataframe(
        portfolio[
            [
                "company_name",
                "overall_score",
                "grade",
                "recommendation",
                "flag",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ==========================================================
    # CHARTS
    # ==========================================================

    left, right = st.columns(2)

    with left:

        sector_chart = (
            portfolio.groupby("broad_sector")
            .size()
            .reset_index(name="Companies")
        )

        fig = px.pie(
            sector_chart,
            names="broad_sector",
            values="Companies",
            hole=0.55,
            title="Sector Allocation",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:

        recommendation_chart = (
            portfolio.groupby("recommendation")
            .size()
            .reset_index(name="Companies")
        )

        fig = px.pie(
            recommendation_chart,
            names="recommendation",
            values="Companies",
            hole=0.55,
            title="Recommendation Mix",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.divider()

    # ==========================================================
    # PORTFOLIO SCORE CHART
    # ==========================================================

    fig = px.bar(
        portfolio.sort_values(
            "overall_score",
            ascending=False,
        ),
        x="company_name",
        y="overall_score",
        color="grade",
        title="Portfolio Score Comparison",
        text="overall_score",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ==========================================================
    # INVESTMENT SUMMARY
    # ==========================================================

    st.subheader("Portfolio Summary")

    if portfolio_score >= 80:

        st.success(
            "Excellent portfolio with strong fundamentals and long-term investment potential."
        )

    elif portfolio_score >= 65:

        st.info(
            "Balanced portfolio with moderate risk and stable growth."
        )

    elif portfolio_score >= 50:

        st.warning(
            "Portfolio quality is average. Consider improving diversification."
        )

    else:

        st.error(
            "High-risk portfolio. Review stock selection before investing."
        )

    st.divider()

    allocation = investment / len(portfolio)

    summary = portfolio.copy()

    summary["Investment (₹)"] = allocation

    st.subheader("Investment Allocation")

    st.dataframe(
        summary[
            [
                "company_name",
                "Investment (₹)",
                "overall_score",
                "grade",
                "recommendation",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

render_footer()