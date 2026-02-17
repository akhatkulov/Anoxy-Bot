import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from dotenv import load_dotenv

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from core.database.session import engine, async_session, DbSessionMiddleware
from handlers import registration, match, common, admin
from create_db import init_db

load_dotenv()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    await init_db()
    
    # Initialize Redis for FSM
    redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    storage = RedisStorage(redis)
    
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # Register Middlewares
    dp.update.middleware(DbSessionMiddleware(async_session))

    # Register Routers
    dp.include_router(admin.router)
    dp.include_router(common.router)
    dp.include_router(registration.router)
    dp.include_router(match.router)

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
