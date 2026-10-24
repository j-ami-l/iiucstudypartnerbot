"""Unit tests for portal authentication, token exchange, and signed session cookies."""

import os
import tempfile
import unittest

from app import db, db_stats
from app.config import settings
from app.utils.tokens import hash_token, make_token
from portal.auth import (
    get_serializer,
    sign_session_cookie,
    verify_session_cookie,
)


class TestPortalAuth(unittest.TestCase):
    """Test suite for token lifecycle and session cookie security."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_auth.db")
        self.orig_db_path = db.get_db_path()
        db.init_db(self.db_path)

        self.orig_secret = settings.PORTAL_SECRET
        settings.PORTAL_SECRET = "super_secure_test_secret_that_is_at_least_32_chars_long!"

    def tearDown(self):
        settings.PORTAL_SECRET = self.orig_secret
        db.set_db_path(self.orig_db_path)
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    def test_token_create_and_consume_once(self):
        token = make_token()
        token_h = hash_token(token)
        telegram_id = 987654

        # 1. Stored token_hash never equals raw token
        self.assertNotEqual(token_h, token)

        # 2. Store token in SQLite
        db_stats.create_portal_token_sync(token_h, telegram_id, ttl_seconds=300)

        # 3. Consume token once -> succeeds and returns telegram_id
        consumed_uid = db_stats.consume_portal_token_sync(token_h)
        self.assertEqual(consumed_uid, telegram_id)

        # 4. Consume token a second time -> fails
        second_consume = db_stats.consume_portal_token_sync(token_h)
        self.assertIsNone(second_consume)

    def test_expired_token_fails(self):
        token = make_token()
        token_h = hash_token(token)
        telegram_id = 112233

        # Insert expired token (expired 60 seconds ago)
        with db._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO portal_tokens (token_hash, telegram_id, expires_at)
                VALUES (?, ?, datetime('now', '-60 seconds'));
                """,
                (token_h, telegram_id),
            )

        consumed_uid = db_stats.consume_portal_token_sync(token_h)
        self.assertIsNone(consumed_uid)

    def test_unknown_token_fails(self):
        random_hash = hash_token("nonexistent_random_token")
        consumed_uid = db_stats.consume_portal_token_sync(random_hash)
        self.assertIsNone(consumed_uid)

    def test_session_cookie_sign_and_verify(self):
        telegram_id = 556677
        cookie_val = sign_session_cookie(telegram_id)
        self.assertIsInstance(cookie_val, str)

        verified_uid = verify_session_cookie(cookie_val)
        self.assertEqual(verified_uid, telegram_id)

    def test_tampered_session_cookie_fails(self):
        cookie_val = sign_session_cookie(556677)
        tampered = cookie_val[:-4] + "wxyz"
        self.assertIsNone(verify_session_cookie(tampered))

    def test_expired_session_cookie_fails(self):
        cookie_val = sign_session_cookie(556677)
        # Verify with max_age_seconds = -1 to ensure expiration
        self.assertIsNone(verify_session_cookie(cookie_val, max_age_seconds=-1))


    def test_short_secret_raises_runtime_error(self):
        settings.PORTAL_SECRET = "too_short"
        with self.assertRaises(RuntimeError):
            get_serializer()
