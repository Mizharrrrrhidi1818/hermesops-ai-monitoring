import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE = Path.home() / "hermes-ai-monitoring"
REPORTS = BASE / "reports"

st.set_page_config(
    page_title="HermesOps Monitoring",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ HermesOps — Server Monitoring")
st.caption(
    "SumoPod VPS | Hermes Agent | "
    "Python Monitoring | Telegram Alerts"
)

with st.sidebar:
    st.header("Dashboard Settings")

    refresh = st.selectbox(
        "Auto-refresh",
        ["30s", "60s", "5min", "Off"],
        index=0,
    )

    period = st.selectbox(
        "History range",
        ["24 Hours", "7 Days", "All Data"],
    )

    st.info(
        "Auto-refresh updates the dashboard view. "
        "New measurements depend on the collector timer."
    )


def load_metrics():
    rows = []

    for file in sorted(
        REPORTS.glob("server_metrics_*.jsonl")
    ):
        with file.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue

                try:
                    record = json.loads(line)
                    if isinstance(record, dict):
                        rows.append(record)
                except json.JSONDecodeError:
                    continue

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    required = [
        "timestamp",
        "cpu_percent",
        "ram_percent",
        "disk_percent",
    ]

    if any(col not in df.columns for col in required):
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
        errors="coerce",
    )

    for col in required[1:]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    df = df.dropna(subset=required)
    return df.sort_values("timestamp")


def load_alert_state():
    file = REPORTS / "alert_state.json"

    if not file.exists():
        return {}

    try:
        return json.loads(file.read_text())
    except (OSError, ValueError):
        return {}


@st.fragment(
    run_every=None if refresh == "Off" else refresh
)
def render_dashboard():
    df = load_metrics()

    if df.empty:
        st.warning(
            "No data available. Run save_metrics.py "
            "and check the collector timer."
        )
        return

    now = pd.Timestamp.now(tz="UTC")
    latest = df.iloc[-1]
    age = now - latest["timestamp"]

    cpu = float(latest["cpu_percent"])
    ram = float(latest["ram_percent"])
    disk = float(latest["disk_percent"])

    uptime = float(latest.get("uptime_hours", 0))

    st.subheader("Current Server Metrics")

    if age > pd.Timedelta(hours=2):
        st.warning(
            "Monitoring data is older than 2 hours. "
            "Check your collector."
        )
    else:
        st.caption("Latest measurement is recent.")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("CPU Usage", f"{cpu:.1f}%")
    c2.metric("RAM Usage", f"{ram:.1f}%")
    c3.metric("Disk Usage", f"{disk:.1f}%")
    c4.metric("Uptime", f"{uptime:.1f} hours")

    warning = (
        cpu >= 85
        or ram >= 85
        or disk >= 90
    )

    if warning:
        st.error("⚠️ Server Health: WARNING")
    else:
        st.success("✅ Server Health: HEALTHY")

    if period == "24 Hours":
        filtered = df[
            df["timestamp"]
            >= now - pd.Timedelta(hours=24)
        ]
    elif period == "7 Days":
        filtered = df[
            df["timestamp"]
            >= now - pd.Timedelta(days=7)
        ]
    else:
        filtered = df

    st.subheader("📈 Resource Usage History")

    if filtered.empty:
        st.info("No measurements in selected period.")
    else:
        plot_df = filtered.melt(
            id_vars="timestamp",
            value_vars=[
                "cpu_percent",
                "ram_percent",
                "disk_percent",
            ],
            var_name="Resource",
            value_name="Usage",
        )

        fig = px.line(
            plot_df,
            x="timestamp",
            y="Usage",
            color="Resource",
            markers=True,
            title="Server Resource Utilization",
            labels={
                "timestamp": "Time (UTC)",
                "Usage": "Usage (%)",
            },
        )

        fig.update_layout(
            yaxis_range=[0, 100],
            hovermode="x unified",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.subheader("🚨 Latest Alert State")

    alert_state = load_alert_state()

    if alert_state:
        st.write(
            "Last alert check:",
            alert_state.get("checked_at", "Unknown"),
        )

        st.write(
            "Alert state:",
            alert_state.get("status", "Unknown"),
        )

        metrics = alert_state.get("alert_metrics", [])

        if metrics:
            st.warning(
                "Affected resources: "
                + ", ".join(map(str, metrics))
            )
        else:
            st.info(
                "No active alert metrics in saved state."
            )
    else:
        st.info("No alert state saved yet.")

    st.subheader("📋 Monitoring Records")

    st.dataframe(
        filtered.sort_values(
            "timestamp",
            ascending=False,
        ).head(200),
        use_container_width=True,
        hide_index=True,
    )

    csv = filtered.to_csv(index=False)

    st.download_button(
        "📥 Download CSV",
        data=csv,
        file_name="hermesops_metrics.csv",
        mime="text/csv",
    )

    st.caption(
        f"Last sample (UTC): {latest['timestamp']} | "
        f"Total records: {len(df)}"
    )


render_dashboard()
