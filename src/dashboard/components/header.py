import streamlit as st

def render_header(title, subtitle):
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#0f172a,#1e3a8a);
            padding:30px;
            border-radius:18px;
            margin-bottom:25px;
            box-shadow:0 10px 30px rgba(0,0,0,.25);
        ">
            <h1 style="color:white;margin:0;">📊 {title}</h1>
            <p style="color:#cbd5e1;font-size:17px;margin-top:10px;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )