from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards import build_keyboard_for_question, MAIN_MENU_KEYBOARD
from core.engine import SurveyEngine
from bot.states import SurveyStates

router = Router()

@router.message(Command("help"))
async def handle_help_command(message: Message) -> None:
    help_text = (
        "📖 **Справка по использованию QuizBot**\n\n"
        "Этот бот предназначен для прохождения интерактивных многоуровневых опросов.\n\n"
        "**Доступные команды:**\n"
        "▶️ /start - Начать работу с ботом\n"
        "📋 /surveys - Посмотреть список доступных тестов\n"
        "ℹ️ /help - Показать это справочное сообщение\n\n"
        "💡 _Внутри опросов система сама ведет вас по нужным вопросам в зависимости от ваших ответов!_"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="ℹ️ Показать справку еще раз", callback_data="refresh_help")
    builder.button(text="⭐ Исходный код на GitHub", url="https://github.com/Shest11/QuizBot")
    builder.adjust(1)

    await message.answer(help_text, reply_markup=builder.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data == "refresh_help", StateFilter("*"))
async def handle_refresh_help_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await handle_help_command(callback.message)


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


@router.message(F.text == "ℹ️ Справка", StateFilter("*"))
async def handle_help_button(message: Message) -> None:
    await handle_help_command(message)


@router.callback_query(F.data.startswith("start_survey:"))
async def handle_survey_selected(callback: CallbackQuery, survey_engine: SurveyEngine, state: FSMContext) -> None:
    survey_id = int(callback.data.split(":", maxsplit=1)[1])
    await callback.answer()

    question = survey_engine.start_survey(callback.from_user.id, survey_id)
    await state.update_data(survey_id=survey_id)
    await state.set_state(SurveyStates.answering)

    if callback.message:
        await _send_question(callback.message, question, state)

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
    else:
        await _send_question(message, result, state)

async def _send_question(message: Message, question, state: FSMContext) -> None:
    data = await state.get_data()
    panel_was_hidden = data.get("panel_hidden", False)
    is_free_text = question.question_type == "free_text"

    if not is_free_text and panel_was_hidden:
        await message.answer("Записал ваш ответ, продолжаем 👇", reply_markup=MAIN_MENU_KEYBOARD)

    await state.update_data(panel_hidden=is_free_text)

    keyboard = build_keyboard_for_question(question)
    await message.answer(question.text, reply_markup=keyboard)