#!/usr/bin/env python3
"""
PTY Flights -> Google Calendar + Email Pricing Alert
SOVRALYS / Enzo Chareyron Di Bacco
Cron : 0 11 * * * /usr/bin/python3 /opt/pty_sync/pty_calendar_sync.py >> /var/log/pty_sync.log 2>&1
"""

import os
import requests
import smtplib
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
AIRPORT_ICAO = "MPTO"
CALENDAR_NAME = "PTY Touristes"
DAYS_AHEAD = 7
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "/opt/pty_sync/token.pickle"
CREDENTIALS_FILE = "/opt/pty_sync/credentials.json"
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
LISTING_ID = os.getenv("LISTING_ID", "")
WINDOWS = [("T00:00", "T11:59"), ("T12:00", "T23:59")]

def get_gcal_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("calendar", "v3", credentials=creds)

def get_or_create_calendar(service):
    for cal in service.calendarList().list().execute().get("items", []):
        if cal.get("summary") == CALENDAR_NAME:
            return cal["id"]
    new_cal = service.calendars().insert(body={
        "summary": CALENDAR_NAME,
        "description": "Daily PTY arrivals — pricing signal for short-term rental",
        "timeZone": "America/Panama"
    }).execute()
    return new_cal["id"]

def fetch_arrivals_for_date(date_str):
    headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"}
    arrivals = []
    for (s, e) in WINDOWS:
        url = (f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/{AIRPORT_ICAO}"
               f"/{date_str}{s}/{date_str}{e}?withLeg=true&direction=Arrival"
               f"&withCancelled=false&withCodeshared=false&withCargo=false&withPrivate=false")
        try:
            arrivals.extend(requests.get(url, headers=headers, timeout=15).json().get("arrivals", []))
        except Exception as ex:
            print(f"API error [{date_str}{s}]: {ex}")
    return arrivals

def aggregate_day(arrivals, date_str):
    total = len(arrivals)
    if not total:
        return None
    airlines, origins, hours = defaultdict(int), defaultdict(int), defaultdict(int)
    for v in arrivals:
        airlines[v.get("airline", {}).get("name", "?")] += 1
        origins[v.get("departure", {}).get("airport", {}).get("iata", "?")] += 1
        t = v.get("arrival", {}).get("scheduledTime", {}).get("local", "")
        try:
            hours[int(t[11:13])] += 1
        except Exception:
            pass
    peak_hour = max(hours, key=hours.get) if hours else 0
    top_origins = sorted(origins.items(), key=lambda x: -x[1])[:5]
    top_airlines = sorted(airlines.items(), key=lambda x: -x[1])[:3]
    if total >= 150:
        signal, action, color, cal_color = "HIGH DEMAND", "Create season +30%", "#c0392b", "11"
    elif total >= 80:
        signal, action, color, cal_color = "MODERATE DEMAND", "Hold current price", "#e67e22", "6"
    else:
        signal, action, color, cal_color = "NORMAL TRAFFIC", "Apply last-minute -10%", "#27ae60", "2"
    return {"total": total, "peak_hour": peak_hour, "peak_count": hours.get(peak_hour, 0),
            "signal": signal, "action": action, "color": color, "cal_color": cal_color,
            "top_origins": top_origins, "top_airlines": top_airlines, "date_str": date_str,
            "title": f"PTY {date_str} — {total} arrivals | Peak {peak_hour:02d}h | {signal}"}

