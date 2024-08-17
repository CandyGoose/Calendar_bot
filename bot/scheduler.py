import asyncio
import logging
from datetime import datetime, time, timedelta

from aiogram import Bot

from bot.events_formatter import get_events
from config.config import AUTHORIZED_USER_IDS
from services.google_calendar import get_google_calendar_service


async def send_morning_events(bot: Bot):
    logging.info("Sending morning events at 07:00")
    try:
        service = get_google_calendar_service()
        events = get_events(service, today_only=True)
        for chat_id in AUTHORIZED_USER_IDS:
            await bot.send_message(chat_id, events, parse_mode="HTML")
        logging.info("Morning events sent successfully")
    except Exception as e:
        logging.error(f"Error sending morning events: {e}")


async def send_evening_events(bot: Bot):
    logging.info("Sending evening events at 23:00")
    try:
        service = get_google_calendar_service()
        events = get_events(service, all_days=True)
        for chat_id in AUTHORIZED_USER_IDS:
            await bot.send_message(chat_id, events, parse_mode="HTML")
        logging.info("Evening events sent successfully")
    except Exception as e:
        logging.error(f"Error sending evening events: {e}")


async def scheduler(bot: Bot):
    while True:
        now = datetime.now()
        morning_target_time = datetime.combine(now.date(), time(7, 0))
        evening_target_time = datetime.combine(now.date(), time(23, 0))

        if now >= morning_target_time:
            morning_target_time += timedelta(days=1)
        if now >= evening_target_time:
            evening_target_time += timedelta(days=1)

        next_run_time = min(morning_target_time, evening_target_time)
        wait_time = (next_run_time - now).total_seconds()

        await asyncio.sleep(wait_time)

        if next_run_time == morning_target_time:
            await send_morning_events(bot)
        elif next_run_time == evening_target_time:
            await send_evening_events(bot)


def schedule_jobs(bot: Bot):
    logging.info("Starting the scheduler")
    asyncio.create_task(scheduler(bot))
