from pathlib import Path
import sys
import streamlit as st

# ==========================================================
# PROJECT PATH
# ==========================================================

CURRENT_DIR = Path(__file__).parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# IMPORT PAGES
# ==========================================================

try:
    from pages import (
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
        "📊 Trend Analysis",
        "🏭 Sector Analysis",
        "💰 Capital Allocation",
        "📄 Annual Reports",
    ],
)

st.sidebar.markdown("---")
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
    "📊 Trend Analysis": trends,
    "🏭 Sector Analysis": sectors,
    "💰 Capital Allocation": capital,
    "📄 Annual Reports": reports,
}

try:

    PAGES[page].render()

except Exception as e:

    st.exception(e)

# ==========================================================
# LOAD PAGE
# ==========================================================

selected_page = PAGES[page]

if hasattr(selected_page, "render"):
    selected_page.render()
else:
    st.error(
        f"{selected_page.__name__} does not contain a render() function."
    )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Sprint", "4")

with col2:
    st.metric("Dashboard Screens", "8")

with col3:
    st.metric("Database", "SQLite")

st.divider()

st.caption(
    "Nifty100 Financial Intelligence Platform | Sprint 4 | Day 22"
)