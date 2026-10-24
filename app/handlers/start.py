"""Telegram handlers for /start and /help commands."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app import db
from app.i18n import t

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command by saving the user and sending the welcome message."""
    if not update.effective_message or not update.effective_user:
        return

    user = update.effective_user
    lang = await db.get_user_language(user.id)
    if context.user_data is not None:
        context.user_data["language"] = lang

    # Persist user in SQLite
    await db.upsert_user(user.id, name=user.full_name, language=lang)

    logger.info("User %s (%s) started the bot", user.id, user.full_name)

    # Deep link: /start practice
    if context.args and context.args[0].lower() == "practice":
        from app.handlers.practice import practice_command

        await practice_command(update, context)
        return

    # Deep link: /start challenge_<note_id>
    if context.args and context.args[0].lower().startswith("challenge_"):
        raw_id = context.args[0].split("_", 1)[1]
        try:
            note_id = int(raw_id)
            note = await db.get_note_by_id(note_id)
            if note and note.get("quiz_json"):
                from app.keyboards import mcq_keyboard
                from app.schemas import StudyResult
                from app.services.quiz_service import QuizService

                study_result = StudyResult.model_validate_json(note["quiz_json"])
                if study_result and study_result.mcqs:
                    quiz_service: QuizService = (
                        context.bot_data.get("quiz_service") or QuizService()
                    )
                    quiz_state = quiz_service.create_quiz(study_result)
                    if context.user_data is not None:
                        context.user_data["quiz_state"] = quiz_state
                        context.user_data["last_note_id"] = note_id
                        context.user_data["last_study_result"] = study_result

                    title = note.get("title") or f"Note #{note_id}"
                    await update.effective_message.reply_text(
                        f"⚔️ <b>Classmate Challenge Accepted!</b>\n"
                        f"You've been challenged on: <b>{title}</b>.\n"
                        f"Let's see how high you can score! Starting quiz:",
                        parse_mode=ParseMode.HTML,
                    )

                    cur_num, mcq, total = quiz_service.get_current_question(quiz_state)
                    q_text = quiz_service.format_question_message(mcq, cur_num, total, lang)
                    await update.effective_message.reply_text(
                        q_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=mcq_keyboard(quiz_state.current_index, note_id=note_id),
                    )
                    return
        except Exception as e:
            logger.warning("Error handling challenge deep link: %s", e, exc_info=True)

    text = t("welcome", lang)
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command by sending instructions."""
    if not update.effective_message or not update.effective_user:
        return

    user = update.effective_user
    lang = await db.get_user_language(user.id)
    text = t("help", lang)
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
