"""Database analytics, question attempt tracking, and portal statistics.

Follows the same SQLite conventions as app/db.py: synchronous queries,
short-lived connections, with async wrappers for Telegram handlers.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from app.config import settings
from app.db import _get_connection, _row_to_dict

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


def get_weak_topics_sync(
    telegram_id: int,
    min_attempts: Optional[int] = None,
    threshold: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Compute topic accuracy stats and mark weak topics.

    Weak topic rule: at least min_attempts and accuracy < threshold.
    Returns topics sorted worst accuracy first, then attempts DESC.
    """
    if min_attempts is None:
        min_attempts = settings.WEAK_MIN_ATTEMPTS
    if threshold is None:
        threshold = settings.WEAK_ACCURACY_THRESHOLD

    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT 
                topic,
                COUNT(*) as attempts,
                SUM(is_correct) as correct
            FROM question_attempts
            WHERE telegram_id = ?
            GROUP BY LOWER(TRIM(topic))
            ORDER BY topic ASC;
            """,
            (telegram_id,),
        ).fetchall()

        topics = []
        for r in rows:
            attempts = int(r["attempts"])
            correct = int(r["correct"] or 0)
            accuracy = int(round((correct / attempts) * 100)) if attempts > 0 else 0
            is_weak = (attempts >= min_attempts) and (accuracy < threshold)
            topics.append(
                {
                    "topic": r["topic"],
                    "attempts": attempts,
                    "correct": correct,
                    "accuracy_percent": accuracy,
                    "is_weak": is_weak,
                }
            )

        topics.sort(key=lambda x: (x["accuracy_percent"], -x["attempts"]))
        return topics


async def get_weak_topics(
    telegram_id: int,
    min_attempts: Optional[int] = None,
    threshold: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Async wrapper to compute weak topics."""
    return await asyncio.to_thread(
        get_weak_topics_sync, telegram_id, min_attempts, threshold
    )


def get_mistakes_sync(
    telegram_id: int,
    topic: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve distinct mistakes where student's latest attempt was incorrect.

    When answered correctly in any later attempt, it leaves the list automatically.
    """
    with _get_connection() as conn:
        query = """
            SELECT 
                qa.note_id, 
                qa.q_index, 
                qa.topic, 
                qa.chosen_index, 
                qa.correct_index, 
                qa.is_correct, 
                qa.created_at,
                n.title as note_title,
                n.quiz_json
            FROM question_attempts qa
            INNER JOIN (
                SELECT note_id, q_index, MAX(id) as max_id
                FROM question_attempts
                WHERE telegram_id = ?
                GROUP BY note_id, q_index
            ) latest ON qa.id = latest.max_id
            INNER JOIN notes n ON qa.note_id = n.id
            WHERE qa.is_correct = 0
        """
        params: List[Any] = [telegram_id]
        if topic:
            query += " AND LOWER(TRIM(qa.topic)) = ?"
            params.append(topic.strip().lower())

        query += " ORDER BY qa.id DESC;"

        rows = conn.execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]


async def get_mistakes(
    telegram_id: int,
    topic: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Async wrapper to retrieve mistakes."""
    return await asyncio.to_thread(get_mistakes_sync, telegram_id, topic)


def count_mistakes_sync(telegram_id: int) -> int:
    """Count active mistakes for a student."""
    return len(get_mistakes_sync(telegram_id))


async def count_mistakes(telegram_id: int) -> int:
    """Async wrapper to count mistakes."""
    return await asyncio.to_thread(count_mistakes_sync, telegram_id)

