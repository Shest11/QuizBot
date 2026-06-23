from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router()

FAKE_SURVEYS = {
    "trevoga_test": "Тест на уровень тревожности",
}

@router.message(Command("surveys"))
async def handle_surveys_list(message: Message) -> None:
    buttons = [
        [InlineKeyboardButton(text=title, callback_data=f"start_survey:{survey_id}")]
        for survey_id, title in FAKE_SURVEYS.items()
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите опрос:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("start_survey:"))
async def handle_survey_selected(callback: CallbackQuery) -> None:
    survey_id = callback.data.split(":", maxsplit=1)[1]
    await callback.answer()  # убирает часы на кнопке в ТГ
    await callback.message.answer(
        f"Вы выбрали опрос '{survey_id}'. "
    )