from pathlib import Path
import sys
import sqlite3

import pandas as pd
import streamlit as st

# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



OUTPUT_DIR = PROJECT_ROOT / "output"
REPORT_DIR = PROJECT_ROOT / "reports"
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Nifty100 Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# GLOBAL CSS
# ==========================================================

st.markdown(
    """
<style>

/* -------------------------------
Main Container
--------------------------------*/
.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

/* -------------------------------
Metric Cards
--------------------------------*/
div[data-testid="stMetric"]{
    background:#111827;
    border:1px solid #374151;
    border-radius:12px;
    padding:16px;
}

/* -------------------------------
Sidebar
--------------------------------*/
section[data-testid="stSidebar"]{
    background:#0f172a;
    border-right:1px solid #374151;
}

/* -------------------------------
Buttons
--------------------------------*/
.stButton>button{
    width:100%;
    border-radius:10px;
}

/* -------------------------------
Tables
--------------------------------*/
[data-testid="stDataFrame"]{
    border-radius:12px;
}

/* -------------------------------
Hide Footer
--------------------------------*/
footer{
    visibility:hidden;
}

</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# CACHE FUNCTIONS
# ==========================================================

@st.cache_data(show_spinner=False)
def load_cluster_insights():

    file = OUTPUT_DIR / "cluster_insights.csv"

    if file.exists():
        return pd.read_csv(file)

    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_cluster_labels():

    file = OUTPUT_DIR / "cluster_labels.csv"

    if file.exists():
        return pd.read_csv(file)

    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_database_summary():

    if not DB_PATH.exists():
        return {
            "companies": 0,
            "sectors": 0,
            "connected": False,
        }

    conn = sqlite3.connect(DB_PATH)

    try:

        companies = pd.read_sql(
            "SELECT COUNT(*) AS total FROM companies",
            conn,
        )["total"][0]

        sectors = pd.read_sql(
            "SELECT COUNT(DISTINCT broad_sector) AS total FROM sectors",
            conn,
        )["total"][0]

    finally:
        conn.close()

    return {
        "companies": int(companies),
        "sectors": int(sectors),
        "connected": True,
    }


# ==========================================================
# LOAD APPLICATION DATA
# ==========================================================

cluster_insights = load_cluster_insights()

cluster_labels = load_cluster_labels()

db_summary = load_database_summary()

# ==========================================================
# GLOBAL VARIABLES
# ==========================================================

TOTAL_COMPANIES = db_summary["companies"]

TOTAL_SECTORS = db_summary["sectors"]

TOTAL_CLUSTERS = (
    cluster_insights["cluster_id"].nunique()
    if not cluster_insights.empty
    else 0
)

DATABASE_STATUS = (
    "Connected"
    if db_summary["connected"]
    else "Disconnected"
)

# ==========================================================
# IMPORT DASHBOARD SCREENS
# ==========================================================

try:

    from screens import (
        home,
        profile,
        clusters,
        trends,
        screener,
        sectors,
        peers,
        capital,
        rankings,
        portfolio,
        reports,
    )

except Exception as e:

    st.error("❌ Failed to load dashboard modules.")

    st.exception(e)

    st.stop()


# ==========================================================
# SIDEBAR HEADER
# ==========================================================

st.sidebar.markdown(
    """
    <div style="text-align:center;padding:10px;">
        <h2 style="color:#60A5FA;margin-bottom:0;">
            📊 Nifty100 
            Financial Intelligence Platform
        </h2>

        
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.divider()


# ==========================================================
# NAVIGATION
# ==========================================================

navigation = {

    "🏠 Home": home,

    "🏢 Company Profile": profile,

    "📊 Cluster Analytics": clusters,

    "📈 Trend Analysis": trends,

    "🔍 Stock Screener": screener,

    "🏭 Sector Analysis": sectors,

    "🤝 Peer Comparison": peers,

    "💰 Capital Allocation": capital,

    "🏆 Rankings": rankings,

    "💼 Portfolio": portfolio,

    "📄 Reports": reports,
}

page = st.sidebar.radio(

    "Navigation",

    list(navigation.keys()),
)

st.sidebar.divider()


# ==========================================================
# DATABASE STATUS
# ==========================================================

st.sidebar.subheader("📊 Database")

c1, c2 = st.sidebar.columns(2)

with c1:

    st.metric(

        "Companies",

        TOTAL_COMPANIES,

    )

with c2:

    st.metric(

        "Sectors",

        TOTAL_SECTORS,

    )




# ==========================================================
# PLATFORM STATUS
# ==========================================================

st.sidebar.divider()

st.sidebar.subheader("🚀 Platform")


st.sidebar.metric(

    "ML Model",

    "K-Means"

)

st.sidebar.metric(

    "Analytics",

    "Ready"

)




# ==========================================================
# QUICK SUMMARY
# ==========================================================

st.sidebar.divider()

if not cluster_insights.empty:

    best_cluster = cluster_insights.loc[
        cluster_insights["companies"].idxmax(),
        "cluster_name",
    ]

    st.sidebar.info(

        f"""
Largest Cluster

**{best_cluster}**

{cluster_insights['companies'].max()} Companies
"""
    )


# ==========================================================
# DEVELOPER PANEL
# ==========================================================

st.sidebar.divider()

st.sidebar.markdown(
"""
### 👨‍💻 Developer

**Gaurav Maurya**

B.Tech Computer Engineering

Nifty100 Financial Intelligence

© 2026
"""
)

# ==========================================================
# APPLICATION LOADER
# ==========================================================

@st.cache_resource
def initialize_platform():
    """
    Initialize platform resources.
    This runs only once per session.
    """
    return {
        "initialized": True,
        "database": DATABASE_STATUS,
        "version": "2.1",
    }


platform = initialize_platform()





# ==========================================================
# PAGE ROUTER
# ==========================================================

selected_page = navigation.get(page)

if selected_page is None:

    st.error("🚫 Requested page not found.")

else:

    with st.spinner("Loading dashboard..."):

        try:

            # Every screen must expose render()
            selected_page.render()

        except AttributeError:

            st.error(
                f"""
The page **{page}** does not contain a render() function.

Expected:

def render():
    ...
"""
            )

        except FileNotFoundError as e:

            st.error("Required project file is missing.")

            with st.expander("Details"):

                st.exception(e)

        except pd.errors.EmptyDataError:

            st.warning("One of the CSV files is empty.")

        except sqlite3.Error as e:

            st.error("Database error.")

            with st.expander("SQLite Error"):

                st.exception(e)

        except Exception as e:

            st.error("Unexpected application error.")

            with st.expander("Show traceback"):

                st.exception(e)


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

left, center, right = st.columns(3)

with left:

    st.caption(
        "👨‍💻 Developed by Gaurav Maurya"
    )

with center:

    st.caption(
        f"Database : {DATABASE_STATUS}"
    )

with right:

    st.caption(
        "Version 2.1"
    )


# ==========================================================
# DEBUG INFORMATION
# ==========================================================

with st.expander("⚙ Platform Information", expanded=False):

    st.write("Project Root")

    st.code(str(PROJECT_ROOT))

    st.write("Database")

    st.code(str(DB_PATH))

    st.write("Output Folder")

    st.code(str(OUTPUT_DIR))

    st.write("Reports Folder")

    st.code(str(REPORT_DIR))

    st.write("Loaded Statistics")

    st.json(
        {
            "Companies": TOTAL_COMPANIES,
            "Sectors": TOTAL_SECTORS,
            "Clusters": TOTAL_CLUSTERS,
            "Database": DATABASE_STATUS,
        }
    )