"""Telegram handlers for /start and /help commands."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.i18n import t

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command by sending the welcome message."""
    if not update.effective_message:
        return

    lang = context.user_data.get("language", "en") if context.user_data else "en"
    text = t("welcome", lang)

    logger.info(
        "User %s sent /start",
        update.effective_user.id if update.effective_user else "unknown",
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command by sending instructions."""
    if not update.effective_message:
        return

    lang = context.user_data.get("language", "en") if context.user_data else "en"
    text = t("help", lang)

    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
