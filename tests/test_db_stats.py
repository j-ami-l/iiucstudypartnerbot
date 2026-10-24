"""Unit tests for P1 study data capture, question attempts, and schema backward compatibility."""

import os
import tempfile
import unittest

from app import db, db_stats
from app.schemas import MCQ, StudyResult


class TestDbStatsAndCapture(unittest.IsolatedAsyncioTestCase):
    """Test suite for question attempts recording, note titles, and backward compatibility."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_stats.db")
        self.orig_db_path = db.get_db_path()
        db.init_db(self.db_path)

    def tearDown(self):
        db.set_db_path(self.orig_db_path)
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    async def test_record_answer_and_retrieve(self):
        # Save a note first
        note_id = await db.save_note(
            telegram_id=1001,
            language="en",
            image_hash="hash123",
            summary_text="Summary",
            quiz_json="{}",
            title="Physics Note",
        )

        # Record answer 1: correct
        att1_id = await db_stats.record_answer(
            telegram_id=1001,
            note_id=note_id,
            q_index=0,
            topic="Newton's 1st Law",
            chosen_index=1,
            correct_index=1,
            is_correct=1,
            source="quiz",
        )
        self.assertGreater(att1_id, 0)

        # Record answer 2: incorrect
        att2_id = await db_stats.record_answer(
            telegram_id=1001,
            note_id=note_id,
            q_index=1,
            topic="Momentum",
            chosen_index=2,
            correct_index=0,
            is_correct=0,
            source="quiz",
        )
        self.assertGreater(att2_id, 0)

        with db._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM question_attempts WHERE telegram_id = ? ORDER BY id ASC;",
                (1001,),
            ).fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["topic"], "Newton's 1st Law")
            self.assertEqual(rows[0]["is_correct"], 1)
            self.assertEqual(rows[1]["topic"], "Momentum")
            self.assertEqual(rows[1]["is_correct"], 0)

    async def test_set_note_title_and_cache_copy(self):
        # 1. Save note with title
        note_id = await db.save_note(
            telegram_id=1001,
            language="en",
            image_hash="shared_hash",
            summary_text="Physics Summary",
            quiz_json='{"mcqs": []}',
            title="Newton's Laws",
        )
        note = await db.get_note_by_id(note_id)
        self.assertEqual(note["title"], "Newton's Laws")

        # 2. Update title via set_note_title
        await db_stats.set_note_title(note_id, "Updated Laws of Motion")
        updated_note = await db.get_note_by_id(note_id)
        self.assertEqual(updated_note["title"], "Updated Laws of Motion")

        # 3. Simulate cache hit for another user
        cached = await db.get_cached_note("shared_hash")
        self.assertIsNotNone(cached)
        copied_title = cached.get("title")
        new_note_id = await db.save_note(
            telegram_id=2002,
            language="en",
            image_hash="shared_hash",
            summary_text=cached["summary_text"],
            quiz_json=cached["quiz_json"],
            title=copied_title,
        )
        user2_note = await db.get_note_by_id(new_note_id)
        self.assertEqual(user2_note["title"], "Updated Laws of Motion")
        self.assertEqual(user2_note["telegram_id"], 2002)

    def test_ensure_column_idempotent(self):
        with db._get_connection() as conn:
            # Check title exists in notes
            db.ensure_column(conn, "notes", "title", "TEXT")
            # Call again to ensure it doesn't fail
            db.ensure_column(conn, "notes", "title", "TEXT")

    def test_old_quiz_json_backward_compatibility(self):
        # Older cached quiz JSON without title and without topic in MCQs
        old_json = """
        {
          "summary": "This is a summary under 120 words.",
          "key_points": ["Point 1", "Point 2", "Point 3"],
          "difficult_terms": [{"term": "Inertia", "meaning": "Resistance to change"}],
          "mcqs": [
            {
              "question": "Q1?",
              "options": ["A", "B", "C", "D"],
              "correct_index": 0,
              "explanation": "Exp 1"
            },
            {
              "question": "Q2?",
              "options": ["A", "B", "C", "D"],
              "correct_index": 1,
              "explanation": "Exp 2"
            },
            {
              "question": "Q3?",
              "options": ["A", "B", "C", "D"],
              "correct_index": 2,
              "explanation": "Exp 3"
            },
            {
              "question": "Q4?",
              "options": ["A", "B", "C", "D"],
              "correct_index": 3,
              "explanation": "Exp 4"
            },
            {
              "question": "Q5?",
              "options": ["A", "B", "C", "D"],
              "correct_index": 0,
              "explanation": "Exp 5"
            }
          ],
          "short_questions": ["SQ1"]
        }
        """
        result = StudyResult.model_validate_json(old_json)
        self.assertIsNone(result.title)
        self.assertEqual(len(result.mcqs), 5)
        for mcq in result.mcqs:
            self.assertEqual(mcq.topic, "General")

    def test_title_and_topic_truncation(self):
        long_title = "A" * 100
        long_topic = "B" * 50
        mcq = MCQ(
            question="What is force?",
            options=["F=ma", "F=mv", "F=m/a", "F=a/m"],
            correct_index=0,
            explanation="Newton's second law",
            topic=long_topic,
        )
        self.assertEqual(len(mcq.topic), 30)
        self.assertEqual(mcq.topic, "B" * 30)

        result = StudyResult(
            title=long_title,
            summary="A short summary",
            mcqs=[mcq] * 5,
        )
        self.assertIsNotNone(result.title)
        self.assertEqual(len(result.title), 60)
        self.assertEqual(result.title, "A" * 60)
