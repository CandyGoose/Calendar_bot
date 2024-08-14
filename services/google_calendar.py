import logging
import os
import pickle

from dateutil import parser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.config import CALENDAR_EMOJIS
from config.config import SCOPES


def get_google_calendar_service():
    logging.info("Getting Google Calendar service")
    creds = None
    try:
        if os.path.exists('config/token.pickle'):
            with open('config/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'config/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('config/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        logging.info("Google Calendar service obtained successfully")
        return service
    except Exception as e:
        logging.error(f"Error getting Google Calendar service: {e}")
        raise


def get_all_calendars(service):
    logging.info("Fetching all calendars")
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        logging.info(f"Fetched {len(calendars)} calendars")
        return calendars
    except Exception as e:
        logging.error(f"Error fetching calendars: {e}")
        raise


def fetch_google_calendar_events(service, time_min, time_max, three_days_later, all_days):
    events_by_date = {}
    all_calendars = get_all_calendars(service)

    for calendar in all_calendars:
        calendar_id = calendar['id']
        calendar_name = calendar['summary']

        if calendar_name == 'Todo':
            continue

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max if not all_days else None,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if events:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                if 'dateTime' in event['start']:
                    start_time = parser.parse(start).strftime('%H:%M')
                    end_time = parser.parse(end).strftime('%H:%M')
                else:
                    start_time = parser.parse(start).strftime('')
                    end_time = parser.parse(end).strftime('')
                dash = "-" if end_time else ""
                event_date = parser.parse(start).date()

                if not all_days and event_date > three_days_later:
                    continue

                emoji = CALENDAR_EMOJIS.get(calendar_name, '')
                event_summary = f"{emoji} {event['summary']} <u>{start_time}{dash}{end_time}</u>"

                if event_date not in events_by_date:
                    events_by_date[event_date] = []

                events_by_date[event_date].append(event_summary)

    return events_by_date
