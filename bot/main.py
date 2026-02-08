import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_config
from bot.db.engine import Base, create_engine, create_session_pool
from bot.handlers import get_all_routers
from bot.middlewares import DbSessionMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    config = load_config()

    engine = create_engine(config.db.url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_pool = create_session_pool(engine)

    # Seed defaults
    from bot.db.repositories import InterestRepo, VipPlanRepo, RoomRepo
    async with session_pool() as session:
        await InterestRepo(session).seed_defaults()
        await VipPlanRepo(session).seed_defaults()
        await RoomRepo(session).seed_defaults()
        await session.commit()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DbSessionMiddleware(session_pool))

    for router in get_all_routers():
        dp.include_router(router)

    dp["bot_username"] = config.bot_username

    logger.info("Bot starting...")

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await engine.dispose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
