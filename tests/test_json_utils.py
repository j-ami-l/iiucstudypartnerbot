"""Unit tests for JSON extraction and repair utilities."""

import unittest
from app.ai.json_utils import extract_json


class TestJsonUtils(unittest.TestCase):
    """Test suite for extract_json function."""

    def test_extract_pure_json(self):
        raw = '{"summary": "Test summary", "score": 10}'
        data = extract_json(raw)
        self.assertEqual(data["summary"], "Test summary")
        self.assertEqual(data["score"], 10)

    def test_extract_fenced_json(self):
        raw = """```json
        {
            "summary": "Inside fence",
            "key_points": ["Point 1"]
        }
        ```"""
        data = extract_json(raw)
        self.assertEqual(data["summary"], "Inside fence")
        self.assertEqual(data["key_points"], ["Point 1"])

    def test_extract_fenced_without_json_tag(self):
        raw = """```
        {
            "summary": "No tag fence"
        }
        ```"""
        data = extract_json(raw)
        self.assertEqual(data["summary"], "No tag fence")

    def test_extract_with_surrounding_prose(self):
        raw = """Here is the extracted study material from your note:
        {
            "summary": "Prose wrapped",
            "key_points": []
        }
        Hope this helps your studies!"""
        data = extract_json(raw)
        self.assertEqual(data["summary"], "Prose wrapped")

    def test_extract_with_trailing_commas(self):
        raw = """{
            "summary": "Trailing commas",
            "items": [
                "one",
                "two",
            ],
        }"""
        data = extract_json(raw)
        self.assertEqual(data["summary"], "Trailing commas")
        self.assertEqual(data["items"], ["one", "two"])

    def test_extract_unreadable_json(self):
        raw = '{"error": "unreadable"}'
        data = extract_json(raw)
        self.assertEqual(data.get("error"), "unreadable")

    def test_extract_invalid_text_raises_error(self):
        raw = "This is just text without any JSON object."
        with self.assertRaises(ValueError):
            extract_json(raw)


if __name__ == "__main__":
    unittest.main()
