import os
import asyncio
from aiogram import Bot, Dispatcher
import logging
from aiogram.client.telegram import TelegramAPIServer
from aiogram.methods import DeleteWebhook
from handlers import register_user_command, dp
from dotenv import load_dotenv

from aiogram.client.session.aiohttp import AiohttpSession

load_dotenv()


async def start_bot() -> None:
    logging.basicConfig(level=logging.DEBUG)
    session = AiohttpSession(
        api=TelegramAPIServer.from_base('http://127.0.0.1:8081')
    )
    bot = Bot(
        os.getenv("BOT_TOKEN"),
        session=session,
    )
    await bot(DeleteWebhook(drop_pending_updates=True))

    register_user_command(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
