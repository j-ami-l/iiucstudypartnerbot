"""Cryptographic token generation and SHA-256 hashing utilities for portal authentication."""

import hashlib
import secrets


def make_token() -> str:
    """Generate a high-entropy cryptographically random URL-safe token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Compute the SHA-256 hex digest of a token string.

    The plaintext token is never stored in the database, only this hash.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
