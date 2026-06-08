# Portfolio Brief — PTY Flights Pricing

## One-line summary

Production-style Python data pipeline that ingests flight-arrival data, transforms it into demand signals, and delivers operational outputs through Google Calendar and email alerts.

## Why this repo matters

This is a personal business project, but the engineering pattern is directly transferable to DataOps, Application Support and Junior Data Engineering roles:

- external API ingestion;
- scheduled execution on Linux;
- business-rule transformation;
- idempotent updates;
- operational alerting;
- environment-variable configuration;
- runtime documentation.

## Recruiter-facing explanation

> I built and deployed a Python automation pipeline that consumes an external API, transforms raw data into business signals, updates an operational calendar, sends daily alerts and runs automatically on Ubuntu through cron. The project demonstrates API integration, scheduling, idempotency, operational logging and production-style documentation.

## Evidence by skill

| Skill | Evidence in repository |
|---|---|
| Python automation | Main sync script orchestrates API calls, aggregation and outputs |
| API integration | AeroDataBox / RapidAPI and Google Calendar API |
| Scheduled operations | Cron-based daily execution on Ubuntu |
| Alerting | Gmail SMTP HTML digest |
| Idempotency | Calendar events are updated rather than duplicated |
| Business rules | Flight counts converted into pricing-demand tiers |
| Secret hygiene | Runtime values provided through environment variables |
| Documentation | Architecture, setup, results and lessons learned documented |

## Interview angles

### For Application & Data Support

> The project shows how I monitor and operate a scheduled data workflow, reason about retries, avoid duplicate outputs and document production constraints.

### For Junior Data Engineer

> The project shows a complete ingestion-to-output pipeline: external API, Python transformation, scheduled execution and downstream operational consumers.

### For DataOps / MLOps path

> This is the operational pattern I will reuse for banking-data projects: automated ingestion, validation, alerting, idempotency, logs and documentation.

## What this repo is not

- It is not a machine-learning model.
- It is not a pricing engine with automated financial execution.
- It is not a large data platform.
- It is not a substitute for upcoming banking-data and MLOps portfolio repositories.

## Next improvements

| Improvement | Why it matters |
|---|---|
| Add structured logging | Better incident investigation |
| Add lightweight tests | Safer refactoring |
| Add data validation summary | Stronger DataOps signal |
| Add retry/backoff handling | More robust external API behavior |
| Add `requirements.txt` if missing | Easier reproducibility |
| Add sanitized sample output | Recruiters can understand the operational result quickly |
