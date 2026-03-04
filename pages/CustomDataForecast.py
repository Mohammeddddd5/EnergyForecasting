import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Energy Forecast - Custom",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

        .stApp { background: #020a18; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        header[data-testid="stHeader"] { background: transparent !important; }

        /* ── Sidebar nuclear option ── */
        [data-testid="stSidebar"] { display: none !important; width: 0px !important; height: 0px !important; }
        [data-testid="stSidebar"] > div { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; visibility: hidden !important; pointer-events: none !important; }
        button[data-testid="collapsedControl"] { display: none !important; visibility: hidden !important; }
        .css-1lcbmhc, .css-1d391kg, .css-hxt7ib, .css-17eq0hr { display: none !important; }
        div[data-testid="stSidebarNav"] { display: none !important; }
        #MainMenu { visibility: hidden !important; display: none !important; }

        .block-container {
            padding-top: 2.8rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 1100px !important;
        }

        .page-title {
            font-family: 'Raleway', sans-serif;
            font-size: 4rem;
            font-weight: 800;
            color: #f0f7ff;
            text-align: center;
            letter-spacing: 0.02em;
            line-height: 1.1;
            margin-bottom: 0;
            text-shadow: 0 2px 14px rgba(0,0,0,0.5);
        }

        .page-subtitle {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.92rem;
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
            font-size: 0.82rem;
            font-weight: 500;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            color: rgba(140, 200, 255, 0.45);
            text-align: center;
            margin-bottom: 0.7rem;
        }

        label[data-testid="stWidgetLabel"] p {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.18em !important;
            text-transform: uppercase !important;
            color: rgba(160, 210, 255, 0.6) !important;
        }

        .warning-wrapper {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.8rem;
            gap: 0.55rem;
        }
        .warning-icon { position: relative; display: inline-block; cursor: pointer; }
        .warning-icon .icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px; height: 20px;
            background: rgba(255, 190, 60, 0.1);
            border: 1px solid rgba(255, 190, 60, 0.55);
            border-radius: 50%;
            color: rgba(255, 205, 90, 0.9);
            font-size: 0.72rem;
            font-weight: 700;
            font-family: 'DM Sans', sans-serif;
        }
        .warning-icon .tooltip {
            visibility: hidden; opacity: 0;
            width: 360px;
            background: rgba(5, 15, 40, 0.98);
            border: 1px solid rgba(255, 190, 60, 0.25);
            color: rgba(255, 215, 130, 0.82);
            font-family: 'DM Sans', sans-serif;
            font-size: 0.78rem; font-weight: 300;
            line-height: 1.7;
            padding: 0.9rem 1.1rem;
            border-radius: 2px;
            position: absolute; z-index: 999;
            top: 140%; left: 50%;
            transform: translateX(-50%);
            transition: opacity 0.2s ease;
            pointer-events: none;
        }
        .warning-icon .tooltip::before {
            content: '';
            position: absolute;
            bottom: 100%; left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-bottom-color: rgba(255, 190, 60, 0.25);
        }
        .warning-icon:hover .tooltip { visibility: visible; opacity: 1; }
        .warning-text {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            font-weight: 300;
            color: rgba(255, 200, 80, 0.6);
            letter-spacing: 0.06em;
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
            font-size: 0.78rem;
            font-weight: 500;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: rgba(140, 200, 255, 0.5);
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-family: 'Raleway', sans-serif;
            font-size: 2.6rem;
            font-weight: 700;
            color: #eaf4ff;
            line-height: 1;
        }
        .metric-sub {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 300;
            color: rgba(140, 200, 255, 0.35);
            letter-spacing: 0.1em;
            margin-top: 0.3rem;
        }

        .back-btn > button {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.75rem !important;
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
            font-family: 'Raleway', sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.22em !important;
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

        div[data-testid="stCaptionContainer"] p {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.78rem !important;
            color: rgba(140, 200, 255, 0.35) !important;
            text-align: center !important;
            letter-spacing: 0.08em !important;
        }

        footer { visibility: hidden; }
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
COMPANY_COLS = [
    "Company_Amercian Electric Power", "Company_Comed",
    "Company_Dayton Power & Light",    "Company_Dominion Energy",
    "Company_Duke Energy Ohio",        "Company_Duquesne Light Company",
    "Company_East Kentucky Power Cooperative", "Company_FirstEnergy",
]
BASE_FEATURE_COLS = ["Hour","Year","Month","WeekDay","Day","Lag_1","Lag_2","Lag_3",
                     "Lag_24","Lag_168","Rolling_mean_24","Rolling_std_24","Exp_Moving_Avg_24"]
ALL_FEATURE_COLS  = BASE_FEATURE_COLS + COMPANY_COLS

FORECAST_MIN   = datetime(2018, 8, 4, 0)
FORECAST_MAX   = datetime(2026, 12, 31, 23)
CHAIN_START    = datetime(2018, 8, 4, 0)
MAX_HOURS      = 8760
DURATION_UNITS = ["Hour(s)", "Day(s)", "Week(s)", "Month(s)", "Year(s)"]
DURATION_HOURS = {"Hour(s)": 1, "Day(s)": 24, "Week(s)": 168, "Month(s)": 720, "Year(s)": 8760}

# ── Load resources ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base, "energy_consumption_model.pkl"), "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = pd.read_csv(os.path.join(base, "test_data.csv"))
    if "Datetime" in df.columns:
        df.drop(columns=["Datetime"], inplace=True)
    df["_dt"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"],
                                    day=df["Day"], hour=df["Hour"]))
    return df

