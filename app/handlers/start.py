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
