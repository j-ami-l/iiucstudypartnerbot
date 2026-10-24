"""Telegram handlers for photo and document image updates with SQLite caching."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app import db
from app.ai.gemma_client import GemmaAPIError, GemmaAuthError, GemmaTimeout
from app.config import settings
from app.i18n import t
from app.keyboards import summary_keyboard
from app.schemas import StudyResult
from app.services.study_service import (
    InvalidJSONError,
    StudyService,
    UnreadableNoteError,
)
from app.utils.formatting import format_study_summary, split_message
from app.utils.image import process_image

logger = logging.getLogger(__name__)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos with SQLite cache check, Gemma analysis, and note persistence."""
    if not update.effective_message or not update.effective_user:
        return

    user = update.effective_user
    lang = await db.get_user_language(user.id)
    await db.upsert_user(user.id, name=user.full_name, language=lang)
    if context.user_data is not None:
        context.user_data["language"] = lang

    # Send initial status message
    status_msg = await update.effective_message.reply_text(
        t("reading_notes", lang), parse_mode=ParseMode.HTML
    )

    try:
        # 1. Download image and capture Telegram identifiers
        file_id = None
        file_unique_id = None

        if update.effective_message.photo:
            photo_obj = update.effective_message.photo[-1]
            file_id = photo_obj.file_id
            file_unique_id = photo_obj.file_unique_id
            tg_file = await context.bot.get_file(file_id)
        elif update.effective_message.document:
            doc = update.effective_message.document
            if not doc.mime_type or not doc.mime_type.startswith("image/"):
                await status_msg.edit_text(
                    t("invalid_file", lang), parse_mode=ParseMode.HTML
                )
                return
            file_id = doc.file_id
            file_unique_id = doc.file_unique_id
            tg_file = await context.bot.get_file(file_id)
        else:
            await status_msg.edit_text(
                t("send_photo_prompt", lang), parse_mode=ParseMode.HTML
            )
            return

        raw_bytes = await tg_file.download_as_bytearray()

        # 2. Resize and compress
        compressed_bytes, width, height, size_kb = process_image(
            bytes(raw_bytes), max_side=settings.MAX_IMAGE_SIDE
        )
        logger.info(
            "Photo preprocessed: %dx%d (%.1f KB)", width, height, size_kb
        )

        # 3. Check SQLite image cache
        img_hash = db.compute_image_hash(compressed_bytes, lang, style="full")
        cached = await db.get_cached_note(img_hash)

        if cached and cached.get("quiz_json"):
            logger.info("Cache hit for note image hash %s", img_hash)
            result = StudyResult.model_validate_json(cached["quiz_json"])
            formatted_text = cached["summary_text"]
            # Insert a new note row for this user copying stored result (AGENT.md Sec 7 & 9)
            note_id = await db.save_note(
                telegram_id=user.id,
                language=lang,
                image_hash=img_hash,
                summary_text=formatted_text,
                quiz_json=cached["quiz_json"],
                file_id=file_id,
                file_unique_id=file_unique_id,
            )
        else:
            logger.info("Cache miss for image hash %s. Calling Gemma...", img_hash)
            study_service: StudyService = (
                context.bot_data.get("study_service") or StudyService()
            )
            result = await study_service.analyze_note(
                compressed_bytes, language=lang
            )
            formatted_text = format_study_summary(result, lang=lang)
            quiz_json_str = result.model_dump_json()

            # Save note to database
            note_id = await db.save_note(
                telegram_id=user.id,
                language=lang,
                image_hash=img_hash,
                summary_text=formatted_text,
                quiz_json=quiz_json_str,
                file_id=file_id,
                file_unique_id=file_unique_id,
            )

        # Save session context for quiz flow and regeneration
        if context.user_data is not None:
            context.user_data["last_study_result"] = result
            context.user_data["last_image_bytes"] = compressed_bytes
            context.user_data["last_note_id"] = note_id

        # 4. Reply with summary and action buttons (containing note_id)
        chunks = split_message(formatted_text)
        await status_msg.edit_text(
            chunks[0],
            parse_mode=ParseMode.HTML,
            reply_markup=summary_keyboard(lang, note_id=note_id),
        )

        for chunk in chunks[1:]:
            await update.effective_message.reply_text(
                chunk, parse_mode=ParseMode.HTML
            )

    except UnreadableNoteError:
        logger.info("Handling unreadable note error for user %s", user.id)
        await status_msg.edit_text(
            t("unreadable_error", lang), parse_mode=ParseMode.HTML
        )
    except GemmaTimeout:
        logger.warning("Handling timeout error for user %s", user.id)
        await status_msg.edit_text(
            t("timeout_error", lang), parse_mode=ParseMode.HTML
        )
    except InvalidJSONError:
        logger.error("Handling invalid JSON error for user %s", user.id)
        await status_msg.edit_text(
            t("invalid_json_error", lang), parse_mode=ParseMode.HTML
        )
    except (GemmaAuthError, GemmaAPIError) as err:
        logger.error("Gemma API error for user %s: %s", user.id, err)
        await status_msg.edit_text(
            t("api_error", lang), parse_mode=ParseMode.HTML
        )
    except Exception as err:
        logger.error("Unexpected error in photo_handler: %s", err, exc_info=True)
        await status_msg.edit_text(
            t("error_generic", lang), parse_mode=ParseMode.HTML
        )


async def non_photo_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Politely reject non-photo, non-command messages."""
    if not update.effective_message or not update.effective_user:
        return

    lang = await db.get_user_language(update.effective_user.id)
    await update.effective_message.reply_text(
        t("send_photo_prompt", lang), parse_mode=ParseMode.HTML
    )
