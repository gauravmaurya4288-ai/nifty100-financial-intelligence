import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils.db import (
    get_peer_groups,
    get_peer_companies,
    get_peer_metrics,
)

from components.header import render_header
from components.footer import render_footer


from components.styles import load_css

load_css()

# ==========================================================
# HELPER
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

    st.title("🤝 Peer Comparison")

    st.caption(
        "Compare a company with others in the same peer group."
    )

    # ======================================================
    # LOAD DATA
    # ======================================================

    with st.spinner("Loading peer comparison..."):

        groups = get_peer_groups()

    if groups.empty:

        st.warning("No peer groups available.")

        return

    # ======================================================
    # PEER GROUP
    # ======================================================

    peer_group = st.selectbox(

        "Select Peer Group",

        sorted(groups["peer_group_name"].unique()),

        key="peer_group"

    )

    companies = get_peer_companies(peer_group)

    if companies.empty:

        st.warning("No companies found.")

        return

    # ======================================================
    # COMPANY
    # ======================================================

    ticker = st.selectbox(

        "Select Company",

        sorted(companies["company_id"].unique()),

        key="peer_company"

    )

    with st.spinner("Loading peer metrics..."):

        df = get_peer_metrics(peer_group)

    if df.empty:

        st.warning("Peer metrics unavailable.")

        return

    df = df.copy()

    # ======================================================
    # CLEAN DATA
    # ======================================================

    metrics = [

        "return_on_equity_pct",

        "return_on_capital_employed_pct",

        "net_profit_margin_pct",

        "debt_to_equity",

        "free_cash_flow_cr",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "composite_quality_score",

    ]

    for col in metrics:

        if col in df.columns:

            df[col] = pd.to_numeric(

                df[col],

                errors="coerce"

            ).fillna(0)

    company = df[

        df["company_id"] == ticker

    ]

    if company.empty:

        st.warning("Company not found.")

        return

    company = company.iloc[0]

    # ======================================================
    # PROFILE
    # ======================================================

    st.divider()

    left, right = st.columns([1, 4])

    with left:

        st.metric(

            "Peer Group",

            peer_group

        )

    with right:

        st.subheader(

            company.get(

                "company_name",

                ticker

            )

        )

        st.write(f"**Ticker:** {ticker}")

        benchmark = "Yes" if company.get("is_benchmark", 0) == 1 else "No"

        st.write(f"**Benchmark Company:** {benchmark}")

    st.divider()

    # ======================================================
    # KPI CARDS
    # ======================================================

    st.subheader("📊 Latest Financial Snapshot")

    c1, c2, c3, c4 = st.columns(4)

    c5, c6, c7, c8 = st.columns(4)

    c1.metric(

        "ROE",

        safe_metric(

            company["return_on_equity_pct"],

            "%"

        )

    )

    c2.metric(

        "ROCE",

        safe_metric(

            company["return_on_capital_employed_pct"],

            "%"

        )

    )

    c3.metric(

        "Net Margin",

        safe_metric(

            company["net_profit_margin_pct"],

            "%"

        )

    )

    c4.metric(

        "Debt/Equity",

        safe_metric(

            company["debt_to_equity"]

        )

    )

    c5.metric(

        "Revenue CAGR",

        safe_metric(

            company["revenue_cagr_5yr"],

            "%"

        )

    )

    c6.metric(

        "PAT CAGR",

        safe_metric(

            company["pat_cagr_5yr"],

            "%"

        )

    )

    c7.metric(

        "Free Cash Flow",

        safe_metric(

            company["free_cash_flow_cr"],

            " Cr",

            0

        )

    )

    c8.metric(

        "Quality Score",

        safe_metric(

            company["composite_quality_score"]

        )

    )

    st.divider()

    # ======================================================
    # RADAR CHART
    # ======================================================

    st.subheader("🕸 Company vs Peer Average")

    labels = [

        "ROE",
        "ROCE",
        "Net Margin",
        "Debt",
        "FCF",
        "Revenue CAGR",
        "PAT CAGR",
        "Quality"

    ]

    # Peer Average
    peer_avg = df[metrics].mean()

    # Company Values
    company_values = company[metrics]

    # ---------- Normalize Data ----------

    radar = pd.DataFrame({

        "Metric": metrics,

        "Company": company_values.values,

        "Peer": peer_avg.values

    })

    for col in ["Company", "Peer"]:

        minimum = radar[col].min()
        maximum = radar[col].max()

        if maximum != minimum:

            radar[col] = (

                (radar[col] - minimum)

                /

                (maximum - minimum)

            ) * 100

        else:

            radar[col] = 50

    fig = go.Figure()

    fig.add_trace(

        go.Scatterpolar(

            r=radar["Company"],

            theta=labels,

            fill="toself",

            name=ticker,

            line=dict(width=3)

        )

    )

    fig.add_trace(

        go.Scatterpolar(

            r=radar["Peer"],

            theta=labels,

            fill="toself",

            name="Peer Average",

            line=dict(width=3)

        )

    )

    fig.update_layout(

        polar=dict(

            radialaxis=dict(

                visible=True,

                range=[0,100]

            )

        ),

        height=650,

        title="Normalized Financial Comparison",

        showlegend=True

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    # ======================================================
    # COMPANY vs PEER TABLE
    # ======================================================

    st.subheader("📊 Company vs Peer Average")

    comparison = pd.DataFrame({

        "Metric":[

            "ROE",

            "ROCE",

            "Net Margin",

            "Debt/Equity",

            "Revenue CAGR",

            "PAT CAGR",

            "Quality Score"

        ],

        "Company":[

            company["return_on_equity_pct"],

            company["return_on_capital_employed_pct"],

            company["net_profit_margin_pct"],

            company["debt_to_equity"],

            company["revenue_cagr_5yr"],

            company["pat_cagr_5yr"],

            company["composite_quality_score"]

        ],

        "Peer Average":[

            peer_avg["return_on_equity_pct"],

            peer_avg["return_on_capital_employed_pct"],

            peer_avg["net_profit_margin_pct"],

            peer_avg["debt_to_equity"],

            peer_avg["revenue_cagr_5yr"],

            peer_avg["pat_cagr_5yr"],

            peer_avg["composite_quality_score"]

        ]

    })

    comparison["Difference"] = (

        comparison["Company"]

        -

        comparison["Peer Average"]

    ).round(2)

    st.dataframe(

        comparison,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # BAR CHART
    # ======================================================

    st.subheader("📈 Metric Comparison")

    bar_df = comparison.melt(

        id_vars="Metric",

        value_vars=[

            "Company",

            "Peer Average"

        ],

        var_name="Category",

        value_name="Value"

    )

    fig = px.bar(

        bar_df,

        x="Metric",

        y="Value",

        color="Category",

        barmode="group",

        text="Value",

        title="Company vs Peer Average"

    )

    fig.update_traces(

        texttemplate="%{text:.2f}",

        textposition="outside"

    )

    fig.update_layout(

        height=550,

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

    # ======================================================
    # PERFORMANCE SUMMARY
    # ======================================================

    st.subheader("🏆 Performance Summary")

    better = (

        comparison["Difference"] > 0

    ).sum()

    same = (

        comparison["Difference"] == 0

    ).sum()

    worse = (

        comparison["Difference"] < 0

    ).sum()

    a, b, c = st.columns(3)

    a.metric(

        "Better Than Peers",

        better

    )

    b.metric(

        "Equal",

        same

    )

    c.metric(

        "Below Peer Average",

        worse

    )

    st.divider()

    # ======================================================
    # PEER RANKINGS
    # ======================================================

    st.subheader("🏆 Peer Rankings")

    ranking = df.copy()

    ranking["Rank"] = (
        ranking["composite_quality_score"]
        .rank(
            ascending=False,
            method="dense"
        )
        .astype(int)
    )

    ranking = ranking.sort_values("Rank")

    display_columns = [

        "Rank",

        "company_id",

        "company_name",

        "is_benchmark",

        "return_on_equity_pct",

        "return_on_capital_employed_pct",

        "net_profit_margin_pct",

        "debt_to_equity",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "composite_quality_score"

    ]

    display_columns = [

        c for c in display_columns

        if c in ranking.columns

    ]

    # Highlight benchmark company
    def highlight_benchmark(row):

        if row.get("is_benchmark", 0) == 1:

            return [

                "background-color:#145A32;color:white;font-weight:bold"

            ] * len(row)

        return [""] * len(row)

    st.dataframe(

        ranking[display_columns]
        .style.apply(
            highlight_benchmark,
            axis=1
        ),

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # TOP PERFORMER
    # ======================================================

    st.subheader("🥇 Top Performer")

    best = ranking.iloc[0]

    left, right = st.columns([2, 1])

    with left:

        st.success(

            f"""
    ### {best.get('company_name', best['company_id'])}

    **Ticker:** {best['company_id']}

    **Composite Score:** {safe_metric(best['composite_quality_score'])}

    **ROE:** {safe_metric(best['return_on_equity_pct'], "%")}

    **Revenue CAGR:** {safe_metric(best['revenue_cagr_5yr'], "%")}
    """

        )

    with right:

        st.metric(

            "Rank",

            int(best["Rank"])

        )

    st.divider()

    # ======================================================
    # PEER STATISTICS
    # ======================================================

    st.subheader("📊 Peer Group Statistics")

    stats = pd.DataFrame({

        "Metric":[

            "Companies",

            "Average ROE",

            "Average ROCE",

            "Average Margin",

            "Average Debt",

            "Average Revenue CAGR",

            "Average PAT CAGR",

            "Average Quality Score"

        ],

        "Value":[

            len(df),

            round(df["return_on_equity_pct"].mean(),2),

            round(df["return_on_capital_employed_pct"].mean(),2),

            round(df["net_profit_margin_pct"].mean(),2),

            round(df["debt_to_equity"].mean(),2),

            round(df["revenue_cagr_5yr"].mean(),2),

            round(df["pat_cagr_5yr"].mean(),2),

            round(df["composite_quality_score"].mean(),2)

        ]

    })

    st.dataframe(

        stats,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # DOWNLOAD CSV
    # ======================================================

    st.subheader("📥 Export Peer Comparison")

    csv = ranking.to_csv(index=False).encode("utf-8")

    st.download_button(

        "📄 Download Peer Comparison",

        data=csv,

        file_name=f"{peer_group}_peer_comparison.csv",

        mime="text/csv",

        use_container_width=True

    )

    st.divider()

    # ======================================================
    # INSIGHTS
    # ======================================================

    st.subheader("💡 Key Insights")

    peer_rank = int(
        ranking.loc[
            ranking["company_id"] == ticker,
            "Rank"
        ].iloc[0]
    )

    if peer_rank == 1:

        st.success(
            f"🏆 {ticker} is the highest-ranked company in the {peer_group} peer group."
        )

    elif peer_rank <= 3:

        st.info(
            f"⭐ {ticker} ranks among the top 3 companies in the peer group."
        )

    else:

        st.warning(
            f"📊 {ticker} is ranked #{peer_rank} in the peer group."
        )

    st.divider()

    # ======================================================
    # FINANCIAL SCORECARD
    # ======================================================

    st.subheader("📈 Financial Scorecard")

    scorecard = pd.DataFrame({

        "Metric":[
            "ROE",
            "ROCE",
            "Net Profit Margin",
            "Debt/Equity",
            "Revenue CAGR",
            "PAT CAGR",
            "Free Cash Flow",
            "Quality Score"
        ],

        "Company":[
            company["return_on_equity_pct"],
            company["return_on_capital_employed_pct"],
            company["net_profit_margin_pct"],
            company["debt_to_equity"],
            company["revenue_cagr_5yr"],
            company["pat_cagr_5yr"],
            company["free_cash_flow_cr"],
            company["composite_quality_score"]
        ],

        "Peer Average":[
            peer_avg["return_on_equity_pct"],
            peer_avg["return_on_capital_employed_pct"],
            peer_avg["net_profit_margin_pct"],
            peer_avg["debt_to_equity"],
            peer_avg["revenue_cagr_5yr"],
            peer_avg["pat_cagr_5yr"],
            peer_avg["free_cash_flow_cr"],
            peer_avg["composite_quality_score"]
        ]

    })

    scorecard["Difference"] = (
        scorecard["Company"] -
        scorecard["Peer Average"]
    ).round(2)

    st.dataframe(
        scorecard,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ======================================================
    # PERFORMANCE ANALYSIS
    # ======================================================

    st.subheader("🎯 Performance Analysis")

    better_metrics = scorecard[
        scorecard["Difference"] > 0
    ]["Metric"].tolist()

    weaker_metrics = scorecard[
        scorecard["Difference"] < 0
    ]["Metric"].tolist()

    left, right = st.columns(2)

    with left:

        st.success("Strengths")

        if better_metrics:

            for metric in better_metrics:
                st.markdown(f"✅ {metric}")

        else:
            st.info("No metrics above peer average.")

    with right:

        st.error("Needs Improvement")

        if weaker_metrics:

            for metric in weaker_metrics:
                st.markdown(f"⚠️ {metric}")

        else:
            st.info("No weak metrics identified.")

    st.divider()

    # ======================================================
    # PEER DISTRIBUTION
    # ======================================================

    st.subheader("📊 Peer Quality Distribution")

    fig = px.histogram(

        df,

        x="composite_quality_score",

        nbins=15,

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

    st.divider()

    # ======================================================
    # PEER SECTOR BREAKDOWN
    # ======================================================

    if "broad_sector" in df.columns:

        st.subheader("🏢 Sector Composition")

        sector_summary = (

            df.groupby("broad_sector")
            .size()
            .reset_index(name="Companies")

        )

        fig = px.pie(

            sector_summary,

            names="broad_sector",

            values="Companies",

            hole=0.45,

            title="Peer Sector Distribution"

        )

        fig.update_layout(height=450)

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    st.divider()

    # ======================================================
    # PAGE PERFORMANCE
    # ======================================================

    elapsed = time.time() - start

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Peer Companies",
        len(df)
    )

    c2.metric(
        "Selected Rank",
        peer_rank
    )

    c3.metric(
        "Load Time",
        f"{elapsed:.2f}s"
    )

    st.divider()

    # ======================================================
    # PAGE FOOTER
    # ======================================================

    st.caption(
        "🤝 Nifty100 Financial Intelligence Dashboard • Peer Comparison"
    )

render_footer()