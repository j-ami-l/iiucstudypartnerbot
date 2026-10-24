"""Unit tests for QuizService scoring and state management."""

import unittest
from app.schemas import MCQ, StudyResult
from app.services.quiz_service import QuizService, QuizState


class TestQuizService(unittest.TestCase):
    """Test suite for QuizService."""

    def setUp(self):
        self.service = QuizService()
        self.study_result = StudyResult(
            summary="Quiz test summary",
            key_points=["Point 1"],
            difficult_terms=[],
            mcqs=[
                MCQ(
                    question=f"Question {i}",
                    options=["Choice A", "Choice B", "Choice C", "Choice D"],
                    correct_index=i % 4,
                    explanation=f"Explanation for question {i}",
                )
                for i in range(5)
            ],
            short_questions=[],
        )

    def test_create_quiz(self):
        state = self.service.create_quiz(self.study_result)
        self.assertEqual(state.total_questions, 5)
        self.assertEqual(state.current_index, 0)
        self.assertEqual(state.score, 0)
        self.assertFalse(state.is_finished)

    def test_check_correct_answer(self):
        state = self.service.create_quiz(self.study_result)
        # Question 0 has correct_index = 0 (A)
        is_correct, letter, exp = self.service.check_answer(state, option_index=0)
        self.assertTrue(is_correct)
        self.assertEqual(letter, "A")
        self.assertEqual(state.score, 1)
        self.assertTrue(state.answered_current)

    def test_check_wrong_answer(self):
        state = self.service.create_quiz(self.study_result)
        # Question 0 correct answer is 0; submit 2 (C)
        is_correct, letter, exp = self.service.check_answer(state, option_index=2)
        self.assertFalse(is_correct)
        self.assertEqual(letter, "A")
        self.assertEqual(state.score, 0)
        self.assertTrue(state.answered_current)

    def test_double_answer_prevention(self):
        state = self.service.create_quiz(self.study_result)
        self.service.check_answer(state, option_index=0)
        with self.assertRaisesRegex(ValueError, "already been answered"):
            self.service.check_answer(state, option_index=1)

    def test_advance_and_finish(self):
        state = self.service.create_quiz(self.study_result)
        for i in range(5):
            self.assertEqual(state.current_index, i)
            self.service.check_answer(state, option_index=i % 4)
            has_next = self.service.next_question(state)
            if i < 4:
                self.assertTrue(has_next)
            else:
                self.assertFalse(has_next)

        self.assertTrue(state.is_finished)
        self.assertEqual(state.score, 5)

        score_card = self.service.format_score_card(state, lang="en")
        self.assertIn("5 / 5", score_card)
        self.assertIn("100%", score_card)


if __name__ == "__main__":
    unittest.main()
