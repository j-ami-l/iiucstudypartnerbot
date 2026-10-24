"""Service for generating one-time magic login tokens and portal dashboard links."""

import logging
from typing import Optional

from app import db_stats
from app.config import settings
from app.utils.tokens import hash_token, make_token

logger = logging.getLogger(__name__)


class PortalLinkService:
    """Creates portal login tokens and builds secure dashboard URLs."""

    async def create_portal_link(self, telegram_id: int) -> Optional[str]:
        """Create a single-use login token and construct the portal URL.

        The token is placed in the URL fragment (#) so that it is never transmitted
        in HTTP request paths or logged by servers or link-preview crawlers.
        """
        base_url = settings.PORTAL_BASE_URL.rstrip("/")
        if not base_url:
            logger.warning("PORTAL_BASE_URL is not configured.")
            return None

        token = make_token()
        token_h = hash_token(token)

        await db_stats.create_portal_token(
            token_h, telegram_id, ttl_seconds=settings.PORTAL_TOKEN_TTL_SECONDS
        )

        return f"{base_url}/login#{token}"
