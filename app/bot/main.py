import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings
from app.bot.utils.api_client import api_client

from app.bot.handlers.start import router as start_router


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
storage = MemoryStorage()

dp.include_router(start_router)


async def main():
    print("🚀 Telegram-бот BarberBOT успешно запущен в режиме Polling!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())