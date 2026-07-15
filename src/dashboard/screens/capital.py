import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_capital_allocation

def render():

    st.title("💰 Capital Allocation")

    df = get_capital_allocation()

    if df.empty:

        st.warning("Capital allocation data unavailable.")

        return
    
    df["capital_allocation_pattern"] = (
    df["capital_allocation_pattern"]
    .fillna("Unknown")
)

    df["market_cap_crore"] = (
        pd.to_numeric(
            df["market_cap_crore"],
            errors="coerce"
        ).fillna(0)
    )

    st.subheader("Overview")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Companies",
        df["company_id"].nunique()
    )

    c2.metric(
        "Patterns",
        df["capital_allocation_pattern"].nunique()
    )

    c3.metric(
        "Average FCF Conversion",
        f"{df['fcf_conversion_pct'].mean():.2f}%"
    )

    c4.metric(
        "Average Quality Score",
        f"{df['composite_quality_score'].mean():.2f}"
    )

    df = df.copy()

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

    # Remove blank company names
    df = df[df["company_name"] != ""]

    # Remove rows where parent == child
    df = df[
        df["capital_allocation_pattern"] != df["company_name"]
    ]

    # Remove duplicates
    df = df.drop_duplicates(
        subset=[
            "capital_allocation_pattern",
            "company_name"
        ]
    )

    st.subheader("Capital Allocation Map")

    fig = px.treemap(

        df,

        path=[
            "capital_allocation_pattern",
            "company_name"
        ],

        values="market_cap_crore",

        color="composite_quality_score",

        hover_data=[
            "free_cash_flow_cr",
            "fcf_conversion_pct"
        ]

    )

    fig.update_layout(
        height=700
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    pattern = st.selectbox(

        "Capital Allocation Pattern",

        sorted(
            df["capital_allocation_pattern"]
            .unique()
        ),

        key="capital_pattern"

    )

    filtered = df[
        df["capital_allocation_pattern"] == pattern
    ]

    st.subheader("Companies")

    cols = [

        "company_id",

        "company_name",

        "broad_sector",

        "market_cap_crore",

        "free_cash_flow_cr",

        "fcf_conversion_pct",

        "capex_intensity_pct",

        "composite_quality_score"

    ]

    st.dataframe(

        filtered[cols]
        .sort_values(
            "composite_quality_score",
            ascending=False
        ),

        use_container_width=True,

        hide_index=True

    )

    st.subheader("Pattern Statistics")

    summary = filtered[[
        "market_cap_crore",
        "free_cash_flow_cr",
        "fcf_conversion_pct",
        "composite_quality_score"
    ]].describe()

    st.dataframe(
        summary,
        use_container_width=True
    )

