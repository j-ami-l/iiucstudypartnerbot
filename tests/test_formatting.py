"""Unit tests for formatting utilities."""

import unittest
from app.schemas import DifficultTerm, MCQ, StudyResult
from app.utils.formatting import format_study_summary, split_message


class TestFormattingUtils(unittest.TestCase):
    """Test suite for message formatting and splitting."""

    def setUp(self):
        self.sample_result = StudyResult(
            summary="This note is about photosynthesis in plants.",
            key_points=[
                "Light dependent reactions produce ATP & NADPH.",
                "Calvin cycle converts CO2 into glucose.",
            ],
            difficult_terms=[
                DifficultTerm(
                    term="Chlorophyll",
                    meaning="Green pigment that absorbs sunlight.",
                )
            ],
            mcqs=[
                MCQ(
                    question=f"Question {i}",
                    options=["A", "B", "C", "D"],
                    correct_index=0,
                    explanation="Reason",
                )
                for i in range(5)
            ],
            short_questions=["What is photosynthesis?"],
        )

    def test_format_study_summary_en(self):
        text = format_study_summary(self.sample_result, lang="en")
        self.assertIn("📖 <b>Summary</b>", text)
        self.assertIn("photosynthesis in plants", text)
        self.assertIn("💡 <b>Key Points</b>", text)
        self.assertIn("• Light dependent reactions produce ATP &amp; NADPH.", text)  # html escaped
        self.assertIn("🔍 <b>Difficult Terms</b>", text)
        self.assertIn("<b>Chlorophyll</b>: Green pigment that absorbs sunlight.", text)

    def test_format_study_summary_bn(self):
        text = format_study_summary(self.sample_result, lang="bn")
        self.assertIn("📖 <b>সারসংক্ষেপ</b>", text)
        self.assertIn("💡 <b>মূল বিষয়সমূহ</b>", text)
        self.assertIn("🔍 <b>কঠিন শব্দার্থ</b>", text)

    def test_split_short_message(self):
        short = "This is a short message."
        chunks = split_message(short, max_chars=100)
        self.assertEqual(chunks, [short])

    def test_split_long_message(self):
        para1 = "Paragraph 1: " + "a" * 80
        para2 = "Paragraph 2: " + "b" * 80
        full_text = f"{para1}\n\n{para2}"
        chunks = split_message(full_text, max_chars=100)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], para1)
        self.assertEqual(chunks[1], para2)


if __name__ == "__main__":
    unittest.main()
