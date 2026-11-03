import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "hermes-ai-monitoring"
REPORTS = BASE / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

script = BASE / "scripts" / "evaluate_health.py"

result = subprocess.run(
    [sys.executable, str(script)],
    capture_output=True,
    text=True,
    timeout=20,
    check=True,
)

metrics = json.loads(result.stdout)

filename = datetime.now(timezone.utc).strftime(
    "server_metrics_%Y-%m.jsonl"
)

output = REPORTS / filename

with output.open("a", encoding="utf-8") as file:
    file.write(json.dumps(metrics) + "\n")

print("Metrics saved:", output)
print("Server status:", metrics["status"])
print("Alerts:", len(metrics["alerts"]))
