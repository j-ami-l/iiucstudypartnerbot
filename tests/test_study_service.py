"""Unit tests for StudyService orchestration and retry logic."""

import unittest
from unittest.mock import AsyncMock
from app.schemas import StudyResult
from app.services.study_service import (
    InvalidJSONError,
    StudyService,
    UnreadableNoteError,
)

VALID_STUDY_JSON = """{
  "summary": "Valid summary of physics notes.",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "difficult_terms": [{"term": "Inertia", "meaning": "Resistance to motion"}],
  "mcqs": [
    {
      "question": "Q1",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0,
      "explanation": "Exp 1"
    },
    {
      "question": "Q2",
      "options": ["A", "B", "C", "D"],
      "correct_index": 1,
      "explanation": "Exp 2"
    },
    {
      "question": "Q3",
      "options": ["A", "B", "C", "D"],
      "correct_index": 2,
      "explanation": "Exp 3"
    },
    {
      "question": "Q4",
      "options": ["A", "B", "C", "D"],
      "correct_index": 3,
      "explanation": "Exp 4"
    },
    {
      "question": "Q5",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0,
      "explanation": "Exp 5"
    }
  ],
  "short_questions": ["Short Q1", "Short Q2"]
}"""


class TestStudyService(unittest.IsolatedAsyncioTestCase):
    """Test suite for StudyService."""

    async def test_analyze_note_success(self):
        mock_client = AsyncMock()
        mock_client.analyze_note.return_value = VALID_STUDY_JSON

        service = StudyService(gemma_client=mock_client)
        result = await service.analyze_note(b"fake_bytes", language="en")

        self.assertIsInstance(result, StudyResult)
        self.assertEqual(result.summary, "Valid summary of physics notes.")
        self.assertEqual(len(result.mcqs), 5)
        self.assertEqual(mock_client.analyze_note.call_count, 1)

    async def test_analyze_note_unreadable(self):
        mock_client = AsyncMock()
        mock_client.analyze_note.return_value = '{"error": "unreadable"}'

        service = StudyService(gemma_client=mock_client)
        with self.assertRaises(UnreadableNoteError):
            await service.analyze_note(b"fake_bytes", language="en")

        self.assertEqual(mock_client.analyze_note.call_count, 1)

    async def test_analyze_note_retry_success(self):
        mock_client = AsyncMock()
        # First call returns invalid JSON, second returns valid JSON
        mock_client.analyze_note.side_effect = [
            "This is corrupted output without JSON",
            VALID_STUDY_JSON,
        ]

        service = StudyService(gemma_client=mock_client)
        result = await service.analyze_note(b"fake_bytes", language="en")

        self.assertIsInstance(result, StudyResult)
        self.assertEqual(mock_client.analyze_note.call_count, 2)

    async def test_analyze_note_retry_failure(self):
        mock_client = AsyncMock()
        # Both calls return invalid JSON
        mock_client.analyze_note.side_effect = [
            "Corrupted 1",
            "Corrupted 2",
        ]

        service = StudyService(gemma_client=mock_client)
        with self.assertRaises(InvalidJSONError):
            await service.analyze_note(b"fake_bytes", language="en")

        self.assertEqual(mock_client.analyze_note.call_count, 2)


if __name__ == "__main__":
    unittest.main()
