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
    page_title="Nifty100 Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
<style>

/* Main Layout */
.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

/* Metric Cards */
div[data-testid="stMetric"]{
    background:#1f2937;
    border:1px solid #374151;
    border-radius:12px;
    padding:16px;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    border-right:1px solid #374151;
}

/* Hide Footer */
footer{
    visibility:hidden;
}

</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# IMPORT SCREENS
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
        rankings,
        portfolio,
    )

except Exception as e:

    st.error(f"Failed to import dashboard pages.\n\n{e}")
    st.stop()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.image(
    "https://img.icons8.com/color/96/stocks-growth.png",
    width=70,
)

st.sidebar.title("Nifty100")

st.sidebar.caption("Financial Intelligence Dashboard")

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
        "🏆 Rankings",
        "💼 Portfolio Simulator",
    ],
)

st.sidebar.divider()

st.sidebar.success("Sprint 4")

st.sidebar.info("Version 2.0")

# ==========================================================
# PAGE REGISTRY
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

    "🏆 Rankings": rankings,

    "💼 Portfolio Simulator": portfolio,

}

# ==========================================================
# ROUTER
# ==========================================================

try:

    selected_page = PAGES.get(page)

    if selected_page is None:
        st.error("Page not found.")
    else:
        selected_page.render()

except Exception as e:

    st.exception(e)