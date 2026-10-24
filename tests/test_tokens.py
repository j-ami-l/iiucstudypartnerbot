"""Unit tests for token generation and SHA-256 hashing."""

import unittest
from app.utils.tokens import hash_token, make_token


class TestTokens(unittest.TestCase):
    """Test suite for app.utils.tokens."""

    def test_make_token_uniqueness_and_length(self):
        t1 = make_token()
        t2 = make_token()
        self.assertIsInstance(t1, str)
        self.assertGreaterEqual(len(t1), 40)
        self.assertNotEqual(t1, t2)

    def test_hash_token_deterministic(self):
        token = "test_token_abc_123"
        h1 = hash_token(token)
        h2 = hash_token(token)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)
        self.assertNotEqual(h1, token)

    def test_hash_token_distinct(self):
        t1 = make_token()
        t2 = make_token()
        self.assertNotEqual(hash_token(t1), hash_token(t2))
