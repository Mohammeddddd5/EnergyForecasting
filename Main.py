import streamlit as st
import base64

st.set_page_config(page_title="Energy Consumption Forecasting App", layout="wide")

with open("bg_image.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

bg_css = f"data:image/png;base64,{img_base64}"

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

        .stApp {{
            background-image: url("{bg_css}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .block-container {{
            position: relative;
            z-index: 1;
            padding-top: 6rem !important;
        }}

        .main-title {{
            font-family: 'Playfair Display', serif;
            font-size: 2.9rem;
            font-weight: 700;
            text-align: center;
            color: #e0f4ff;
            letter-spacing: 0.01em;
            line-height: 1.2;
            margin-bottom: 0.4rem;
            text-shadow: 0 2px 8px rgba(0,0,0,0.4);
        }}

        .title-divider {{
            width: 50px;
            height: 2px;
            background: rgba(160, 220, 255, 0.6);
            margin: 1.2rem auto 0.8rem auto;
        }}

        .subtitle {{
            font-family: 'Lato', sans-serif;
            font-size: 0.82rem;
            text-align: center;
            color: rgba(160, 220, 255, 0.75);
            letter-spacing: 0.28em;
            text-transform: uppercase;
            font-weight: 300;
            margin-bottom: 3.5rem;
        }}

        div[data-testid="stVerticalBlock"] .stButton > button {{
            font-family: 'Lato', sans-serif !important;
            font-size: 0.82rem !important;
            font-weight: 400 !important;
            letter-spacing: 0.2em !important;
            text-transform: uppercase !important;
            color: #a0dcff !important;
            background: rgba(0, 100, 180, 0.25) !important;
            border: 1.5px solid rgba(0, 160, 255, 0.45) !important;
            border-radius: 0px !important;
            padding: 1rem 2rem !important;
            width: 100% !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            box-shadow: none !important;
        }}

        div[data-testid="stVerticalBlock"] .stButton > button:hover {{
            color: #ffffff !important;
            background: rgba(0, 140, 255, 0.28) !important;
            border-color: rgba(0, 200, 255, 0.9) !important;
            box-shadow: 3px 3px 0px rgba(0, 160, 255, 0.2) !important;
            transform: translate(-2px, -2px) !important;
        }}

        div[data-testid="stVerticalBlock"] .stButton > button:active {{
            transform: translate(0px, 0px) !important;
            box-shadow: none !important;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.2, 1])

with col2:
    st.markdown('<div class="main-title">Energy Consumption<br>Forecasting System</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Select a module to begin</div>', unsafe_allow_html=True)

    if st.button("Forecast Using Test Data", use_container_width=True):
        st.switch_page("pages/TestDataForecast.py")
    st.write("")
    if st.button("Custom Forecasting", use_container_width=True):
        st.switch_page("pages/CustomDataForecast.py")
