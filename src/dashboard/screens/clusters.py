from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from components.styles import load_css

# ==========================================================
# Project Paths
# ==========================================================

CURRENT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = CURRENT_DIR.parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output"
DB_DIR = PROJECT_ROOT / "db"
REPORT_DIR = PROJECT_ROOT / "reports"

# ==========================================================
# Cached Data Loaders
# ==========================================================

@st.cache_data(show_spinner=False)
def load_cluster_insights():
    """Load cluster summary."""

    file = OUTPUT_DIR / "cluster_insights.csv"

    if not file.exists():
        return pd.DataFrame()

    return pd.read_csv(file)


@st.cache_data(show_spinner=False)
def load_cluster_labels():
    """Load company cluster labels."""

    file = OUTPUT_DIR / "cluster_labels.csv"

    if not file.exists():
        return pd.DataFrame()

    return pd.read_csv(file)


@st.cache_data(show_spinner=False)
def load_company_data():
    """
    Merge company information with cluster labels.

    Expected file:
    output/company_clusters.csv
    """

    file = OUTPUT_DIR / "company_clusters.csv"

    if not file.exists():
        return pd.DataFrame()

    return pd.read_csv(file)


# ==========================================================
# Helper Functions
# ==========================================================

def calculate_health_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cluster health score.
    """

    health = df.copy()

    if health.empty:
        return health

    health["health_score"] = (
        health["return_on_equity_pct"] * 0.35
        + health["revenue_cagr_5yr"] * 0.25
        + health["operating_profit_margin_pct"] * 0.25
        - health["debt_to_equity"] * 5
    )

    return health


def format_cluster_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns for display.
    """

    if df.empty:
        return df

    return df.rename(
        columns={
            "cluster_id": "Cluster ID",
            "cluster_name": "Cluster Name",
            "companies": "Companies",
            "return_on_equity_pct": "ROE (%)",
            "debt_to_equity": "Debt / Equity",
            "revenue_cagr_5yr": "Revenue CAGR (%)",
            "net_cash_flow": "Net Cash Flow",
            "operating_profit_margin_pct": "OPM (%)",
            "investment_profile": "Investment Profile",
        }
    )


def get_cluster_statistics(insights: pd.DataFrame) -> dict:

    load_css
    """
    Compute dashboard statistics.
    """

    if insights.empty:

        return {
            "companies": 0,
            "clusters": 0,
            "largest_cluster": "N/A",
            "largest_size": 0,
            "average_roe": 0,
            "average_debt": 0,
        }

    largest = insights.loc[
        insights["companies"].idxmax()
    ]

    return {

        "companies": int(insights["companies"].sum()),

        "clusters": int(insights["cluster_id"].nunique()),

        "largest_cluster": largest["cluster_name"],

        "largest_size": int(largest["companies"]),

        "average_roe": round(
            insights["return_on_equity_pct"].mean(),
            2,
        ),

        "average_debt": round(
            insights["debt_to_equity"].mean(),
            2,
        ),
    }


# ==========================================================
# Load Data
# ==========================================================

cluster_insights = load_cluster_insights()

cluster_labels = load_cluster_labels()

company_df = load_company_data()

health_df = calculate_health_score(cluster_insights)

display_df = format_cluster_table(cluster_insights)

stats = get_cluster_statistics(cluster_insights)

# ==========================================================
# HEADER
# ==========================================================

def render_header():
    """Render dashboard title."""

    st.title("📊 Cluster Analytics")

    st.caption(
        "Analyze Nifty100 companies using machine learning clustering, "
        "financial metrics and investment insights."
    )

    st.divider()


# ==========================================================
# KPI CARDS
# ==========================================================

def render_kpis():
    """Display KPI metrics."""

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Companies",
            stats["companies"],
        )

    with c2:
        st.metric(
            "Clusters",
            stats["clusters"],
        )

    with c3:
        st.metric(
            "Largest Cluster",
            stats["largest_cluster"],
        )

    with c4:
        st.metric(
            "Largest Size",
            stats["largest_size"],
        )

    st.divider()


# ==========================================================
# CLUSTER TABLE
# ==========================================================

def render_cluster_table():
    """Display formatted cluster summary."""

    st.subheader("📋 Cluster Summary")

    if display_df.empty:

        st.warning("Cluster summary not available.")

        return

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()


# ==========================================================
# CLUSTER OVERVIEW
# ==========================================================

