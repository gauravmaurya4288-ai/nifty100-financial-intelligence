import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_ratios,
    get_pl,
)


from components.header import render_header
from components.styles import load_css

load_css()
# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def safe_value(value, suffix="", decimals=2):
    """Safely format numeric values."""
    if pd.isna(value):
        return "N/A"

    if isinstance(value, (int, float)):
        return f"{round(value, decimals)}{suffix}"

    return str(value)


# ==========================================================
# PAGE
# ==========================================================

def render():

    load_css()

    start_time = time.time()

    st.title("🏢 Company Profile")

    st.caption("Detailed financial profile of every Nifty100 company")

    # ======================================================
    # LOAD DATA
    # ======================================================

    with st.spinner("Loading company data..."):

        companies = get_companies()
        ratios = get_ratios()

    if companies.empty:

        st.error("Company master not found.")
        return

    if ratios.empty:

        st.error("Financial ratios unavailable.")
        return

    # ======================================================
    # SEARCH BOX
    # ======================================================

    search_options = sorted(
        companies["company_id"].dropna().unique()
    )

    ticker = st.selectbox(
        "Select Company",
        search_options,
        key="profile_company"
    )

    # ======================================================
    # COMPANY DATA
    # ======================================================

    company = companies[
        companies["company_id"] == ticker
    ]

    if company.empty:

        st.warning("Ticker not found.")

        return

    company = company.iloc[0]

    history = ratios[
        ratios["company_id"] == ticker
    ].copy()

    if history.empty:

        st.warning("Financial data unavailable.")

        return

    history = history.sort_values("year")

    latest = history.iloc[-1]

    # ======================================================
    # PROFILE HEADER
    # ======================================================

    st.divider()

    left, right = st.columns([1, 4])

    with left:

        logo = company.get("company_logo")

        if pd.notna(logo):

            st.image(
                logo,
                width=130
            )

    with right:

        st.subheader(
            company.get(
                "company_name",
                ticker
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**Ticker:** {ticker}")

            st.write(
                f"**Face Value:** {safe_value(company.get('face_value'))}"
            )

            st.write(
                f"**Book Value:** {safe_value(company.get('book_value'))}"
            )

        with col2:

            st.write(
                f"**ROE:** {safe_value(company.get('roe_percentage'), '%')}"
            )

            st.write(
                f"**ROCE:** {safe_value(company.get('roce_percentage'), '%')}"
            )

    st.divider()

    # ======================================================
    # ABOUT COMPANY
    # ======================================================

    st.subheader("About Company")

    about = company.get("about_company")

    if pd.notna(about):

        st.write(about)

    else:

        st.info("Company description not available.")

    st.divider()

    # ======================================================
    # KPI CARDS
    # ======================================================

    st.subheader("Latest Financial Snapshot")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "ROE",
        safe_value(
            latest["return_on_equity_pct"],
            "%"
        )
    )

    c2.metric(
        "ROCE",
        safe_value(
            latest["return_on_capital_employed_pct"],
            "%"
        )
    )

    c3.metric(
        "Net Margin",
        safe_value(
            latest["net_profit_margin_pct"],
            "%"
        )
    )

    c4.metric(
        "Debt / Equity",
        safe_value(
            latest["debt_to_equity"]
        )
    )

    c5.metric(
        "Revenue CAGR",
        safe_value(
            latest["revenue_cagr_5yr"],
            "%"
        )
    )

    c6.metric(
        "Free Cash Flow",
        safe_value(
            latest["free_cash_flow_cr"],
            " Cr",
            0
        )
    )

    st.divider()
    # ==========================================================
# 10 YEAR REVENUE & NET PROFIT
# ==========================================================

    st.subheader("📈 Revenue & Net Profit Trend (10 Years)")

    pl = get_pl(ticker)

    if not pl.empty:

        pl = pl.copy()

        pl["year"] = pl["year"].astype(str)

        numeric_cols = ["sales", "net_profit"]

        for col in numeric_cols:

            if col in pl.columns:

                pl[col] = pd.to_numeric(
                    pl[col],
                    errors="coerce"
                )

        fig = go.Figure()

        if "sales" in pl.columns:

            fig.add_trace(

                go.Bar(

                    x=pl["year"],

                    y=pl["sales"],

                    name="Revenue",

                    opacity=0.8

                )

            )

        if "net_profit" in pl.columns:

            fig.add_trace(

                go.Scatter(

                    x=pl["year"],

                    y=pl["net_profit"],

                    mode="lines+markers",

                    name="Net Profit",

                    yaxis="y2"

                )

            )

        fig.update_layout(

            title="Revenue vs Net Profit",

            height=520,

            hovermode="x unified",

            margin=dict(

                l=20,

                r=20,

                t=60,

                b=20

            ),

            yaxis=dict(

                title="Revenue"

            ),

            yaxis2=dict(

                title="Net Profit",

                overlaying="y",

                side="right"

            )

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    else:

        st.info("Profit & Loss history unavailable.")

    st.divider()

    # ==========================================================
    # ROE vs ROCE
    # ==========================================================

    st.subheader("📊 ROE vs ROCE Performance")

    history = history.copy()

    history["year"] = history["year"].astype(str)

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=history["year"],

            y=history["return_on_equity_pct"],

            mode="lines+markers",

            name="ROE",

            line=dict(width=3)

        )

    )

    fig.add_trace(

        go.Scatter(

            x=history["year"],

            y=history["return_on_capital_employed_pct"],

            mode="lines+markers",

            name="ROCE",

            yaxis="y2",

            line=dict(width=3)

        )

    )

    fig.update_layout(

        title="ROE vs ROCE",

        height=520,

        hovermode="x unified",

        margin=dict(

            l=20,

            r=20,

            t=60,

            b=20

        ),

        yaxis=dict(

            title="ROE (%)"

        ),

        yaxis2=dict(

            title="ROCE (%)",

            overlaying="y",

            side="right"

        )

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    # ==========================================================
    # FINANCIAL HEALTH
    # ==========================================================

    st.subheader("💹 Financial Health")

    h1, h2, h3 = st.columns(3)

    h1.metric(

        "Interest Coverage",

        safe_value(

            latest["interest_coverage"]

        )

    )

    h2.metric(

        "Asset Turnover",

        safe_value(

            latest["asset_turnover"]

        )

    )

    h3.metric(

        "FCF Conversion",

        safe_value(

            latest["fcf_conversion_pct"],

            "%"

        )

    )

    st.divider()

    # ==========================================================
    # INVESTMENT SUMMARY
    # ==========================================================

    st.subheader("⭐ Investment Summary")

    score = latest.get("composite_quality_score", None)

    if pd.isna(score):

        recommendation = "Insufficient Data"
        risk = "Unknown"

    elif score >= 80:

        recommendation = "Strong Buy"
        risk = "Low"

    elif score >= 60:

        recommendation = "Buy"
        risk = "Moderate"

    elif score >= 40:

        recommendation = "Hold"
        risk = "Moderate"

    elif score >= 20:

        recommendation = "Avoid"
        risk = "High"

    else:

        recommendation = "High Risk"
        risk = "Very High"

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Quality Score",
        safe_value(score)
    )

    c2.metric(
        "Recommendation",
        recommendation
    )

    c3.metric(
        "Risk Level",
        risk
    )

    st.divider()

    # ==========================================================
    # VALUATION SNAPSHOT
    # ==========================================================

    st.subheader("💰 Valuation Snapshot")

    v1, v2, v3, v4 = st.columns(4)

    v1.metric(
        "P/E Ratio",
        safe_value(latest.get("pe_ratio"))
    )

    v2.metric(
        "P/B Ratio",
        safe_value(latest.get("pb_ratio"))
    )

    v3.metric(
        "EV / EBITDA",
        safe_value(latest.get("ev_ebitda"))
    )

    v4.metric(
        "Dividend Yield",
        safe_value(
            latest.get("dividend_yield_pct"),
            "%"
        )
    )

    st.divider()

    # ==========================================================
    # GROWTH METRICS
    # ==========================================================

    st.subheader("📈 Growth Metrics")

    g1, g2, g3 = st.columns(3)

    g1.metric(
        "Revenue CAGR (5Y)",
        safe_value(
            latest.get("revenue_cagr_5yr"),
            "%"
        )
    )

    g2.metric(
        "PAT CAGR (5Y)",
        safe_value(
            latest.get("pat_cagr_5yr"),
            "%"
        )
    )

    g3.metric(
        "EPS CAGR (5Y)",
        safe_value(
            latest.get("eps_cagr_5yr"),
            "%"
        )
    )

    st.divider()

    # ==========================================================
    # FINANCIAL DATA TABLE
    # ==========================================================

    st.subheader("📋 Financial History")

    display_cols = [
        "year",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "pe_ratio",
        "pb_ratio",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
    ]

    available_cols = [
        col for col in display_cols
        if col in history.columns
    ]

    st.dataframe(
        history[available_cols],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ==========================================================
    # DOWNLOAD CSV
    # ==========================================================

    csv = history.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Financial History",
        data=csv,
        file_name=f"{ticker}_financial_history.csv",
        mime="text/csv",
    )

    st.divider()

    # ==========================================================
    # PROFILE STATISTICS
    # ==========================================================

    st.subheader("📊 Dataset Summary")

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Years Available",
        len(history)
    )

    s2.metric(
        "Latest Year",
        history.iloc[-1]["year"]
    )

    s3.metric(
        "First Year",
        history.iloc[0]["year"]
    )

    st.divider()

    # ==========================================================
    # LOAD TIME
    # ==========================================================

    elapsed = time.time() - start_time

    st.caption(
        f"⚡ Profile loaded in {elapsed:.2f} seconds"
    )

    # ==========================================================
    # PROS & CONS
    # ==========================================================

    st.divider()

    st.subheader("✅ Pros & ⚠️ Cons")

    pros = []
    cons = []

    # ---------- Pros ----------

    roe = latest.get("return_on_equity_pct")
    if pd.notna(roe) and roe >= 20:
        pros.append(f"Strong Return on Equity ({roe:.2f}%)")

    roce = latest.get("return_on_capital_employed_pct")
    if pd.notna(roce) and roce >= 20:
        pros.append(f"Healthy ROCE ({roce:.2f}%)")

    de = latest.get("debt_to_equity")
    if pd.notna(de) and de <= 0.5:
        pros.append("Low Debt Company")

    rev = latest.get("revenue_cagr_5yr")
    if pd.notna(rev) and rev >= 15:
        pros.append(f"Good Revenue Growth ({rev:.2f}%)")

    pat = latest.get("pat_cagr_5yr")
    if pd.notna(pat) and pat >= 15:
        pros.append(f"Strong Profit Growth ({pat:.2f}%)")

    div = latest.get("dividend_yield_pct")
    if pd.notna(div) and div >= 2:
        pros.append(f"Healthy Dividend Yield ({div:.2f}%)")

    # ---------- Cons ----------

    if pd.notna(de) and de > 1.5:
        cons.append(f"High Debt ({de:.2f})")

    pe = latest.get("pe_ratio")
    if pd.notna(pe) and pe > 60:
        cons.append(f"Expensive Valuation (P/E {pe:.2f})")

    margin = latest.get("net_profit_margin_pct")
    if pd.notna(margin) and margin < 5:
        cons.append(f"Low Profit Margin ({margin:.2f}%)")

    fcf = latest.get("free_cash_flow_cr")
    if pd.notna(fcf) and fcf < 0:
        cons.append("Negative Free Cash Flow")

    interest = latest.get("interest_coverage")
    if pd.notna(interest) and interest < 2:
        cons.append("Weak Interest Coverage")

    if len(pros) == 0:
        pros.append("No major positive indicators identified.")

    if len(cons) == 0:
        cons.append("No major financial concerns identified.")

    left, right = st.columns(2)

    with left:

        st.success("Strengths")

        for item in pros:
            st.markdown(f"✅ {item}")

    with right:

        st.error("Weaknesses")

        for item in cons:
            st.markdown(f"⚠️ {item}")

    # ==========================================================
    # COMPANY SNAPSHOT
    # ==========================================================

    st.divider()

    st.subheader("📌 Company Snapshot")

    snapshot = pd.DataFrame({

        "Metric":[
            "Company",
            "Ticker",
            "Sector",
            "Latest Year",
            "ROE",
            "ROCE",
            "P/E",
            "Debt/Equity",
            "Quality Score"
        ],

        "Value":[
            company.get("company_name","N/A"),
            ticker,
            company.get("broad_sector","N/A"),
            latest.get("year","N/A"),
            safe_value(latest.get("return_on_equity_pct"),"%"),
            safe_value(latest.get("return_on_capital_employed_pct"),"%"),
            safe_value(latest.get("pe_ratio")),
            safe_value(latest.get("debt_to_equity")),
            safe_value(score)
        ]

    })

    st.dataframe(
        snapshot,
        use_container_width=True,
        hide_index=True
    )

    # ==========================================================
    # PAGE FOOTER
    # ==========================================================

    st.divider()

    st.caption(
        "📈 Nifty100 Financial Intelligence Dashboard • Company Profile Module"
    )

