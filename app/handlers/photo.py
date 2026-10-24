"""Telegram handlers for photo and document image updates."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.ai.gemma_client import GemmaAPIError, GemmaAuthError, GemmaTimeout
from app.config import settings
from app.i18n import t
from app.services.study_service import (
    InvalidJSONError,
    StudyService,
    UnreadableNoteError,
)
from app.utils.formatting import format_study_summary, split_message
from app.utils.image import process_image

logger = logging.getLogger(__name__)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos: download, process, call StudyService, and reply with summary."""
    if not update.effective_message:
        return

    lang = context.user_data.get("language", "en") if context.user_data else "en"

    # Send initial status message
    status_msg = await update.effective_message.reply_text(
        t("reading_notes", lang), parse_mode=ParseMode.HTML
    )

    try:
        # 1. Identify and download image file
        if update.effective_message.photo:
            photo_obj = update.effective_message.photo[-1]
            tg_file = await context.bot.get_file(photo_obj.file_id)
        elif update.effective_message.document:
            doc = update.effective_message.document
            if not doc.mime_type or not doc.mime_type.startswith("image/"):
                await status_msg.edit_text(
                    t("invalid_file", lang), parse_mode=ParseMode.HTML
                )
                return
            tg_file = await context.bot.get_file(doc.file_id)
        else:
            await status_msg.edit_text(
                t("send_photo_prompt", lang), parse_mode=ParseMode.HTML
            )
            return

        raw_bytes = await tg_file.download_as_bytearray()

        # 2. Resize and compress image
        compressed_bytes, width, height, size_kb = process_image(
            bytes(raw_bytes), max_side=settings.MAX_IMAGE_SIDE
        )
        logger.info(
            "Photo preprocessed: %dx%d (%.1f KB). Calling StudyService...",
            width,
            height,
            size_kb,
        )

        # 3. Analyze note via StudyService
        study_service: StudyService = (
            context.bot_data.get("study_service") or StudyService()
        )
        result = await study_service.analyze_note(
            compressed_bytes, language=lang
        )

        # Save result in user context for quiz flow (F4)
        if context.user_data is not None:
            context.user_data["last_study_result"] = result

        # 4. Format and reply with summary, key points, and difficult terms
        formatted_text = format_study_summary(result, lang=lang)
        chunks = split_message(formatted_text)

        # Edit status message with first chunk
        await status_msg.edit_text(chunks[0], parse_mode=ParseMode.HTML)

        # If summary was very long, send any remaining chunks as replies
        for chunk in chunks[1:]:
            await update.effective_message.reply_text(
                chunk, parse_mode=ParseMode.HTML
            )

    except UnreadableNoteError:
        logger.info("Handling unreadable note error for user")
        await status_msg.edit_text(
            t("unreadable_error", lang), parse_mode=ParseMode.HTML
        )
    except GemmaTimeout:
        logger.warning("Handling timeout error for user")
        await status_msg.edit_text(
            t("timeout_error", lang), parse_mode=ParseMode.HTML
        )
    except InvalidJSONError:
        logger.error("Handling invalid JSON error for user")
        await status_msg.edit_text(
            t("invalid_json_error", lang), parse_mode=ParseMode.HTML
        )
    except (GemmaAuthError, GemmaAPIError) as err:
        logger.error("Gemma API failure during photo handling: %s", err)
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
    if not update.effective_message:
        return

    lang = context.user_data.get("language", "en") if context.user_data else "en"
    await update.effective_message.reply_text(
        t("send_photo_prompt", lang), parse_mode=ParseMode.HTML
    )
