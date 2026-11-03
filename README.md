# HermesOps — Self-Hosted AI Server Monitoring & Telegram Automation

A Python-based server monitoring and automation project running on an Ubuntu VPS. It combines resource monitoring, threshold-based alerts, Telegram notifications, an interactive Streamlit dashboard, and an optional AI analysis layer powered by Hermes Agent and OpenRouter.

## Project Overview

HermesOps was developed to explore the integration of Linux infrastructure, Python automation, monitoring dashboards, messaging APIs, and LLM-based analysis.

The monitoring and alerting components operate independently of the AI provider, allowing server health checks to continue even when an LLM API is temporarily rate-limited.

## Technology Stack

| Category | Technology |
|---|---|
| Programming | Python 3 |
| Infrastructure | Ubuntu Linux VPS (SumoPod) |
| AI Agent | Hermes Agent |
| LLM Provider | OpenRouter |
| Notifications | Telegram Bot API |
| Dashboard | Streamlit, Plotly, pandas |
| Automation | systemd services and timers |
| Testing | Python unittest |
| Version Control | Git & GitHub |

## Core Features

- CPU, RAM, disk utilization, and uptime monitoring
- JSON and JSONL metrics collection
- Configurable threshold-based health evaluation
- Telegram alert and recovery notifications
- Duplicate alert suppression
- Scheduled monitoring with systemd
- Interactive dashboard and CSV export
- Read-only health snapshots for AI analysis

## System Architecture

Ubuntu VPS → Python Metrics Collector → JSONL Storage

- JSONL Storage → Streamlit Dashboard
- Health Evaluation → Telegram Alert System
- Health Snapshot → Hermes Agent → OpenRouter → Telegram

The monitoring and alerting pipelines do not require OpenRouter API availability.

## Verified Test Results

Five automated unit tests passed:

| Test Case | Result |
|---|---|
| Normal resource status | PASS |
| High CPU alert generation | PASS |
| Duplicate alert suppression | PASS |
| Recovery notification | PASS |
| Simulated notification failure | PASS |

**Unit Test Results:** 5/5 passed (100%)

**Execution Time:** 0.006 seconds for the recorded unit-test run.

These results validate specific application logic using simulated inputs and mocked notifications. They do not represent production uptime or real Telegram delivery latency.

## Example Monitoring Snapshot

Recorded on November 3, 2026:

| Metric | Recorded Value |
|---|---:|
| CPU Usage | 1.01% |
| RAM Usage | 45.02% |
| Disk Usage | 36.47% |
| Uptime | 1.23 hours |
| Health Status | HEALTHY |

## Getting Started

1. Provision an Ubuntu Linux environment.
2. Clone this repository.
3. Create a Python virtual environment.
4. Install dependencies using `pip install -r requirements.txt`.
5. Configure Telegram credentials privately using `config/telegram.json`.
6. Run the monitoring scripts under `scripts/`.
7. Run `python -m unittest discover -s tests -v`.
8. Start Streamlit with `streamlit run dashboard/app.py`.

The included systemd configurations and deployment guidance should be reviewed and adapted before production use.

## Security

- API tokens are excluded from version control.
- Monitoring scripts use read-only system information.
- Streamlit is intended to be accessed through a secured SSH tunnel.
- Telegram credentials must not be hardcoded into public source files.
- AI responses are advisory and do not authorize privileged server operations.

## Limitations

- Monitoring intervals affect alert detection latency.
- Telegram delivery depends on external network availability.
- The current alert implementation provides basic state-based deduplication.
- AI features depend on available OpenRouter models and rate limits.
- Continuous uptime and reboot-recovery verification require separate operational testing.

## Roadmap

- [x] Implement resource monitoring
- [x] Implement Telegram API integration
- [x] Pass five monitoring and alert unit tests
- [x] Generate structured AI health snapshots
- [ ] Complete dashboard deployment verification
- [ ] Complete automated timer reliability testing
- [ ] Verify Hermes analysis against live snapshots
- [ ] Add extended monitoring and reliability metrics

## Disclaimer

This repository documents an engineering portfolio project and is not a fully managed production observability platform.
