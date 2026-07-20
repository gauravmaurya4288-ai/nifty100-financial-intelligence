import streamlit as st


def load_css():

    st.markdown(
        """
<style>

/* ================================
   Main App
================================ */

.stApp{
    background:#0f172a;
    color:white;
}

/* ================================
Sidebar
================================ */

section[data-testid="stSidebar"]{

    background:#111827;
    border-right:1px solid #1f2937;
}

/* ================================
Titles
================================ */

h1{
    color:#60a5fa;
    font-weight:800;
}

h2{
    color:white;
}

h3{
    color:#e2e8f0;
}

/* ================================
Metric Cards
================================ */

div[data-testid="metric-container"]{

    background:#1e293b;

    border-radius:14px;

    padding:18px;

    border:1px solid #334155;

    box-shadow:0 6px 18px rgba(0,0,0,.25);
}

/* ================================
Buttons
================================ */

.stButton>button{

    width:100%;

    border-radius:12px;

    height:48px;

    border:none;

    background:#2563eb;

    color:white;

    font-weight:600;
}

.stButton>button:hover{

    background:#1d4ed8;
}

/* ================================
Dataframes
================================ */

[data-testid="stDataFrame"]{

    border-radius:14px;

    overflow:hidden;
}

/* ================================
Charts
================================ */

.js-plotly-plot{

    border-radius:16px;

}

/* ================================
Footer
================================ */

.footer{

    text-align:center;

    color:#94a3b8;

    padding:20px;

    margin-top:40px;

    border-top:1px solid #334155;

}

</style>

""",
        unsafe_allow_html=True,
    )