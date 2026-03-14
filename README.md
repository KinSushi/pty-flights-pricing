# PTY Flights Pricing — Real-Time Flight Data Pipeline

> **Stack:** Python · Google Calendar API · AeroDataBox API · Gmail SMTP · Ubuntu · Cron
> **Status:** Production (live since March 2026)
> **Context:** Personal project — short-term rental pricing optimization, Panama City

---

## Problem Statement

Short-term rental platforms (Airbnb, Booking.com) rely on static or delayed pricing signals. Tocumen International Airport (PTY) receives 150–220+ flights/day on peak days — a direct proxy for tourist demand that standard dynamic pricing tools don't fully capture at the local level.

**Goal:** Build an automated pipeline that ingests real-time flight arrival data and translates it into actionable pricing signals, updated daily with zero manual intervention.

---

## Architecture

```
AeroDataBox API (RapidAPI)
        ↓
REST polling — 2 calls/day per date × 7-day rolling window
        ↓
Python Pipeline (Ubuntu 24.04 / OVH VPS)
        ↓
Aggregation: total arrivals, peak hour, top origins, top airlines
        ↓
Google Calendar API v3
        ↓
Upsert daily events — color-coded by demand signal
        ↓
Gmail SMTP
        ↓
HTML pricing alert email with direct property management deep-link

Cron (06:00 Panama / 11:00 UTC) — fully automated
```

---

## Key Features

- **Rolling 7-day forecast** — fetches confirmed schedules daily as data matures
- **Smart aggregation** — peak hour detection, origin breakdown, airline distribution
- **3-tier pricing signal** — HIGH (150+ flights) / MODERATE (80–150) / NORMAL (<80)
- **Google Calendar integration** — color-coded all-day events with full stats
- **HTML email alert** — daily digest with direct action link to property manager
- **Idempotent upserts** — safe re-runs, updates existing events without duplicates
- **Zero secrets in code** — fully environment-variable driven

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Flight data | AeroDataBox via RapidAPI (free tier — 2000 req/month) |
| Calendar | Google Calendar API v3 (OAuth2 + token refresh) |
| Email | Gmail SMTP over SSL (App Password) |
| Infra | Ubuntu 24.04, OVH VPS, cron |
| Auth | google-auth-oauthlib, token.pickle with auto-refresh |

---

## Setup

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 \
            google-api-python-client requests

export RAPIDAPI_KEY="..."
export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PASSWORD="..."
export EMAIL_TO="your@gmail.com"

python3 pty_calendar_sync.py

# Cron — daily 06:00 Panama = 11:00 UTC
0 11 * * * /usr/bin/python3 /opt/pty_sync/pty_calendar_sync.py >> /var/log/pty_sync.log 2>&1
```

---

## Results

- 7-day forward demand visibility updated daily
- Zero manual data collection
- ~420 API calls/month — within free tier
- Integrated with existing property management workflow (Your.Rentals + PriceLabs)

---

## Lessons Learned

- AeroDataBox IATA endpoint returns empty for PTY — ICAO code (MPTO) required
- Google OAuth token expires in 7 days (Test mode) — renewal reminder scheduled
- Rolling window outperforms static lookups for dynamic pricing use cases

---

## Author

Enzo Chareyron Di Bacco — SOVRALYS LLC
AI/Data Engineering trajectory — Panama City
github.com/KinSushi
