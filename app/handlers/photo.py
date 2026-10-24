"""Telegram handlers for photo and document image updates."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.config import settings
from app.i18n import t
from app.utils.image import process_image

logger = logging.getLogger(__name__)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos: download, process, and confirm receipt."""
    if not update.effective_message:
        return

    lang = context.user_data.get("language", "en") if context.user_data else "en"

    # Send initial status message
    status_msg = await update.effective_message.reply_text(
        t("reading_notes", lang), parse_mode=ParseMode.HTML
    )

    try:
        if update.effective_message.photo:
            # Telegram provides multiple sizes; the last one is the highest resolution
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

        # Download raw image bytes
        raw_bytes = await tg_file.download_as_bytearray()

        # Resize (max side ~1280px) and compress as JPEG ~80 quality
        _, width, height, size_kb = process_image(
            bytes(raw_bytes), max_side=settings.MAX_IMAGE_SIDE
        )

        logger.info(
            "Photo processed for user %s: %dx%d (%.1f KB)",
            update.effective_user.id if update.effective_user else "unknown",
            width,
            height,
            size_kb,
        )

        # In F2, confirm receipt with dimensions and size (AI comes in F3)
        confirmation = t(
            "photo_received", lang, width=width, height=height, size_kb=size_kb
        )
        await status_msg.edit_text(confirmation, parse_mode=ParseMode.HTML)

    except Exception as err:
        logger.error("Error processing photo: %s", err, exc_info=True)
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
