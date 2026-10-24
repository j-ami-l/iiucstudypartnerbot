"""Telegram callback query handlers for the quiz flow and note regeneration."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.i18n import t
from app.keyboards import (
    mcq_keyboard,
    next_question_keyboard,
    quiz_finished_keyboard,
    summary_keyboard,
)
from app.services.quiz_service import QuizService
from app.services.study_service import StudyService
from app.utils.formatting import format_study_summary, split_message

logger = logging.getLogger(__name__)


async def quiz_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Route all quiz-related inline button callbacks."""
    query = update.callback_query
    if not query or not query.data:
        return

    data = query.data
    lang = context.user_data.get("language", "en") if context.user_data else "en"
    quiz_service: QuizService = context.bot_data.get("quiz_service") or QuizService()

    # 1. Start Quiz from summary button
    if data == "act:quiz":
        await query.answer()
        study_result = (
            context.user_data.get("last_study_result")
            if context.user_data
            else None
        )
        if not study_result or not study_result.mcqs:
            await query.edit_message_text(
                t("stale_quiz", lang), parse_mode=ParseMode.HTML
            )
            return

        quiz_state = quiz_service.create_quiz(study_result)
        context.user_data["quiz_state"] = quiz_state

        cur_num, mcq, total = quiz_service.get_current_question(quiz_state)
        q_text = quiz_service.format_question_message(mcq, cur_num, total, lang)
        await query.edit_message_text(
            q_text,
            parse_mode=ParseMode.HTML,
            reply_markup=mcq_keyboard(quiz_state.current_index),
        )
        return

    # 2. Answer submitted for question (qa:{q_index}:{option_index})
    if data.startswith("qa:"):
        parts = data.split(":")
        if len(parts) != 3:
            await query.answer()
            return

        q_index = int(parts[1])
        option_index = int(parts[2])

        quiz_state = (
            context.user_data.get("quiz_state") if context.user_data else None
        )
        if not quiz_state or quiz_state.is_finished:
            await query.answer(t("stale_quiz", lang), show_alert=True)
            return

        # Double-tap and out-of-order protection
        if (
            q_index != quiz_state.current_index
            or quiz_state.answered_current
        ):
            await query.answer(t("already_answered", lang))
            return

        current_mcq = quiz_state.mcqs[quiz_state.current_index]
        is_correct, correct_letter, _ = quiz_service.check_answer(
            quiz_state, option_index
        )
        await query.answer("✅" if is_correct else "❌")

        is_last = quiz_state.current_index == quiz_state.total_questions - 1
        feedback_text = quiz_service.format_answer_feedback(
            current_mcq, is_correct, correct_letter, lang=lang
        )

        await query.edit_message_text(
            feedback_text,
            parse_mode=ParseMode.HTML,
            reply_markup=next_question_keyboard(lang, is_last=is_last),
        )
        return

    # 3. Next Question button (act:next_q)
    if data == "act:next_q":
        await query.answer()
        quiz_state = (
            context.user_data.get("quiz_state") if context.user_data else None
        )
        if not quiz_state:
            await query.edit_message_text(
                t("stale_quiz", lang), parse_mode=ParseMode.HTML
            )
            return

        has_next = quiz_service.next_question(quiz_state)
        if has_next:
            cur_num, mcq, total = quiz_service.get_current_question(quiz_state)
            q_text = quiz_service.format_question_message(
                mcq, cur_num, total, lang
            )
            await query.edit_message_text(
                q_text,
                parse_mode=ParseMode.HTML,
                reply_markup=mcq_keyboard(quiz_state.current_index),
            )
        else:
            # Quiz completed: show score card
            score_text = quiz_service.format_score_card(quiz_state, lang)
            await query.edit_message_text(
                score_text,
                parse_mode=ParseMode.HTML,
                reply_markup=quiz_finished_keyboard(lang),
            )
        return

    # 4. Retry Quiz button (act:retry_quiz)
    if data == "act:retry_quiz":
        await query.answer()
        study_result = (
            context.user_data.get("last_study_result")
            if context.user_data
            else None
        )
        if not study_result or not study_result.mcqs:
            await query.edit_message_text(
                t("stale_quiz", lang), parse_mode=ParseMode.HTML
            )
            return

        quiz_state = quiz_service.create_quiz(study_result)
        context.user_data["quiz_state"] = quiz_state

        cur_num, mcq, total = quiz_service.get_current_question(quiz_state)
        q_text = quiz_service.format_question_message(mcq, cur_num, total, lang)
        await query.edit_message_text(
            q_text,
            parse_mode=ParseMode.HTML,
            reply_markup=mcq_keyboard(quiz_state.current_index),
        )
        return

    # 5. New Note button (act:new_note)
    if data == "act:new_note":
        await query.answer()
        if query.message:
            await query.message.reply_text(
                t("send_photo_prompt", lang), parse_mode=ParseMode.HTML
            )
        return

    # 6. Regenerate summary button (act:regen)
    if data == "act:regen":
        await query.answer()
        image_bytes = (
            context.user_data.get("last_image_bytes")
            if context.user_data
            else None
        )
        if not image_bytes:
            if query.message:
                await query.message.reply_text(
                    t("send_photo_prompt", lang), parse_mode=ParseMode.HTML
                )
            return

        await query.edit_message_text(
            t("regenerating", lang), parse_mode=ParseMode.HTML
        )
        study_service: StudyService = (
            context.bot_data.get("study_service") or StudyService()
        )
        try:
            new_result = await study_service.analyze_note(
                image_bytes, language=lang
            )
            if context.user_data is not None:
                context.user_data["last_study_result"] = new_result

            formatted_text = format_study_summary(new_result, lang=lang)
            chunks = split_message(formatted_text)
            await query.edit_message_text(
                chunks[0],
                parse_mode=ParseMode.HTML,
                reply_markup=summary_keyboard(lang),
            )
            for chunk in chunks[1:]:
                if query.message:
                    await query.message.reply_text(
                        chunk, parse_mode=ParseMode.HTML
                    )
        except Exception as err:
            logger.error("Error during regeneration: %s", err)
            await query.edit_message_text(
                t("error_generic", lang), parse_mode=ParseMode.HTML
            )
        return
