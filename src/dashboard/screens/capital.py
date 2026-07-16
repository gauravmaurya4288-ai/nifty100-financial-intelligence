import time
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_capital_allocation


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def safe_metric(value, suffix="", decimals=2):
    """Format metrics safely."""
    if pd.isna(value):
        return "N/A"

    if isinstance(value, (int, float)):
        return f"{round(value, decimals):,}{suffix}"

    return str(value)


# ==========================================================
# PAGE
# ==========================================================

def render():

    start = time.time()

    st.title("💰 Capital Allocation Analysis")

    st.caption(
        "Analyze how companies allocate capital using Free Cash Flow, CAPEX intensity and capital allocation patterns."
    )

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    with st.spinner("Loading capital allocation data..."):

        df = get_capital_allocation()

    if df.empty:

        st.warning("Capital allocation data unavailable.")

        return

    df = df.copy()

    # ------------------------------------------------------
    # CLEAN DATA
    # ------------------------------------------------------

    numeric_columns = [

        "market_cap_crore",

        "free_cash_flow_cr",

        "fcf_conversion_pct",

        "capex_intensity_pct",

        "composite_quality_score"

    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(

                df[col],

                errors="coerce"

            )

    df["capital_allocation_pattern"] = (

        df["capital_allocation_pattern"]

        .fillna("Unknown")

        .astype(str)

        .str.strip()

    )

    df["company_name"] = (

        df["company_name"]

        .fillna(df["company_id"])

        .astype(str)

        .str.strip()

    )

    df = df[df["company_name"] != ""]

    df = df.drop_duplicates()

    # ------------------------------------------------------
    # OVERVIEW
    # ------------------------------------------------------

    st.divider()

    st.subheader("📊 Capital Allocation Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(

        "Companies",

        df["company_id"].nunique()

    )

    c2.metric(

        "Allocation Patterns",

        df["capital_allocation_pattern"].nunique()

    )

    c3.metric(

        "Total Market Cap",

        safe_metric(

            df["market_cap_crore"].sum(),

            " Cr",

            0

        )

    )

    c4.metric(

        "Average Quality",

        safe_metric(

            df["composite_quality_score"].mean()

        )

    )

    st.divider()

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    st.subheader("📈 Financial Snapshot")

    a, b, c = st.columns(3)

    d, e, f = st.columns(3)

    a.metric(

        "Average FCF",

        safe_metric(

            df["free_cash_flow_cr"].mean(),

            " Cr"

        )

    )

    b.metric(

        "Average FCF Conversion",

        safe_metric(

            df["fcf_conversion_pct"].mean(),

            "%"

        )

    )

    c.metric(

        "Average CAPEX Intensity",

        safe_metric(

            df["capex_intensity_pct"].mean(),

            "%"

        )

    )

    d.metric(

        "Highest Quality Score",

        safe_metric(

            df["composite_quality_score"].max()

        )

    )

    e.metric(

        "Highest Market Cap",

        safe_metric(

            df["market_cap_crore"].max(),

            " Cr",

            0

        )

    )

    top_company = (

        df

        .sort_values(

            "composite_quality_score",

            ascending=False

        )

        .iloc[0]["company_name"]

    )

    f.metric(

        "Top Company",

        top_company

    )

    st.divider()

        # ==========================================================
    # CAPITAL ALLOCATION TREEMAP
    # ==========================================================

    st.subheader("🌳 Capital Allocation Treemap")

    treemap_df = df.copy()

    treemap_df = treemap_df.dropna(

        subset=[
            "market_cap_crore",
            "composite_quality_score"
        ]

    )

    fig = px.treemap(

        treemap_df,

        path=[

            "capital_allocation_pattern",

            "company_name"

        ],

        values="market_cap_crore",

        color="composite_quality_score",

        color_continuous_scale="Viridis",

        hover_data={

            "free_cash_flow_cr":":,.2f",

            "fcf_conversion_pct":":.2f",

            "capex_intensity_pct":":.2f",

            "market_cap_crore":":,.0f"

        }

    )

    fig.update_layout(

        height=700,

        margin=dict(

            l=10,

            r=10,

            t=50,

            b=10

        )

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    # ==========================================================
    # PATTERN DISTRIBUTION
    # ==========================================================

    st.subheader("📊 Capital Allocation Pattern Distribution")

    pattern_summary = (

        df

        .groupby("capital_allocation_pattern")

        .agg(

            Companies=("company_id","count"),

            Market_Cap=("market_cap_crore","sum"),

            Avg_Quality=("composite_quality_score","mean")

        )

        .reset_index()

        .sort_values(

            "Companies",

            ascending=False

        )

    )

    fig = px.bar(

        pattern_summary,

        x="capital_allocation_pattern",

        y="Companies",

        color="Avg_Quality",

        text="Companies",

        hover_data=[

            "Market_Cap"

        ],

        title="Companies by Capital Allocation Pattern"

    )

    fig.update_traces(

        textposition="outside"

    )

    fig.update_layout(

        height=500,

        xaxis_title="Pattern",

        yaxis_title="Companies",

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

    st.divider()

    # ==========================================================
    # FCF CONVERSION DISTRIBUTION
    # ==========================================================

    st.subheader("💵 FCF Conversion Distribution")

    fig = px.histogram(

        df,

        x="fcf_conversion_pct",

        nbins=20,

        color="capital_allocation_pattern",

        title="Distribution of FCF Conversion"

    )

    fig.update_layout(

        height=450,

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

    st.divider()

    # ==========================================================
    # QUALITY SCORE DISTRIBUTION
    # ==========================================================

    st.subheader("⭐ Quality Score Distribution")

    fig = px.box(

        df,

        x="capital_allocation_pattern",

        y="composite_quality_score",

        color="capital_allocation_pattern",

        points="all",

        title="Quality Score by Allocation Pattern"

    )

    fig.update_layout(

        height=500,

        showlegend=False,

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

    st.divider()

        # ==========================================================
    # PATTERN SELECTOR
    # ==========================================================

    st.subheader("🔍 Analyze Capital Allocation Pattern")

    pattern = st.selectbox(

        "Select Capital Allocation Pattern",

        sorted(df["capital_allocation_pattern"].unique()),

        key="capital_pattern"

    )

    filtered = df[
        df["capital_allocation_pattern"] == pattern
    ].copy()

    st.divider()

    # ==========================================================
    # PATTERN OVERVIEW
    # ==========================================================

    st.subheader(f"📊 {pattern} Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Companies",
        filtered["company_id"].nunique()
    )

    c2.metric(
        "Market Cap",
        safe_metric(
            filtered["market_cap_crore"].sum(),
            " Cr",
            0
        )
    )

    c3.metric(
        "Avg FCF Conversion",
        safe_metric(
            filtered["fcf_conversion_pct"].mean(),
            "%"
        )
    )

    c4.metric(
        "Avg Quality",
        safe_metric(
            filtered["composite_quality_score"].mean()
        )
    )

    st.divider()

    # ==========================================================
    # TOP CAPITAL ALLOCATORS
    # ==========================================================

    st.subheader("🏆 Top Capital Allocators")

    top = (

        filtered

        .sort_values(

            "composite_quality_score",

            ascending=False

        )

        .head(10)

    )

    fig = px.bar(

        top,

        x="company_id",

        y="composite_quality_score",

        color="fcf_conversion_pct",

        text="composite_quality_score",

        hover_name="company_name",

        title="Top Companies"

    )

    fig.update_traces(

        texttemplate="%{text:.1f}",

        textposition="outside"

    )

    fig.update_layout(

        height=500,

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

    st.divider()

    # ==========================================================
    # COMPANY RANKING
    # ==========================================================

    st.subheader("📋 Company Ranking")

    ranking = filtered.copy()

    ranking["Rank"] = (

        ranking["composite_quality_score"]

        .rank(

            ascending=False,

            method="dense"

        )

        .astype(int)

    )

    ranking = ranking.sort_values("Rank")

    st.dataframe(

        ranking[

            [

                "Rank",

                "company_id",

                "company_name",

                "broad_sector",

                "market_cap_crore",

                "free_cash_flow_cr",

                "fcf_conversion_pct",

                "capex_intensity_pct",

                "composite_quality_score"

            ]

        ].round(2),

        use_container_width=True,

        hide_index=True,

        height=450

    )

    st.divider()

    # ==========================================================
    # PATTERN STATISTICS
    # ==========================================================

    st.subheader("📈 Pattern Statistics")

    statistics = pd.DataFrame({

        "Metric":[

            "Companies",

            "Average Market Cap",

            "Average Free Cash Flow",

            "Average FCF Conversion",

            "Average CAPEX Intensity",

            "Average Quality Score"

        ],

        "Value":[

            filtered["company_id"].nunique(),

            round(filtered["market_cap_crore"].mean(),2),

            round(filtered["free_cash_flow_cr"].mean(),2),

            round(filtered["fcf_conversion_pct"].mean(),2),

            round(filtered["capex_intensity_pct"].mean(),2),

            round(filtered["composite_quality_score"].mean(),2)

        ]

    })

    st.dataframe(

        statistics,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ==========================================================
    # CAPITAL ALLOCATION INSIGHTS
    # ==========================================================

    st.subheader("💡 Insights")

    strengths = []

    concerns = []

    if filtered["fcf_conversion_pct"].mean() >= 80:
        strengths.append("Excellent Free Cash Flow conversion.")

    if filtered["capex_intensity_pct"].mean() <= 25:
        strengths.append("Efficient capital expenditure.")

    if filtered["composite_quality_score"].mean() >= 60:
        strengths.append("High quality companies dominate this pattern.")

    if filtered["fcf_conversion_pct"].mean() < 50:
        concerns.append("Weak cash flow conversion.")

    if filtered["capex_intensity_pct"].mean() > 50:
        concerns.append("Capital expenditure is relatively high.")

    left, right = st.columns(2)

    with left:

        st.success("Strengths")

        if strengths:

            for item in strengths:

                st.markdown(f"✅ {item}")

        else:

            st.info("No significant strengths identified.")

    with right:

        st.warning("Areas to Watch")

        if concerns:

            for item in concerns:

                st.markdown(f"⚠️ {item}")

        else:

            st.info("No major concerns identified.")

    st.divider()

        # ==========================================================
    # EXPORT DATA
    # ==========================================================

    st.subheader("📥 Export Capital Allocation Data")

    export_df = ranking.copy()

    csv = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(

        label="📄 Download Capital Allocation Report",

        data=csv,

        file_name=f"{pattern}_capital_allocation.csv",

        mime="text/csv",

        use_container_width=True

    )

    st.divider()

    # ==========================================================
    # CAPITAL EFFICIENCY SCORE
    # ==========================================================

    st.subheader("🏆 Capital Efficiency Score")

    score = 0

    avg_fcf = filtered["fcf_conversion_pct"].mean()
    avg_capex = filtered["capex_intensity_pct"].mean()
    avg_quality = filtered["composite_quality_score"].mean()
    avg_cashflow = filtered["free_cash_flow_cr"].mean()

    # Free Cash Flow Conversion
    if avg_fcf >= 90:
        score += 25
    elif avg_fcf >= 70:
        score += 20
    elif avg_fcf >= 50:
        score += 15
    elif avg_fcf >= 30:
        score += 10

    # CAPEX Intensity (Lower is Better)
    if avg_capex <= 20:
        score += 25
    elif avg_capex <= 35:
        score += 20
    elif avg_capex <= 50:
        score += 15
    elif avg_capex <= 70:
        score += 10

    # Quality Score
    if avg_quality >= 80:
        score += 25
    elif avg_quality >= 60:
        score += 20
    elif avg_quality >= 40:
        score += 15
    elif avg_quality >= 20:
        score += 10

    # Free Cash Flow
    if avg_cashflow >= 10000:
        score += 25
    elif avg_cashflow >= 5000:
        score += 20
    elif avg_cashflow >= 1000:
        score += 15
    elif avg_cashflow >= 0:
        score += 10

    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B+"
    elif score >= 60:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"

    s1, s2 = st.columns(2)

    s1.metric(

        "Efficiency Score",

        f"{score}/100"

    )

    s2.metric(

        "Grade",

        grade

    )

    st.divider()

    # ==========================================================
    # DASHBOARD SUMMARY
    # ==========================================================

    st.subheader("📊 Dashboard Summary")

    summary = pd.DataFrame({

        "Metric":[

            "Capital Pattern",

            "Companies",

            "Average Market Cap",

            "Average Free Cash Flow",

            "Average FCF Conversion",

            "Average CAPEX Intensity",

            "Average Quality Score"

        ],

        "Value":[

            pattern,

            filtered["company_id"].nunique(),

            round(filtered["market_cap_crore"].mean(),2),

            round(filtered["free_cash_flow_cr"].mean(),2),

            round(filtered["fcf_conversion_pct"].mean(),2),

            round(filtered["capex_intensity_pct"].mean(),2),

            round(filtered["composite_quality_score"].mean(),2)

        ]

    })

    st.dataframe(

        summary,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ==========================================================
    # BEST COMPANY
    # ==========================================================

    st.subheader("🥇 Best Company")

    best = (

        filtered

        .sort_values(

            "composite_quality_score",

            ascending=False

        )

        .iloc[0]

    )

    st.success(f"""

### {best['company_name']}

**Company ID:** {best['company_id']}

**Sector:** {best['broad_sector']}

**Quality Score:** {best['composite_quality_score']:.2f}

**FCF Conversion:** {best['fcf_conversion_pct']:.2f}%

**Free Cash Flow:** ₹ {best['free_cash_flow_cr']:,.2f} Cr

""")

    st.divider()

    # ==========================================================
    # PAGE PERFORMANCE
    # ==========================================================

    elapsed = time.time() - start

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "Companies",

        filtered["company_id"].nunique()

    )

    c2.metric(

        "Patterns",

        df["capital_allocation_pattern"].nunique()

    )

    c3.metric(

        "Load Time",

        f"{elapsed:.2f} sec"

    )

    st.divider()

    # ==========================================================
    # FOOTER
    # ==========================================================

    st.caption(
        "💰 Nifty100 Financial Intelligence Dashboard • Capital Allocation Analysis"
    )