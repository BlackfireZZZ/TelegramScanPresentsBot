import asyncio
import os
from structlog import get_logger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from src.handlers import router
from src.gifts import get_client
from src.database import Database
from config import BOT_TOKEN, ADMINS


async def try_load_session():
    if 'main.session' not in os.listdir('session'):
        client = await get_client()
        await client.stop()


async def startup_info(bot: Bot):
    logger = get_logger()
    me = await bot.get_me()

    for admin in ADMINS:
        Database.new_user(admin)

    await logger.ainfo(f'start bot: @{me.username}')


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
        parse_mode='html'
    ))

    dp = Dispatcher()
    dp.include_router(router)

    await try_load_session()
    await startup_info(bot)

    bot.user_session = await get_client()
    await dp.start_polling(bot) 


if __name__ == '__main__':
    asyncio.run(main())