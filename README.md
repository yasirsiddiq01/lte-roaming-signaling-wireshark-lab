---
title: LTE Roaming Signaling Troubleshooting Lab
emoji: 📡
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8501
pinned: false
tags:
  - streamlit
  - telecom
  - roaming
  - wireshark
---


# LTE Roaming Signaling and Wireshark Troubleshooting Lab

This is a self-directed telecom integration lab for analyzing simulated LTE roaming signaling events.

The project is designed to demonstrate basic understanding of roaming integration testing, signaling troubleshooting, Wireshark-style investigation, and technical reporting.

## Purpose

The lab simulates roaming signaling sessions and detects integration issues such as:

* authentication timeout
* missing signaling events
* APN mismatch
* GTP session setup failure
* unconfigured roaming partner
* high signaling latency
* missing charging trigger

## Project Scope

This project uses simulated signaling event data. It does not use real operator PCAP files, private subscriber data, or confidential roaming traces.

## Main Components

* `data/mock_roaming_signaling_events.csv` — simulated roaming signaling events
* `src/signaling_analyzer.py` — analyzes sessions and detects issues
* `reports/signaling_issues.csv` — generated issue report
* `reports/session_summary.csv` — generated session-level summary
* `docs/wireshark_filters.md` — Wireshark filters for LTE roaming troubleshooting
* `run_project.py` — runs the analysis pipeline

## How to Run

```bash
python run_project.py
```

## Generated Outputs

After running the project, check:

```text
reports/signaling_issues.csv
reports/session_summary.csv
```

## Relevance

This project supports portfolio preparation for technical roaming integration roles by covering:

* LTE roaming signaling flow analysis
* Diameter and GTPv2 troubleshooting concepts
* APN/session failure investigation
* Wireshark filter documentation
* integration issue reporting
* technical test documentation

## Disclaimer

This is a portfolio learning project. It is not a production telecom system and does not process real roaming traffic.
