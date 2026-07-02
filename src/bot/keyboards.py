from __future__ import annotations
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from core.models import Question


MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📋 Показать опросы"), KeyboardButton(text="ℹ️ Справка")]],
    resize_keyboard=True,
)

def build_keyboard_for_question(question: Question) -> InlineKeyboardMarkup | ReplyKeyboardRemove:
    if question.question_type == "free_text":
        return ReplyKeyboardRemove()

    buttons = [
        [InlineKeyboardButton(text=answer.text, callback_data=f"answer:{answer.text}")]
        for answer in question.answers
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)