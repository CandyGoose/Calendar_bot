import datetime
import logging

from services.google_calendar import fetch_google_calendar_events
from services.google_sheets import init_google_sheets, fetch_smm_events
from services.todoist import fetch_todoist_tasks


def format_events(events_by_date, days_of_week, today, tomorrow, day_after_tomorrow):
    separator = "\n" + 35 * "="
    formatted_events = []

    for event_date, sources in sorted(events_by_date.items()):
        if event_date < today:
            date_label = "Дедлайн прошел ❌"
        elif event_date == today:
            date_label = "Сегодня"
        elif event_date == tomorrow:
            date_label = "Завтра"
        elif event_date == day_after_tomorrow:
            date_label = "Послезавтра"
        else:
            date_label = event_date.strftime('%d.%m')

        day_of_week = days_of_week[event_date.weekday()]

        formatted_events.append(separator + "\n")
        formatted_events.append(f"<b>{date_label} {event_date.strftime('%d.%m')} ({day_of_week})</b>")

        if event_date.weekday() == 0:
            formatted_events.append("\n<b><i>----- Megabyte -----</i></b>")
            formatted_events.append("💻 Vk")
        elif event_date.weekday() == 4:
            formatted_events.append("\n<b><i>----- Megabyte -----</i></b>")
            formatted_events.append("💻 Vk/Tg")

        if sources.get('sheets'):
            formatted_events.append("\n<b><i>----- IS -----</i></b>")
            formatted_events.extend(sources['sheets'])

        if sources.get('todoist'):
            formatted_events.append("\n<b><i>----- Todoist -----</i></b>")
            formatted_events.extend(sources['todoist'])

        if sources.get('calendar'):
            formatted_events.append("\n<b><i>----- Google Calendar -----</i></b>")
            formatted_events.extend(sources['calendar'])

        if 'general' in sources:
            formatted_events.extend(sources['general'])

    formatted_events.append(separator)
    return "\n".join(formatted_events)


def get_events(service, all_days=False, today_only=False):
    logging.info("Fetching and formatting events")

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    logging.info(f"Current time (UTC+3): {now}")

    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = today + datetime.timedelta(days=2)
    three_days_later = today + datetime.timedelta(days=3)

    time_min = now.isoformat() + 'Z'
    time_max = (now + datetime.timedelta(days=3)).isoformat() + 'Z' if not all_days else None

    days_of_week = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

    try:
        events_by_date = {}

        # Google Sheets
        data = init_google_sheets()
        smm_events_by_date = fetch_smm_events(data, today)
        for date, events in smm_events_by_date.items():
            if (today_only and date > today) or (not all_days and date > day_after_tomorrow):
                continue
            events_by_date.setdefault(date, {}).setdefault('sheets', []).extend(events)

        # Todoist
        todoist_tasks_by_date = fetch_todoist_tasks(all_days)
        for task_date, tasks in todoist_tasks_by_date.items():
            if (today_only and task_date > today) or (not all_days and task_date > day_after_tomorrow):
                continue
            events_by_date.setdefault(task_date, {}).setdefault('todoist', []).extend(tasks)

        # Google Calendar
        google_calendar_events = fetch_google_calendar_events(service, time_min, time_max, three_days_later, all_days)
        for date, events in google_calendar_events.items():
            if (today_only and date > today) or (not all_days and date > day_after_tomorrow):
                continue
            events_by_date.setdefault(date, {}).setdefault('calendar', []).extend(events)

        if not events_by_date:
            logging.info("No events found for the next few days")
            return 'Нет предстоящих мероприятий следующие 3 дня ✅'

        if today not in events_by_date or not any(events_by_date[today].values()):
            events_by_date[today] = {"general": ["Задач на сегодня нет ✅"]}

        return format_events(events_by_date, days_of_week, today, tomorrow, day_after_tomorrow)

    except Exception as e:
        logging.error(f"Error fetching or formatting events: {e}")
        raise
