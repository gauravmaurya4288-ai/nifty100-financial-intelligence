import time
import pandas as pd
import streamlit as st
import plotly.express as px

from utils.db import get_sector_analysis


# ==========================================
# Helper
# ==========================================

def safe(value, suffix=""):

    if pd.isna(value):
        return "N/A"

    return f"{round(value,2)}{suffix}"


# ==========================================
# Main Page
# ==========================================

def render():

    start = time.time()

    st.title("🏭 Sector Analysis")

    st.caption(
        "Analyze companies across different sectors of the Nifty100 universe."
    )

    # --------------------------------------
    # Load Data
    # --------------------------------------

    with st.spinner("Loading sector data..."):

        df = get_sector_analysis()

    if df.empty:

        st.error("Sector data not available.")

        return

    # --------------------------------------
    # Convert Numeric Columns
    # --------------------------------------

    numeric_columns = [

        "market_cap_crore",

        "return_on_equity_pct",

        "return_on_capital_employed_pct",

        "net_profit_margin_pct",

        "revenue_cagr_5yr",

        "composite_quality_score"

    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # --------------------------------------
    # Sector Selection
    # --------------------------------------

    sectors = sorted(

        df["broad_sector"]

        .dropna()

        .unique()

    )

    selected_sector = st.selectbox(

        "Select Sector",

        sectors,

        key="sector"

    )

    sector_df = df[

        df["broad_sector"] == selected_sector

    ].copy()

    if sector_df.empty:

        st.warning("No data available.")

        return
    
        st.divider()

    st.subheader(selected_sector)

    col1, col2, col3 = st.columns(3)

    col1.metric(

        "Companies",

        sector_df["company_id"].nunique()

    )

    col2.metric(

        "Sub-sectors",

        sector_df["sub_sector"].nunique()

    )

    col3.metric(

        "Market Cap",

        safe(

            sector_df["market_cap_crore"].sum(),

            " Cr"

        )

    )

    st.divider()

    st.subheader("Financial Snapshot")

    a,b,c = st.columns(3)

    d,e,f = st.columns(3)

    a.metric(

        "Median ROE",

        safe(

            sector_df["return_on_equity_pct"].median(),

            "%"

        )

    )

    b.metric(

        "Median ROCE",

        safe(

            sector_df["return_on_capital_employed_pct"].median(),

            "%"

        )

    )

    c.metric(

        "Median Margin",

        safe(

            sector_df["net_profit_margin_pct"].median(),

            "%"

        )

    )

    d.metric(

        "Revenue CAGR",

        safe(

            sector_df["revenue_cagr_5yr"].median(),

            "%"

        )

    )

    e.metric(

        "Quality Score",

        safe(

            sector_df["composite_quality_score"].median()

        )

    )

    f.metric(

        "Top Company",

        sector_df.sort_values(

            "composite_quality_score",

            ascending=False

        ).iloc[0]["company_id"]

    )

    st.divider()
        # ==========================================
    # REVENUE CAGR vs ROE
    # ==========================================

    st.subheader("📈 Revenue Growth vs ROE")

    bubble = sector_df.dropna(
        subset=[
            "revenue_cagr_5yr",
            "return_on_equity_pct",
            "market_cap_crore"
        ]
    )

    if not bubble.empty:

        fig = px.scatter(

            bubble,

            x="revenue_cagr_5yr",

            y="return_on_equity_pct",

            size="market_cap_crore",

            color="sub_sector",

            hover_name="company_name",

            text="company_id",

            size_max=60,

            title=f"{selected_sector} Companies"

        )

        fig.update_traces(

            marker=dict(

                opacity=0.80,

                line=dict(width=1)

            ),

            textposition="top center"

        )

        fig.update_layout(

            height=650,

            xaxis_title="Revenue CAGR (%)",

            yaxis_title="Return on Equity (%)",

            legend_title="Sub Sector",

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

        st.info("Not enough data for bubble chart.")

    st.divider()

    # ==========================================
    # MEDIAN KPI COMPARISON
    # ==========================================

    st.subheader("📊 Sector KPI Comparison")

    kpi = pd.DataFrame({

        "Metric":[

            "ROE",

            "ROCE",

            "Net Margin",

            "Revenue CAGR",

            "Quality Score"

        ],

        "Value":[

            sector_df["return_on_equity_pct"].median(),

            sector_df["return_on_capital_employed_pct"].median(),

            sector_df["net_profit_margin_pct"].median(),

            sector_df["revenue_cagr_5yr"].median(),

            sector_df["composite_quality_score"].median()

        ]

    })

    fig = px.bar(

        kpi,

        x="Metric",

        y="Value",

        color="Metric",

        text="Value",

        title="Median Financial Metrics"

    )

    fig.update_traces(

        texttemplate="%{text:.2f}",

        textposition="outside"

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

    # ==========================================
    # QUALITY SCORE DISTRIBUTION
    # ==========================================

    st.subheader("🏆 Quality Score Distribution")

    fig = px.histogram(

        sector_df,

        x="composite_quality_score",

        nbins=15,

        title="Composite Quality Score"

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

    st.divider()

    # ==========================================
    # TOP COMPANIES
    # ==========================================

    st.subheader("🥇 Top 10 Companies")

    top = (

        sector_df

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

        color="composite_quality_score",

        hover_name="company_name",

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

    st.divider()

        # ==========================================
    # COMPANY TABLE
    # ==========================================

    st.subheader("📋 Companies in Selected Sector")

    company_table = (

        sector_df

        .sort_values(

            "composite_quality_score",

            ascending=False

        )

        [

            [

                "company_id",

                "company_name",

                "sub_sector",

                "market_cap_crore",

                "return_on_equity_pct",

                "return_on_capital_employed_pct",

                "net_profit_margin_pct",

                "revenue_cagr_5yr",

                "composite_quality_score"

            ]

        ]

    )

    st.dataframe(

        company_table.round(2),

        use_container_width=True,

        hide_index=True,

        height=500

    )

    st.divider()

    # ==========================================
    # DOWNLOAD CSV
    # ==========================================

    st.subheader("📥 Export Data")

    csv = company_table.to_csv(index=False).encode("utf-8")

    st.download_button(

        label="📄 Download Sector Report",

        data=csv,

        file_name=f"{selected_sector}_sector_analysis.csv",

        mime="text/csv",

        use_container_width=True

    )

    st.divider()

    # ==========================================
    # SECTOR HEALTH SCORE
    # ==========================================

    st.subheader("🏆 Sector Health Score")

    score = 0

    median_roe = sector_df["return_on_equity_pct"].median()
    median_roce = sector_df["return_on_capital_employed_pct"].median()
    median_margin = sector_df["net_profit_margin_pct"].median()
    median_growth = sector_df["revenue_cagr_5yr"].median()
    median_quality = sector_df["composite_quality_score"].median()

    if median_roe >= 20:
        score += 20

    if median_roce >= 20:
        score += 20

    if median_margin >= 15:
        score += 20

    if median_growth >= 15:
        score += 20

    if median_quality >= 60:
        score += 20

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

    col1, col2 = st.columns(2)

    col1.metric(

        "Health Score",

        f"{score}/100"

    )

    col2.metric(

        "Grade",

        grade

    )

    st.divider()

    # ==========================================
    # DASHBOARD SUMMARY
    # ==========================================

    st.subheader("📌 Dashboard Summary")

    summary = pd.DataFrame({

        "Metric":[

            "Sector",

            "Companies",

            "Sub-sectors",

            "Median ROE",

            "Median ROCE",

            "Median Margin",

            "Median Revenue CAGR",

            "Median Quality Score",

            "Total Market Cap (Cr)"

        ],

        "Value":[

            selected_sector,

            sector_df["company_id"].nunique(),

            sector_df["sub_sector"].nunique(),

            round(median_roe,2),

            round(median_roce,2),

            round(median_margin,2),

            round(median_growth,2),

            round(median_quality,2),

            round(sector_df["market_cap_crore"].sum(),2)

        ]

    })

    st.dataframe(

        summary,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ==========================================
    # PAGE PERFORMANCE
    # ==========================================

    elapsed = time.time() - start

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "Companies",

        sector_df["company_id"].nunique()

    )

    c2.metric(

        "Sub-sectors",

        sector_df["sub_sector"].nunique()

    )

    c3.metric(

        "Load Time",

        f"{elapsed:.2f} sec"

    )

    st.divider()

    # ==========================================
    # FOOTER
    # ==========================================

    st.caption(
        "📊 Nifty100 Financial Intelligence Dashboard • Sector Analysis"
    )