def render_cluster_overview():
    """Display quick insights."""

    if cluster_insights.empty:
        return

    left, right = st.columns(2)

    with left:

        highest_roe = cluster_insights.loc[
            cluster_insights["return_on_equity_pct"].idxmax()
        ]

        highest_growth = cluster_insights.loc[
            cluster_insights["revenue_cagr_5yr"].idxmax()
        ]

        st.success(
            f"🏆 Highest ROE : **{highest_roe['cluster_name']}**"
        )

        st.info(
            f"📈 Fastest Growth : **{highest_growth['cluster_name']}**"
        )

    with right:

        highest_debt = cluster_insights.loc[
            cluster_insights["debt_to_equity"].idxmax()
        ]

        highest_cash = cluster_insights.loc[
            cluster_insights["net_cash_flow"].idxmax()
        ]

        st.warning(
            f"⚠ Highest Debt : **{highest_debt['cluster_name']}**"
        )

        st.success(
            f"💰 Highest Cash Flow : **{highest_cash['cluster_name']}**"
        )

    st.divider()


# ==========================================================
# DATA QUALITY
# ==========================================================

def render_dataset_information():
    """Display dataset statistics."""

    st.subheader("📈 Dataset Statistics")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Average ROE",
            f"{stats['average_roe']} %",
        )

        st.metric(
            "Average Debt",
            stats["average_debt"],
        )

    with col2:

        st.metric(
            "Companies Analysed",
            stats["companies"],
        )

        st.metric(
            "Clusters Generated",
            stats["clusters"],
        )

    st.divider()

    # ==========================================================
# CHARTS
# ==========================================================

