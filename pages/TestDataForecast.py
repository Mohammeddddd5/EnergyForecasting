import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime
import os

st.set_page_config(page_title="Energy Forecast — Predictions", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

        .stApp { background: #03080f; }

        header[data-testid="stHeader"] { background: transparent !important; }
        button[data-testid="collapsedControl"] { opacity: 0 !important; pointer-events: none !important; }

        .block-container {
            padding-top: 2.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1200px !important;
        }

        .page-title {
            font-family: 'Playfair Display', serif;
            font-size: 2.6rem;
            font-weight: 700;
            color: #cce4ff;
            margin-bottom: 0.2rem;
            text-align: center;
        }

        .page-subtitle {
            font-family: 'Lato', sans-serif;
            font-size: 0.88rem;
            color: rgba(140, 190, 255, 0.55);
            letter-spacing: 0.25em;
            text-transform: uppercase;
            font-weight: 300;
            margin-bottom: 2rem;
            text-align: center;
        }

        .divider {
            width: 40px;
            height: 2px;
            background: rgba(100, 180, 255, 0.4);
            margin: 0.5rem auto 1.1rem auto;
        }

        .section-label {
            font-family: 'Lato', sans-serif;
            font-size: 0.78rem;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            color: rgba(140, 190, 255, 0.45);
            margin-bottom: 0.6rem;
            text-align: center;
        }

        label[data-testid="stWidgetLabel"] p {
            font-family: 'Lato', sans-serif !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.15em !important;
            text-transform: uppercase !important;
            color: rgba(140, 190, 255, 0.6) !important;
        }

        .metric-row {
            display: flex;
            gap: 0;
            border: 1px solid rgba(80,150,255,0.15);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 0.7rem;
        }
        .metric-cell {
            flex: 1;
            padding: 1.2rem 1.5rem;
            background: rgba(15, 35, 80, 0.4);
            border-right: 1px solid rgba(80,150,255,0.12);
            text-align: center;
        }
        .metric-cell:last-child { border-right: none; }
        .metric-label {
            font-family: 'Lato', sans-serif;
            font-size: 0.68rem;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: rgba(120, 170, 255, 0.5);
            margin-bottom: 0.4rem;
        }
        .metric-value {
            font-family: 'Playfair Display', serif;
            font-size: 1.85rem;
            font-weight: 600;
            color: #cce4ff;
        }
        .metric-sub {
            font-family: 'Lato', sans-serif;
            font-size: 0.65rem;
            color: rgba(140, 190, 255, 0.35);
            letter-spacing: 0.1em;
            margin-top: 0.2rem;
        }

        .stButton > button {
            font-family: 'Lato', sans-serif !important;
            font-size: 0.76rem !important;
            font-weight: 400 !important;
            letter-spacing: 0.2em !important;
            text-transform: uppercase !important;
            color: #8ac4ff !important;
            background: rgba(30, 90, 180, 0.15) !important;
            border: 1.5px solid rgba(80, 160, 255, 0.4) !important;
            border-radius: 0px !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.25s ease !important;
            box-shadow: none !important;
        }
        .stButton > button:hover {
            color: #ffffff !important;
            background: rgba(50, 130, 255, 0.25) !important;
            border-color: rgba(100, 200, 255, 0.85) !important;
            transform: translate(-2px, -2px) !important;
            box-shadow: 3px 3px 0px rgba(80, 160, 255, 0.18) !important;
        }
        .back-btn > button { 
            font-family: 'Lato', sans-serif !important; 
            font-size: 0.68rem !important; 
            letter-spacing: 0.18em !important; 
            text-transform: uppercase !important; 
            color: rgba(140, 190, 255, 0.5) !important; 
            background: transparent !important; 
            border: 1px solid rgba(80, 160, 255, 0.2) !important; 
            border-radius: 0px !important; 
            padding: 0.4rem 1rem !important; 
            margin-bottom: 1rem !important; 
        }
        .back-btn > button:hover { 
            color: #cce4ff !important; 
            border-color: rgba(80, 160, 255, 0.5) !important; 
            background: transparent !important; 
            transform: translate(-1px, 0px) !important; 
            box-shadow: none !important; 
        }
        #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
st.markdown('<div class="back-btn">', unsafe_allow_html=True)
if st.button("← Back", key="back"):
    st.switch_page("Main.py")
st.markdown('</div>', unsafe_allow_html=True)
COMPANIES = [
    "American Electric Power", "Comed", "Dayton Power & Light",
    "Duke Energy Ohio", "Dominion Energy", "Duquesne Light Company",
    "East Kentucky Power Cooperative", "FirstEnergy"
]

COMPANY_MAP = {
    "American Electric Power":         "Amercian Electric Power",  # typo matches training
    "Comed":                           "Comed",
    "Dayton Power & Light":            "Dayton Power & Light",
    "Duke Energy Ohio":                "Duke Energy Ohio",
    "Dominion Energy":                 "Dominion Energy",
    "Duquesne Light Company":          "Duquesne Light Company",
    "East Kentucky Power Cooperative": "East Kentucky Power Cooperative",
    "FirstEnergy":                     "FirstEnergy",
}

DATE_MIN = datetime(2016, 8, 1, 0)
DATE_MAX = datetime(2018, 8, 3, 23)

VIRIDIS = ["#3ecfcf","#3eabcf","#3e87cf","#5c6fcf",
           "#7c56cf","#a056cf","#cf56b8","#cf5680"]

BASE_FEATURE_COLS = ["Hour","Year","Month","WeekDay","Day",
                     "Lag_1","Lag_2","Lag_3","Lag_24","Lag_168",
                     "Rolling_mean_24","Rolling_std_24","Exp_Moving_Avg_24"]

COMPANY_COLS = [
    "Company_Amercian Electric Power",
    "Company_Comed",
    "Company_Dayton Power & Light",
    "Company_Dominion Energy",
    "Company_Duke Energy Ohio",
    "Company_Duquesne Light Company",
    "Company_East Kentucky Power Cooperative",
    "Company_FirstEnergy",
]

ALL_FEATURE_COLS = BASE_FEATURE_COLS + COMPANY_COLS

# ── Load resources ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    base = os.path.dirname(__file__)
    with open(os.path.join(base, "..", "energy_consumption_model.pkl"), "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    df = pd.read_csv(os.path.join(base, "..", "PJM_Energy_Consumption_Preprocessed.csv"))
    if "Datetime" in df.columns:
        df.drop(columns=["Datetime"], inplace=True)
    df["_dt"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"],
                                    day=df["Day"],   hour=df["Hour"]))
    return df

model   = load_model()
df_full = load_data()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Forecast vs Actual Results</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Model predictions on historical test data</div>', unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Date Range &amp; Company</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 1, 2])
with c1:
    start_date = st.date_input("From", value=DATE_MIN.date(),
                               min_value=DATE_MIN.date(), max_value=DATE_MAX.date())
with c2:
    start_hour = st.selectbox("Hour", list(range(24)), index=0, key="sh")
with c3:
    end_date = st.date_input("To", value=DATE_MAX.date(),
                             min_value=DATE_MIN.date(), max_value=DATE_MAX.date())
with c4:
    end_hour = st.selectbox("Hour", list(range(24)), index=23, key="eh")
with c5:
    selected_company = st.selectbox("Company", [
        "All Companies (Separated)",
        "All PJM (Combined)",
    ] + COMPANIES)

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([0.38, 0.24, 0.38])
with btn_col:
    run = st.button("Run Forecast", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Results ────────────────────────────────────────────────────────────────────
if run:
    start_dt = datetime.combine(start_date, datetime.min.time()).replace(hour=start_hour)
    end_dt   = datetime.combine(end_date,   datetime.min.time()).replace(hour=end_hour)

    if start_dt >= end_dt:
        st.error("Start datetime must be before end datetime.")
        st.stop()

    mask     = (df_full["_dt"] >= start_dt) & (df_full["_dt"] <= end_dt)
    df_range = df_full[mask].copy()

    if df_range.empty:
        st.warning("No data found for the selected range.")
        st.stop()

    companies_to_plot = COMPANIES if selected_company in ["All Companies (Separated)", "All PJM (Combined)"] else [selected_company]

    fig = go.Figure()
    all_actual, all_predicted = [], []

    # ── All PJM Combined ──────────────────────────────────────────────────────
    if selected_company == "All PJM (Combined)":
        combined_pred = pd.Series(dtype=float)
        combined_true = pd.Series(dtype=float)

        for company_label in companies_to_plot:
            original_name = COMPANY_MAP[company_label]
            df_c = df_range[df_range["Company"] == original_name].copy()
            if df_c.empty:
                continue

            df_encoded = pd.get_dummies(df_c, columns=["Company"])
            for col in COMPANY_COLS:
                if col not in df_encoded.columns:
                    df_encoded[col] = 0

            y_pred_c = np.exp(np.clip(model.predict(df_encoded[ALL_FEATURE_COLS]), -500, 500))
            y_true_c = df_c["Energy_Consumption"].values

            pred_series = pd.Series(y_pred_c, index=df_c["_dt"].values)
            true_series = pd.Series(y_true_c, index=df_c["_dt"].values)

            combined_pred = combined_pred.add(pred_series, fill_value=0)
            combined_true = combined_true.add(true_series, fill_value=0)

        all_actual.extend(combined_true.values)
        all_predicted.extend(combined_pred.values)

        fig.add_trace(go.Scatter(
            x=combined_pred.index, y=combined_pred.values, mode="lines",
            name="All PJM — Predicted",
            line=dict(color="#4db8ff", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=combined_true.index, y=combined_true.values, mode="lines",
            name="All PJM — Actual",
            line=dict(color="rgba(255,90,90,0.9)", width=2.5, dash="dash"),
        ))

    # ── All Companies Separated or Single Company ─────────────────────────────
    else:
        for i, company_label in enumerate(companies_to_plot):
            original_name = COMPANY_MAP[company_label]
            df_c = df_range[df_range["Company"] == original_name].copy()
            if df_c.empty:
                continue

            df_encoded = pd.get_dummies(df_c, columns=["Company"])
            for col in COMPANY_COLS:
                if col not in df_encoded.columns:
                    df_encoded[col] = 0

            y_true = df_c["Energy_Consumption"].values
            y_pred = np.exp(np.clip(model.predict(df_encoded[ALL_FEATURE_COLS]), -500, 500))

            all_actual.extend(y_true)
            all_predicted.extend(y_pred)
            dt_idx = df_c["_dt"]

            if selected_company == "All Companies (Separated)":
                fig.add_trace(go.Scatter(
                    x=dt_idx, y=y_pred, mode="lines",
                    name=f"{company_label} — Predicted",
                    line=dict(color=VIRIDIS[i % len(VIRIDIS)], width=1.5),
                    opacity=0.9,
                ))
                fig.add_trace(go.Scatter(
                    x=dt_idx, y=y_true, mode="lines",
                    name=f"{company_label} — Actual",
                    line=dict(color="rgba(255,90,90,0.75)", width=2, dash="dash"),
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=dt_idx, y=y_pred, mode="lines",
                    name="Predicted",
                    line=dict(color="#4db8ff", width=2),
                ))
                fig.add_trace(go.Scatter(
                    x=dt_idx, y=y_true, mode="lines",
                    name="Actual",
                    line=dict(color="rgba(255,90,90,0.9)", width=2.5, dash="dash"),
                ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8, 18, 40, 0.9)",
        font=dict(family="Lato, sans-serif", color="#7ab0e8", size=11),
        legend=dict(
            bgcolor="rgba(5,12,30,0.85)",
            bordercolor="rgba(80,150,255,0.15)",
            borderwidth=1,
            font=dict(size=10, color="#99c0f0"),
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="left",   x=0,
        ),
        xaxis=dict(
            gridcolor="rgba(80,150,255,0.07)",
            linecolor="rgba(80,150,255,0.2)",
            tickfont=dict(color="#5a88cc", size=10),
            tickformat="%b %Y",
            rangeslider=dict(visible=True, bgcolor="rgba(8,18,40,0.6)", thickness=0.03),
            rangeselector=dict(
                bgcolor="rgba(8,18,40,0.95)",
                activecolor="rgba(50,130,255,0.45)",
                bordercolor="rgba(80,150,255,0.2)",
                font=dict(color="#7ab0e8", size=10),
                buttons=[
                    dict(count=1,  label="1M", step="month", stepmode="backward"),
                    dict(count=3,  label="3M", step="month", stepmode="backward"),
                    dict(count=6,  label="6M", step="month", stepmode="backward"),
                    dict(count=1,  label="1Y", step="year",  stepmode="backward"),
                    dict(step="all", label="All"),
                ],
            ),
        ),
        yaxis=dict(
            gridcolor="rgba(80,150,255,0.07)",
            linecolor="rgba(80,150,255,0.2)",
            tickfont=dict(color="#5a88cc", size=10),
            title="Energy Consumption (MW)",
            title_font=dict(size=10, color="rgba(120,170,255,0.45)"),
        ),
        hovermode="x unified",
        margin=dict(l=8, r=8, t=36, b=40),
        height=480,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Metrics ────────────────────────────────────────────────────────────────
    if all_actual and all_predicted:
        arr_actual = np.array(all_actual)
        arr_pred   = np.array(all_predicted)
        mask_fin   = np.isfinite(arr_actual) & np.isfinite(arr_pred)
        arr_actual = arr_actual[mask_fin]
        arr_pred   = arr_pred[mask_fin]

        mse  = mean_squared_error(arr_actual, arr_pred)
        r2   = r2_score(arr_actual, arr_pred)
        rmse = np.sqrt(mse)

        st.markdown(f"""
            <div class="metric-row">
                <div class="metric-cell">
                    <div class="metric-label">Mean Squared Error</div>
                    <div class="metric-value">{mse:,.0f}</div>
                    <div class="metric-sub">MW²</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-label">Root MSE</div>
                    <div class="metric-value">{rmse:,.1f}</div>
                    <div class="metric-sub">MW</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-label">R² Score</div>
                    <div class="metric-value">{r2:.4f}</div>
                    <div class="metric-sub">Coefficient of determination</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div style="text-align:center;padding:3.5rem 2rem;font-family:'Lato',sans-serif;
                    color:rgba(140,190,255,0.25);font-size:0.8rem;letter-spacing:0.2em;
                    text-transform:uppercase;border:1px dashed rgba(80,150,255,0.12);border-radius:2px;">
            Configure inputs above and click Run Forecast
        </div>
    """, unsafe_allow_html=True)