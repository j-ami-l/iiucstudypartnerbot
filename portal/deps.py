"""FastAPI dependencies for the portal backend."""

from fastapi import HTTPException, Request, status

from portal.auth import SESSION_COOKIE_NAME, verify_session_cookie


def get_current_user(request: Request) -> int:
    """Extract and verify authenticated telegram_id exclusively from the session cookie."""
    cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not_logged_in",
        )

    telegram_id = verify_session_cookie(cookie)
    if telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not_logged_in",
        )

    return telegram_id
