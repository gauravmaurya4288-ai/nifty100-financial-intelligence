import streamlit as st
import pandas as pd

from utils.db import get_screener_data


def render():

    st.title("🔍 Stock Screener")

    # =====================================================
    # LOAD DATA
    # =====================================================

    df = get_screener_data()

    if df.empty:
        st.warning("No screener data available.")
        return

    # Replace missing numeric values
    numeric_cols = [
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "interest_coverage",
        "composite_quality_score",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # =====================================================
    # QUICK SCREENERS
    # =====================================================

    st.subheader("📌 Quick Screeners")

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    quality = c1.button("⭐ Quality")
    value = c2.button("💰 Value")
    growth = c3.button("🚀 Growth")

    dividend = c4.button("💵 Dividend")
    debtfree = c5.button("🛡 Debt Free")
    turnaround = c6.button("🔄 Turnaround")

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================

    st.sidebar.header("Screening Filters")

    roe = st.sidebar.slider(
        "Minimum ROE (%)",
        0.0,
        50.0,
        15.0,
        key="screener_roe",
    )

    debt = st.sidebar.slider(
        "Maximum Debt / Equity",
        0.0,
        5.0,
        1.0,
        key="screener_debt",
    )

    fcf = st.sidebar.slider(
        "Minimum Free Cash Flow",
        float(df["free_cash_flow_cr"].min()),
        float(df["free_cash_flow_cr"].max()),
        0.0,
        key="screener_fcf",
    )

    revenue = st.sidebar.slider(
        "Minimum Revenue CAGR",
        0.0,
        40.0,
        10.0,
        key="screener_revenue",
    )

    pat = st.sidebar.slider(
        "Minimum PAT CAGR",
        0.0,
        40.0,
        10.0,
        key="screener_pat",
    )

    opm = st.sidebar.slider(
        "Minimum Operating Margin",
        0.0,
        60.0,
        15.0,
        key="screener_opm",
    )

    pe = st.sidebar.slider(
        "Maximum PE",
        0.0,
        100.0,
        50.0,
        key="screener_pe",
    )

    pb = st.sidebar.slider(
        "Maximum PB",
        0.0,
        20.0,
        5.0,
        key="screener_pb",
    )

    div = st.sidebar.slider(
        "Minimum Dividend Yield",
        0.0,
        10.0,
        1.0,
        key="screener_dividend",
    )

    icr = st.sidebar.slider(
        "Minimum Interest Coverage",
        0.0,
        100.0,
        5.0,
        key="screener_icr",
    )

    # =====================================================
    # DEFAULT FILTERING
    # =====================================================

    result = df.copy()

    result = result[
        (result["return_on_equity_pct"] >= roe)
        & (result["debt_to_equity"] <= debt)
        & (result["free_cash_flow_cr"] >= fcf)
        & (result["revenue_cagr_5yr"] >= revenue)
        & (result["pat_cagr_5yr"] >= pat)
        & (result["operating_profit_margin_pct"] >= opm)
        & (result["pe_ratio"] <= pe)
        & (result["pb_ratio"] <= pb)
        & (result["dividend_yield_pct"] >= div)
        & (result["interest_coverage"] >= icr)
    ]

    # =====================================================
    # PRESET SCREENERS
    # =====================================================

    if quality:
        result = df[
            (df["return_on_equity_pct"] >= 20)
            & (df["debt_to_equity"] <= 0.5)
            & (df["composite_quality_score"] >= 60)
        ]

    elif value:
        result = df[
            (df["pe_ratio"] <= 20)
            & (df["pb_ratio"] <= 3)
        ]

    elif growth:
        result = df[
            (df["revenue_cagr_5yr"] >= 15)
            & (df["pat_cagr_5yr"] >= 15)
        ]

    elif dividend:
        result = df[
            df["dividend_yield_pct"] >= 2
        ]

    elif debtfree:
        result = df[
            df["debt_to_equity"] <= 0.2
        ]

    elif turnaround:
        result = df[
            (df["free_cash_flow_cr"] > 0)
            & (df["interest_coverage"] >= 3)
        ]

    # =====================================================
    # SUMMARY
    # =====================================================

    st.subheader("📊 Screener Summary")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Matching Companies", len(result))

    m2.metric(
        "Average ROE",
        f"{result['return_on_equity_pct'].mean():.2f}%"
        if len(result)
        else "0"
    )

    m3.metric(
        "Average PE",
        f"{result['pe_ratio'].mean():.2f}"
        if len(result)
        else "0"
    )

    m4.metric(
        "Average Score",
        f"{result['composite_quality_score'].mean():.2f}"
        if len(result)
        else "0"
    )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    csv = result.to_csv(index=False)

    st.download_button(
        "📥 Download CSV",
        csv,
        file_name="stock_screener.csv",
        mime="text/csv",
    )

    # =====================================================
    # RESULTS
    # =====================================================

    st.subheader("📋 Matching Companies")

    display_cols = [
        "company_id",
        "company_name",
        "broad_sector",
        "return_on_equity_pct",
        "debt_to_equity",
        "pe_ratio",
        "pb_ratio",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "composite_quality_score",
    ]

    display_cols = [c for c in display_cols if c in result.columns]

    if len(result):

        st.dataframe(
            result[display_cols]
            .sort_values(
                "composite_quality_score",
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No companies match the selected filters.")