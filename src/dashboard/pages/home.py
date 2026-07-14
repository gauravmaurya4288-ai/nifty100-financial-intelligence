import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)

def render():

    st.title("🏠 Nifty100 Dashboard")

    st.markdown(
        "### Financial Intelligence Overview"
    )

    # ============================================
    # LOAD DATA
    # ============================================

    companies = get_companies()

    ratios = get_ratios()

    sectors = get_sectors()

    # ============================================
    # YEAR FILTER
    # ============================================

    years = [

        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
        "2024"

    ]

    year = st.sidebar.selectbox(
    "Financial Year",
    years,
    index=len(years) - 1,
    key="home_year_selector"
    )

    # ============================================
    # FILTER
    # ============================================

    latest = ratios[
        ratios["year"].astype(str).str.contains(year)
    ].copy()

    st.caption(

        f"Showing Dashboard for {year}"

    )

    # ============================================
    # KPIs
    # ============================================

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(

        "Companies",

        latest["company_id"].nunique()

    )

    c2.metric(

        "Average ROE",

        f"{latest['return_on_equity_pct'].mean():.2f}%"

    )

    c3.metric(

        "Median P/E",

        f"{latest['pe_ratio'].median():.2f}"

    )

    c4.metric(

        "Median D/E",

        f"{latest['debt_to_equity'].median():.2f}"

    )

    c5.metric(

        "Revenue CAGR",

        f"{latest['revenue_cagr_5yr'].median():.2f}%"

    )

    debt_free = (

        latest["debt_to_equity"] < 0.5

    ).sum()

    c6.metric(

        "Debt Free",

        debt_free

    )

    st.divider()

    # ==========================================================
    # SECTOR ANALYSIS
    # ==========================================================

    st.subheader("🏢 Sector Distribution")

    # Merge latest financial data with sector master
    sector_data = latest.merge(
        sectors[["company_id", "broad_sector"]],
        on="company_id",
        how="left"
    )

    # Replace missing sectors
    sector_data["broad_sector"] = (
        sector_data["broad_sector"]
        .fillna("Unknown")
    )

    # Create summary
    sector_summary = (
        sector_data.groupby("broad_sector", dropna=False)
        .agg(Companies=("company_id", "nunique"))
        .reset_index()
        .sort_values("Companies", ascending=False)
    )

    # Debug (remove later)
    with st.expander("Debug"):
        st.write("Latest Shape:", latest.shape)
        st.write("Sector Shape:", sectors.shape)
        st.write("Merged Shape:", sector_data.shape)
        st.dataframe(sector_summary)

    # Draw chart only if data exists
    if len(sector_summary) > 0:

        fig = px.pie(
            sector_summary,
            names="broad_sector",
            values="Companies",
            hole=0.45,
            title="Companies by Broad Sector",
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")

        fig.update_layout(
            height=550,
            showlegend=True,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No sector data available.")

    

    # ============================================
    # TOP COMPANIES
    # ============================================

    st.subheader("Top 5 Companies by Composite Quality Score")

    top = (
        latest
        .sort_values(
            "composite_quality_score",
            ascending=False
        )
        .head(5)
    )

    st.dataframe(
        top[
            [
                "company_id",
                "composite_quality_score",
                "return_on_equity_pct",
                "pe_ratio",
                "debt_to_equity"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Sector Summary")

    st.dataframe(
        sector_summary,
        use_container_width=True,
        hide_index=True
    )