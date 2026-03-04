import streamlit as st
import base64

st.set_page_config(
    page_title="Energy Consumption Forecasting App",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open("bg_image.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

bg_css = f"data:image/png;base64,{img_base64}"

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

        .stApp {{
            background-image: url("{bg_css}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] {{ display: none !important; width: 0 !important; }}
        [data-testid="collapsedControl"],
        button[data-testid="collapsedControl"] {{ display: none !important; visibility: hidden !important; }}
        .css-1lcbmhc, .css-1d391kg {{ display: none !important; }}

        .block-container {{
            position: relative;
            z-index: 1;
            padding-top: 6rem !important;
        }}

        .main-title {{
            font-family: 'Raleway', sans-serif;
            font-size: 3.6rem;
            font-weight: 700;
            text-align: center;
            color: #e8f4ff;
            letter-spacing: 0.04em;
            line-height: 1.15;
            margin-bottom: 0.4rem;
            text-shadow: 0 2px 18px rgba(0,0,0,0.55), 0 0 40px rgba(80,160,255,0.15);
        }}

        .title-divider {{
            width: 50px;
            height: 2px;
            background: rgba(160, 220, 255, 0.6);
            margin: 1.2rem auto 0.8rem auto;
        }}

        .subtitle {{
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            text-align: center;
            color: rgba(160, 220, 255, 0.75);
            letter-spacing: 0.28em;
            text-transform: uppercase;
            font-weight: 300;
            margin-bottom: 3.5rem;
        }}

        .tutorial-text {{
            font-family: 'DM Sans', sans-serif;
            font-size: 0.88rem;
            text-align: center;
            color: rgba(160, 210, 255, 0.5);
            margin-top: 1.6rem;
            font-weight: 300;
            letter-spacing: 0.02em;
        }}

        .tutorial-text a {{
            color: rgba(130, 200, 255, 0.85);
            text-decoration: underline;
            text-underline-offset: 3px;
            transition: color 0.2s;
        }}

        .tutorial-text a:hover {{
            color: #c0e8ff;
        }}

        div[data-testid="stVerticalBlock"] .stButton > button {{
            font-family: 'Raleway', sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.18em !important;
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

    st.markdown("""
        <div class="tutorial-text">
            Don't know how the app works?
            <a href="https://drive.google.com/file/d/10OBBjraNlSLmsx1whsSZxnDUE6wBkqMb/view" target="_blank">Click here for tutorial</a>
        </div>
    """, unsafe_allow_html=True)