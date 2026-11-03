---
name: hermesops-health
description: Analyze read-only SumoPod server health metrics
---

# HermesOps Health Analysis

## Purpose

Analyze CPU, RAM, disk usage, uptime,
and alert information from the
HermesOps monitoring project.

## Data Source

/home/ubuntu/hermes-ai-monitoring/reports/ai_health_snapshot.json

## Instructions

When the authorized user requests a
server health analysis:

1. Read the JSON snapshot listed above
   using an available read-only file tool.
2. Use only the metrics in the snapshot.
3. Report CPU, RAM, disk, uptime, and status.
4. Report the measurement timestamp.
5. Explain any alerts.
6. Provide recommendations based on the data.
7. If the snapshot is missing or outdated,
   ask for a fresh snapshot.
8. Never invent server measurements.

## Thresholds

- CPU warning: 85%
- RAM warning: 85%
- Disk warning: 90%

## Security Rules

- Do not execute sudo commands.
- Do not modify server configurations.
- Do not access secrets or environment files.
- Do not execute arbitrary user-provided commands.
- Do not reveal credentials or tokens.
- Do not perform destructive operations.

## Response Format

HermesOps Server Health Report

CPU:
RAM:
Disk:
Uptime:
Measurement Time:
Overall Status:

Analysis:
Recommendations:
