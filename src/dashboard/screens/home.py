import streamlit as st
import pandas as pd
import plotly.express as px
from components.header import render_header
from components.styles import load_css
from components.footer import render_footer


load_css()

from utils.db import (
    get_companies,
    get_ratios,
    get_sectors,
)


# ==========================================================
# Helper
# ==========================================================

def safe_metric(value, suffix=""):

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}{suffix}"


# ==========================================================
# Render
# ==========================================================

def render():

    render_header(
    "Nifty100 Financial Intelligence",
    "Professional analytics platform for Indian equity research"
    )

    with st.spinner("Loading dashboard..."):

        companies = get_companies()
        ratios = get_ratios()
        sectors = get_sectors()

    if ratios.empty:

        st.error("No financial data available.")

        return

    # ======================================================
    # Year Filter
    # ======================================================

    years = sorted(

        ratios["year"].astype(str).unique(),

        reverse=True

    )

    year = st.sidebar.selectbox(

        "Financial Year",

        years,

        key="home_year"

    )

    latest = ratios[
        ratios["year"].astype(str).str.contains(year)
    ].copy()

    st.caption(f"Showing Dashboard for {year}")

    if latest.empty:

        st.warning("No records found.")

        return

    # ======================================================
    # KPIs
    # ======================================================

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Companies",
        latest["company_id"].nunique()
    )

    c2.metric(
        "Average ROE",
        safe_metric(
            latest["return_on_equity_pct"].mean(),
            "%"
        )
    )

    c3.metric(
        "Median P/E",
        safe_metric(
            latest["pe_ratio"].median()
        )
    )

    c4.metric(
        "Median D/E",
        safe_metric(
            latest["debt_to_equity"].median()
        )
    )

    c5.metric(
        "Revenue CAGR",
        safe_metric(
            latest["revenue_cagr_5yr"].median(),
            "%"
        )
    )

    debt_free = latest[
        latest["debt_to_equity"] <= 0.5
    ]["company_id"].nunique()

    c6.metric(
        "Debt Free",
        debt_free
    )

    st.divider()

    # ======================================================
    # Sector Distribution
    # ======================================================

    st.subheader("🏢 Sector Distribution")

    sector_df = sectors.copy()

    if "broad_sector" not in sector_df.columns:

        st.warning("Sector information unavailable.")

    else:

        sector_summary = (

            sector_df

            .groupby("broad_sector")

            .size()

            .reset_index(name="Companies")

            .sort_values(

                "Companies",

                ascending=False

            )

        )

        fig = px.pie(

            sector_summary,

            names="broad_sector",

            values="Companies",

            hole=0.55,

            title="Companies by Broad Sector"

        )

        fig.update_traces(

            textposition="inside",

            textinfo="percent+label"

        )

        fig.update_layout(

            height=520,

            margin=dict(

                l=20,

                r=20,

                t=50,

                b=20

            )

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    st.divider()

    # ======================================================
    # Top Companies
    # ======================================================

    st.subheader("🏆 Top 5 Companies by Composite Quality Score")

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

                "debt_to_equity",

            ]

        ],

        use_container_width=True,

        hide_index=True,

    )

    st.divider()

    # ======================================================
    # Sector Summary
    # ======================================================

    st.subheader("📊 Sector Summary")

    if not sectors.empty:

        summary = (

            sectors

            .groupby("broad_sector")

            .size()

            .reset_index(name="Companies")

            .sort_values(

                "Companies",

                ascending=False

            )

        )

        st.dataframe(

            summary,

            use_container_width=True,

            hide_index=True,

        )

    else:

        st.info("Sector data unavailable.")


render_footer()