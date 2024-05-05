import sys
import logging
import asyncio

from bot.bot import dp, bot
from handlers import *
from db.repository import UserRepository


async def runbot():
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print("Stopping the bot...")


def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    
    dp.include_routers(
        admin_router,
        manager_router,
        anonymous_router
    )

    UserRepository.create_admin()
    asyncio.run(runbot())


if __name__ == "__main__":
    main()
