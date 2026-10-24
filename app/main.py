"""SnapStudy AI entrypoint."""

import logging
from app.config import settings
from app.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for running SnapStudy."""
    setup_logging(settings.LOG_LEVEL)
    logger.info("SnapStudy starting")


if __name__ == "__main__":
    main()
