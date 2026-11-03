#!/usr/bin/env python3

import json
import sys
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "hermes-ai-monitoring"
CONFIG = BASE / "config" / "telegram.json"
STATE = BASE / "reports" / "alert_state.json"
MONITOR = BASE / "scripts" / "evaluate_health.py"


def send_telegram(message):
    config = json.loads(CONFIG.read_text())

    url = (
        "https://api.telegram.org/bot"
        + config["bot_token"]
        + "/sendMessage"
    )

    payload = json.dumps({
        "chat_id": config["chat_id"],
        "text": message
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(
        request, timeout=15
    ) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise RuntimeError("Telegram rejected message")


def collect_metrics():
    result = subprocess.run(
        [sys.executable, str(MONITOR)],
        capture_output=True,
        text=True,
        check=True,
        timeout=20
    )

    return json.loads(result.stdout)


def main():
    # Safe one-time connection test.
    if "--test" in sys.argv:
        send_telegram(
            "✅ Telegram monitoring test successful."
        )
        print("Test message sent")
        return

    metrics = collect_metrics()
    alerts = metrics.get("alerts", [])

    current_status = (
        "WARNING" if alerts else "HEALTHY"
    )

    previous_status = None

    if STATE.exists():
        previous_status = json.loads(
            STATE.read_text()
        ).get("status")

    # Send an alert when warning first occurs.
    if current_status == "WARNING":
        current_metrics = sorted(
            a["metric"] for a in alerts
        )

        previous_metrics = []

        if STATE.exists():
            previous_metrics = json.loads(
                STATE.read_text()
            ).get("alert_metrics", [])

        if (
            previous_status != "WARNING"
            or current_metrics != previous_metrics
        ):
            message = "🚨 SERVER HEALTH WARNING\n\n"

            for alert in alerts:
                message += (
                    f"{alert['metric']}: "
                    f"{alert['value']}% "
                    f"(limit {alert['threshold']}%)\n"
                )

            message += (
                "\nCheck SumoPod server resources."
            )

            send_telegram(message)

    # Send recovery notification.
    elif previous_status == "WARNING":
        send_telegram(
            "✅ SERVER RECOVERED\n"
            "CPU, RAM, and disk are below thresholds."
        )

    # Persist state only after successful delivery.
    STATE.parent.mkdir(
        parents=True, exist_ok=True
    )

    STATE.write_text(json.dumps({
        "status": current_status,
        "alert_metrics": sorted(
            a["metric"] for a in alerts
        ),
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat()
    }))

    print("Monitoring completed:", current_status)


if __name__ == "__main__":
    main()
