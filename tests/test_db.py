"""Unit tests for SQLite database persistence and caching layer."""

import os
import tempfile
import unittest
from app import db


class TestDatabaseLayer(unittest.IsolatedAsyncioTestCase):
    """Test suite for app.db operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_snapstudy.db")
        # Save original and configure test path
        self.orig_db_path = db.get_db_path()
        db.init_db(self.db_path)

    def tearDown(self):
        db.set_db_path(self.orig_db_path)
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    async def test_upsert_and_get_user(self):
        # 1. New user default language 'en'
        await db.upsert_user(12345, name="Student One", language="en")
        lang = await db.get_user_language(12345)
        self.assertEqual(lang, "en")

        # 2. Change language to 'bn'
        await db.set_user_language(12345, "bn")
        updated_lang = await db.get_user_language(12345)
        self.assertEqual(updated_lang, "bn")

    async def test_save_note_and_cache_lookup(self):
        img_bytes = b"fake_jpeg_image_content"
        img_hash = db.compute_image_hash(img_bytes, language="en", style="full")

        # Initial cache lookup should be empty
        cached = await db.get_cached_note(img_hash)
        self.assertIsNone(cached)

        # Save note
        note_id = await db.save_note(
            telegram_id=12345,
            language="en",
            image_hash=img_hash,
            summary_text="<b>Summary text</b>",
            quiz_json='{"mcqs": []}',
            file_id="tg_file_123",
            file_unique_id="tg_unique_123",
        )
        self.assertIsInstance(note_id, int)
        self.assertGreater(note_id, 0)

        # Cache lookup should now return the saved note
        cached = await db.get_cached_note(img_hash)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["summary_text"], "<b>Summary text</b>")
        self.assertEqual(cached["file_id"], "tg_file_123")

    async def test_save_quiz_attempt(self):
        attempt_id = await db.save_quiz_attempt(
            note_id=1, telegram_id=12345, score=4, total=5
        )
        self.assertIsInstance(attempt_id, int)
        self.assertGreater(attempt_id, 0)


if __name__ == "__main__":
    unittest.main()
