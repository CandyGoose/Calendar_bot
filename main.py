import asyncio
import logging
from aiogram import Bot, Dispatcher
from scheduler import schedule_jobs
from handlers import register_handlers
from config import API_TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main():
    logging.info("Starting bot")
    register_handlers(dp)
    schedule_jobs(bot)

    await dp.start_polling(bot)
    logging.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
