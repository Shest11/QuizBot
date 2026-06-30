from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

from bot.handlers.survey_flow import router as survey_router
from core.db.database import create_db_engine, create_session_factory, init_db
from core.engine import SurveyEngine

load_dotenv()

async def handle_start(message: Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📋 Показать опросы")]],
        resize_keyboard=True,
    )
    await message.answer(
        "Добро пожаловать! Я бот для прохождения опросов.",
        reply_markup=keyboard,
    )

def get_bot_token() -> str:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN")
    return token

async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=get_bot_token())
    dispatcher = Dispatcher()

    db_engine = create_db_engine("quizbot.db")
    init_db(db_engine)
    session_factory = create_session_factory(db_engine)
    survey_engine = SurveyEngine(session_factory=session_factory)
    dispatcher["survey_engine"] = survey_engine

    dispatcher.include_router(survey_router)
    dispatcher.message.register(handle_start, CommandStart())

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
