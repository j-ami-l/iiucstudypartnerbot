"""Telegram callback query handlers for the quiz flow, scoring persistence, and regeneration."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, RetryAfter
from telegram.ext import ContextTypes

from app import db, db_stats
from app.i18n import t
from app.keyboards import (
    mcq_keyboard,
    next_question_keyboard,
    quiz_finished_keyboard,
    summary_keyboard,
)
from app.schemas import StudyResult
from app.services.quiz_service import QuizService
from app.services.study_service import StudyService
from app.utils.formatting import format_study_summary, split_message

logger = logging.getLogger(__name__)


async def _safe_edit(query, text: str, **kwargs) -> bool:
    """Safely edit query message text ignoring message not modified and handling RetryAfter."""
    try:
        await query.edit_message_text(text, **kwargs)
        return True
    except BadRequest as err:
        if "message is not modified" in str(err).lower():
            return True
        logger.warning("BadRequest during query edit: %s", err)
        return False
    except RetryAfter as err:
        logger.warning("Telegram RetryAfter: %ds. Skipping edit.", err.retry_after)
        return False
    except Exception as err:
        logger.error("Error editing message: %s", err)
        return False


async def quiz_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Route all quiz-related inline button callbacks with SQLite persistence and safe edits."""
    query = update.callback_query
    if not query or not query.data or not update.effective_user:
        return

    data = query.data
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    quiz_service: QuizService = context.bot_data.get("quiz_service") or QuizService()

    # 1. Start Quiz from summary button: act:quiz or act:quiz:{note_id}
    if data.startswith("act:quiz"):
        await query.answer()
        parts = data.split(":")
        note_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None

        study_result = (
            context.user_data.get("last_study_result")
            if context.user_data
            else None
        )
        if not study_result and note_id is not None:
            note_row = await db.get_note_by_id(note_id)
            if note_row and note_row.get("quiz_json"):
                study_result = StudyResult.model_validate_json(
                    note_row["quiz_json"]
                )
                if context.user_data is not None:
                    context.user_data["last_study_result"] = study_result

        if not study_result or not study_result.mcqs:
            await _safe_edit(query, t("stale_quiz", lang), parse_mode=ParseMode.HTML)
            return

        quiz_state = quiz_service.create_quiz(study_result)
        if context.user_data is not None:
            context.user_data["quiz_state"] = quiz_state
            if note_id:
                context.user_data["last_note_id"] = note_id

        cur_num, mcq, total = quiz_service.get_current_question(quiz_state)
        q_text = quiz_service.format_question_message(mcq, cur_num, total, lang)
        await _safe_edit(
            query,
            q_text,
            parse_mode=ParseMode.HTML,
            reply_markup=mcq_keyboard(quiz_state.current_index, note_id=note_id),
        )
        return

    # 2. Answer submitted: qa:{note_id}:{q_index}:{opt_index} or qa:{q_index}:{opt_index}
    if data.startswith("qa:"):
        parts = data.split(":")
        note_id = None
        if len(parts) == 4:
            note_id = int(parts[1]) if parts[1].isdigit() else None
            q_index = int(parts[2])
            option_index = int(parts[3])
        elif len(parts) == 3:
            q_index = int(parts[1])
            option_index = int(parts[2])
        else:
            await query.answer()
            return

        if note_id is None and context.user_data:
            note_id = context.user_data.get("last_note_id")

        quiz_state = (
            context.user_data.get("quiz_state") if context.user_data else None
        )
        if not quiz_state or quiz_state.is_finished:
            await query.answer(t("stale_quiz", lang), show_alert=True)
            return

        # Double-tap and out-of-order check
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

        # In private chat, write one question_attempts row per answered question
        if update.effective_chat and update.effective_chat.type == "private":
            try:
                topic = getattr(current_mcq, "topic", "General") or "General"
                await db_stats.record_answer(
                    telegram_id=user.id,
                    note_id=note_id if note_id is not None else 0,
                    q_index=quiz_state.current_index,
                    topic=topic,
                    chosen_index=option_index,
                    correct_index=current_mcq.correct_index,
                    is_correct=1 if is_correct else 0,
                    source="quiz",
                )
            except Exception as err:
                logger.error("Failed to record question attempt: %s", err)

        is_last = quiz_state.current_index == quiz_state.total_questions - 1
        feedback_text = quiz_service.format_answer_feedback(
            current_mcq, is_correct, correct_letter, lang=lang
        )

        await _safe_edit(
            query,
            feedback_text,
            parse_mode=ParseMode.HTML,
            reply_markup=next_question_keyboard(
                lang, is_last=is_last, note_id=note_id
            ),
        )
        return

    # 3. Next Question button: act:next_q or act:next_q:{note_id}
    if data.startswith("act:next_q"):
        await query.answer()
        parts = data.split(":")
        note_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
        if not note_id and context.user_data:
            note_id = context.user_data.get("last_note_id")

        quiz_state = (
            context.user_data.get("quiz_state") if context.user_data else None
        )
        if not quiz_state:
            await _safe_edit(query, t("stale_quiz", lang), parse_mode=ParseMode.HTML)
            return

        has_next = quiz_service.next_question(quiz_state)
        if has_next:
            cur_num, mcq, total = quiz_service.get_current_question(quiz_state)
            q_text = quiz_service.format_question_message(
                mcq, cur_num, total, lang
            )
            await _safe_edit(
                query,
                q_text,
                parse_mode=ParseMode.HTML,
                reply_markup=mcq_keyboard(
                    quiz_state.current_index, note_id=note_id
                ),
            )
        else:
            # Quiz completed: save attempt to SQLite
            if note_id:
                try:
                    await db.save_quiz_attempt(
                        note_id=note_id,
                        telegram_id=user.id,
                        score=quiz_state.score,
                        total=quiz_state.total_questions,
                    )
                    logger.info(
                        "Saved quiz attempt for user %s on note %s: %d/%d",
                        user.id,
                        note_id,
                        quiz_state.score,
                        quiz_state.total_questions,
                    )
                except Exception as err:
                    logger.error("Failed to save quiz attempt: %s", err)

            score_text = quiz_service.format_score_card(quiz_state, lang)
            await _safe_edit(
                query,
                score_text,
                parse_mode=ParseMode.HTML,
                reply_markup=quiz_finished_keyboard(lang, note_id=note_id),
            )
        return

    # 4. Retry Quiz button: act:retry_quiz or act:retry_quiz:{note_id}
    if data.startswith("act:retry_quiz"):
        await query.answer()
        parts = data.split(":")
        note_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
        if not note_id and context.user_data:
            note_id = context.user_data.get("last_note_id")

        study_result = (
            context.user_data.get("last_study_result")
            if context.user_data
            else None
        )
        if not study_result and note_id is not None:
            note_row = await db.get_note_by_id(note_id)
            if note_row and note_row.get("quiz_json"):
                study_result = StudyResult.model_validate_json(
                    note_row["quiz_json"]
                )

        if not study_result or not study_result.mcqs:
            await _safe_edit(query, t("stale_quiz", lang), parse_mode=ParseMode.HTML)
            return

        quiz_state = quiz_service.create_quiz(study_result)
        if context.user_data is not None:
            context.user_data["quiz_state"] = quiz_state

        cur_num, mcq, total = quiz_service.get_current_question(quiz_state)
        q_text = quiz_service.format_question_message(mcq, cur_num, total, lang)
        await _safe_edit(
            query,
            q_text,
            parse_mode=ParseMode.HTML,
            reply_markup=mcq_keyboard(quiz_state.current_index, note_id=note_id),
        )
        return

    # 5. New Note button
    if data == "act:new_note":
        await query.answer()
        if query.message:
            await query.message.reply_text(
                t("send_photo_prompt", lang), parse_mode=ParseMode.HTML
            )
        return

    # 6. Regenerate summary button: act:regen or act:regen:{note_id}
    if data.startswith("act:regen"):
        await query.answer()
        parts = data.split(":")
        note_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None

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

        await _safe_edit(query, t("regenerating", lang), parse_mode=ParseMode.HTML)
        study_service: StudyService = (
            context.bot_data.get("study_service") or StudyService()
        )
        try:
            # Force regeneration (bypass cache)
            new_result = await study_service.analyze_note(
                image_bytes, language=lang
            )
            formatted_text = format_study_summary(new_result, lang=lang)
            img_hash = db.compute_image_hash(image_bytes, lang, style="full")

            new_note_id = await db.save_note(
                telegram_id=user.id,
                language=lang,
                image_hash=img_hash,
                summary_text=formatted_text,
                quiz_json=new_result.model_dump_json(),
            )

            if context.user_data is not None:
                context.user_data["last_study_result"] = new_result
                context.user_data["last_note_id"] = new_note_id

            chunks = split_message(formatted_text)
            await _safe_edit(
                query,
                chunks[0],
                parse_mode=ParseMode.HTML,
                reply_markup=summary_keyboard(lang, note_id=new_note_id),
            )
            for chunk in chunks[1:]:
                if query.message:
                    await query.message.reply_text(
                        chunk, parse_mode=ParseMode.HTML
                    )
        except Exception as err:
            logger.error("Error during regeneration: %s", err)
            await _safe_edit(query, t("error_generic", lang), parse_mode=ParseMode.HTML)
        return
