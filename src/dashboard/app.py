from pathlib import Path
import sys
import streamlit as st

# ==========================================================
# PROJECT PATH
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Nifty100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* Reduce page padding */
.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

/* Metric Card */
div[data-testid="stMetric"]{
    background-color:#1f2937;
    border:1px solid #374151;
    border-radius:12px;
    padding:16px;
}

/* Metric Label */
div[data-testid="stMetricLabel"]{
    font-size:15px;
    font-weight:600;
}

/* Metric Value */
div[data-testid="stMetricValue"]{
    font-size:32px;
    font-weight:bold;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    border-right:1px solid #2d3748;
}

footer{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# IMPORT PAGES
# ==========================================================

try:

    from screens import (
        home,
        profile,
        screener,
        peers,
        trends,
        sectors,
        capital,
        reports,
    )

except Exception as e:

    st.error(f"Error importing dashboard pages:\n\n{e}")
    st.stop()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("📈 Nifty100 Analytics")

page = st.sidebar.radio(

    "Navigation",

    [
        "🏠 Home",
        "🏢 Company Profile",
        "🔍 Screener",
        "🤝 Peer Comparison",
        "📈 Trend Analysis",
        "🏭 Sector Analysis",
        "💰 Capital Allocation",
        "📄 Annual Reports",
    ],

    key="main_navigation",

)

st.sidebar.divider()

st.sidebar.success("Sprint 4 Dashboard")

st.sidebar.caption("Version 1.0")

# ==========================================================
# PAGE ROUTER
# ==========================================================

PAGES = {

    "🏠 Home": home,
    "🏢 Company Profile": profile,
    "🔍 Screener": screener,
    "🤝 Peer Comparison": peers,
    "📈 Trend Analysis": trends,
    "🏭 Sector Analysis": sectors,
    "💰 Capital Allocation": capital,
    "📄 Annual Reports": reports,

}

try:

    PAGES[page].render()

except Exception as e:

    st.exception(e)

