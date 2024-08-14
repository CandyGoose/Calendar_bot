import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.config import SCOPES, SHEETS

def init_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name("config/calendar.json", SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SHEETS)
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_values()
    return data

def find_dates_above_name(data, name, start_date, start_row=280):
    dates = []
    current_date = start_date

    for row_index in range(start_row - 1, len(data)):
        row = data[row_index]
        for col_index, cell in enumerate(row):
            if cell.strip().lower() == name.lower():
                if row_index > 0:
                    number_above = data[row_index - 1][col_index].strip()
                    try:
                        day = int(number_above)

                        if day < current_date.day:
                            current_date = current_date.replace(month=current_date.month + 1, day=day)
                        else:
                            current_date = current_date.replace(day=day)

                        non_empty_count = 0
                        for i in range(2, 6):
                            if row_index + i < len(data) and data[row_index + i][col_index].strip():
                                non_empty_count += 1

                        dates.append((row_index + 1, col_index + 1, current_date.strftime('%d.%m.%Y'), non_empty_count))
                    except ValueError:
                        continue

    return dates

def fetch_smm_events(data, today):
    start_date = datetime.datetime(2024, 7, 12)
    smm_events_by_date = {}
    smm_events = find_dates_above_name(data, "Вера", start_date, start_row=280)

    for _, _, event_date_str, non_empty_count in smm_events:
        event_date = datetime.datetime.strptime(event_date_str, '%d.%m.%Y').date()

        if event_date < today:
            continue

        smm_summary = f"💻 СММ"
        if non_empty_count > 0:
            smm_summary += f" ({non_empty_count})"

        if event_date not in smm_events_by_date:
            smm_events_by_date[event_date] = []

        smm_events_by_date[event_date].append(smm_summary)

    return smm_events_by_date
