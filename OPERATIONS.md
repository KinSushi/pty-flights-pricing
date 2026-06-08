# Operations Notes — PTY Flights Pricing

This document records the operational behavior expected from the scheduled flight-pricing pipeline.

## Runtime expectation

| Component | Expected behavior |
|---|---|
| Cron | Runs once per day at 06:00 Panama / 11:00 UTC |
| API ingestion | Fetches flight-arrival data for the rolling 7-day window |
| Aggregation | Computes arrivals, peak hour, top origins and top airlines |
| Calendar output | Upserts all-day events without duplicate entries |
| Email output | Sends an HTML digest to the configured recipient |
| Logs | Appends runtime output to `/var/log/pty_sync.log` |

## Manual run

```bash
python3 pty_calendar_sync.py
```

Use manual execution when:

- cron did not run;
- OAuth credentials were refreshed;
- API behavior changed;
- environment variables were updated;
- the calendar output needs to be regenerated.

## Health checks

```bash
# Cron entry
crontab -l

# Recent logs
tail -n 100 /var/log/pty_sync.log

# Disk pressure
df -h

# Python version
python3 --version

# Environment variables, names only
env | grep -E "RAPIDAPI|GMAIL|EMAIL" | cut -d= -f1
```

## Failure modes

| Symptom | Likely cause | First check |
|---|---|---|
| No calendar update | Cron failure or Google API auth issue | `tail -n 100 /var/log/pty_sync.log` |
| Empty flight response | API endpoint or airport-code issue | Check PTY vs MPTO behavior |
| Email not received | SMTP credentials or recipient config | Verify `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `EMAIL_TO` |
| Duplicate calendar events | Idempotency check failing | Review event lookup/update logic |
| API quota error | Request volume or free-tier limit | Check RapidAPI dashboard |

## Incident note template

```markdown
# Incident: <short title>

## Date / time

YYYY-MM-DD HH:MM local time

## Impact

Which output failed: API ingestion, calendar update, email alert or cron run?

## Symptoms

Log excerpt, error message or missing output.

## Root cause

Technical explanation after investigation.

## Resolution

Steps taken to restore operation.

## Preventive action

What will be changed to avoid recurrence?
```

## Reproducibility improvement backlog

- Add `requirements.txt`.
- Add structured logging.
- Add basic unit tests for demand-tier calculation.
- Add a dry-run mode that prints intended calendar updates without writing them.
- Add sanitized sample email and calendar output screenshots.
