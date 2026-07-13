import streamlit as st

def render():

    st.title("🏢 Company Profile")

    ticker = st.text_input("Search Company")

    st.info("Company Profile screen will be developed on Day 23.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.empty()

    with col2:
        st.empty()