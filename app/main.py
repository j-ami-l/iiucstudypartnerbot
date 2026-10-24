"""Main entrypoint for SnapStudy AI Telegram bot."""

import logging
import sys
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.config import settings
from app.handlers.photo import non_photo_handler, photo_handler
from app.handlers.start import help_handler, start_handler
from app.i18n import t
from app.logging_setup import setup_logging

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler logging exceptions and sending a friendly message."""
    logger.error("Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        lang = (
            context.user_data.get("language", "en")
            if context.user_data
            else "en"
        )
        try:
            await update.effective_message.reply_text(
                t("error_generic", lang), parse_mode=ParseMode.HTML
            )
        except Exception:
            pass


def build_application() -> Application:
    """Build and configure the Telegram Application."""
    if not settings.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set in .env. Cannot start bot.")
        sys.exit(1)

    app = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))

    # Register photo and document image handlers
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.Document.IMAGE, photo_handler))

    # Polite fallback for non-photo text messages
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, non_photo_handler)
    )

    # Register global error handler
    app.add_error_handler(error_handler)

    return app


def main() -> None:
    """Initialize logging and run polling."""
    setup_logging(settings.LOG_LEVEL)
    logger.info("SnapStudy starting")

    application = build_application()
    logger.info("Starting Telegram bot polling...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
