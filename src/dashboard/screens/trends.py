import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_company_history
)

def render():

    st.title("📈 Trend Analysis")

    companies = get_companies()

    ticker = st.selectbox(
        "Select Company",
        sorted(companies["company_id"].dropna().unique()),
        key="trend_company"
    )

    history = get_company_history(ticker)

    if history.empty:
        st.warning("No historical financial data available.")
        return
    
    metric_options = {
    "ROE":"return_on_equity_pct",
    "ROCE":"return_on_capital_employed_pct",
    "Net Margin":"net_profit_margin_pct",
    "Operating Margin":"operating_profit_margin_pct",
    "Debt / Equity":"debt_to_equity",
    "Interest Coverage":"interest_coverage",
    "Revenue CAGR":"revenue_cagr_5yr",
    "PAT CAGR":"pat_cagr_5yr",
    "Composite Score":"composite_quality_score"
}

    selected = st.multiselect(
        "Select Metrics (Maximum 3)",
        list(metric_options.keys()),
        default=["ROE"],
        max_selections=3,
        key="trend_metrics"
    )

    if len(selected) == 0:
        st.info("Please select at least one metric.")
        return

    fig = go.Figure()

    for item in selected:

        column = metric_options[item]

        fig.add_trace(
            go.Scatter(
                x=history["year"],
                y=history[column],
                mode="lines+markers",
                name=item
            )
        )

    fig.update_layout(
        title=f"{ticker} Financial Trends",
        height=650,
        hovermode="x unified",
        xaxis_title="Financial Year",
        yaxis_title="Value",
        legend_title="Metrics"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📊 Year-over-Year Growth")

    growth = history.copy()

    for item in selected:

        column = metric_options[item]

        growth[f"{item} YoY %"] = growth[column].pct_change() * 100

    display_cols = ["year"] + [f"{item} YoY %" for item in selected]

    st.dataframe(
        growth[display_cols].round(2),
        use_container_width=True,
        hide_index=True
    )

    csv = growth.to_csv(index=False)

    st.download_button(
        "📥 Download Trend Data",
        csv,
        file_name=f"{ticker}_trend_analysis.csv",
        mime="text/csv"
    )
