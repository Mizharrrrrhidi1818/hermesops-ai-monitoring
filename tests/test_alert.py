import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


BASE = Path.home() / "hermes-ai-monitoring"
SCRIPT = BASE / "scripts" / "telegram_alert.py"

spec = importlib.util.spec_from_file_location(
    "telegram_alert", SCRIPT
)
alert = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alert)


def sample_metrics(cpu=20, ram=35, disk=40):
    values = {
        "cpu_percent": cpu,
        "ram_percent": ram,
        "disk_percent": disk,
    }

    limits = {
        "cpu_percent": 85,
        "ram_percent": 85,
        "disk_percent": 90,
    }

    warnings = [
        {
            "metric": key,
            "value": value,
            "threshold": limits[key],
        }
        for key, value in values.items()
        if value >= limits[key]
    ]

    return {
        **values,
        "uptime_hours": 12,
        "status": "WARNING" if warnings else "HEALTHY",
        "alerts": warnings,
    }


class TestTelegramAlert(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.state = Path(self.temp.name) / "state.json"
        self.state_patch = patch.object(
            alert, "STATE", self.state
        )
        self.state_patch.start()
        self.addCleanup(self.state_patch.stop)

        self.messages = []

        self.sender_patch = patch.object(
            alert, "send_telegram",
            side_effect=self.messages.append
        )
        self.sender_patch.start()
        self.addCleanup(self.sender_patch.stop)

    def run_metrics(self, metrics):
        with patch.object(
            alert, "collect_metrics",
            return_value=metrics
        ):
            alert.main()

    def test_normal_status(self):
        self.run_metrics(sample_metrics())
        self.assertEqual(len(self.messages), 0)

    def test_high_cpu_warning(self):
        self.run_metrics(sample_metrics(cpu=95))
        self.assertEqual(len(self.messages), 1)
        self.assertIn("WARNING", self.messages[0])

    def test_no_duplicate_alert(self):
        self.run_metrics(sample_metrics(cpu=95))
        self.run_metrics(sample_metrics(cpu=96))
        self.assertEqual(len(self.messages), 1)

    def test_recovery_notification(self):
        self.run_metrics(sample_metrics(cpu=95))
        self.run_metrics(sample_metrics(cpu=20))

        self.assertEqual(len(self.messages), 2)
        self.assertIn("RECOVERED", self.messages[1])

    def test_failed_delivery_does_not_save_state(self):
        with patch.object(
            alert,
            "send_telegram",
            side_effect=RuntimeError("Simulated failure")
        ):
            with self.assertRaises(RuntimeError):
                self.run_metrics(sample_metrics(cpu=95))

        self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
