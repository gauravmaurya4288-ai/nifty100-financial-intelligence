import streamlit as st
from datetime import datetime


def render_footer():

    current_year = datetime.now().year

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <hr style="margin-top:40px;border:1px solid #334155;">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            color:#94A3B8;
            font-size:14px;
            padding:10px 0;
            flex-wrap:wrap;
        ">

            <div>
                📊 <b>Nifty100 Financial Intelligence</b><br>
                Professional Equity Analytics Platform
            </div>

            <div style="text-align:right;">

                Version 2.0<br>

                © {current_year} Gaurav Maurya

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )