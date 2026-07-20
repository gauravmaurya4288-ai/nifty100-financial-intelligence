import time
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_annual_reports
from components.styles import load_css

load_css()

# ==========================================================
# HELPER
# ==========================================================

def safe_metric(value):

    if pd.isna(value):
        return "N/A"

    return value


# ==========================================================
# PAGE
# ==========================================================

def render():

    start = time.time()

    st.title("📄 Annual Reports")

    st.caption(
        "View and download annual reports of Nifty100 companies."
    )

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    with st.spinner("Loading annual reports..."):

        df = get_annual_reports()

    if df.empty:

        st.warning("No annual report data available.")

        return

    df = df.copy()

    df["status"] = (

        df["status"]

        .fillna("Unavailable")

        .astype(str)

        .str.strip()

    )

    df["company_name"] = (

        df["company_name"]

        .fillna(df["company_id"])

    )

    # ------------------------------------------------------
    # COMPANY SELECTOR
    # ------------------------------------------------------

    companies = sorted(

        df["company_id"]

        .dropna()

        .unique()

    )

    ticker = st.selectbox(

        "Select Company",

        companies,

        key="reports_company"

    )

    reports = (

        df[df["company_id"] == ticker]

        .sort_values(

            "year",

            ascending=False

        )

        .reset_index(drop=True)

    )

    if reports.empty:

        st.warning("No reports available.")

        return

    company_name = reports.iloc[0]["company_name"]

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    st.divider()

    st.subheader(company_name)

    st.caption(f"Company ID: {ticker}")

    st.divider()

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    available = (

        reports["status"]

        .eq("Available")

        .sum()

    )

    unavailable = (

        reports["status"]

        .eq("Unavailable")

        .sum()

    )

    latest_year = reports["year"].max()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(

        "Available Years",

        len(reports)

    )

    c2.metric(

        "Reports Available",

        int(available)

    )

    c3.metric(

        "Reports Missing",

        int(unavailable)

    )

    c4.metric(

        "Latest Report",

        latest_year

    )

    st.divider()

    # ------------------------------------------------------
    # REPORT OVERVIEW
    # ------------------------------------------------------

    st.subheader("📊 Report Overview")

    left, right = st.columns([2,1])

    with left:

        st.info(f"""

**Company:** {company_name}

**Reports Available:** {available}

**Reports Missing:** {unavailable}

**Coverage:** {(available/len(reports))*100:.1f}%

""")

    with right:

        st.metric(

            "Coverage",

            f"{(available/len(reports))*100:.1f}%"

        )

    st.divider()

        # ==========================================================
    # REPORT AVAILABILITY TIMELINE
    # ==========================================================

    st.subheader("📈 Report Availability Timeline")

    timeline = reports.copy()

    timeline["Available"] = timeline["status"].apply(
        lambda x: 1 if x == "Available" else 0
    )

    fig = px.line(

        timeline,

        x="year",

        y="Available",

        markers=True,

        text="status",

        title="Annual Report Availability"

    )

    fig.update_traces(

        line=dict(width=4),

        marker=dict(size=10),

        textposition="top center"

    )

    fig.update_layout(

        height=450,

        yaxis=dict(

            tickmode="array",

            tickvals=[0,1],

            ticktext=["Unavailable","Available"]

        ),

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
    # STATUS DISTRIBUTION
    # ==========================================================

    st.subheader("🥧 Report Status Distribution")

    status_summary = (

        reports

        .groupby("status")

        .size()

        .reset_index(name="Count")

    )

    fig = px.pie(

        status_summary,

        names="status",

        values="Count",

        hole=0.45,

        title="Available vs Missing Reports"

    )

    fig.update_layout(

        height=450

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    # ==========================================================
    # YEAR-WISE STATUS
    # ==========================================================

    st.subheader("📊 Year-wise Report Status")

    status_bar = reports.copy()

    status_bar["Available"] = status_bar["status"].apply(

        lambda x: 1 if x == "Available" else 0

    )

    fig = px.bar(

        status_bar,

        x="year",

        y="Available",

        color="status",

        text="status",

        title="Annual Report Status"

    )

    fig.update_traces(

        textposition="outside"

    )

    fig.update_layout(

        height=450,

        yaxis=dict(

            tickmode="array",

            tickvals=[0,1],

            ticktext=["Unavailable","Available"]

        ),

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
    # REPORT HISTORY
    # ==========================================================

    st.subheader("📋 Report History")

    history = reports.copy()

    history["Status"] = history["status"].apply(

        lambda x:

        "✅ Available"

        if x == "Available"

        else "❌ Unavailable"

    )

    st.dataframe(

        history[

            [

                "year",

                "Status"

            ]

        ],

        use_container_width=True,

        hide_index=True

    )

    st.divider()

        # ==========================================================
    # LATEST REPORT
    # ==========================================================

    st.subheader("🥇 Latest Available Report")

    available_reports = reports[
        reports["status"] == "Available"
    ]

    if not available_reports.empty:

        latest = available_reports.iloc[0]

        left, right = st.columns([3, 1])

        with left:

            st.success(f"""
### {company_name}

**Latest Report Year:** {latest['year']}

**Status:** {latest['status']}
""")

            if (
                pd.notna(latest["report_url"])
                and str(latest["report_url"]).strip() != ""
            ):

                st.link_button(

                    "📥 Open Latest Annual Report",

                    latest["report_url"]

                )

        with right:

            st.metric(

                "Latest Year",

                latest["year"]

            )

    else:

        st.warning("No annual reports are available.")

    st.divider()

    # ==========================================================
    # REPORT LINKS
    # ==========================================================

    st.subheader("📚 Annual Report Library")

    for _, row in reports.iterrows():

        col1, col2, col3 = st.columns([1, 2, 2])

        with col1:

            st.write(f"**{row['year']}**")

        with col2:

            if row["status"] == "Available":

                st.success("Available")

            else:

                st.error("Unavailable")

        with col3:

            if (

                row["status"] == "Available"

                and pd.notna(row["report_url"])

                and str(row["report_url"]).strip() != ""

            ):

                st.link_button(

                    "📄 Open Report",

                    row["report_url"],

                    key=f"report_{row['year']}"

                )

            else:

                st.caption("-")

    st.divider()

    # ==========================================================
    # REPORT STATISTICS
    # ==========================================================

    st.subheader("📊 Report Statistics")

    statistics = pd.DataFrame({

        "Metric": [

            "Total Reports",

            "Available Reports",

            "Unavailable Reports",

            "Coverage (%)"

        ],

        "Value": [

            len(reports),

            available,

            unavailable,

            round((available / len(reports)) * 100, 2)

        ]

    })

    st.dataframe(

        statistics,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ==========================================================
    # REPORT INSIGHTS
    # ==========================================================

    st.subheader("💡 Insights")

    insights = []

    if available == len(reports):

        insights.append("Complete report history is available.")

    elif available >= len(reports) * 0.75:

        insights.append("Most annual reports are available.")

    else:

        insights.append("Several annual reports are missing.")

    if latest_year == reports["year"].max():

        insights.append("Latest financial year is covered.")

    if unavailable > 0:

        insights.append(
            f"{unavailable} report(s) are unavailable."
        )

    for insight in insights:

        st.info(insight)

    st.divider()

    # ==========================================================
    # MISSING REPORTS
    # ==========================================================

    missing = reports[
        reports["status"] != "Available"
    ]

    if not missing.empty:

        st.subheader("⚠ Missing Reports")

        st.dataframe(

            missing[

                [

                    "year",

                    "status"

                ]

            ],

            use_container_width=True,

            hide_index=True

        )

        st.divider()

            # ==========================================================
    # EXPORT REPORT INDEX
    # ==========================================================

    st.subheader("📥 Export Report Index")

    csv = reports.to_csv(index=False).encode("utf-8")

    st.download_button(

        label="📄 Download Report Index",

        data=csv,

        file_name=f"{ticker}_annual_reports.csv",

        mime="text/csv",

        use_container_width=True

    )

    st.divider()

    # ==========================================================
    # REPORT AVAILABILITY SCORE
    # ==========================================================

    st.subheader("🏆 Report Availability Score")

    coverage = (available / len(reports)) * 100

    score = 0

    if coverage == 100:
        score = 100
    elif coverage >= 90:
        score = 90
    elif coverage >= 75:
        score = 75
    elif coverage >= 50:
        score = 50
    else:
        score = 25

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

        "Availability Score",

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

            "Company",

            "Company ID",

            "Latest Report",

            "Available Reports",

            "Missing Reports",

            "Coverage (%)"

        ],

        "Value":[

            company_name,

            ticker,

            latest_year,

            available,

            unavailable,

            round(coverage,2)

        ]

    })

    st.dataframe(

        summary,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ==========================================================
    # QUICK STATUS
    # ==========================================================

    st.subheader("📌 Report Status")

    if coverage == 100:

        st.success("✅ Complete annual report history available.")

    elif coverage >= 75:

        st.info("📘 Most annual reports are available.")

    elif coverage >= 50:

        st.warning("⚠ Some annual reports are missing.")

    else:

        st.error("❌ Report history is largely incomplete.")

    st.divider()

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    elapsed = time.time() - start

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "Years",

        len(reports)

    )

    c2.metric(

        "Coverage",

        f"{coverage:.1f}%"

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
        "📄 Nifty100 Financial Intelligence Dashboard • Annual Reports"
    )