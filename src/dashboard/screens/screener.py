import time
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_screener_data


# ==========================================================
# HELPERS
# ==========================================================

def safe_metric(value, suffix="", decimals=2):
    if pd.isna(value):
        return "N/A"

    if isinstance(value, (int, float)):
        return f"{round(value, decimals)}{suffix}"

    return str(value)


# ==========================================================
# PAGE
# ==========================================================

def render():

    start = time.time()

    st.title("🔍 Stock Screener")

    st.caption(
        "Filter and discover high-quality Nifty100 companies."
    )

    # ======================================================
    # LOAD DATA
    # ======================================================

    with st.spinner("Loading screener data..."):

        df = get_screener_data()

    if df.empty:

        st.warning("No screener data available.")

        return

    df = df.copy()

    # ======================================================
    # CLEAN DATA
    # ======================================================

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

            df[col] = pd.to_numeric(

                df[col],

                errors="coerce"

            ).fillna(0)

    # ======================================================
    # QUICK SCREENERS
    # ======================================================

    st.subheader("⚡ Quick Screeners")

    b1, b2, b3 = st.columns(3)
    b4, b5, b6 = st.columns(3)

    quality = b1.button(
        "⭐ Quality",
        use_container_width=True
    )

    value = b2.button(
        "💰 Value",
        use_container_width=True
    )

    growth = b3.button(
        "🚀 Growth",
        use_container_width=True
    )

    dividend = b4.button(
        "💵 Dividend",
        use_container_width=True
    )

    debtfree = b5.button(
        "🛡 Debt Free",
        use_container_width=True
    )

    turnaround = b6.button(
        "🔄 Turnaround",
        use_container_width=True
    )

    st.divider()

    # ======================================================
    # SIDEBAR
    # ======================================================

    st.sidebar.header("📊 Screener Filters")

    # Company Search

    companies = sorted(
        df["company_id"].dropna().unique()
    )

    selected_company = st.sidebar.selectbox(

        "Company",

        ["All Companies"] + companies,

        key="scr_company"

    )

    # Sector Filter

    sectors = sorted(

        df["broad_sector"]

        .fillna("Unknown")

        .unique()

    )

    selected_sector = st.sidebar.selectbox(

        "Sector",

        ["All Sectors"] + sectors,

        key="scr_sector"

    )

    # Market Cap

    if "market_cap_category" in df.columns:

        caps = sorted(

            df["market_cap_category"]

            .fillna("Unknown")

            .unique()

        )

        selected_cap = st.sidebar.selectbox(

            "Market Cap",

            ["All"] + caps,

            key="scr_cap"

        )

    else:

        selected_cap = "All"

    st.sidebar.divider()

    st.sidebar.subheader("Financial Filters")

    roe = st.sidebar.slider(

        "Minimum ROE (%)",

        0.0,

        50.0,

        15.0,

        key="roe"

    )

    debt = st.sidebar.slider(

        "Maximum Debt/Equity",

        0.0,

        5.0,

        1.0,

        key="debt"

    )

    revenue = st.sidebar.slider(

        "Minimum Revenue CAGR",

        0.0,

        40.0,

        10.0,

        key="rev"

    )

    pat = st.sidebar.slider(

        "Minimum PAT CAGR",

        0.0,

        40.0,

        10.0,

        key="pat"

    )

    opm = st.sidebar.slider(

        "Minimum Operating Margin",

        0.0,

        60.0,

        15.0,

        key="opm"

    )

    pe = st.sidebar.slider(

        "Maximum PE",

        0.0,

        100.0,

        50.0,

        key="pe"

    )

    pb = st.sidebar.slider(

        "Maximum PB",

        0.0,

        20.0,

        5.0,

        key="pb"

    )

    dividend_yield = st.sidebar.slider(

        "Minimum Dividend Yield",

        0.0,

        10.0,

        1.0,

        key="div"

    )

    icr = st.sidebar.slider(

        "Minimum Interest Coverage",

        0.0,

        100.0,

        5.0,

        key="icr"

    )

    fcf = st.sidebar.slider(

        "Minimum Free Cash Flow",

        float(df["free_cash_flow_cr"].min()),

        float(df["free_cash_flow_cr"].max()),

        0.0,

        key="fcf"

    )

    st.sidebar.divider()

    reset = st.sidebar.button(

        "🔄 Reset Filters",

        use_container_width=True

    )

    # ======================================================
    # APPLY FILTERS
    # ======================================================

    result = df.copy()

    # Company Filter
    if selected_company != "All Companies":
        result = result[
            result["company_id"] == selected_company
        ]

    # Sector Filter
    if selected_sector != "All Sectors":
        result = result[
            result["broad_sector"] == selected_sector
        ]

    # Market Cap Filter
    if selected_cap != "All" and "market_cap_category" in result.columns:
        result = result[
            result["market_cap_category"] == selected_cap
        ]

    # Financial Filters
    result = result[
        (result["return_on_equity_pct"] >= roe)
        & (result["debt_to_equity"] <= debt)
        & (result["free_cash_flow_cr"] >= fcf)
        & (result["revenue_cagr_5yr"] >= revenue)
        & (result["pat_cagr_5yr"] >= pat)
        & (result["operating_profit_margin_pct"] >= opm)
        & (result["pe_ratio"] <= pe)
        & (result["pb_ratio"] <= pb)
        & (result["dividend_yield_pct"] >= dividend_yield)
        & (result["interest_coverage"] >= icr)
    ]

    # ======================================================
    # QUICK SCREENERS
    # ======================================================

    if quality:

        result = df[
            (df["return_on_equity_pct"] >= 20)
            &
            (df["debt_to_equity"] <= 0.50)
            &
            (df["composite_quality_score"] >= 60)
        ]

    elif value:

        result = df[
            (df["pe_ratio"] <= 20)
            &
            (df["pb_ratio"] <= 3)
        ]

    elif growth:

        result = df[
            (df["revenue_cagr_5yr"] >= 15)
            &
            (df["pat_cagr_5yr"] >= 15)
        ]

    elif dividend:

        result = df[
            df["dividend_yield_pct"] >= 2
        ]

    elif debtfree:

        result = df[
            df["debt_to_equity"] <= 0.20
        ]

    elif turnaround:

        result = df[
            (df["free_cash_flow_cr"] > 0)
            &
            (df["interest_coverage"] >= 3)
        ]

    # ======================================================
    # RESET FILTERS
    # ======================================================

    if reset:

        st.rerun()

    st.divider()

    # ======================================================
    # RESULT SUMMARY
    # ======================================================

    st.subheader("📊 Screening Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Matching Companies",
        len(result)
    )

    avg_roe = (
        result["return_on_equity_pct"].mean()
        if not result.empty else 0
    )

    avg_pe = (
        result["pe_ratio"].mean()
        if not result.empty else 0
    )

    avg_score = (
        result["composite_quality_score"].mean()
        if not result.empty else 0
    )

    best_score = (
        result["composite_quality_score"].max()
        if not result.empty else 0
    )

    c2.metric(
        "Average ROE",
        safe_metric(avg_roe, "%")
    )

    c3.metric(
        "Average Score",
        safe_metric(avg_score)
    )

    c4.metric(
        "Highest Score",
        safe_metric(best_score)
    )

    st.divider()

    # ======================================================
    # TOP COMPANY
    # ======================================================

    if not result.empty:

        top_company = result.sort_values(
            "composite_quality_score",
            ascending=False
        ).iloc[0]

        st.success(
            f"🏆 Top Match: **{top_company['company_id']}** | "
            f"Quality Score: {safe_metric(top_company['composite_quality_score'])}"
        )

    else:

        st.warning(
            "No companies match the selected filters."
        )

    st.divider()

    # ======================================================
    # SORT OPTIONS
    # ======================================================

    sort_column = st.selectbox(

        "Sort Results By",

        [
            "composite_quality_score",
            "return_on_equity_pct",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "pe_ratio",
            "pb_ratio",
            "market_cap_crore",
        ],

        key="sort_column"

    )

    ascending = st.checkbox(

        "Ascending Order",

        value=False,

        key="sort_order"

    )

    if sort_column in result.columns:

        result = result.sort_values(

            sort_column,

            ascending=ascending

        )

    st.divider()

    # ======================================================
    # VISUAL ANALYTICS
    # ======================================================

    st.subheader("📈 Screener Analytics")

    if not result.empty:

        left, right = st.columns(2)

        # ==================================================
        # SECTOR DISTRIBUTION
        # ==================================================

        with left:

            if "broad_sector" in result.columns:

                sector_summary = (
                    result.groupby("broad_sector")
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

                    hole=0.45,

                    title="Sector Distribution"

                )

                fig.update_layout(

                    height=450,

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

        # ==================================================
        # QUALITY SCORE HISTOGRAM
        # ==================================================

        with right:

            fig = px.histogram(

                result,

                x="composite_quality_score",

                nbins=20,

                title="Quality Score Distribution"

            )

            fig.update_layout(

                height=450,

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

    else:

        st.info("No data available for charts.")

    st.divider()

    # ======================================================
    # TOP 10 COMPANIES
    # ======================================================

    st.subheader("🏆 Top 10 Companies")

    if not result.empty:

        top10 = (

            result

            .sort_values(

                "composite_quality_score",

                ascending=False

            )

            .head(10)

        )

        fig = px.bar(

            top10,

            x="company_id",

            y="composite_quality_score",

            color="composite_quality_score",

            text="composite_quality_score",

            title="Top Companies by Quality Score"

        )

        fig.update_traces(

            texttemplate="%{text:.1f}",

            textposition="outside"

        )

        fig.update_layout(

            height=500,

            xaxis_title="Company",

            yaxis_title="Quality Score",

            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    else:

        st.warning("No companies available.")

    st.divider()

    # ======================================================
    # SUMMARY STATISTICS
    # ======================================================

    st.subheader("📊 Statistics")

    stats = pd.DataFrame({

        "Metric":[

            "Companies",

            "Average ROE",

            "Average PE",

            "Average PB",

            "Average Revenue CAGR",

            "Average PAT CAGR",

            "Highest Score",

            "Lowest Score"

        ],

        "Value":[

            len(result),

            round(result["return_on_equity_pct"].mean(),2) if len(result) else 0,

            round(result["pe_ratio"].mean(),2) if len(result) else 0,

            round(result["pb_ratio"].mean(),2) if len(result) else 0,

            round(result["revenue_cagr_5yr"].mean(),2) if len(result) else 0,

            round(result["pat_cagr_5yr"].mean(),2) if len(result) else 0,

            round(result["composite_quality_score"].max(),2) if len(result) else 0,

            round(result["composite_quality_score"].min(),2) if len(result) else 0

        ]

    })

    st.dataframe(

        stats,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # DOWNLOAD RESULTS
    # ======================================================

    st.subheader("📥 Export Results")

    csv = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📄 Download Filtered Companies (CSV)",
        data=csv,
        file_name="nifty100_screening_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()

    # ======================================================
    # RESULT TABLE
    # ======================================================

    st.subheader("📋 Matching Companies")

    if result.empty:

        st.warning("No companies match the selected screening criteria.")

    else:

        display_columns = [

            "company_id",
            "company_name",
            "broad_sector",
            "market_cap_category",
            "return_on_equity_pct",
            "debt_to_equity",
            "pe_ratio",
            "pb_ratio",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "free_cash_flow_cr",
            "dividend_yield_pct",
            "interest_coverage",
            "composite_quality_score",

        ]

        display_columns = [
            col
            for col in display_columns
            if col in result.columns
        ]

        styled = (

            result[display_columns]

            .sort_values(

                sort_column,

                ascending=ascending

            )

            .reset_index(drop=True)

        )

        st.dataframe(

            styled,

            use_container_width=True,

            hide_index=True,

            height=550,

        )

    st.divider()

    # ======================================================
    # BEST MATCH
    # ======================================================

    if not result.empty:

        best = result.sort_values(

            "composite_quality_score",

            ascending=False

        ).iloc[0]

        st.success(

            f"""
    🏆 **Best Match**

    **Company:** {best.get('company_name', best['company_id'])}

    **Ticker:** {best['company_id']}

    **Quality Score:** {safe_metric(best['composite_quality_score'])}

    **ROE:** {safe_metric(best['return_on_equity_pct'], '%')}

    **Revenue CAGR:** {safe_metric(best['revenue_cagr_5yr'], '%')}
    """

        )

    st.divider()

    # ======================================================
    # SCREENING NOTES
    # ======================================================

    with st.expander("ℹ️ Screening Notes"):

        st.markdown("""

    ### Quality Screen

    - ROE ≥ 20%
    - Debt/Equity ≤ 0.5
    - Composite Score ≥ 60

    ### Value Screen

    - PE ≤ 20
    - PB ≤ 3

    ### Growth Screen

    - Revenue CAGR ≥ 15%
    - PAT CAGR ≥ 15%

    ### Dividend Screen

    - Dividend Yield ≥ 2%

    ### Debt Free

    - Debt/Equity ≤ 0.20

    ### Turnaround

    - Positive Free Cash Flow
    - Interest Coverage ≥ 3

    """)

    st.divider()

    # ======================================================
    # PAGE PERFORMANCE
    # ======================================================

    load_time = time.time() - start

    left, right = st.columns(2)

    left.caption(
        f"⚡ Loaded in **{load_time:.2f} sec**"
    )

    right.caption(
        f"📊 {len(result)} Companies Displayed"
    )

    st.divider()

    st.caption(
        "📈 Nifty100 Financial Intelligence Dashboard • Advanced Stock Screener"
    )