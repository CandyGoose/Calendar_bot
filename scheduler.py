import logging
import asyncio
from datetime import datetime, time, timedelta
from google_calendar import get_google_calendar_service
from events_formatter import get_events
from aiogram import Bot
from config import AUTHORIZED_USER_IDS


async def send_daily_events(bot: Bot):
    logging.info("Sending daily events at 07:00")
    try:
        service = get_google_calendar_service()
        events = get_events(service)
        for chat_id in AUTHORIZED_USER_IDS:
            await bot.send_message(chat_id, events, parse_mode="HTML")
        logging.info("Daily events sent successfully")
    except Exception as e:
        logging.error(f"Error sending daily events: {e}")


async def scheduler(bot: Bot):
    while True:
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(7, 0))

        if now >= target_time:
            target_time += timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        logging.info(f"Waiting for {wait_time / 60:.2f} minutes until 07:00")
        await asyncio.sleep(wait_time)

        await send_daily_events(bot)


def schedule_jobs(bot: Bot):
    logging.info("Starting the scheduler")
    asyncio.create_task(scheduler(bot))
