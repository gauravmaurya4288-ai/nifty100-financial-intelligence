import streamlit as st


def render_sidebar():

    st.sidebar.markdown(
        """
        <div style="text-align:center;padding:15px 10px;">
            <h2 style="margin-bottom:0;color:#60A5FA;">
                📊 Nifty100 AI
            </h2>
            <p style="color:#94A3B8;font-size:13px;">
                Financial Intelligence Platform
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🏢 Company Profile",
            "📈 Trend Analysis",
            "🔍 Stock Screener",
            "🏭 Sector Analysis",
            "🤝 Peer Comparison",
            "💰 Capital Allocation",
            "🏆 Rankings",
            "💼 Portfolio",
            "📄 Annual Reports",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.divider()

    st.sidebar.markdown("### 📊 Database")

    st.sidebar.metric("Companies", "92")
    st.sidebar.metric("Coverage", "Nifty100")
    st.sidebar.metric("Version", "v2.0")

    st.sidebar.divider()

    st.sidebar.caption(
        "Developed by Gaurav Maurya\n\n© 2026 Financial Intelligence"
    )

    return page