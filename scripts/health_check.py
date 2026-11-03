#!/usr/bin/env python3

import json
import os
import shutil
import time
from datetime import datetime, timezone


def read_cpu_times():
    with open("/proc/stat", encoding="utf-8") as f:
        values = list(map(int, f.readline().split()[1:]))

    idle = values[3] + values[4]
    return sum(values), idle


def cpu_usage():
    total1, idle1 = read_cpu_times()
    time.sleep(1)
    total2, idle2 = read_cpu_times()

    delta_total = total2 - total1
    delta_idle = idle2 - idle1

    if delta_total == 0:
        return 0.0

    return round(
        100 * (1 - delta_idle / delta_total), 2
    )


def memory_usage():
    mem = {}

    with open("/proc/meminfo", encoding="utf-8") as f:
        for line in f:
            key, value = line.split(":", 1)
            mem[key] = int(value.strip().split()[0])

    total = mem["MemTotal"]
    available = mem["MemAvailable"]

    return round(100 * (total - available) / total, 2)


def disk_usage():
    disk = shutil.disk_usage("/")
    return round(100 * disk.used / disk.total, 2)


def get_uptime():
    with open("/proc/uptime", encoding="utf-8") as f:
        return round(float(f.read().split()[0]) / 3600, 2)


def main():
    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": cpu_usage(),
        "ram_percent": memory_usage(),
        "disk_percent": disk_usage(),
        "uptime_hours": get_uptime(),
    }

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
