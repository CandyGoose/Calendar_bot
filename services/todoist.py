import datetime

from dateutil import parser
from todoist_api_python.api import TodoistAPI

from config.config import LABEL_EMOJIS, TODOIST_TOKEN


def get_todoist_tasks(all_days=False):
    api = TodoistAPI(TODOIST_TOKEN)
    tasks_by_date = {}

    tasks = api.get_tasks()
    now = datetime.datetime.utcnow()
    three_days_later = now + datetime.timedelta(days=3)

    for task in tasks:
        if task.due and task.due.date:
            due_date = parser.parse(task.due.date).date()
            if not all_days and due_date > three_days_later.date():
                continue
            due_time = parser.parse(task.due.datetime).strftime('%H:%M') if task.due.datetime else ""
            task_labels = [LABEL_EMOJIS.get(label_name, '') for label_name in task.labels]
            task_labels_text = f"{' '.join(task_labels)}" if task_labels else "✔️"
            task_description = f"{task_labels_text} {task.content} <u>{due_time}</u>"

            if due_date not in tasks_by_date:
                tasks_by_date[due_date] = []
            tasks_by_date[due_date].append((task_description, task_labels))

    for date in tasks_by_date:
        tasks_by_date[date].sort(key=lambda x: x[1])

    formatted_tasks_by_date = {}
    for date, tasks in tasks_by_date.items():
        formatted_tasks_by_date[date] = [task[0] for task in tasks]

    return formatted_tasks_by_date


def fetch_todoist_tasks(all_days):
    return get_todoist_tasks(all_days)
