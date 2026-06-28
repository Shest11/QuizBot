from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from bot.keyboards import build_keyboard_for_question
from core.engine import SurveyEngine

router = Router()

def setup_survey_flow_router(survey_engine: SurveyEngine) -> Router:

    @router.message(Command("surveys"))
    async def handle_surveys_list(message: Message) -> None:
        surveys = survey_engine.list_available_surveys()
        buttons = [
            [InlineKeyboardButton(text=survey.title, callback_data=f"start_survey:{survey.id}")]
            for survey in surveys
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Выберите опрос:", reply_markup=keyboard)

    @router.message(F.text == "📋 Показать опросы")
    async def handle_surveys_button(message: Message) -> None:
        await handle_surveys_list(message)

    @router.callback_query(lambda c: c.data.startswith("start_survey:"))
    async def handle_survey_selected(callback: CallbackQuery) -> None:
        survey_id = int(callback.data.split(":", maxsplit=1)[1])
        await callback.answer()

        question = survey_engine.start_survey(callback.from_user.id, survey_id)
        keyboard = build_keyboard_for_question(question)
        await callback.message.answer(question.text, reply_markup=keyboard)

    return router