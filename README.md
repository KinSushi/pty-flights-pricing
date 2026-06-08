# PTY Flights Pricing — Operational Data Pipeline

<div align="center">

**Python automation pipeline turning flight-arrival data into daily pricing signals**

Python · REST APIs · Google Calendar · Email alerting · Ubuntu · Cron · Idempotent updates

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-E95420?style=flat&logo=ubuntu&logoColor=white)
![Cron](https://img.shields.io/badge/Cron-Scheduled%20Job-2EA043?style=flat)
![Google Calendar](https://img.shields.io/badge/Google%20Calendar-API%20v3-4285F4?style=flat&logo=googlecalendar&logoColor=white)
![Gmail](https://img.shields.io/badge/Gmail-SMTP-EA4335?style=flat&logo=gmail&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live%20since%20Mar%202026-2EA043?style=flat)

</div>

---

## Executive summary

This repository documents a production-style Python data pipeline that ingests flight-arrival data for Tocumen International Airport, transforms it into demand indicators, and pushes the result into operational tools: Google Calendar and daily email alerts.

The business use case is short-term rental pricing in Panama City, but the engineering pattern is transferable to DataOps and banking-data roles: API ingestion, scheduling, idempotent updates, business-rule transformation, alerting, operational logs and secret hygiene.

---

## Documentation index

| Document | Purpose |
|---|---|
| [PORTFOLIO.md](PORTFOLIO.md) | Recruiter-facing explanation of the DataOps signal |
| [OPERATIONS.md](OPERATIONS.md) | Runtime expectations, health checks, failure modes and incident template |
| [README.md](README.md) | Architecture, setup, operational controls and portfolio bridge |

---

## Problem statement

Short-term rental platforms often rely on static or delayed pricing signals. Tocumen International Airport (PTY / MPTO) receives a high daily volume of arrivals, which can act as a local proxy for short-term demand.

**Goal:** build an automated pipeline that ingests flight-arrival data and translates it into actionable pricing signals, updated daily with zero manual data collection.

---

## Architecture

```text
AeroDataBox API via RapidAPI
        |
        | REST polling — rolling 7-day window
        v
Python pipeline on Ubuntu
        |
        | Validate response · aggregate arrivals · derive demand tier
        v
Operational outputs
        |
        |-- Google Calendar API v3
        |     |-- idempotent event upserts
        |     +-- color-coded demand signals
        |
        +-- Gmail SMTP
              +-- HTML alert email with direct action link

Cron schedule: daily at 06:00 Panama / 11:00 UTC
```

---

## Key features

| Feature | Engineering signal |
|---|---|
| Rolling 7-day forecast | Handles data maturation and avoids static one-shot collection |
| REST API ingestion | External API integration, request handling and data extraction |
| Smart aggregation | Peak hour, origin breakdown, airline distribution and total arrivals |
| 3-tier demand signal | Business-rule transformation into HIGH / MODERATE / NORMAL |
| Idempotent Google Calendar upserts | Safe re-runs without duplicate events |
| HTML email alert | Automated operational notification with direct action link |
| Cron automation | Scheduled production-style execution on Ubuntu |
| Environment-variable configuration | No secrets committed in code |

---

## Why this matters for DataOps / banking-data roles

Although this is a personal business project, the pattern matches production data work:

| Banking/DataOps skill | Evidence in this repo |
|---|---|
| API ingestion | External data pulled from AeroDataBox / RapidAPI |
| Scheduled jobs | Daily cron execution on Ubuntu |
| Data validation | Response parsing and demand-signal computation |
| Operational alerting | HTML email digest generated automatically |
| Idempotency | Calendar events are updated rather than duplicated |
| Workflow integration | Data output is pushed into existing operational tools |
| Secret hygiene | Credentials loaded through environment variables |
| Documentation | Architecture, setup, lessons learned and operational constraints documented |

This repo is therefore positioned as a production-data automation artifact, not just a local script.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Flight data | AeroDataBox via RapidAPI |
| Calendar output | Google Calendar API v3 |
| Email output | Gmail SMTP over SSL |
| Runtime | Ubuntu 24.04 |
| Scheduler | cron |
| Auth | OAuth2 token refresh + environment variables |

---

## Setup

```bash
# Install dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 \
            google-api-python-client requests

# Runtime configuration
export RAPIDAPI_KEY="..."
export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PASSWORD="..."
export EMAIL_TO="your@gmail.com"

# Run manually
python3 pty_calendar_sync.py

# Cron — daily 06:00 Panama = 11:00 UTC
0 11 * * * /usr/bin/python3 /opt/pty_sync/pty_calendar_sync.py >> /var/log/pty_sync.log 2>&1
```

---

## Operational controls

| Control | Purpose |
|---|---|
| Idempotent event update | Avoid calendar duplication after retries or re-runs |
| Rolling-window polling | Refreshes near-term dates as airline schedules mature |
| Log redirection | Preserves execution history through `/var/log/pty_sync.log` |
| Environment variables | Keeps secrets outside version control |
| Free-tier awareness | Keeps estimated API usage below expected limits |
| Manual execution path | Allows troubleshooting outside cron |

---

## Results

- 7-day forward demand visibility updated daily.
- Zero manual data collection after deployment.
- Estimated API usage kept within the free-tier envelope.
- Calendar and email outputs integrated into the existing pricing workflow.
- Operational pattern reusable for future DataOps projects.

---

## Lessons learned

- AeroDataBox IATA endpoint returned empty results for PTY; the ICAO code MPTO was required.
- Google OAuth token behavior required explicit attention to refresh and test-mode limitations.
- Rolling windows are more robust than static lookups for demand-signal workflows.
- Idempotent writes are essential for scheduled jobs that may be retried.

---

## Portfolio bridge

This repo supports the broader Swiss banking/data portfolio by proving:

1. Python automation on a Linux runtime.
2. API-to-business-signal transformation.
3. Scheduled execution and operational alerting.
4. Documentation of constraints and production behavior.

Next portfolio step: apply the same engineering pattern to banking-style datasets in `banking-dataops-monitoring` and `fraud-mlops-control-tower`.

---

## Author

Enzo Chareyron Di Bacco — KinSushi  
Data / MLOps trajectory — regulated financial systems focus
