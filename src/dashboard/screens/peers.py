import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import (
    get_peer_groups,
    get_peer_companies,
    get_peer_metrics,
)

def render():

    st.title("🤝 Peer Comparison")

    groups = get_peer_groups()

    peer_group = st.selectbox(
        "Select Peer Group",
        groups["peer_group_name"],
        key="peer_group"
    )

    companies = get_peer_companies(peer_group)

    company = st.selectbox(
        "Select Company",
        companies["company_id"],
        key="peer_company"
    )

    df = get_peer_metrics(peer_group)

    if df.empty:
        st.warning("No peer data.")
        return
    
    metrics = [

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "net_profit_margin_pct",

    "debt_to_equity",

    "free_cash_flow_cr",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "composite_quality_score"

    ]

    labels = [

    "ROE",

    "ROCE",

    "NPM",

    "D/E",

    "FCF",

    "Revenue CAGR",

    "PAT CAGR",

    "Composite"

    ]

    company_row = df[df.company_id == company]

    peer_avg = df[metrics].mean()

    fig = go.Figure()

    fig.add_trace(

    go.Scatterpolar(

    r=company_row.iloc[0][metrics].values,

    theta=labels,

    fill="toself",

    name=company

    )

    )

    fig.add_trace(

    go.Scatterpolar(

    r=peer_avg.values,

    theta=labels,

    fill="toself",

    name="Peer Average"

    )

    )

    fig.update_layout(

    polar=dict(

    radialaxis=dict(

    visible=True

    )

    ),

    height=650,

    showlegend=True

    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Peer Comparison Table")

    show = [

    "company_id",

    "company_name",

    "is_benchmark",

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "net_profit_margin_pct",

    "debt_to_equity",

    "free_cash_flow_cr",

    "composite_quality_score"

    ]

    table = df[show]

    st.dataframe(

    table,

    use_container_width=True,

    hide_index=True

    )


    def highlight(row):

        if row["is_benchmark"] == 1:

            return ["background-color:#145A32;color:white"]*len(row)

        return [""]*len(row)

    st.dataframe(

    table.style.apply(highlight,axis=1),

    use_container_width=True

    )

