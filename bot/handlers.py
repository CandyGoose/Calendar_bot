import logging

from aiogram import Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from bot.events_formatter import get_events
from config.config import AUTHORIZED_USER_IDS
from services.google_calendar import get_google_calendar_service


async def start(message: types.Message):
    logging.info(f"Received /start command from user {message.from_user.id}")
    if message.from_user.id not in AUTHORIZED_USER_IDS:
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return
    await message.answer('Привет! Используй команду /events, чтобы получить список мероприятий.')


async def events(message: types.Message):
    logging.info(f"Received /events command from user {message.from_user.id}")
    if message.from_user.id not in AUTHORIZED_USER_IDS:
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return
    try:
        service = get_google_calendar_service()
        events = get_events(service)
        await message.answer(events, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Error fetching events: {e}")
        await message.answer("Произошла ошибка при получении мероприятий.")


async def all_events(message: types.Message):
    logging.info(f"Received /all_events command from user {message.from_user.id}")
    if message.from_user.id not in AUTHORIZED_USER_IDS:
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return
    try:
        service = get_google_calendar_service()
        events = get_events(service, all_days=True)
        await message.answer(events, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Error fetching all events: {e}")
        await message.answer("Произошла ошибка при получении всех мероприятий.")


def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command("start"))
    dp.message.register(events, Command("events"))
    dp.message.register(all_events, Command("all_events"))