def upsert_event(service, calendar_id, agg):
    desc = (f"PTY ARRIVALS — {agg['date_str']}\n"
            f"Total flights : {agg['total']}\nPeak : {agg['peak_hour']:02d}:00 ({agg['peak_count']} flights)\n\n"
            f"Top origins :\n" + "\n".join(f"  {k}: {v}" for k,v in agg["top_origins"]) +
            "\n\nTop airlines :\n" + "\n".join(f"  {k}: {v}" for k,v in agg["top_airlines"]) +
            f"\n\nSIGNAL : {agg['signal']}\nACTION : {agg['action']}\nSource : AeroDataBox / RapidAPI")
    body = {"summary": agg["title"], "description": desc,
            "start": {"date": agg["date_str"], "timeZone": "America/Panama"},
            "end": {"date": agg["date_str"], "timeZone": "America/Panama"},
            "colorId": agg["cal_color"]}
    res = service.events().list(calendarId=calendar_id,
        timeMin=f"{agg['date_str']}T00:00:00-05:00",
        timeMax=f"{agg['date_str']}T23:59:59-05:00",
        q="PTY", singleEvents=True).execute()
    existing = res.get("items", [])
    if existing:
        service.events().update(calendarId=calendar_id, eventId=existing[0]["id"], body=body).execute()
        print(f"Updated [{agg['date_str']}]: {agg['total']} flights")
    else:
        service.events().insert(calendarId=calendar_id, body=body).execute()
        print(f"Created [{agg['date_str']}]: {agg['total']} flights")

def send_pricing_alert(days_data):
    if not GMAIL_PASSWORD:
        print("GMAIL_APP_PASSWORD not set — skipping email")
        return
    today_str = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d")
    rows, actions = "", []
    for agg in [d for d in days_data if d]:
        rows += (f"<tr><td style='padding:8px'>{agg['date_str']}</td>"
                 f"<td style='padding:8px;text-align:center;font-weight:bold'>{agg['total']}</td>"
                 f"<td style='padding:8px;color:{agg['color']}'>{agg['signal']}</td>"
                 f"<td style='padding:8px;color:{agg['color']}'><b>{agg['action']}</b></td></tr>")
        if agg['total'] >= 150:
            actions.append(agg['date_str'])
    alert = ""
    if actions:
        alert = (f"<div style='background:#fff3cd;border-left:4px solid #f39c12;padding:15px;margin:20px 0;border-radius:4px'>"
                 f"<b>{len(actions)} day(s) requiring price adjustment:</b> {' | '.join(actions)}<br><br>"
                 f"<a href='https://app.your.rentals/listings/{LISTING_ID}/rates' "
                 f"style='background:#c0392b;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;font-weight:bold'>"
                 f"Open Your.Rentals Rates</a></div>")
    html = (f"<html><body style='font-family:Arial,sans-serif;max-width:620px;margin:0 auto'>"
            f"<div style='background:#1a1a2e;color:white;padding:20px;border-radius:8px 8px 0 0'>"
            f"<h2 style='margin:0'>PTY Pricing Alert</h2>"
            f"<p style='color:#aaa;margin:5px 0 0'>Short-term rental — Panama City — {today_str}</p></div>"
            f"<div style='background:white;padding:20px;border-radius:0 0 8px 8px'>"
            f"<h3>7-day flight forecast — PTY arrivals</h3>"
            f"<table style='width:100%;border-collapse:collapse'>"
            f"<tr style='background:#f0f0f0'><th style='padding:8px;text-align:left'>Date</th>"
            f"<th style='padding:8px'>Flights</th><th style='padding:8px'>Signal</th>"
            f"<th style='padding:8px;text-align:left'>Action</th></tr>{rows}</table>"
            f"{alert}"
            f"<p style='color:#aaa;font-size:12px'>AeroDataBox API | Cron 06:00 Panama | SOVRALYS</p>"
            f"</div></body></html>")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"PTY Pricing Alert — {today_str}"
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html, "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_USER, GMAIL_PASSWORD)
            s.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())
        print(f"Email sent -> {EMAIL_TO}")
    except Exception as ex:
        print(f"Email error: {ex}")

def main():
    print(f"\n{'='*50}\nPTY FLIGHTS SYNC — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*50}\n")
    service = get_gcal_service()
    calendar_id = get_or_create_calendar(service)
    today = datetime.now(timezone(timedelta(hours=-5))).date()
    days_data = []
    for i in range(DAYS_AHEAD):
        date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"--- {date_str}")
        arrivals = fetch_arrivals_for_date(date_str)
        print(f"  {len(arrivals)} flights")
        if not arrivals:
            days_data.append(None)
            continue
        agg = aggregate_day(arrivals, date_str)
        upsert_event(service, calendar_id, agg)
        days_data.append(agg)
    send_pricing_alert(days_data)
    print("\nSync complete\n")

if __name__ == "__main__":
    main()
