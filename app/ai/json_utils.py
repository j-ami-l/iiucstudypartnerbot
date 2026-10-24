"""JSON extraction and repair utilities for AI responses."""

import json
import re
from typing import Any, Dict


def extract_json(raw_text: str) -> Dict[str, Any]:
    """Extract and parse a JSON dictionary from raw AI response text.

    Handles:
    - Fenced markdown code blocks (```json ... ``` or ``` ... ```)
    - Leading or trailing conversation / prose
    - Trailing commas before closing braces or brackets

    Raises:
        ValueError: If no valid JSON dictionary could be found or parsed.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Cannot extract JSON from empty text")

    text = raw_text.strip()

    # 1. Check for fenced code block: ```json ... ``` or ``` ... ```
    fence_pattern = r"```(?:json)?\s*\n?([\s\S]*?)\n?```"
    match = re.search(fence_pattern, text, re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
    else:
        candidate = text

    # 2. Try direct parse first
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError(f"Extracted JSON is a {type(parsed).__name__}, expected a dict")
    except json.JSONDecodeError:
        pass

    # 3. Locate the outermost JSON object braces { ... }
    first_brace = candidate.find("{")
    last_brace = candidate.rfind("}")
    if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
        # Check if the whole text has braces somewhere outside candidate
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
            raise ValueError(f"No JSON object braces found in text: {text[:100]}...")
        candidate = text[first_brace : last_brace + 1]
    else:
        candidate = candidate[first_brace : last_brace + 1]

    # Try parsing after brace slicing
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError(f"Extracted JSON is a {type(parsed).__name__}, expected a dict")
    except json.JSONDecodeError:
        pass

    # 4. Attempt repair: remove single-line comments and trailing commas
    repaired = _repair_json(candidate)
    try:
        parsed = json.loads(repaired)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError(f"Extracted JSON is a {type(parsed).__name__}, expected a dict")
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse JSON after repair: {err}") from err


def _repair_json(text: str) -> str:
    """Repair common JSON formatting defects from LLM output."""
    # Remove single line comments // ...
    cleaned = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
    # Remove trailing commas before closing braces or brackets: , } -> } and , ] -> ]
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    return cleaned.strip()
