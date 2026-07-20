import streamlit as st


def kpi_card(title, value, delta=None, icon="📊"):

    delta_html = ""

    if delta:
        color = "#22c55e" if delta.startswith("+") else "#ef4444"

        delta_html = f"""
        <p style="
            color:{color};
            font-size:15px;
            margin-top:8px;
            font-weight:600;">
            {delta}
        </p>
        """

    st.markdown(
        f"""
        <div style="
            background:#1e293b;
            border-radius:18px;
            padding:22px;
            border:1px solid #334155;
            box-shadow:0 10px 24px rgba(0,0,0,.25);
            transition:0.3s;
        ">

            <div style="font-size:30px;">
                {icon}
            </div>

            <p style="
                color:#94a3b8;
                font-size:14px;
                margin-bottom:5px;">
                {title}
            </p>

            <h2 style="
                color:white;
                margin:0;">
                {value}
            </h2>

            {delta_html}

        </div>
        """,
        unsafe_allow_html=True,
    )