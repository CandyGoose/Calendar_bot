import datetime
import logging

from services.google_calendar import fetch_google_calendar_events
from services.google_sheets import init_google_sheets, fetch_smm_events
from services.todoist import fetch_todoist_tasks


def format_events(events_by_date, days_of_week, today, tomorrow, day_after_tomorrow):
    separator = "\n" + 30 * "-"
    formatted_events = []

    for event_date, events in sorted(events_by_date.items()):
        if event_date > day_after_tomorrow:
            continue

        if event_date < today:
            date_label = "Дедлайн прошел ❌"
        elif event_date == today:
            date_label = "Сегодня"
        elif event_date == tomorrow:
            date_label = "Завтра"
        elif event_date == day_after_tomorrow:
            date_label = "Послезавтра"
        else:
            date_label = ""

        day_of_week = days_of_week[event_date.weekday()]

        formatted_events.append(separator + "\n")
        formatted_events.append(f"<b>{date_label} {event_date.strftime('%d.%m')} ({day_of_week})</b>")
        formatted_events.extend(events)

    formatted_events.append(separator)
    return "\n".join(formatted_events)


def get_events(service, all_days=False):
    logging.info("Fetching and formatting events")

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    logging.info(f"Current time (UTC+3): {now}")

    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = today + datetime.timedelta(days=2)
    three_days_later = today + datetime.timedelta(days=3)

    time_min = now.isoformat() + 'Z'
    time_max = (now + datetime.timedelta(days=3)).isoformat() + 'Z'

    days_of_week = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

    try:
        events_by_date = {}

        todoist_tasks_by_date = fetch_todoist_tasks(all_days)
        for task_date, tasks in todoist_tasks_by_date.items():
            if task_date not in events_by_date:
                events_by_date[task_date] = []
            events_by_date[task_date].extend(tasks)

        data = init_google_sheets()
        smm_events_by_date = fetch_smm_events(data, today)
        for date, events in smm_events_by_date.items():
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].extend(events)

        google_calendar_events = fetch_google_calendar_events(service, time_min, time_max, three_days_later, all_days)
        for date, events in google_calendar_events.items():
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].extend(events)

        if not events_by_date:
            logging.info("No events found for the next few days")
            return 'Нет предстоящих мероприятий следующие 3 дня ✅'

        if today not in events_by_date:
            events_by_date[today] = ['Задач на сегодня нет ✅']

        return format_events(events_by_date, days_of_week, today, tomorrow, day_after_tomorrow)

    except Exception as e:
        logging.error(f"Error fetching or formatting events: {e}")
        raise
