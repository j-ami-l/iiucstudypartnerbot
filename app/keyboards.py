"""Inline keyboard builders for SnapStudy AI."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.i18n import t


def summary_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Keyboard attached below the study summary."""
    keyboard = [
        [
            InlineKeyboardButton(t("btn_quiz", lang), callback_data="act:quiz"),
            InlineKeyboardButton(t("btn_regen", lang), callback_data="act:regen"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def mcq_keyboard(q_index: int) -> InlineKeyboardMarkup:
    """Keyboard for answering an MCQ with A, B, C, D choices."""
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"qa:{q_index}:0"),
            InlineKeyboardButton("B", callback_data=f"qa:{q_index}:1"),
            InlineKeyboardButton("C", callback_data=f"qa:{q_index}:2"),
            InlineKeyboardButton("D", callback_data=f"qa:{q_index}:3"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def next_question_keyboard(lang: str = "en", is_last: bool = False) -> InlineKeyboardMarkup:
    """Keyboard shown after an answer is submitted."""
    label = t("btn_see_score" if is_last else "btn_next", lang)
    keyboard = [
        [InlineKeyboardButton(label, callback_data="act:next_q")]
    ]
    return InlineKeyboardMarkup(keyboard)


def quiz_finished_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Keyboard shown on the quiz completion score card."""
    keyboard = [
        [
            InlineKeyboardButton(t("btn_retry_quiz", lang), callback_data="act:retry_quiz"),
            InlineKeyboardButton(t("btn_new_note", lang), callback_data="act:new_note"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
