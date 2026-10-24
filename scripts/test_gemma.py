"""Standalone smoke test script for Gemma 4 note understanding.

Usage:
    python scripts/test_gemma.py <image_path> [en|bn]

Example:
    python scripts/test_gemma.py samples/note1.jpg en
    python scripts/test_gemma.py samples/note1.jpg bn
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Reconfigure stdout/stderr to UTF-8 for Windows console compatibility (handles emojis and Bangla script)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path so 'app' imports work seamlessly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ai.gemma_client import (
    GemmaAPIError,
    GemmaAuthError,
    GemmaClient,
    GemmaTimeout,
)
from app.ai.json_utils import extract_json
from app.schemas import StudyResult, UnreadableResult
from pydantic import ValidationError


async def run_smoke_test(image_path: str, language: str) -> int:
    """Run smoke test on a given image file and language."""
    path = Path(image_path)
    if not path.is_file():
        print(f"❌ Error: Image file not found at '{image_path}'")
        return 1

    try:
        image_bytes = path.read_bytes()
    except Exception as err:
        print(f"❌ Error reading image file: {err}")
        return 1

    print(f"📷 Testing image: {path.name} ({len(image_bytes) / 1024:.1f} KB)")
    print(f"🌐 Target language: {language.upper()}")
    print("⏳ Sending request to Gemma 4 via configured provider...")

    client = GemmaClient()
    start_time = time.perf_counter()

    try:
        raw_output = await client.analyze_note(image_bytes, language=language)
        latency = time.perf_counter() - start_time
    except GemmaAuthError as err:
        latency = time.perf_counter() - start_time
        print(f"\n❌ AUTHENTICATION ERROR (after {latency:.2f}s):")
        print(f"   {err}")
        print("   👉 Check that GEMMA_API_KEY is properly set in your .env file.")
        return 2
    except GemmaTimeout as err:
        latency = time.perf_counter() - start_time
        print(f"\n❌ TIMEOUT ERROR (after {latency:.2f}s):")
        print(f"   {err}")
        print("   👉 Upstream model took too long to respond. Check connection or timeout setting.")
        return 3
    except GemmaAPIError as err:
        latency = time.perf_counter() - start_time
        status = f" (HTTP {err.status_code})" if err.status_code else ""
        print(f"\n❌ GEMMA API ERROR{status} (after {latency:.2f}s):")
        print(f"   {err}")
        return 4
    except Exception as err:
        latency = time.perf_counter() - start_time
        print(f"\n❌ UNEXPECTED ERROR (after {latency:.2f}s): {err}")
        return 5

    print("\n" + "=" * 60)
    print("📝 RAW MODEL OUTPUT:")
    print("=" * 60)
    print(raw_output)

    print("\n" + "=" * 60)
    print("🔍 PARSING & SCHEMA VALIDATION:")
    print("=" * 60)

    try:
        data = extract_json(raw_output)
    except ValueError as err:
        print(f"❌ BAD JSON: Could not extract valid JSON from response.")
        print(f"   Details: {err}")
        print(f"\n⏱️ Latency: {latency:.2f}s")
        return 6

    # Check for unreadable outcome
    if data.get("error") == "unreadable":
        try:
            UnreadableResult.model_validate(data)
            print("⚠️ NOTE MARKED UNREADABLE:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print(f"\n⏱️ Latency: {latency:.2f}s")
            print("✅ Status: Recognized as unreadable note successfully.")
            return 0
        except ValidationError as val_err:
            print(f"❌ Bad unreadable format: {val_err}")
            return 6

    # Validate full StudyResult
    try:
        validated = StudyResult.model_validate(data)
        print(json.dumps(validated.model_dump(), indent=2, ensure_ascii=False))
        print("\n" + "=" * 60)
        print("✅ VALIDATION SUCCESS:")
        print(f"- Summary length: {len(validated.summary.split())} words")
        print(f"- Key points: {len(validated.key_points)}")
        print(f"- Difficult terms: {len(validated.difficult_terms)}")
        print(f"- MCQs: {len(validated.mcqs)} (All have 4 options and valid correct_index)")
        print(f"- Short questions: {len(validated.short_questions)}")
        print(f"\n⏱️ Latency: {latency:.2f}s")
        return 0
    except ValidationError as err:
        print(f"❌ SCHEMA VALIDATION FAILED:")
        print(f"   {err}")
        print(f"\n⏱️ Latency: {latency:.2f}s")
        return 6


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_gemma.py <image_path> [en|bn]")
        print("Example: python scripts/test_gemma.py samples/note1.jpg en")
        sys.exit(1)

    image_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "en"

    exit_code = asyncio.run(run_smoke_test(image_path, language))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
