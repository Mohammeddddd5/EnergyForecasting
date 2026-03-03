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
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

        .stApp { background: #020a18; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        header[data-testid="stHeader"] { background: transparent !important; }
        button[data-testid="collapsedControl"] { opacity: 0 !important; pointer-events: none !important; }

        .block-container {
            padding-top: 2.8rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 1100px !important;
        }

        .page-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 3.2rem;
            font-weight: 600;
            color: #f0f7ff;
            text-align: center;
            letter-spacing: 0.02em;
            line-height: 1.1;
            margin-bottom: 0;
        }

        .page-subtitle {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 300;
            color: rgba(180, 215, 255, 0.45);
            letter-spacing: 0.35em;
            text-transform: uppercase;
            text-align: center;
            margin-top: 0.5rem;
            margin-bottom: 0.6rem;
        }

        .divider {
            width: 32px;
            height: 1px;
            background: rgba(140, 200, 255, 0.35);
            margin: 0.7rem auto 1.6rem auto;
        }

        .section-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.65rem;
            font-weight: 500;
            letter-spacing: 0.32em;
            text-transform: uppercase;
            color: rgba(140, 200, 255, 0.38);
            text-align: center;
            margin-bottom: 0.7rem;
        }

        label[data-testid="stWidgetLabel"] p {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.65rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.22em !important;
            text-transform: uppercase !important;
            color: rgba(160, 210, 255, 0.5) !important;
        }

        .metric-row {
            display: flex;
            border: 1px solid rgba(100, 170, 255, 0.12);
            border-radius: 1px;
            overflow: hidden;
            margin-top: 1rem;
        }
        .metric-cell {
            flex: 1;
            padding: 1.3rem 1.6rem;
            background: rgba(10, 30, 70, 0.35);
            border-right: 1px solid rgba(100, 170, 255, 0.1);
            text-align: center;
        }
        .metric-cell:last-child { border-right: none; }
        .metric-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.62rem;
            font-weight: 500;
            letter-spacing: 0.25em;
            text-transform: uppercase;
            color: rgba(140, 200, 255, 0.45);
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.1rem;
            font-weight: 600;
            color: #eaf4ff;
            line-height: 1;
        }
        .metric-sub {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.6rem;
            font-weight: 300;
            color: rgba(140, 200, 255, 0.28);
            letter-spacing: 0.1em;
            margin-top: 0.3rem;
        }

        .back-btn > button {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.62rem !important;
            font-weight: 400 !important;
            letter-spacing: 0.2em !important;
            text-transform: uppercase !important;
            color: rgba(140, 200, 255, 0.4) !important;
            background: transparent !important;
            border: 1px solid rgba(100, 170, 255, 0.15) !important;
            border-radius: 0px !important;
            padding: 0.35rem 0.9rem !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }
        .back-btn > button:hover {
            color: #d0eaff !important;
            border-color: rgba(100, 170, 255, 0.4) !important;
            background: rgba(100, 170, 255, 0.05) !important;
            transform: none !important;
            box-shadow: none !important;
        }

        .stButton > button {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.68rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.25em !important;
            text-transform: uppercase !important;
            color: #cce8ff !important;
            background: rgba(30, 90, 200, 0.18) !important;
            border: 1px solid rgba(100, 170, 255, 0.4) !important;
            border-radius: 0px !important;
            padding: 0.8rem 1.5rem !important;
            transition: all 0.22s ease !important;
            box-shadow: none !important;
        }
        .stButton > button:hover {
            color: #ffffff !important;
            background: rgba(60, 130, 255, 0.28) !important;
            border-color: rgba(160, 210, 255, 0.8) !important;
            transform: translate(-2px, -2px) !important;
            box-shadow: 3px 3px 0px rgba(100, 170, 255, 0.15) !important;
        }

        #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ── Back button ────────────────────────────────────────────────────────────────
st.markdown('<div class="back-btn">', unsafe_allow_html=True)
if st.button("← Back", key="back"):
    st.switch_page("streamlit_app.py")
st.markdown('</div>', unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
COMPANIES = [
    "American Electric Power", "Comed", "Dayton Power & Light",
    "Duke Energy Ohio", "Dominion Energy", "Duquesne Light Company",
    "East Kentucky Power Cooperative", "FirstEnergy"
]

COMPANY_MAP = {
    "American Electric Power":         "Amercian Electric Power",
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

VIRIDIS = ["#38bdf8","#7dd3fc","#a5f3fc","#67e8f9",
           "#22d3ee","#06b6d4","#0891b2","#0e7490"]

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
st.markdown('<div class="page-title">Forecast vs Actual</div>', unsafe_allow_html=True)
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
            line=dict(color="#7dd4fc", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=combined_true.index, y=combined_true.values, mode="lines",
            name="All PJM — Actual",
            line=dict(color="rgba(255,100,100,0.85)", width=2.5, dash="dash"),
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
                    line=dict(color="rgba(255,100,100,0.7)", width=2, dash="dash"),
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=dt_idx, y=y_pred, mode="lines",
                    name="Predicted",
                    line=dict(color="#7dd4fc", width=2),
                ))
                fig.add_trace(go.Scatter(
                    x=dt_idx, y=y_true, mode="lines",
                    name="Actual",
                    line=dict(color="rgba(255,100,100,0.85)", width=2.5, dash="dash"),
                ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(4, 14, 38, 0.95)",
        font=dict(family="DM Sans, sans-serif", color="#93c5fd", size=11),
        legend=dict(
            bgcolor="rgba(2, 8, 25, 0.9)",
            bordercolor="rgba(100, 170, 255, 0.15)",
            borderwidth=1,
            font=dict(size=10, color="#bfdbfe"),
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="left",   x=0,
        ),
        xaxis=dict(
            gridcolor="rgba(100, 170, 255, 0.06)",
            linecolor="rgba(100, 170, 255, 0.18)",
            tickfont=dict(color="#4a7fc0", size=10),
            tickformat="%b %Y",
            hoverformat="%Y-%m-%d %H:00",
            rangeslider=dict(visible=True, bgcolor="rgba(4,14,38,0.7)", thickness=0.03),
            rangeselector=dict(
                bgcolor="rgba(4,14,38,0.95)",
                activecolor="rgba(50,130,255,0.45)",
                bordercolor="rgba(100,170,255,0.2)",
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
            gridcolor="rgba(100, 170, 255, 0.06)",
            linecolor="rgba(100, 170, 255, 0.18)",
            tickfont=dict(color="#4a7fc0", size=10),
            title="Energy Consumption (MW)",
            title_font=dict(size=10, color="rgba(140, 200, 255, 0.38)"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(2, 8, 28, 0.95)",
            bordercolor="rgba(100, 170, 255, 0.25)",
            font=dict(family="DM Sans, sans-serif", size=11, color="#e0f0ff"),
        ),
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
        <div style="text-align:center;padding:3.5rem 2rem;font-family:'DM Sans',sans-serif;
                    color:rgba(140,200,255,0.18);font-size:0.72rem;letter-spacing:0.25em;
                    text-transform:uppercase;border:1px solid rgba(100,170,255,0.08);border-radius:1px;">
            Configure inputs above and click Run Forecast
        </div>
    """, unsafe_allow_html=True)