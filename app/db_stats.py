"""Database analytics, question attempt tracking, and portal statistics.

Follows the same SQLite conventions as app/db.py: synchronous queries,
short-lived connections, with async wrappers for Telegram handlers.
"""

import asyncio
import logging
from typing import Optional

from app.db import _get_connection

logger = logging.getLogger(__name__)


def record_answer_sync(
    telegram_id: int,
    note_id: int,
    q_index: int,
    topic: str,
    chosen_index: int,
    correct_index: int,
    is_correct: int,
    source: str = "quiz",
) -> int:
    """Record a single question attempt synchronously.

    Args:
        telegram_id: Student Telegram ID
        note_id: Associated note row ID
        q_index: Index of question in note's quiz_json
        topic: Concept/subtopic name
        chosen_index: Option index selected by user (0-3)
        correct_index: Actual correct option index (0-3)
        is_correct: 1 if chosen_index == correct_index, else 0
        source: 'quiz' or 'practice'

    Returns:
        The inserted attempt row ID.
    """
    clean_topic = (topic or "General").strip()[:30]
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO question_attempts (
                telegram_id, note_id, q_index, topic, chosen_index, correct_index, is_correct, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                telegram_id,
                note_id,
                q_index,
                clean_topic,
                chosen_index,
                correct_index,
                1 if is_correct else 0,
                source,
            ),
        )
        return cursor.lastrowid


async def record_answer(
    telegram_id: int,
    note_id: int,
    q_index: int,
    topic: str,
    chosen_index: int,
    correct_index: int,
    is_correct: int,
    source: str = "quiz",
) -> int:
    """Async wrapper to record a question attempt."""
    return await asyncio.to_thread(
        record_answer_sync,
        telegram_id,
        note_id,
        q_index,
        topic,
        chosen_index,
        correct_index,
        is_correct,
        source,
    )


def set_note_title_sync(note_id: int, title: str) -> None:
    """Update note title synchronously."""
    clean_title = (title or "").strip()[:60]
    with _get_connection() as conn:
        conn.execute(
            "UPDATE notes SET title = ? WHERE id = ?;", (clean_title, note_id)
        )


async def set_note_title(note_id: int, title: str) -> None:
    """Async wrapper to update note title."""
    await asyncio.to_thread(set_note_title_sync, note_id, title)
