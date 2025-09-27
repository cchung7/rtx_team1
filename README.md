# rtx_team1

# AQI Predictor – Walking Skeleton

## Overview
This is a team course project that predicts tomorrow’s Air Quality Index (AQI) category - 
    - (Good / Moderate / USG / Unhealthy+) for a county using:
    - **EPA AQI history** (daily summaries)
    - **NWS forecast** (forward-looking weather)

The is simple complete pipeline: ingest --> store --> build features --> train --> predict --> visualize.

---

## Quick Start

Clone the repo and install dependencies:
```bash
git clone <repo-url>
cd rtx_team1
make setup
