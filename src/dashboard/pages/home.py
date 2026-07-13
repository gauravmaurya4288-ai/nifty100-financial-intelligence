import streamlit as st

def render():

    st.title("🏠 Home Dashboard")

    st.markdown("### Nifty100 Financial Intelligence Dashboard")

    st.info("This page will display portfolio KPIs, sector overview and top companies.")

    col1, col2, col3 = st.columns(3)

    col1.metric("Companies", "--")
    col2.metric("Average ROE", "--")
    col3.metric("Median P/E", "--")

    st.divider()

    st.subheader("Sector Overview")
    st.empty()

    st.subheader("Top Companies")
    st.empty()