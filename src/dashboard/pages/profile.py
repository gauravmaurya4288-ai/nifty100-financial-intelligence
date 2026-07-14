import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_ratios,
    get_pl,
)


def render():

    st.title("🏢 Company Profile")

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    companies = get_companies()
    ratios = get_ratios()

    # ==========================================================
    # COMPANY SELECTOR
    # ==========================================================

    company_list = sorted(companies["company_id"].dropna().unique())

    ticker = st.selectbox(
        "Select Company",
        company_list,
        key="profile_company"
    )

    # ==========================================================
    # COMPANY MASTER
    # ==========================================================

    company = companies[
        companies["company_id"] == ticker
    ]

    if company.empty:
        st.warning("Ticker not found.")
        return

    company = company.iloc[0]

    st.divider()

    st.subheader("🏢 About Company")

    about = company.get("about_company")

    if pd.notna(about):

        st.write(about)

    else:

        st.info("Company description not available.")

    # ==========================================================
    # FINANCIAL RATIOS
    # ==========================================================

    history = (
        ratios[
            ratios["company_id"] == ticker
        ]
        .copy()
    )

    if history.empty:
        st.warning("Financial ratios not available.")
        return

    history = history.sort_values("year")

    latest = history.iloc[-1]

    # ==========================================================
    # PROFILE CARD
    # ==========================================================

    st.divider()

    c1, c2 = st.columns([1, 3])

    with c1:

        logo = company.get("company_logo")

        if pd.notna(logo):
            st.image(logo, width=120)

    with c2:

        st.subheader(company.get("company_name", ticker))

        st.write(f"**Ticker:** {ticker}")

        st.write(f"**Face Value:** {company.get('face_value', 'N/A')}")

        st.write(f"**Book Value:** {company.get('book_value', 'N/A')}")

    st.divider()

    # ==========================================================
    # KPI CARDS
    # ==========================================================

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    k1.metric(
        "ROE",
        f"{latest['return_on_equity_pct']:.2f}%"
        if pd.notna(latest["return_on_equity_pct"])
        else "N/A"
    )

    k2.metric(
        "ROCE",
        f"{latest['return_on_capital_employed_pct']:.2f}%"
        if pd.notna(latest["return_on_capital_employed_pct"])
        else "N/A"
    )

    k3.metric(
        "Net Margin",
        f"{latest['net_profit_margin_pct']:.2f}%"
        if pd.notna(latest["net_profit_margin_pct"])
        else "N/A"
    )

    k4.metric(
        "Debt/Equity",
        f"{latest['debt_to_equity']:.2f}"
        if pd.notna(latest["debt_to_equity"])
        else "N/A"
    )

    k5.metric(
        "Revenue CAGR",
        f"{latest['revenue_cagr_5yr']:.2f}%"
        if pd.notna(latest["revenue_cagr_5yr"])
        else "N/A"
    )

    k6.metric(
        "Free Cash Flow",
        f"{latest['free_cash_flow_cr']:.0f} Cr"
        if pd.notna(latest["free_cash_flow_cr"])
        else "N/A"
    )

    st.divider()

    # ==========================================================
    # PROFIT & LOSS DATA
    # ==========================================================

    pl = get_pl(ticker)

    if not pl.empty:

        pl = pl.copy()

        pl["year"] = pl["year"].astype(str)

        # Revenue Chart

        if "sales" in pl.columns:

            fig1 = px.bar(
                pl,
                x="year",
                y="sales",
                title="Revenue (10 Years)",
                text="sales"
            )

            fig1.update_layout(height=450)

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        # Net Profit Chart

        if "net_profit" in pl.columns:

            fig2 = px.bar(
                pl,
                x="year",
                y="net_profit",
                title="Net Profit (10 Years)",
                text="net_profit"
            )

            fig2.update_layout(height=450)

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    # ==========================================================
    # ROE VS ROCE
    # ==========================================================

    history = history.copy()
    history["year"] = history["year"].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=history["year"],
            y=history["return_on_equity_pct"],
            mode="lines+markers",
            name="ROE"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=history["year"],
            y=history["return_on_capital_employed_pct"],
            mode="lines+markers",
            name="ROCE"
        )
    )

    fig.update_layout(
        title="ROE vs ROCE Trend",
        height=500,
        xaxis_title="Year",
        yaxis_title="Percentage"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.success("Company Profile Loaded Successfully")
    """
    st.divider()

    st.subheader("✅ Pros & Cons")

    pros_cons = get_pros_cons(ticker)

    if pros_cons.empty:

        st.info("Pros & Cons unavailable.")

    else:

        left, right = st.columns(2)

        with left:

            st.success("Pros")

            for item in pros_cons["pros"].dropna():

                st.markdown(f"✅ {item}")

        with right:

            st.error("Cons")

            for item in pros_cons["cons"].dropna():

                st.markdown(f"❌ {item}")
    """
    # INVESTMENT SUMMARY

    st.divider()

    st.subheader("Investment Summary")

    score = latest["composite_quality_score"]

    if score >= 80:

        st.success("★★★★★ Excellent Company")

    elif score >= 70:

        st.success("★★★★ Strong Company")

    elif score >= 60:

        st.info("★★★ Good Company")

    elif score >= 50:

        st.warning("★★ Average Company")

    else:

        st.error("★ Weak Company")
 

    # FInancial Summary

    st.subheader("Financial Health")

    col1,col2,col3=st.columns(3)

    col1.metric(
        "Interest Coverage",
        round(latest["interest_coverage"],2)
    )

    col2.metric(
        "Asset Turnover",
        round(latest["asset_turnover"],2)
    )

    col3.metric(
        "FCF Conversion",
        round(latest["fcf_conversion_pct"],2)
    )

    # Download Button

    csv = history.to_csv(index=False)

    st.download_button(

        "Download Financial History",

        csv,

        file_name=f"{ticker}_financial_history.csv",

        mime="text/csv"
    )

