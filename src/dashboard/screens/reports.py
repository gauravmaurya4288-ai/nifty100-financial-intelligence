import streamlit as st
import pandas as pd

from utils.db import get_annual_reports


def render():

    st.title("📄 Annual Reports")

    df = get_annual_reports()

    if df.empty:
        st.warning("No annual report data available.")
        return

    # ==========================================
    # Company Selector
    # ==========================================

    companies = sorted(df["company_id"].dropna().unique())

    ticker = st.selectbox(
        "Select Company",
        companies,
        key="reports_company"
    )

    reports = (
        df[df["company_id"] == ticker]
        .sort_values("year", ascending=False)
        .reset_index(drop=True)
    )

    company_name = reports.iloc[0]["company_name"]

    # ==========================================
    # Header
    # ==========================================

    st.subheader(company_name)

    c1, c2 = st.columns(2)

    c1.metric(
        "Available Years",
        len(reports)
    )

    available = reports["status"].eq("Available").sum()

    c2.metric(
        "Reports Available",
        int(available)
    )

    st.divider()

    # ==========================================
    # Reports Table
    # ==========================================

    st.subheader("Report History")

    display = reports.copy()

    display["Status"] = display["status"].apply(
        lambda x: "✅ Available"
        if x == "Available"
        else "❌ Unavailable"
    )

    st.dataframe(

        display[
            [
                "year",
                "Status"
            ]
        ],

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # ==========================================
    # Links
    # ==========================================

    st.subheader("Open Reports")

    for _, row in reports.iterrows():

        year = row["year"]

        url = row["report_url"]

        status = row["status"]

        col1, col2 = st.columns([1,3])

        with col1:

            st.write(f"**{year}**")

        with col2:

            if status == "Available" and str(url).strip() != "":

                st.link_button(
                    "📥 Open Annual Report",
                    url
                )

            else:

                st.error("Report Unavailable")

    st.divider()

    # ==========================================
    # Download
    # ==========================================

    csv = reports.to_csv(index=False)

    st.download_button(

        "📥 Download Report Index",

        csv,

        file_name=f"{ticker}_annual_reports.csv",

        mime="text/csv"

    )

    st.success("Annual Reports Module Ready")