model   = load_model()
df_full = load_data()

# ── Forecast function ──────────────────────────────────────────────────────────
def forecast_company(company_original, chain_start, end_dt, df_seed, model):
    df_c = df_seed[df_seed["Company"] == company_original].copy()
    df_c = df_c.sort_values("_dt").reset_index(drop=True)
    history     = list(df_c["Energy_Consumption"].values.clip(min=1))
    company_col = f"Company_{company_original}"
    results     = []
    current_dt  = chain_start

    while current_dt <= end_dt:
        def get_lag(n):
            idx = len(history) - n
            return history[idx] if idx >= 0 else history[0]

        recent_24       = history[max(0, len(history)-24):]
        rolling_mean_24 = np.mean(recent_24)
        rolling_std_24  = np.std(recent_24) if len(recent_24) > 1 else 0.0
        alpha = 1 - 1/24
        ema   = history[-1]
        for val in reversed(recent_24[:-1]):
            ema = alpha * ema + (1 - alpha) * val

        row = {
            "Hour": current_dt.hour, "Year": current_dt.year, "Month": current_dt.month,
            "WeekDay": current_dt.weekday(), "Day": current_dt.day,
            "Lag_1": get_lag(1), "Lag_2": get_lag(2), "Lag_3": get_lag(3),
            "Lag_24": get_lag(24), "Lag_168": get_lag(168),
            "Rolling_mean_24": rolling_mean_24, "Rolling_std_24": rolling_std_24,
            "Exp_Moving_Avg_24": ema,
        }
        for col in COMPANY_COLS:
            row[col] = 1 if col == company_col else 0

        X        = pd.DataFrame([row])[ALL_FEATURE_COLS]
        log_pred = np.clip(model.predict(X)[0], -500, 500)
        pred_mw  = np.exp(log_pred)
        results.append((current_dt, pred_mw))
        history.append(pred_mw)
        current_dt += timedelta(hours=1)

    return results

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Custom Forecast</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Future energy consumption projections</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="warning-wrapper">
        <div class="warning-icon">
            <span class="icon">!</span>
            <div class="tooltip">
                This model was trained on data from 2004 to mid-2016 and tested on data from
                mid-2016 to mid-2018. Using it to forecast consumption for recent dates
                (e.g. current year) will most likely not be accurate due to distribution
                shift and compounding lag errors over long horizons.
            </div>
        </div>
        <span class="warning-text">Accuracy warning &mdash; hover for details</span>
    </div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Forecast Settings</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 2])
with c1:
    start_date = st.date_input("Start Date", value=FORECAST_MIN.date(),
                               min_value=FORECAST_MIN.date(), max_value=FORECAST_MAX.date())
with c2:
    start_hour = st.selectbox("Start Hour", list(range(24)), index=0, key="sh")
with c3:
    duration_val = st.number_input("Duration", min_value=1, max_value=8760, value=1, step=1)
with c4:
    duration_unit = st.selectbox("Unit", DURATION_UNITS, index=2)
with c5:
    selected_company = st.selectbox("Company", ["All PJM (Combined)"] + COMPANIES)

start_dt_preview = datetime.combine(start_date, datetime.min.time()).replace(hour=start_hour)
preview_hours    = min(int(duration_val * DURATION_HOURS[duration_unit]), MAX_HOURS)
preview_end      = start_dt_preview + timedelta(hours=preview_hours - 1)
if int(duration_val * DURATION_HOURS[duration_unit]) > MAX_HOURS:
    st.warning(f"Duration exceeds 1 year and will be capped. Forecast ends at {preview_end.strftime('%Y-%m-%d %H:00')}.")
