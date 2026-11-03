#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE = Path.home() / "hermes-ai-monitoring"
SCRIPT = BASE / "scripts" / "evaluate_health.py"
OUTPUT = BASE / "reports" / "ai_health_snapshot.json"

result = subprocess.run(
    [sys.executable, str(SCRIPT)],
    capture_output=True,
    text=True,
    check=True,
    timeout=20,
)

metrics = json.loads(result.stdout)

required = [
    "timestamp",
    "cpu_percent",
    "ram_percent",
    "disk_percent",
    "uptime_hours",
    "status",
    "alerts",
]

if not all(key in metrics for key in required):
    raise ValueError("Missing required monitoring fields")

snapshot = {
    "timestamp": metrics["timestamp"],
    "cpu_percent": metrics["cpu_percent"],
    "ram_percent": metrics["ram_percent"],
    "disk_percent": metrics["disk_percent"],
    "uptime_hours": metrics["uptime_hours"],
    "status": metrics["status"],
    "alerts": metrics["alerts"],
    "generated_at": datetime.now(
        timezone.utc
    ).isoformat(),
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

temporary = OUTPUT.with_suffix(".tmp")
temporary.write_text(
    json.dumps(snapshot, indent=2) + "\n",
    encoding="utf-8",
)
temporary.chmod(0o600)
temporary.replace(OUTPUT)

print("AI snapshot generated successfully")
print(json.dumps(snapshot, indent=2))
