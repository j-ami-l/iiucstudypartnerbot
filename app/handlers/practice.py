"""Telegram handlers for /weak, /practice, and practice quiz callback interactions."""

import html
import logging
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, RetryAfter
from telegram.ext import ContextTypes

from app import db, db_stats
from app.i18n import t
from app.keyboards import (
    practice_finished_keyboard,
    practice_mcq_keyboard,
    practice_next_keyboard,
    weak_topics_keyboard,
)
from app.services.practice_service import PracticeService, PracticeState

logger = logging.getLogger(__name__)


async def _safe_edit(query, text: str, **kwargs) -> bool:
    """Safely edit query message text ignoring not modified and handling RetryAfter."""
    try:
        await query.edit_message_text(text, **kwargs)
        return True
    except BadRequest as err:
        if "message is not modified" in str(err).lower():
            return True
        logger.warning("BadRequest during practice edit: %s", err)
        return False
    except RetryAfter as err:
        logger.warning("Telegram RetryAfter: %ds. Skipping edit.", err.retry_after)
        return False
    except Exception as err:
        logger.error("Error editing practice message: %s", err)
        return False


async def weak_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /weak command: list student's weak topics with accuracy."""
    if not update.effective_user or not update.effective_message:
        return

    user = update.effective_user
    lang = await db.get_user_language(user.id)

    topics = await db_stats.get_weak_topics(user.id)
    if not topics:
        await update.effective_message.reply_text(
            t("take_quiz_first", lang), parse_mode=ParseMode.HTML
        )
        return

    weak_list = [w for w in topics if w.get("is_weak")]
    if not weak_list:
        # Check if they have mistakes anyway
        mistakes_count = await db_stats.count_mistakes(user.id)
        reply_markup = weak_topics_keyboard(lang) if mistakes_count > 0 else None
        await update.effective_message.reply_text(
            t("all_topics_strong", lang),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
        return

    bullets = "".join(
        t(
            "weak_topic_item",
            lang,
            topic=html.escape(w["topic"]),
            accuracy=w["accuracy_percent"],
            correct=w["correct"],
            attempts=w["attempts"],
        )
        for w in weak_list[:5]
    )

    msg_text = f"{t('weak_topics_title', lang)}{bullets}"
    await update.effective_message.reply_text(
        msg_text,
        parse_mode=ParseMode.HTML,
        reply_markup=weak_topics_keyboard(lang),
    )


async def _start_practice_session(
    user_id: int,
    lang: str,
    context: ContextTypes.DEFAULT_TYPE,
    topic_filter: Optional[str] = None,
    query=None,
    message=None,
) -> None:
    """Helper to initialize and send the first question of a practice session."""
    practice_service: PracticeService = (
        context.bot_data.get("practice_service") or PracticeService()
    )

    questions = await practice_service.build_practice_set(
        user_id, topic_filter=topic_filter
    )
    if not questions:
        text = t("no_mistakes", lang)
        if query:
            await _safe_edit(query, text, parse_mode=ParseMode.HTML)
        elif message:
            await message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    state: PracticeState = practice_service.create_practice(questions)
    if context.user_data is not None:
        context.user_data["practice_state"] = state
        context.user_data["practice_topic_filter"] = topic_filter

    cur_num, item, total = practice_service.get_current_question(state)
    q_text = practice_service.format_question_message(item, cur_num, total, lang)

    reply_markup = practice_mcq_keyboard(state.current_index)
    if query:
        await _safe_edit(query, q_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    elif message:
        await message.reply_text(q_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def practice_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /practice [topic] command."""
    if not update.effective_user or not update.effective_message:
        return

    user = update.effective_user
    lang = await db.get_user_language(user.id)
    topic_filter = " ".join(context.args).strip() if context.args else None

    await _start_practice_session(
        user_id=user.id,
        lang=lang,
        context=context,
        topic_filter=topic_filter,
        message=update.effective_message,
    )


async def practice_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle practice-related callback queries (qp:* and act:practice)."""
    query = update.callback_query
    if not query or not query.data or not update.effective_user:
        return

    data = query.data
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    practice_service: PracticeService = (
        context.bot_data.get("practice_service") or PracticeService()
    )

    # 1. Start practice from inline button (act:practice)
    if data == "act:practice":
        await query.answer()
        await _start_practice_session(
            user_id=user.id,
            lang=lang,
            context=context,
            query=query,
        )
        return

    # 2. Answer practice question: qp:ans:{q_index}:{opt_index}
    if data.startswith("qp:ans:"):
        parts = data.split(":")
        if len(parts) != 4:
            await query.answer()
            return

        q_index = int(parts[2])
        option_index = int(parts[3])

        state: Optional[PracticeState] = (
            context.user_data.get("practice_state") if context.user_data else None
        )
        if not state or state.is_finished:
            await query.answer(t("practice_stale", lang), show_alert=True)
            return

        # Double-tap and index check
        if q_index != state.current_index or state.answered_current:
            await query.answer(t("already_answered", lang))
            return

        current_item = state.questions[state.current_index]
        is_correct, correct_letter, _ = practice_service.check_answer(
            state, option_index
        )
        await query.answer("✅" if is_correct else "❌")

        # Record attempt with source='practice' and original note_id/q_index
        try:
            await db_stats.record_answer(
                telegram_id=user.id,
                note_id=current_item.note_id,
                q_index=current_item.q_index,
                topic=current_item.topic,
                chosen_index=option_index,
                correct_index=current_item.mcq.correct_index,
                is_correct=1 if is_correct else 0,
                source="practice",
            )
        except Exception as err:
            logger.error("Failed to record practice answer: %s", err)

        is_last = state.current_index == state.total_questions - 1
        feedback_text = practice_service.format_answer_feedback(
            current_item, is_correct, correct_letter, lang=lang
        )

        await _safe_edit(
            query,
            feedback_text,
            parse_mode=ParseMode.HTML,
            reply_markup=practice_next_keyboard(lang, is_last=is_last),
        )
        return

    # 3. Next question button: qp:next
    if data == "qp:next":
        await query.answer()
        state = (
            context.user_data.get("practice_state") if context.user_data else None
        )
        if not state:
            await _safe_edit(
                query, t("practice_stale", lang), parse_mode=ParseMode.HTML
            )
            return

        has_next = practice_service.next_question(state)
        if has_next:
            cur_num, item, total = practice_service.get_current_question(state)
            q_text = practice_service.format_question_message(
                item, cur_num, total, lang
            )
            await _safe_edit(
                query,
                q_text,
                parse_mode=ParseMode.HTML,
                reply_markup=practice_mcq_keyboard(state.current_index),
            )
        else:
            # Practice completed: fetch remaining weak topics
            weak_topics = await db_stats.get_weak_topics(user.id)
            score_text = practice_service.format_score_card(
                state, weak_topics, lang
            )
            await _safe_edit(
                query,
                score_text,
                parse_mode=ParseMode.HTML,
                reply_markup=practice_finished_keyboard(lang),
            )
        return

    # 4. Retry practice: qp:retry
    if data == "qp:retry":
        await query.answer()
        topic_filter = (
            context.user_data.get("practice_topic_filter")
            if context.user_data
            else None
        )
        await _start_practice_session(
            user_id=user.id,
            lang=lang,
            context=context,
            topic_filter=topic_filter,
            query=query,
        )
        return
