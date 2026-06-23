from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

async def handle_start(message: Message) -> None:
    await message.answer("Добро пожаловать! Я бот для прохождения опросов.")

def get_bot_token() -> str:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN")
    return token

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=get_bot_token())
    dispatcher = Dispatcher()

    dispatcher.message.register(handle_start, CommandStart())
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
