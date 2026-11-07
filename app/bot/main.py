import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.core.config import settings
from app.bot.utils.api_client import api_client

from app.bot.handlers.start import router as start_router
from app.bot.handlers.booking import router as booking_router
from app.bot.handlers.barber import router as barber_router


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
storage = RedisStorage.from_url(settings.redis_fsm_url)
dp = Dispatcher(storage=storage)

dp.include_router(start_router)
dp.include_router(booking_router)
dp.include_router(barber_router)

async def main():
    print("🚀 Telegram-бот BarberBOT успешно запущен в режиме Polling!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())