def render_cluster_distribution():
    """Companies per cluster."""

    st.subheader("📊 Companies per Cluster")

    if cluster_insights.empty:
        st.info("No cluster data available.")
        return

    fig = px.bar(
        cluster_insights,
        x="cluster_name",
        y="companies",
        color="cluster_name",
        text="companies",
        title="Company Distribution Across Clusters",
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        showlegend=False,
        xaxis_title="Cluster",
        yaxis_title="Companies",
        height=500,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()


# ==========================================================
# METRIC COMPARISON
# ==========================================================

def render_metric_comparison():

    st.subheader("📈 Financial Metrics Comparison")

    if cluster_insights.empty:
        return

    metrics = {
        "Return on Equity": "return_on_equity_pct",
        "Debt to Equity": "debt_to_equity",
        "Revenue CAGR": "revenue_cagr_5yr",
        "Operating Margin": "operating_profit_margin_pct",
        "Net Cash Flow": "net_cash_flow",
    }

    selected = st.selectbox(
        "Select Metric",
        list(metrics.keys()),
    )

    column = metrics[selected]

    fig = px.bar(
        cluster_insights,
        x="cluster_name",
        y=column,
        color="cluster_name",
        text_auto=".2f",
    )

    fig.update_layout(
        showlegend=False,
        height=500,
        xaxis_title="Cluster",
        yaxis_title=selected,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()


# ==========================================================
# BUBBLE CHART
# ==========================================================

def render_bubble_chart():

    st.subheader("🫧 Risk vs Profitability")

    if cluster_insights.empty:
        return

    fig = px.scatter(
        cluster_insights,
        x="debt_to_equity",
        y="return_on_equity_pct",
        size="companies",
        color="cluster_name",
        hover_name="cluster_name",
        size_max=70,
    )

    fig.update_layout(
        xaxis_title="Debt to Equity",
        yaxis_title="Return on Equity (%)",
        height=600,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()


# ==========================================================
# RADAR CHART
# ==========================================================

def render_radar_chart():

    st.subheader("🎯 Cluster Financial Profile")

    if cluster_insights.empty:
        return

    cluster = st.selectbox(
        "Choose Cluster",
        cluster_insights["cluster_name"],
        key="radar_cluster",
    )

    row = cluster_insights[
        cluster_insights["cluster_name"] == cluster
    ].iloc[0]

    categories = [
        "ROE",
        "Debt",
        "Revenue CAGR",
        "Cash Flow",
        "OPM",
    ]

    values = [
        row["return_on_equity_pct"],
        row["debt_to_equity"],
        row["revenue_cagr_5yr"],
        row["net_cash_flow"] / 1000,
        row["operating_profit_margin_pct"],
    ]

    fig = px.line_polar(
        r=values,
        theta=categories,
        line_close=True,
    )

    fig.update_traces(fill="toself")

    fig.update_layout(height=650)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()


# ==========================================================
# TREEMAP
# ==========================================================

def render_treemap():

    st.subheader("🌳 Sector Distribution")

    if company_df.empty:
        st.info("Company data unavailable.")
        return

    fig = px.treemap(
        company_df,
        path=["broad_sector", "company_name"],
        color="cluster_id",
        title="Companies by Sector",
    )

    fig.update_layout(height=700)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    # ==========================================================
# COMPANY EXPLORER
# ==========================================================

def render_company_explorer():

    st.subheader("🔍 Company Explorer")

    if company_df.empty:
        st.warning("Company dataset not available.")
        return

    cluster_options = ["All"] + sorted(
        cluster_insights["cluster_name"].unique().tolist()
    )

    selected_cluster = st.selectbox(
        "Filter by Cluster",
        cluster_options,
        key="cluster_filter",
    )

    filtered_df = company_df.copy()

    if selected_cluster != "All":

        cluster_id = cluster_insights.loc[
            cluster_insights["cluster_name"] == selected_cluster,
            "cluster_id",
        ].iloc[0]

        filtered_df = filtered_df[
            filtered_df["cluster_id"] == cluster_id
        ]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()


# ==========================================================
# COMPANY COMPARISON
# ==========================================================

def render_company_comparison():

    st.subheader("⚖ Company Comparison")

    if company_df.empty:
        return

    companies = sorted(company_df["company_name"].dropna().unique())

    c1, c2 = st.columns(2)

    with c1:
        company1 = st.selectbox(
            "Company A",
            companies,
            key="company_a",
        )

    with c2:
        company2 = st.selectbox(
            "Company B",
            companies,
            index=1 if len(companies) > 1 else 0,
            key="company_b",
        )

    comparison = company_df[
        company_df["company_name"].isin([company1, company2])
    ]

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()


# ==========================================================
# HEALTH SCORE
# ==========================================================

def render_health_scores():

    st.subheader("⭐ Cluster Health Scores")

    if health_df.empty:
        return

    ranking = health_df[
        ["cluster_name", "health_score"]
    ].sort_values(
        "health_score",
        ascending=False,
    )

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        ranking,
        x="cluster_name",
        y="health_score",
        color="cluster_name",
        title="Cluster Health Score Ranking",
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()


# ==========================================================
# AI INSIGHTS
# ==========================================================

def render_ai_insights():

    st.subheader("🧠 AI Investment Insight")

    if health_df.empty:
        return

    best = health_df.sort_values(
        "health_score",
        ascending=False,
    ).iloc[0]

    st.success(
        f"""
### 🏆 Best Investment Cluster

**{best['cluster_name']}**

Health Score : **{best['health_score']:.2f}**

This cluster demonstrates the strongest overall financial profile
based on profitability, revenue growth, operating margin,
and leverage.
"""
    )

    st.info(
        """
### 📌 Interpretation

• Higher ROE indicates stronger profitability.

• Lower Debt/Equity suggests lower financial risk.

• Higher Revenue CAGR reflects stronger long-term growth.

• Strong Operating Margin improves business quality.

• Health Score combines all these indicators into a single ranking.
"""
    )

    st.divider()


# ==========================================================
# DOWNLOADS
# ==========================================================

def render_downloads():

    st.subheader("📥 Export Data")

    if not cluster_insights.empty:

        st.download_button(
            label="⬇ Download Cluster Insights",
            data=cluster_insights.to_csv(index=False),
            file_name="cluster_insights.csv",
            mime="text/csv",
        )

    if not company_df.empty:

        st.download_button(
            label="⬇ Download Company Clusters",
            data=company_df.to_csv(index=False),
            file_name="company_clusters.csv",
            mime="text/csv",
        )


# ==========================================================
# MAIN RENDER FUNCTION
# ==========================================================

def render():
    """Render the Cluster Analytics page."""

    render_header()

    render_kpis()

    render_cluster_table()

    render_cluster_overview()

    render_dataset_information()

    render_cluster_distribution()

    render_metric_comparison()

    render_bubble_chart()

    render_radar_chart()

    render_treemap()

    render_company_explorer()

    render_company_comparison()

    render_health_scores()

    render_ai_insights()

    render_downloads()

    load_css()