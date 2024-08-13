import os
import pickle
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import SCOPES


def get_google_calendar_service():
    logging.info("Getting Google Calendar service")
    creds = None
    try:
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
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
