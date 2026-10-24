"""Authentication, session cookie signing/verification, and token exchange for the portal."""

import logging
from typing import Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import settings

logger = logging.getLogger(__name__)

SESSION_COOKIE_NAME = "snapstudy_session"
SESSION_SALT = "snapstudy-portal-session"


def get_serializer() -> URLSafeTimedSerializer:
    """Return itsdangerous serializer configured with PORTAL_SECRET."""
    secret = settings.PORTAL_SECRET
    if not secret or len(secret) < 32:
        raise RuntimeError(
            "PORTAL_SECRET is empty or shorter than 32 characters. "
            "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))' "
            "and set it in your .env file."
        )
    return URLSafeTimedSerializer(secret, salt=SESSION_SALT)


def sign_session_cookie(telegram_id: int) -> str:
    """Cryptographically sign a session cookie containing the student's telegram_id."""
    serializer = get_serializer()
    return serializer.dumps({"uid": telegram_id})


def verify_session_cookie(
    cookie_value: str, max_age_seconds: Optional[int] = None
) -> Optional[int]:
    """Verify session cookie signature and expiration.

    Returns telegram_id if valid, or None if tampered, expired, or invalid.
    """
    if not cookie_value:
        return None

    if max_age_seconds is None:
        max_age_seconds = settings.PORTAL_SESSION_DAYS * 86400

    serializer = get_serializer()
    try:
        data = serializer.loads(cookie_value, max_age=max_age_seconds)
        if isinstance(data, dict) and "uid" in data:
            return int(data["uid"])
        return None
    except (SignatureExpired, BadSignature) as err:
        logger.debug("Invalid session cookie: %s", err)
        return None
    except Exception as err:
        logger.warning("Unexpected error verifying session cookie: %s", err)
        return None
