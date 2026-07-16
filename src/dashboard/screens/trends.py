import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils.db import (
    get_companies,
    get_company_history
)

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

    st.title("📈 Trend Analysis")

    st.caption(
        "Analyze long-term financial trends for every Nifty100 company."
    )

    # ======================================================
    # LOAD DATA
    # ======================================================

    with st.spinner("Loading company data..."):

        companies = get_companies()

    if companies.empty:

        st.warning("Company master not available.")

        return

    # ======================================================
    # COMPANY SELECTION
    # ======================================================

    ticker = st.selectbox(

        "Select Company",

        sorted(
            companies["company_id"]
            .dropna()
            .unique()
        ),

        key="trend_company"

    )

    with st.spinner("Loading financial history..."):

        history = get_company_history(ticker)

    if history.empty:

        st.warning("Historical financial data unavailable.")

        return

    history = history.copy()

    history = history.sort_values("year")

    # ======================================================
    # NUMERIC CONVERSION
    # ======================================================

    numeric_columns = [

        "return_on_equity_pct",

        "return_on_capital_employed_pct",

        "net_profit_margin_pct",

        "operating_profit_margin_pct",

        "debt_to_equity",

        "interest_coverage",

        "revenue_cagr_5yr",

        "pat_cagr_5yr",

        "composite_quality_score"

    ]

    for col in numeric_columns:

        if col in history.columns:

            history[col] = pd.to_numeric(

                history[col],

                errors="coerce"

            )

    latest = history.iloc[-1]

    company = companies[
        companies["company_id"] == ticker
    ]

    if not company.empty:

        company = company.iloc[0]

    # ======================================================
    # COMPANY CARD
    # ======================================================

    st.divider()

    left, right = st.columns([1,4])

    with left:

        logo = company.get("company_logo")

        if pd.notna(logo):

            st.image(
                logo,
                width=120
            )

    with right:

        st.subheader(

            company.get(
                "company_name",
                ticker
            )

        )

        st.write(f"**Ticker:** {ticker}")

        if "broad_sector" in company.index:

            st.write(
                f"**Sector:** {company['broad_sector']}"
            )

        if "market_cap_category" in company.index:

            st.write(
                f"**Market Cap:** {company['market_cap_category']}"
            )

    st.divider()

    # ======================================================
    # KPI CARDS
    # ======================================================

    st.subheader("📊 Latest Financial Snapshot")

    c1,c2,c3,c4 = st.columns(4)

    c5,c6,c7,c8 = st.columns(4)

    c1.metric(

        "ROE",

        safe_metric(
            latest["return_on_equity_pct"],
            "%"
        )

    )

    c2.metric(

        "ROCE",

        safe_metric(
            latest["return_on_capital_employed_pct"],
            "%"
        )

    )

    c3.metric(

        "Net Margin",

        safe_metric(
            latest["net_profit_margin_pct"],
            "%"
        )

    )

    c4.metric(

        "Operating Margin",

        safe_metric(
            latest["operating_profit_margin_pct"],
            "%"
        )

    )

    c5.metric(

        "Debt / Equity",

        safe_metric(
            latest["debt_to_equity"]
        )

    )

    c6.metric(

        "Interest Coverage",

        safe_metric(
            latest["interest_coverage"]
        )

    )

    c7.metric(

        "Revenue CAGR",

        safe_metric(
            latest["revenue_cagr_5yr"],
            "%"
        )

    )

    c8.metric(

        "Quality Score",

        safe_metric(
            latest["composite_quality_score"]
        )

    )

    st.divider()

    # ======================================================
    # METRIC SELECTOR
    # ======================================================

    metric_options = {

        "ROE":"return_on_equity_pct",

        "ROCE":"return_on_capital_employed_pct",

        "Net Margin":"net_profit_margin_pct",

        "Operating Margin":"operating_profit_margin_pct",

        "Debt / Equity":"debt_to_equity",

        "Interest Coverage":"interest_coverage",

        "Revenue CAGR":"revenue_cagr_5yr",

        "PAT CAGR":"pat_cagr_5yr",

        "Quality Score":"composite_quality_score"

    }

    selected_metrics = st.multiselect(

        "Select up to 3 metrics",

        list(metric_options.keys()),

        default=["ROE"],

        max_selections=3,

        key="trend_metrics"

    )

    if len(selected_metrics) == 0:

        st.info("Please select at least one metric.")

        return

    st.divider()

    # ======================================================
    # FINANCIAL TREND CHART
    # ======================================================

    st.subheader("📈 Financial Trend Analysis")

    fig = go.Figure()

    colors = [

        "#4CAF50",
        "#2196F3",
        "#FF9800"

    ]

    for i, metric in enumerate(selected_metrics):

        column = metric_options[metric]

        temp = history.copy()

        temp["YoY"] = temp[column].pct_change() * 100

        hover = []

        for _, row in temp.iterrows():

            if pd.isna(row["YoY"]):

                hover.append(
                    f"{metric}: {row[column]:.2f}"
                )

            else:

                hover.append(

                    f"{metric}: {row[column]:.2f}"
                    f"<br>YoY: {row['YoY']:.2f}%"

                )

        fig.add_trace(

            go.Scatter(

                x=temp["year"],

                y=temp[column],

                mode="lines+markers+text",

                name=metric,

                line=dict(

                    width=3,

                    color=colors[i % len(colors)]

                ),

                marker=dict(

                    size=8

                ),

                text=[

                    "" if pd.isna(v)

                    else f"{v:.1f}%"

                    for v in temp["YoY"]

                ],

                textposition="top center",

                hovertext=hover,

                hoverinfo="text"

            )

        )

    fig.update_layout(

        title=f"{ticker} Financial Performance",

        height=650,

        hovermode="x unified",

        legend_title="Metrics",

        margin=dict(

            l=20,

            r=20,

            t=60,

            b=20

        ),

        xaxis_title="Financial Year",

        yaxis_title="Value",

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    # ======================================================
    # LATEST METRIC COMPARISON
    # ======================================================

    st.subheader("📊 Latest Metric Comparison")

    comparison = []

    for metric in selected_metrics:

        col = metric_options[metric]

        comparison.append({

            "Metric": metric,

            "Latest": latest[col],

            "Average": history[col].mean(),

            "Highest": history[col].max(),

            "Lowest": history[col].min()

        })

    comparison = pd.DataFrame(comparison)

    st.dataframe(

        comparison.round(2),

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # TREND SUMMARY
    # ======================================================

    st.subheader("📌 Trend Summary")

    summary_cols = st.columns(len(selected_metrics))

    for idx, metric in enumerate(selected_metrics):

        col = metric_options[metric]

        first = history[col].iloc[0]

        last = history[col].iloc[-1]

        if pd.notna(first) and first != 0:

            change = ((last - first) / abs(first)) * 100

        else:

            change = 0

        summary_cols[idx].metric(

            metric,

            safe_metric(last),

            delta=f"{change:.2f}%"

        )

    st.divider()

    # ======================================================
    # YEAR OVER YEAR ANALYSIS
    # ======================================================

    st.subheader("📈 Year-over-Year Growth")

    growth = history.copy()

    for metric in selected_metrics:

        column = metric_options[metric]

        growth[f"{metric} YoY %"] = (
            growth[column].pct_change() * 100
        )

    display_cols = ["year"]

    for metric in selected_metrics:

        display_cols.append(metric_options[metric])
        display_cols.append(f"{metric} YoY %")

    available = [

        c for c in display_cols

        if c in growth.columns

    ]

    st.dataframe(

        growth[available].round(2),

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # DESCRIPTIVE STATISTICS
    # ======================================================

    st.subheader("📊 Statistical Summary")

    stats = []

    for metric in selected_metrics:

        column = metric_options[metric]

        stats.append({

            "Metric": metric,

            "Average": history[column].mean(),

            "Median": history[column].median(),

            "Maximum": history[column].max(),

            "Minimum": history[column].min(),

            "Std Dev": history[column].std()

        })

    stats = pd.DataFrame(stats)

    st.dataframe(

        stats.round(2),

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # PERFORMANCE SCORECARD
    # ======================================================

    st.subheader("🏆 Performance Scorecard")

    scorecard = []

    for metric in selected_metrics:

        column = metric_options[metric]

        first = history[column].iloc[0]

        latest_value = history[column].iloc[-1]

        if pd.notna(first) and first != 0:

            overall_growth = (
                (latest_value - first)
                /
                abs(first)
            ) * 100

        else:

            overall_growth = 0

        trend = "Improving"

        if overall_growth < 0:

            trend = "Declining"

        scorecard.append({

            "Metric": metric,

            "Latest": latest_value,

            "Overall Growth %": overall_growth,

            "Trend": trend

        })

    scorecard = pd.DataFrame(scorecard)

    st.dataframe(

        scorecard.round(2),

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # BEST & WEAKEST METRIC
    # ======================================================

    st.subheader("⭐ Key Insights")

    best_metric = scorecard.loc[
        scorecard["Overall Growth %"].idxmax()
    ]

    worst_metric = scorecard.loc[
        scorecard["Overall Growth %"].idxmin()
    ]

    left, right = st.columns(2)

    with left:

        st.success(

            f"""
    ### 🚀 Strongest Trend

    **Metric:** {best_metric['Metric']}

    **Growth:** {best_metric['Overall Growth %']:.2f}%
    """

        )

    with right:

        st.warning(

            f"""
    ### 📉 Weakest Trend

    **Metric:** {worst_metric['Metric']}

    **Growth:** {worst_metric['Overall Growth %']:.2f}%
    """

        )

    st.divider()

    # ======================================================
    # COMPLETE FINANCIAL HISTORY
    # ======================================================

    st.subheader("📋 Complete Financial History")

    history_display = history.copy()

    history_display = history_display.round(2)

    st.dataframe(

        history_display,

        use_container_width=True,

        hide_index=True,

        height=450

    )

    st.divider()

    # ======================================================
    # DOWNLOAD TREND DATA
    # ======================================================

    st.subheader("📥 Export Trend Analysis")

    csv = history.to_csv(index=False).encode("utf-8")

    st.download_button(

        label="📄 Download Trend Analysis",

        data=csv,

        file_name=f"{ticker}_trend_analysis.csv",

        mime="text/csv",

        use_container_width=True

    )

    st.divider()

    # ======================================================
    # COMPANY PERFORMANCE SUMMARY
    # ======================================================

    st.subheader("📌 Performance Summary")

    summary = pd.DataFrame({

        "Metric":[

            "Company",

            "Financial Years",

            "Latest Year",

            "Earliest Year",

            "Average ROE",

            "Average ROCE",

            "Average Net Margin",

            "Average Quality Score"

        ],

        "Value":[

            company.get("company_name", ticker),

            len(history),

            history.iloc[-1]["year"],

            history.iloc[0]["year"],

            round(history["return_on_equity_pct"].mean(),2),

            round(history["return_on_capital_employed_pct"].mean(),2),

            round(history["net_profit_margin_pct"].mean(),2),

            round(history["composite_quality_score"].mean(),2)

        ]

    })

    st.dataframe(

        summary,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ======================================================
    # OVERALL INSIGHTS
    # ======================================================

    st.subheader("💡 Trend Insights")

    positive = []
    negative = []

    if latest["return_on_equity_pct"] >= history["return_on_equity_pct"].mean():
        positive.append("ROE is above the long-term average.")
    else:
        negative.append("ROE is below the long-term average.")

    if latest["return_on_capital_employed_pct"] >= history["return_on_capital_employed_pct"].mean():
        positive.append("ROCE is improving.")

    if latest["debt_to_equity"] <= history["debt_to_equity"].mean():
        positive.append("Debt levels are well controlled.")
    else:
        negative.append("Debt has increased over time.")

    if latest["revenue_cagr_5yr"] >= 15:
        positive.append("Strong long-term revenue growth.")

    if latest["pat_cagr_5yr"] >= 15:
        positive.append("Strong profit growth.")

    if latest["interest_coverage"] < 2:
        negative.append("Low interest coverage.")

    if latest["net_profit_margin_pct"] < 5:
        negative.append("Profit margins are relatively low.")

    left, right = st.columns(2)

    with left:

        st.success("Strengths")

        if positive:

            for item in positive:

                st.markdown(f"✅ {item}")

        else:

            st.info("No major strengths identified.")

    with right:

        st.error("Areas to Watch")

        if negative:

            for item in negative:

                st.markdown(f"⚠️ {item}")

        else:

            st.info("No major concerns identified.")

    st.divider()

    # ======================================================
    # TREND HEALTH SCORE
    # ======================================================

    st.subheader("🏆 Trend Health Score")

    score = 0

    if latest["return_on_equity_pct"] >= 20:
        score += 20

    if latest["return_on_capital_employed_pct"] >= 20:
        score += 20

    if latest["revenue_cagr_5yr"] >= 15:
        score += 20

    if latest["pat_cagr_5yr"] >= 15:
        score += 20

    if latest["debt_to_equity"] <= 0.5:
        score += 20

    grade = "D"

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

    c1, c2 = st.columns(2)

    c1.metric(

        "Trend Score",

        f"{score}/100"

    )

    c2.metric(

        "Overall Grade",

        grade

    )

    st.divider()

    # ======================================================
    # PAGE PERFORMANCE
    # ======================================================

    elapsed = time.time() - start

    a, b, c = st.columns(3)

    a.metric(

        "Years Analysed",

        len(history)

    )

    b.metric(

        "Metrics Selected",

        len(selected_metrics)

    )

    c.metric(

        "Load Time",

        f"{elapsed:.2f}s"

    )

    st.divider()

    # ======================================================
    # FOOTER
    # ======================================================

    st.caption(

        "📈 Nifty100 Financial Intelligence Dashboard • Trend Analysis"

    )