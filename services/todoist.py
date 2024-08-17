import datetime
import pytz
from dateutil import parser
from todoist_api_python.api import TodoistAPI
from config.config import LABEL_EMOJIS, TODOIST_TOKEN, PRIORITY_EMOJIS

moscow_tz = pytz.timezone('Europe/Moscow')


def get_todoist_tasks(all_days=False):
    api = TodoistAPI(TODOIST_TOKEN)
    tasks_by_date = {}

    tasks = api.get_tasks()
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(moscow_tz)
    three_days_later = now + datetime.timedelta(days=3)

    for task in tasks:
        if task.due and task.due.date:
            due_date = parser.parse(task.due.date).date()
            if not all_days and due_date > three_days_later.date():
                continue

            due_time = None
            end_time = None
            if task.due.datetime:
                start_time = parser.parse(task.due.datetime)
                if start_time.tzinfo is None:
                    start_time = moscow_tz.localize(start_time)
                else:
                    start_time = start_time.astimezone(moscow_tz)

                due_time = start_time.strftime('%H:%M')

                if task.duration:
                    if task.duration.unit == "minute":
                        end_time = (start_time + datetime.timedelta(minutes=task.duration.amount)).strftime('%H:%M')
                    elif task.duration.unit == "hour":
                        end_time = (start_time + datetime.timedelta(hours=task.duration.amount)).strftime('%H:%M')

            priority_emoji = PRIORITY_EMOJIS.get(task.priority, '▫️️️')
            task_labels = [LABEL_EMOJIS.get(label_name, '') for label_name in task.labels]
            task_labels_text = f"{' '.join(task_labels)}" if task_labels else "✔️"
            if end_time:
                task_description = f"{priority_emoji} {task.content} <u>{due_time} - {end_time}</u> {task_labels_text}"
            elif due_time:
                task_description = f"{priority_emoji} {task.content} <u>{due_time}</u> {task_labels_text}"
            else:
                task_description = f"{priority_emoji} {task.content} {task_labels_text}"

            if due_date not in tasks_by_date:
                tasks_by_date[due_date] = []
            tasks_by_date[due_date].append((task_description, start_time if due_time else None, task.priority))

    for date in tasks_by_date:
        tasks_by_date[date].sort(key=lambda x: (x[1] is not None, x[1], -x[2]))

    formatted_tasks_by_date = {}
    for date, tasks in tasks_by_date.items():
        formatted_tasks_by_date[date] = [task[0] for task in tasks]

    return formatted_tasks_by_date


def fetch_todoist_tasks(all_days):
    return get_todoist_tasks(all_days)
