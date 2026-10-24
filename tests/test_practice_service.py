"""Unit tests for P5: Weak topics, practice sets, latest attempt wins, and 2-per-note cap."""

import json
import os
import tempfile
import unittest

from app import db, db_stats
from app.services.practice_service import PracticeService


class TestPracticeService(unittest.IsolatedAsyncioTestCase):
    """Test suite for practice set generation, thresholds, and mistake notebook."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_practice.db")
        self.orig_db_path = db.get_db_path()
        db.init_db(self.db_path)
        self.service = PracticeService()

    def tearDown(self):
        db.set_db_path(self.orig_db_path)
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            pass

    def _sample_quiz_json(self, num_questions: int = 5, topic_prefix: str = "Topic"):
        mcqs = []
        for i in range(num_questions):
            mcqs.append(
                {
                    "question": f"Question {i+1}?",
                    "options": ["Opt A", "Opt B", "Opt C", "Opt D"],
                    "correct_index": 0,
                    "explanation": f"Explanation for Q{i+1}",
                    "topic": f"{topic_prefix} {i+1}",
                }
            )
        return json.dumps(
            {
                "title": "Sample Note",
                "summary": "Sample summary",
                "mcqs": mcqs,
            }
        )

    async def test_weak_topics_threshold(self):
        user_id = 5001

        # Topic "Inertia": 2 attempts, 1 correct -> 50% accuracy.
        # With min_attempts=2, threshold=60% -> is_weak = True
        await db_stats.record_answer(
            user_id, note_id=1, q_index=0, topic="Inertia",
            chosen_index=0, correct_index=0, is_correct=1
        )
        await db_stats.record_answer(
            user_id, note_id=1, q_index=1, topic="Inertia",
            chosen_index=1, correct_index=0, is_correct=0
        )

        # Topic "Momentum": only 1 attempt, 0 correct -> 0% accuracy.
        # With min_attempts=2 -> is_weak = False (insufficient attempts)
        await db_stats.record_answer(
            user_id, note_id=1, q_index=2, topic="Momentum",
            chosen_index=1, correct_index=0, is_correct=0
        )

        # Topic "Friction": 3 attempts, 3 correct -> 100% accuracy.
        # With threshold=60% -> is_weak = False
        for _ in range(3):
            await db_stats.record_answer(
                user_id, note_id=1, q_index=3, topic="Friction",
                chosen_index=0, correct_index=0, is_correct=1
            )

        topics = await db_stats.get_weak_topics(user_id, min_attempts=2, threshold=60)
        topic_map = {t["topic"]: t for t in topics}

        self.assertTrue(topic_map["Inertia"]["is_weak"])
        self.assertEqual(topic_map["Inertia"]["accuracy_percent"], 50)

        self.assertFalse(topic_map["Momentum"]["is_weak"])
        self.assertEqual(topic_map["Momentum"]["attempts"], 1)

        self.assertFalse(topic_map["Friction"]["is_weak"])
        self.assertEqual(topic_map["Friction"]["accuracy_percent"], 100)

    async def test_latest_attempt_wins_rule(self):
        user_id = 5002
        note_id = await db.save_note(
            telegram_id=user_id,
            language="en",
            image_hash="note_hash_1",
            summary_text="Summary text",
            quiz_json=self._sample_quiz_json(5),
            title="Note 1",
        )

        # 1. Answer question 0 incorrectly -> should appear in mistakes notebook
        await db_stats.record_answer(
            user_id, note_id=note_id, q_index=0, topic="Topic 1",
            chosen_index=2, correct_index=0, is_correct=0, source="quiz"
        )

        mistakes = await db_stats.get_mistakes(user_id)
        self.assertEqual(len(mistakes), 1)
        self.assertEqual(mistakes[0]["note_id"], note_id)
        self.assertEqual(mistakes[0]["q_index"], 0)

        # 2. Student retries question 0 and answers correctly in practice
        await db_stats.record_answer(
            user_id, note_id=note_id, q_index=0, topic="Topic 1",
            chosen_index=0, correct_index=0, is_correct=1, source="practice"
        )

        # Latest attempt is correct -> leaves the mistake notebook automatically!
        mistakes_after = await db_stats.get_mistakes(user_id)
        self.assertEqual(len(mistakes_after), 0)

        # 3. If later answered incorrectly again -> returns to notebook
        await db_stats.record_answer(
            user_id, note_id=note_id, q_index=0, topic="Topic 1",
            chosen_index=3, correct_index=0, is_correct=0, source="quiz"
        )
        mistakes_reopened = await db_stats.get_mistakes(user_id)
        self.assertEqual(len(mistakes_reopened), 1)

    async def test_two_per_note_cap_and_weakness_priority(self):
        user_id = 5003

        # Create Note A with 4 questions and Note B with 3 questions
        note_a = await db.save_note(
            telegram_id=user_id, language="en", image_hash="hash_a",
            summary_text="Note A summary", quiz_json=self._sample_quiz_json(5, "TopicA"),
            title="Note A",
        )
        note_b = await db.save_note(
            telegram_id=user_id, language="en", image_hash="hash_b",
            summary_text="Note B summary", quiz_json=self._sample_quiz_json(5, "TopicB"),
            title="Note B",
        )

        # Record 4 mistakes on Note A
        for q in range(4):
            await db_stats.record_answer(
                user_id, note_id=note_a, q_index=q, topic=f"TopicA {q+1}",
                chosen_index=1, correct_index=0, is_correct=0
            )

        # Record 2 mistakes on Note B
        for q in range(2):
            await db_stats.record_answer(
                user_id, note_id=note_b, q_index=q, topic=f"TopicB {q+1}",
                chosen_index=1, correct_index=0, is_correct=0
            )

        # Total 6 mistakes across 2 notes. Build practice set:
        practice_items = await self.service.build_practice_set(user_id)

        # Total questions returned should be 4 (2 from Note A, 2 from Note B)
        self.assertEqual(len(practice_items), 4)

        counts_per_note = {}
        for item in practice_items:
            counts_per_note[item.note_id] = counts_per_note.get(item.note_id, 0) + 1

        self.assertEqual(counts_per_note[note_a], 2)
        self.assertEqual(counts_per_note[note_b], 2)

    async def test_max_five_questions_cap(self):
        user_id = 5004

        # Create 3 notes, 2 mistakes each (total 6 mistakes)
        notes = []
        for i in range(3):
            nid = await db.save_note(
                telegram_id=user_id, language="en", image_hash=f"hash_multi_{i}",
                summary_text="Summary", quiz_json=self._sample_quiz_json(5, f"Note{i}"),
                title=f"Note {i}",
            )
            notes.append(nid)
            for q in range(2):
                await db_stats.record_answer(
                    user_id, note_id=nid, q_index=q, topic=f"Note{i} Topic",
                    chosen_index=1, correct_index=0, is_correct=0
                )

        practice_items = await self.service.build_practice_set(user_id)
        # Should be capped at exactly 5 questions
        self.assertEqual(len(practice_items), 5)

    async def test_topic_filter_and_zero_mistakes(self):
        user_id = 5005
        note_id = await db.save_note(
            telegram_id=user_id, language="en", image_hash="hash_filter",
            summary_text="Summary", quiz_json=self._sample_quiz_json(5),
            title="Note Filter",
        )

        await db_stats.record_answer(
            user_id, note_id=note_id, q_index=0, topic="Inertia",
            chosen_index=1, correct_index=0, is_correct=0
        )
        await db_stats.record_answer(
            user_id, note_id=note_id, q_index=1, topic="Gravity",
            chosen_index=1, correct_index=0, is_correct=0
        )

        # 1. Filter by "inertia"
        items = await self.service.build_practice_set(user_id, topic_filter="inertia")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].topic, "Inertia")

        # 2. Filter by nonexistent topic
        empty_items = await self.service.build_practice_set(user_id, topic_filter="Thermodynamics")
        self.assertEqual(len(empty_items), 0)

        # 3. Nonexistent user
        no_mistakes = await self.service.build_practice_set(999999)
        self.assertEqual(len(no_mistakes), 0)
