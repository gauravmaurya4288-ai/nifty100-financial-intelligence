import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_sector_analysis

def render():

    st.title("📊 Sector Analysis")

    df = get_sector_analysis()

    if df.empty:
        st.warning("No sector data available.")
        return
    sector = st.selectbox(

    "Select Sector",

    sorted(df["broad_sector"].dropna().unique()),

    key="sector_dropdown"

    )

    sector_df = df[
        df["broad_sector"] == sector
    ].copy()
        
    st.subheader("Sector Summary")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Companies",
        sector_df["company_id"].nunique()
    )

    c2.metric(
        "Median ROE",
        f"{sector_df['return_on_equity_pct'].median():.2f}%"
    )

    c3.metric(
        "Median Revenue CAGR",
        f"{sector_df['revenue_cagr_5yr'].median():.2f}%"
    )

    c4.metric(
        "Median Score",
        f"{sector_df['composite_quality_score'].median():.2f}"
    )

    st.subheader("Revenue vs ROE")

    fig = px.scatter(

        sector_df,

        x="revenue_cagr_5yr",

        y="return_on_equity_pct",

        size="market_cap_crore",

        color="sub_sector",

        hover_name="company_name",

        text="company_id",

        size_max=60

    )

    fig.update_layout(

        height=650,

        xaxis_title="Revenue CAGR (%)",

        yaxis_title="ROE (%)"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.subheader("Sector Median KPIs")

    summary = pd.DataFrame({

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

        summary,

        x="Metric",

        y="Value",

        text="Value"

    )

    fig.update_layout(

        height=450

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.subheader("Companies")

    cols = [

        "company_id",

        "company_name",

        "sub_sector",

        "market_cap_crore",

        "return_on_equity_pct",

        "revenue_cagr_5yr",

        "composite_quality_score"

    ]

    st.dataframe(

        sector_df[cols].sort_values(

            "composite_quality_score",

            ascending=False

        ),

        use_container_width=True,

        hide_index=True

    )