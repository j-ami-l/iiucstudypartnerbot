"""Telegram handler for /portal command: magic-link dashboard authentication."""

import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from app import db
from app.config import settings
from app.i18n import t
from app.services.portal_link_service import PortalLinkService

logger = logging.getLogger(__name__)


async def portal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /portal command: issue a secure, single-use login link with disabled previews."""
    if not update.effective_user or not update.effective_message or not update.effective_chat:
        return

    user = update.effective_user
    lang = await db.get_user_language(user.id)

    # 1. Private chat guard: /portal works ONLY in a private chat
    if update.effective_chat.type != "private":
        logger.info("User %s requested /portal outside private chat", user.id)
        await update.effective_message.reply_text(
            t("portal_private_only", lang), parse_mode=ParseMode.HTML
        )
        return

    # 2. Check if PORTAL_BASE_URL is configured
    if not settings.PORTAL_BASE_URL:
        logger.warning("User %s requested /portal but PORTAL_BASE_URL is not set", user.id)
        await update.effective_message.reply_text(
            t("portal_not_set_up", lang), parse_mode=ParseMode.HTML
        )
        return

    portal_link_service: PortalLinkService = (
        context.bot_data.get("portal_link_service") or PortalLinkService()
    )

    portal_link = await portal_link_service.create_portal_link(user.id)
    if not portal_link:
        await update.effective_message.reply_text(
            t("portal_not_set_up", lang), parse_mode=ParseMode.HTML
        )
        return

    # 3. Send URL button with link previews disabled
    keyboard = [
        [
            InlineKeyboardButton(
                t("btn_open_portal", lang), url=portal_link
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    link_preview = LinkPreviewOptions(is_disabled=True)

    try:
        await update.effective_message.reply_text(
            t("portal_link_msg", lang),
            reply_markup=reply_markup,
            link_preview_options=link_preview,
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as err:
        # Fall back to plain text if Telegram rejects non-https/localhost URL buttons
        logger.warning(
            "Telegram rejected portal URL button (%s). Falling back to plain text.",
            err,
        )
        await update.effective_message.reply_text(
            f"{t('portal_link_msg', lang)}\n\n{portal_link}",
            link_preview_options=link_preview,
            parse_mode=ParseMode.HTML,
        )
