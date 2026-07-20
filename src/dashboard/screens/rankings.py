import streamlit as st
import plotly.express as px

from src.analytics.ranking import (
    top_companies,
    value_picks,
    growth_companies,
    quality_companies,
    top_roe_companies,
    sector_rankings,
    grade_distribution,
    recommendation_distribution,
)

from components.styles import load_css

load_css()

def render():
    """Render the Rankings Dashboard."""

    st.title("🏆 Company Rankings")
    st.caption(
        "Explore company rankings generated using the Financial Intelligence Engine."
    )

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    try:
        top_df = top_companies(100)
        value_df = value_picks(100)
        growth_df = growth_companies(100)
        quality_df = quality_companies(100)
        roe_df = top_roe_companies(100)
        sector_df = sector_rankings()
        grade_df = grade_distribution()
        recommendation_df = recommendation_distribution()

    except Exception as e:
        st.error(f"Unable to load ranking data.\n\n{e}")
        return

    # ==========================================================
    # KPI CARDS
    # ==========================================================

    buy_count = (top_df["recommendation"] == "🟢 Buy").sum()
    discount_count = (top_df["flag"] == "Discount").sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Highest Score",
        int(top_df["overall_score"].max()),
    )

    c2.metric(
        "Average Score",
        round(top_df["overall_score"].mean(), 1),
    )

    c3.metric(
        "Buy Rated",
        int(buy_count),
    )

    c4.metric(
        "Discount Stocks",
        int(discount_count),
    )

    st.divider()

    # ==========================================================
    # FILTERS
    # ==========================================================

    f1, f2 = st.columns(2)

    sector = f1.selectbox(
        "Sector",
        ["All"]
        + sorted(
            top_df["broad_sector"]
            .dropna()
            .unique()
            .tolist()
        ),
    )

    grade = f2.selectbox(
        "Grade",
        ["All"]
        + sorted(
            top_df["grade"]
            .dropna()
            .unique()
            .tolist()
        ),
    )

    filtered = top_df.copy()

    if sector != "All":
        filtered = filtered[
            filtered["broad_sector"] == sector
        ]

    if grade != "All":
        filtered = filtered[
            filtered["grade"] == grade
        ]

    # ==========================================================
    # TABS
    # ==========================================================

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🏆 Top Companies",
            "💰 Value Picks",
            "📈 Growth",
            "⭐ Quality",
            "💹 ROE",
            "🏭 Sector Rankings",
        ]
    )

    with tab1:
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.dataframe(
            value_df,
            use_container_width=True,
            hide_index=True,
        )

    with tab3:
        st.dataframe(
            growth_df,
            use_container_width=True,
            hide_index=True,
        )

    with tab4:
        st.dataframe(
            quality_df,
            use_container_width=True,
            hide_index=True,
        )

    with tab5:
        st.dataframe(
            roe_df,
            use_container_width=True,
            hide_index=True,
        )

    with tab6:
        st.dataframe(
            sector_df,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ==========================================================
    # VISUALIZATIONS
    # ==========================================================

    left, right = st.columns(2)

    with left:

        fig = px.pie(
            grade_df,
            names="grade",
            values="companies",
            hole=0.55,
            title="Grade Distribution",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:

        fig = px.pie(
            recommendation_df,
            names="recommendation",
            values="companies",
            hole=0.55,
            title="Recommendation Distribution",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    fig = px.bar(
        sector_df,
        x="avg_score",
        y="broad_sector",
        orientation="h",
        text="avg_score",
        title="Average Score by Sector",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ==========================================================
    # DOWNLOAD
    # ==========================================================

    st.divider()

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Rankings CSV",
        csv,
        "company_rankings.csv",
        "text/csv",
    )