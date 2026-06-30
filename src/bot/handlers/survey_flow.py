from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext

from bot.keyboards import build_keyboard_for_question
from core.engine import SurveyEngine
from bot.states import SurveyStates

router = Router()

@router.message(Command("surveys"))
async def handle_surveys_list(message: Message, survey_engine: SurveyEngine) -> None:
    surveys = survey_engine.list_available_surveys()
    buttons = [
        [InlineKeyboardButton(text=survey.title, callback_data=f"start_survey:{survey.id}")]
        for survey in surveys
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите опрос:", reply_markup=keyboard)


@router.message(F.text == "📋 Показать опросы")
async def handle_surveys_button(message: Message, survey_engine: SurveyEngine) -> None:
    await handle_surveys_list(message, survey_engine)


@router.callback_query(F.data.startswith("start_survey:"))
async def handle_survey_selected(callback: CallbackQuery, survey_engine: SurveyEngine, state: FSMContext) -> None:
    survey_id = int(callback.data.split(":", maxsplit=1)[1])
    await callback.answer()

    question = survey_engine.start_survey(callback.from_user.id, survey_id)
    await state.update_data(survey_id=survey_id)
    await state.set_state(SurveyStates.answering)

    keyboard = build_keyboard_for_question(question)
    if callback.message:
        await callback.message.answer(question.text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("answer:"), SurveyStates.answering)
async def handle_button_answer(callback: CallbackQuery, survey_engine: SurveyEngine, state: FSMContext) -> None:
    answer_text = callback.data.split(":", maxsplit=1)[1]
    await callback.answer()
    if callback.message:
        await _process_answer(callback.message, callback.from_user.id, answer_text, survey_engine, state)

@router.message(SurveyStates.answering)
async def handle_text_answer(message: Message, survey_engine: SurveyEngine, state: FSMContext) -> None:
    await _process_answer(message, message.from_user.id, message.text, survey_engine, state)

async def _process_answer(
    message: Message, user_id: int, answer_text: str, survey_engine: SurveyEngine, state: FSMContext) -> None:
    data = await state.get_data()
    survey_id = data.get("survey_id")
    if survey_id is None:
        await message.answer("Сначала выберите опрос: /surveys")
        return

    try:
        result = survey_engine.answer(user_id, survey_id, answer_text)
    except Exception:
        import traceback
        traceback.print_exc()
        await message.answer(
            "Не получилось обработать ваш ответ. Попробуйте /surveys, чтоб начать опрос заново."
        )
        return

    if isinstance(result, str):
        await state.clear()
        surveys = survey_engine.list_available_surveys()
        buttons = [
            [InlineKeyboardButton(text=survey.title, callback_data=f"start_survey:{survey.id}")]
            for survey in surveys
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(f"Опрос завершен!\n\n{result}", reply_markup=keyboard)