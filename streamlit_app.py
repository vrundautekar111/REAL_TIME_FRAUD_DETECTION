import json
import random
from datetime import datetime

import httpx
import plotly.graph_objects as go
import streamlit as st

# PAGE CONFIG


st.set_page_config(
    page_title="Fraud Analytics | Real-Time Monitoring",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_DEFAULT = "http://127.0.0.1:8000"

# DARK DASHBOARD STYLING


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #080b12;
        --panel: #10141e;
        --panel2: #0c1018;
        --border: #202635;
        --text: #f3f5fa;
        --muted: #858da0;
        --pink: #ff315c;
        --orange: #ff9f0a;
        --green: #00d6a0;
        --cyan: #00c8f8;
        --purple: #a56bff;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at top left, #11182a 0%, transparent 42%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #0b0f18;
    }

    .block-container {
        max-width: 1600px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        background: #0c1018;
        border: 1px solid var(--border);
        padding: 18px 22px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
    }

    .brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 13px;
        background: linear-gradient(135deg, #ff315c, #ff7a20);
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 22px;
        box-shadow: 0 5px 25px #ff315c35;
    }

    .brand-title {
        color: #f5f6fa;
        font-size: 19px;
        font-weight: 800;
        margin: 0;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 11px;
        margin-top: 4px;
    }

    .status-pill {
        display: inline-block;
        border: 1px solid #075943;
        background: #06271f;
        color: var(--green);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 11px;
        font-weight: 700;
    }

    .section-heading {
        font-size: 16px;
        font-weight: 700;
        color: #f3f5fa;
        margin: 7px 0 12px 0;
    }

    .metric-card {
        min-height: 110px;
        background: linear-gradient(145deg, #111620, #0c1018);
        border: 1px solid #202635;
        border-radius: 13px;
        padding: 17px 17px 13px 17px;
        margin-bottom: 10px;
    }

    .metric-card.highlight {
        background: linear-gradient(140deg, #28101c, #160e18);
        border-color: #4c1a2a;
    }

    .metric-label {
        font-size: 11px;
        color: #9299aa;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #f5f6fa;
        font-size: clamp(20px, 2vw, 28px);
        font-weight: 800;
        letter-spacing: -0.8px;
    }

    .metric-value.pink { color: var(--pink); }
    .metric-value.green { color: var(--green); }
    .metric-value.cyan { color: var(--cyan); }
    .metric-value.orange { color: var(--orange); }

    .metric-note {
        font-size: 10px;
        color: #838b9c;
        margin-top: 8px;
    }

    .panel {
        background: #0e121b;
        border: 1px solid #202635;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
    }

    .panel-title {
        color: #f3f5fa;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .panel-subtitle {
        color: #828a9b;
        font-size: 10px;
        margin-bottom: 12px;
    }

    .origin-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #151923;
        border: 1px solid #242b3a;
        border-radius: 9px;
        padding: 12px;
        margin-top: 9px;
    }

    .origin-name {
        font-size: 12px;
        font-weight: 600;
        color: #e8ebf3;
    }

    .origin-count {
        font-size: 10px;
        color: #858da0;
        margin-top: 4px;
    }

    .origin-score {
        font-weight: 800;
        font-size: 13px;
    }

    .fraud-row {
        margin: 15px 0;
    }

    .fraud-row-head {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        font-size: 11px;
        margin-bottom: 8px;
        color: #d7dbe5;
    }

    .progress-track {
        height: 7px;
        background: #252a35;
        border-radius: 10px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        border-radius: 10px;
    }

    .health-box {
        background: #121722;
        border: 1px solid #202635;
        padding: 14px 6px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 9px;
    }

    .health-number {
        font-size: 21px;
        font-weight: 800;
    }

    .health-label {
        color: #858da0;
        font-size: 10px;
        margin-top: 5px;
    }

    .transaction-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        border-bottom: 1px solid #242a37;
        padding: 12px 0;
        font-size: 11px;
    }

    .transaction-id {
        color: #aeb5c4;
    }

    .transaction-amount {
        color: #e9ecf4;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: #111620;
        border: 1px solid #252b39;
        border-radius: 12px;
        padding: 12px;
    }

    div.stButton > button {
        background: #151a26;
        color: #eef0f6;
        border: 1px solid #30384a;
        border-radius: 8px;
        min-height: 38px;
    }

    div.stButton > button:hover {
        background: #252d40;
        color: white;
        border-color: #ff315c;
    }

    div[data-testid="stForm"] {
        background: #0e121b;
        border: 1px solid #252b39;
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #252b39;
        border-radius: 10px;
    }

    footer {
        visibility: hidden;
    }

    @media (max-width: 800px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .topbar {
            padding: 13px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# SESSION STATE


if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

if "recent_transactions" not in st.session_state:
    st.session_state.recent_transactions = []

if "time_range" not in st.session_state:
    st.session_state.time_range = "24H"

# SIDEBAR


with st.sidebar:
    st.markdown("## 🛡️ Fraud Analytics")
    st.caption("Monitoring navigation")
    api_url = st.text_input("FastAPI URL", value=API_DEFAULT).strip().rstrip("/")
    st.markdown("---")
    st.radio(
        "Dashboard sections",
        ["Overview", "Transaction Analyzer", "Model Health", "API Metrics"],
        key="navigation",
    )
    st.markdown("---")
    st.caption("Real-Time Fraud Detection")
    st.caption("Machine Learning Monitoring")

# BACKEND CONNECTION


health_data = {}
metrics_data = {}
backend_online = False

try:
    health_response = httpx.get(f"{api_url}/health", timeout=4)
    health_data = health_response.json()
    backend_online = health_response.status_code == 200
except (httpx.HTTPError, ValueError):
    backend_online = False

if backend_online:
    try:
        metrics_response = httpx.get(f"{api_url}/metrics", timeout=4)
        if metrics_response.is_success:
            metrics_data = metrics_response.json()
    except (httpx.HTTPError, ValueError):
        metrics_data = {}

# TOP HEADER


status_text = "● SYSTEM ACTIVE" if backend_online else "● API OFFLINE"
status_color = "#00d6a0" if backend_online else "#ff315c"

st.markdown(
    f"""
    <div class="topbar">
        <div class="brand">
            <div class="brand-icon">🛡️</div>
            <div>
                <div class="brand-title">Fraud Analytics</div>
                <div class="brand-subtitle">
                    Real-time detection metrics &amp; model performance
                </div>
            </div>
        </div>
        <div style="color:{status_color};font-weight:800;font-size:11px">
            {status_text}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not backend_online:
    st.warning(
        "FastAPI is offline. Start it in another terminal to enable live predictions."
    )

# Time filters are visual controls for the timeline.
filter_cols = st.columns([6, 1, 1, 1])

with filter_cols[1]:
    if st.button("24H", use_container_width=True):
        st.session_state.time_range = "24H"
with filter_cols[2]:
    if st.button("7D", use_container_width=True):
        st.session_state.time_range = "7D"
with filter_cols[3]:
    if st.button("30D", use_container_width=True):
        st.session_state.time_range = "30D"

st.caption(
    f"View: {st.session_state.time_range}  ·  "
    f"Updated {datetime.now().strftime('%H:%M:%S')}"
)

# METRIC CARDS


st.markdown('<div class="section-heading">Security Overview</div>', unsafe_allow_html=True)

requests_total = int(metrics_data.get("requests_total", 0) or 0)
predictions_total = int(metrics_data.get("predictions_total", 0) or 0)
fraud_predictions = int(metrics_data.get("fraud_predictions", 0) or 0)
errors_total = int(metrics_data.get("errors_total", 0) or 0)
uptime = float(metrics_data.get("uptime_seconds", 0) or 0)

# Only metrics actually returned by the API are shown as live values.
metric_cols = st.columns(5)

cards = [
    (
        "Requests Received",
        f"{requests_total:,}",
        "pink",
        "Actual API request counter",
    ),
    (
        "Fraud Predictions",
        f"{fraud_predictions:,}",
        "pink",
        "Actual fraud classifications",
    ),
    (
        "Transactions Analyzed",
        f"{predictions_total:,}",
        "green",
        "Actual prediction counter",
    ),
    (
        "API Errors",
        f"{errors_total:,}",
        "cyan",
        "Actual HTTP/API errors",
    ),
    (
        "API Uptime",
        f"{uptime:.0f}s",
        "orange",
        "Since the last API restart",
    ),
]

for col, (label, value, color, note) in zip(metric_cols, cards):
    with col:
        st.markdown(
            f"""
            <div class="metric-card {'highlight' if color == 'pink' else ''}">
                <div class="metric-label">{label}</div>
                <div class="metric-value {color}">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# DETECTION TIMELINE + ORIGINS


left, right = st.columns([1.9, 1])

with left:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Detection Timeline</div>
            <div class="panel-subtitle">
                Fraud classifications from the current dashboard session
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = st.session_state.prediction_history

    if history:
        fraud_count = sum(
            1 for item in history if item["classification"] == "Fraud"
        )
        legitimate_count = len(history) - fraud_count

        timeline = go.Figure()
        timeline.add_trace(
            go.Scatter(
                x=["Session start", "Current"],
                y=[0, fraud_count],
                mode="lines+markers",
                name="Fraud",
                line=dict(color="#ff315c", width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(255,49,92,0.12)",
            )
        )
        timeline.add_trace(
            go.Scatter(
                x=["Session start", "Current"],
                y=[0, legitimate_count],
                mode="lines+markers",
                name="Legitimate",
                line=dict(color="#ff9f0a", width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(255,159,10,0.08)",
            )
        )
        timeline.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e121b",
            plot_bgcolor="#0e121b",
            height=285,
            margin=dict(l=10, r=10, t=15, b=10),
            legend=dict(orientation="h", y=1.12, x=0),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(
                title="Session count",
                gridcolor="#202635",
                zeroline=False,
            ),
        )
        st.plotly_chart(timeline, use_container_width=True)
    else:
        st.info(
            "No session predictions yet. Analyze transactions below to populate this chart."
        )

with right:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">High-Risk Origins</div>
            <div class="panel-subtitle">
                Geographic origin analytics require location data
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Your current dataset does not provide reliable country-level origin "
        "information. Add verified location data before enabling this panel."
    )

# FRAUD PATTERNS + MODEL HEALTH + RECENT TRANSACTIONS


pattern_col, health_col, recent_col = st.columns([1.2, 1, 0.85])

with pattern_col:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Fraud by Pattern</div>
            <div class="panel-subtitle">
                Prediction categories currently available
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fraud_n = len([
        item for item in st.session_state.prediction_history
        if item["classification"] == "Fraud"
    ])
    legitimate_n = len(st.session_state.prediction_history) - fraud_n

    pattern_data = [
        ("Fraud classifications", fraud_n, "#ff315c"),
        ("Legitimate classifications", legitimate_n, "#ff9f0a"),
        ("API errors", errors_total, "#a56bff"),
    ]
    maximum = max([item[1] for item in pattern_data] + [1])

    for name, count, color in pattern_data:
        width = max(0, min(100, count / maximum * 100))
        st.markdown(
            f"""
            <div class="fraud-row">
                <div class="fraud-row-head">
                    <span>{name}</span>
                    <b>{count:,}</b>
                </div>
                <div class="progress-track">
                    <div class="progress-fill"
                         style="width:{width}%;background:{color}"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with health_col:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">ML Model Health</div>
            <div class="panel-subtitle">
                Live status and saved evaluation results
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    model_loaded = bool(health_data.get("model_loaded", backend_online))

    st.markdown(
        f"""
        <div class="health-box">
            <div class="health-number" style="color:{'#00d6a0' if model_loaded else '#ff315c'}">
                {'READY' if model_loaded else 'OFFLINE'}
            </div>
            <div class="health-label">Model availability</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="health-box">
            <div class="health-number" style="color:#00c8f8">—</div>
            <div class="health-label">Precision · Evaluation required</div>
        </div>
        <div class="health-box">
            <div class="health-number" style="color:#a56bff">—</div>
            <div class="health-label">Recall · Evaluation required</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Populate precision, recall, F1 and PR-AUC from "
        "your real held-out evaluation report."
    )

with recent_col:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Recent Predictions</div>
            <div class="panel-subtitle">
                Current browser session
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    recent = list(reversed(st.session_state.recent_transactions[-5:]))

    if recent:
        for item in recent:
            color = "#ff315c" if item["classification"] == "Fraud" else "#00d6a0"
            st.markdown(
                f"""
                <div class="transaction-row">
                    <span class="transaction-id">
                        <span style="color:{color}">●</span>
                        {item['id']}
                    </span>
                    <span class="transaction-amount">
                        {item['classification']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No predictions yet.")

# TRANSACTION ANALYZER


st.markdown("---")
st.markdown("## Transaction Analyzer")
st.caption(
    "Submit a transaction to your real FastAPI model. "
    "Use the exact feature names expected by your trained model."
)

default_features = {"Time": 0.0}
default_features.update({f"V{i}": 0.0 for i in range(1, 29)})
default_features["Amount"] = 100.0

with st.expander("Analyze a transaction", expanded=False):
    st.write("Enter transaction features as JSON.")
    st.caption(
        "The example fields below are for the standard Kaggle dataset. "
        "Your saved model must use these exact features for the example to work."
    )

    with st.form("transaction_form"):
        transaction_text = st.text_area(
            "Transaction JSON",
            value=json.dumps({"features": default_features}, indent=2),
            height=260,
        )
        submitted = st.form_submit_button(
            "Analyze Transaction",
            use_container_width=True,
        )

    if submitted:
        try:
            payload = json.loads(transaction_text)

            if not isinstance(payload, dict):
                raise ValueError("The input must be a JSON object.")

            if "features" not in payload:
                payload = {"features": payload}

            if not isinstance(payload["features"], dict):
                raise ValueError("'features' must be a JSON object.")

            if not backend_online:
                st.error("FastAPI is offline. Start the backend first.")
            else:
                with st.spinner("Running model prediction..."):
                    response = httpx.post(
                        f"{api_url}/predict",
                        json=payload,
                        timeout=30,
                    )

                if response.is_success:
                    body = response.json()
                    result = body.get("result", body)

                    is_fraud = bool(result.get("is_fraud", False))
                    probability = float(result.get("fraud_probability", 0))

                    classification = "Fraud" if is_fraud else "Legitimate"

                    if is_fraud:
                        st.error("🚨 Potential Fraud Detected")
                    else:
                        st.success("✅ Classified as Legitimate")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Classification", classification)
                    col2.metric("Fraud Probability", f"{probability:.2%}")
                    col3.metric(
                        "Decision Threshold",
                        f"{float(result.get('threshold', 0.5)):.2%}",
                    )

                    st.session_state.prediction_history.append(
                        {
                            "classification": classification,
                            "probability": probability,
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                        }
                    )
                    st.session_state.recent_transactions.append(
                        {
                            "id": f"TXN-{random.randint(10000, 99999)}",
                            "classification": classification,
                            "probability": probability,
                        }
                    )

                    with st.expander("Full API response"):
                        st.json(body)

                    st.info("Refresh the page to update the dashboard panels.")
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"API error {response.status_code}: {detail}")

        except json.JSONDecodeError:
            st.error("Invalid JSON. Check commas, braces and quotation marks.")
        except (ValueError, TypeError) as exc:
            st.error(f"Invalid input: {exc}")
        except httpx.HTTPError as exc:
            st.error(f"Could not contact FastAPI: {exc}")

# FOOTER


st.markdown("---")
st.caption(
    "REAL-TIME FRAUD DETECTION  ·  FastAPI + Streamlit + scikit-learn"
)
