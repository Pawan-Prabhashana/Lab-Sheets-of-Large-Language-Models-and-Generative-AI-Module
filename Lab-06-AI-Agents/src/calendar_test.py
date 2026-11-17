# calendar_test.py — verify Google Calendar OAuth (read + write)
import os.path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CAL_TZ = "Asia/Colombo"

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)   # opens your browser once
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def main():
    service = get_calendar_service()
    tz = ZoneInfo(CAL_TZ)

    # 1) WRITE: create a test event tomorrow at 15:00
    start = (datetime.now(tz) + timedelta(days=1)).replace(
        hour=15, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    event = {
        "summary": "Lab 6 Test Event",
        "start": {"dateTime": start.isoformat(), "timeZone": CAL_TZ},
        "end": {"dateTime": end.isoformat(), "timeZone": CAL_TZ},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    print("Created:", created.get("summary"), "->", created.get("htmlLink"))

    # 2) READ: list the next 2 days
    now = datetime.now(tz)
    later = now + timedelta(days=2)
    events = service.events().list(
        calendarId="primary", timeMin=now.isoformat(), timeMax=later.isoformat(),
        singleEvents=True, orderBy="startTime").execute().get("items", [])
    print("\nUpcoming events:")
    for e in events:
        s = e["start"].get("dateTime", e["start"].get("date"))
        print(" ", s, "-", e.get("summary", "(no title)"))

if __name__ == "__main__":
    main()
