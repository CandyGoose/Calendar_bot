import logging
import datetime
from dateutil import parser
from config import CALENDAR_EMOJIS
from google_calendar import get_all_calendars
from todoist import get_todoist_tasks


def get_events(service, all_days=False):
    logging.info("Fetching and formatting events")
    separator = "\n" + 45 * "-"
    now = datetime.datetime.utcnow()
    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = today + datetime.timedelta(days=2)
    three_days_later = today + datetime.timedelta(days=3)

    time_min = now.isoformat() + 'Z'
    time_max = (now + datetime.timedelta(days=3)).isoformat() + 'Z'

    try:
        all_calendars = get_all_calendars(service)
        events_by_date = {}

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

        todoist_tasks_by_date = get_todoist_tasks(all_days)
        for task_date, tasks in todoist_tasks_by_date.items():
            if task_date not in events_by_date:
                events_by_date[task_date] = []
            events_by_date[task_date].extend(tasks)

        if not events_by_date:
            logging.info("No events found for the next few days")
            return 'Нет предстоящих мероприятий ✅'

        if today not in events_by_date:
            events_by_date[today] = ['Задач на сегодня нет ✅']

        formatted_events = []
        for event_date, events in sorted(events_by_date.items()):
            if event_date < today:
                date_label = "❌ Дедлайн прошел"
            elif event_date == today:
                date_label = "Сегодня"
            elif event_date == tomorrow:
                date_label = "Завтра"
            elif event_date == day_after_tomorrow:
                date_label = "Послезавтра"
            else:
                date_label = ""

            formatted_events.append(separator + "\n")
            formatted_events.append(f"<b>{date_label} {event_date.strftime('%d.%m')}</b>")
            formatted_events.extend(events)

        formatted_events.append(separator)
        logging.info("Events formatted successfully")
        return "\n".join(formatted_events)
    except Exception as e:
        logging.error(f"Error fetching or formatting events: {e}")
        raise