else:
    st.caption(f"Forecast covers {preview_hours:,} hour(s) · ends {preview_end.strftime('%Y-%m-%d %H:00')}")

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([0.38, 0.24, 0.38])
with btn_col:
    run = st.button("Run Forecast", use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Results ────────────────────────────────────────────────────────────────────
if run:
    start_dt    = datetime.combine(start_date, datetime.min.time()).replace(hour=start_hour)
    total_hours = min(int(duration_val * DURATION_HOURS[duration_unit]), MAX_HOURS)
    end_dt      = min(start_dt + timedelta(hours=total_hours - 1), FORECAST_MAX)

    if start_dt < FORECAST_MIN:
        st.error(f"Start date must be on or after {FORECAST_MIN.strftime('%Y-%m-%d')}.")
        st.stop()

    companies_to_run = COMPANIES if selected_company == "All PJM (Combined)" else [selected_company]
    fig             = go.Figure()
    all_predictions = []
    peak_dt         = None

    with st.spinner("Generating forecast — chaining hourly predictions..."):
        if selected_company == "All PJM (Combined)":
            combined = pd.Series(dtype=float)
            for company_label in companies_to_run:
                results     = forecast_company(COMPANY_MAP[company_label], CHAIN_START, end_dt, df_full, model)
                pred_series = pd.Series({dt: val for dt, val in results if dt >= start_dt})
                combined    = combined.add(pred_series, fill_value=0)
            combined        = combined.sort_index()
            all_predictions = list(combined.values)
            peak_dt         = combined.index[combined.values.argmax()]
            fig.add_trace(go.Scatter(
                x=combined.index, y=combined.values, mode="lines",
                name="All PJM — Forecast", showlegend=False,
                line=dict(color="#7dd4fc", width=2),
            ))
        else:
            results  = forecast_company(COMPANY_MAP[selected_company], CHAIN_START, end_dt, df_full, model)
            filtered = [(dt, val) for dt, val in results if dt >= start_dt]
            dts, vals        = [r[0] for r in filtered], [r[1] for r in filtered]
            all_predictions  = vals
            peak_dt          = dts[int(np.argmax(vals))]
            fig.add_trace(go.Scatter(
                x=dts, y=vals, mode="lines",
                name=f"{selected_company} — Forecast", showlegend=False,
                line=dict(color="#7dd4fc", width=2),
            ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(4, 14, 38, 0.95)",
        showlegend=False,
        font=dict(family="DM Sans, sans-serif", color="#93c5fd", size=12),
        xaxis=dict(
            gridcolor="rgba(100, 170, 255, 0.06)",
            linecolor="rgba(100, 170, 255, 0.18)",
            tickfont=dict(color="#4a7fc0", size=12),
            tickformat="%b %Y",
            hoverformat="%Y-%m-%d %H:00",
            rangeslider=dict(visible=True, bgcolor="rgba(4,14,38,0.7)", thickness=0.03),
        ),
        yaxis=dict(
            gridcolor="rgba(100, 170, 255, 0.06)",
            linecolor="rgba(100, 170, 255, 0.18)",
            tickfont=dict(color="#4a7fc0", size=12),
            title="Predicted Consumption (MW)",
            title_font=dict(size=12, color="rgba(140, 200, 255, 0.45)"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(2, 8, 28, 0.95)",
            bordercolor="rgba(100, 170, 255, 0.25)",
            font=dict(family="DM Sans, sans-serif", size=12, color="#e0f0ff"),
        ),
        margin=dict(l=8, r=8, t=8, b=40),
        height=480,
    )

    st.plotly_chart(fig, use_container_width=True)

    if all_predictions:
        arr = np.array(all_predictions)
        arr = arr[np.isfinite(arr)]
        st.markdown(f"""
            <div class="metric-row">
                <div class="metric-cell">
                    <div class="metric-label">Average Consumption</div>
                    <div class="metric-value">{np.mean(arr):,.0f}</div>
                    <div class="metric-sub">MW</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-label">Peak Consumption Hour</div>
                    <div class="metric-value" style="font-size:1.5rem;">{pd.Timestamp(peak_dt).strftime("%Y-%m-%d %H:00")}</div>
                    <div class="metric-sub">Datetime of highest forecast</div>
                </div>
                <div class="metric-cell">
                    <div class="metric-label">Peak Hour Consumption</div>
                    <div class="metric-value">{np.max(arr):,.0f}</div>
                    <div class="metric-sub">MW</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div style="text-align:center;padding:3.5rem 2rem;font-family:'DM Sans',sans-serif;
                    color:rgba(140,200,255,0.18);font-size:0.85rem;letter-spacing:0.25em;
                    text-transform:uppercase;border:1px solid rgba(100,170,255,0.08);border-radius:1px;">
            Configure inputs above and click Run Forecast
        </div>
    """, unsafe_allow_html=True)