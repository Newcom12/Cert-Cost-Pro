"""Точка входа: запуск бота CertCost Pro."""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger
from redis.asyncio import Redis

from src.config import get_settings
from src.database import get_engine, get_session_factory, init_db
from src.logging_config import setup_logging
from src.bot.middlewares import DbSessionMiddleware
from src.bot.handlers import admin, user


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    storage = RedisStorage(redis=redis, state_ttl=86400)  # 24 ч — затем сброс FSM

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    engine = get_engine(settings.database_url)
    session_factory = get_session_factory(engine)
    await init_db(engine)

    dp.update.middleware(DbSessionMiddleware(session_factory))
    dp.include_router(user.router, prefix="")
    dp.include_router(admin.router, prefix="")

    logger.info("CertCost Pro bot starting...")
    try:
        await dp.start_polling(bot)
    finally:
        await redis.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
