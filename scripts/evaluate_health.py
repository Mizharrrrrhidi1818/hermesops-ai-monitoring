#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

script = Path(__file__).with_name("health_check.py")

result = subprocess.run(
    [sys.executable, str(script)],
    capture_output=True,
    text=True,
    check=True,
    timeout=15,
)

metrics = json.loads(result.stdout)

thresholds = {
    "cpu_percent": 85,
    "ram_percent": 85,
    "disk_percent": 90,
}

alerts = []

for metric, threshold in thresholds.items():
    if metrics[metric] >= threshold:
        alerts.append({
            "metric": metric,
            "value": metrics[metric],
            "threshold": threshold
        })

metrics["status"] = "WARNING" if alerts else "HEALTHY"
metrics["alerts"] = alerts

print(json.dumps(metrics, indent=2))
