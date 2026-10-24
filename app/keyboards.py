"""Inline keyboard builders for SnapStudy AI."""

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.i18n import t


def summary_keyboard(
    lang: str = "en", note_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    """Keyboard attached below the study summary."""
    quiz_data = f"act:quiz:{note_id}" if note_id is not None else "act:quiz"
    regen_data = f"act:regen:{note_id}" if note_id is not None else "act:regen"
    keyboard = [
        [
            InlineKeyboardButton(t("btn_quiz", lang), callback_data=quiz_data),
            InlineKeyboardButton(t("btn_regen", lang), callback_data=regen_data),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def mcq_keyboard(
    q_index: int, note_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    """Keyboard for answering an MCQ with A, B, C, D choices."""
    prefix = f"qa:{note_id}:{q_index}" if note_id is not None else f"qa:{q_index}"
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"{prefix}:0"),
            InlineKeyboardButton("B", callback_data=f"{prefix}:1"),
            InlineKeyboardButton("C", callback_data=f"{prefix}:2"),
            InlineKeyboardButton("D", callback_data=f"{prefix}:3"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def next_question_keyboard(
    lang: str = "en", is_last: bool = False, note_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    """Keyboard shown after an answer is submitted."""
    label = t("btn_see_score" if is_last else "btn_next", lang)
    cb_data = f"act:next_q:{note_id}" if note_id is not None else "act:next_q"
    keyboard = [[InlineKeyboardButton(label, callback_data=cb_data)]]
    return InlineKeyboardMarkup(keyboard)


def quiz_finished_keyboard(
    lang: str = "en", note_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    """Keyboard shown on the quiz completion score card."""
    retry_data = (
        f"act:retry_quiz:{note_id}" if note_id is not None else "act:retry_quiz"
    )
    keyboard = [
        [
            InlineKeyboardButton(t("btn_retry_quiz", lang), callback_data=retry_data),
            InlineKeyboardButton(t("btn_new_note", lang), callback_data="act:new_note"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
