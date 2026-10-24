"""Database analytics, question attempt tracking, and portal statistics.

Follows the same SQLite conventions as app/db.py: synchronous queries,
short-lived connections, with async wrappers for Telegram handlers.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

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
        items = []
        for r in rows:
            raw_quiz = r["quiz_json"]
            q_idx = int(r["q_index"])
            question_text = ""
            options_list: List[str] = []
            explanation_text = ""
            if raw_quiz:
                try:
                    import json
                    parsed = json.loads(raw_quiz)
                    mcqs = parsed.get("mcqs", [])
                    if 0 <= q_idx < len(mcqs):
                        mcq = mcqs[q_idx]
                        question_text = mcq.get("question", "")
                        options_list = mcq.get("options", [])
                        explanation_text = mcq.get("explanation", "")
                except Exception:
                    pass

            items.append(
                {
                    "note_id": r["note_id"],
                    "note_title": r["note_title"],
                    "q_index": q_idx,
                    "topic": r["topic"],
                    "question": question_text,
                    "options": options_list,
                    "chosen_index": r["chosen_index"],
                    "correct_index": r["correct_index"],
                    "explanation": explanation_text,
                    "last_attempt_at": to_iso_z(r["created_at"]),
                    "quiz_json": raw_quiz,
                }
            )
        return items


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


# --- Portal Magic-Link Token and Analytics Queries ---


def create_portal_token_sync(
    token_hash: str, telegram_id: int, ttl_seconds: int = 300
) -> None:
    """Store token hash with UTC expiry inside SQLite."""
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO portal_tokens (token_hash, telegram_id, expires_at)
            VALUES (?, ?, datetime('now', '+' || ? || ' seconds'));
            """,
            (token_hash, telegram_id, ttl_seconds),
        )


async def create_portal_token(
    token_hash: str, telegram_id: int, ttl_seconds: int = 300
) -> None:
    """Async wrapper to create portal token."""
    await asyncio.to_thread(
        create_portal_token_sync, token_hash, telegram_id, ttl_seconds
    )


def consume_portal_token_sync(token_hash: str) -> Optional[int]:
    """Atomically consume a portal token (unused AND not expired).

    Returns telegram_id if successful, or None if invalid/expired/used.
    """
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE portal_tokens
            SET used_at = datetime('now')
            WHERE token_hash = ?
              AND used_at IS NULL
              AND expires_at > datetime('now');
            """,
            (token_hash,),
        )
        if cursor.rowcount == 1:
            row = conn.execute(
                "SELECT telegram_id FROM portal_tokens WHERE token_hash = ?;",
                (token_hash,),
            ).fetchone()
            if row:
                return int(row["telegram_id"])
        return None


async def consume_portal_token(token_hash: str) -> Optional[int]:
    """Async wrapper to consume a portal token."""
    return await asyncio.to_thread(consume_portal_token_sync, token_hash)


def to_iso_z(dt_str: Optional[str]) -> str:
    """Convert SQLite UTC timestamp 'YYYY-MM-DD HH:MM:SS' to ISO 8601 with trailing Z."""
    if not dt_str:
        return ""
    clean = dt_str.strip().replace(" ", "T")
    if not clean.endswith("Z"):
        clean += "Z"
    return clean


def get_user_info_sync(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve basic user record for /api/me."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT telegram_id, name, language, created_at FROM users WHERE telegram_id = ?;",
            (telegram_id,),
        ).fetchone()
        if not row:
            return None
        d = _row_to_dict(row)
        d["created_at"] = to_iso_z(d.get("created_at"))
        return d


def get_user_notes_sync(
    telegram_id: int, limit: int = 20, offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    """Retrieve paginated note summaries for user."""
    limit = min(max(1, limit), 50)
    with _get_connection() as conn:
        total_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM notes WHERE telegram_id = ?;",
            (telegram_id,),
        ).fetchone()
        total = int(total_row["cnt"]) if total_row else 0

        rows = conn.execute(
            """
            SELECT id, title, language, summary_text, quiz_json, created_at
            FROM notes
            WHERE telegram_id = ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?;
            """,
            (telegram_id, limit, offset),
        ).fetchall()

        items = []
        for r in rows:
            nid = r["id"]
            # Look up last attempt score on this note
            att_row = conn.execute(
                """
                SELECT score, total FROM quiz_attempts
                WHERE note_id = ? AND telegram_id = ?
                ORDER BY id DESC LIMIT 1;
                """,
                (nid, telegram_id),
            ).fetchone()
            last_score = att_row["score"] if att_row else None
            last_total = att_row["total"] if att_row else None

            # Extract topics and quiz_ready
            raw_quiz = r["quiz_json"]
            quiz_ready = bool(raw_quiz)
            topics: List[str] = []
            if raw_quiz:
                try:
                    import json
                    parsed = json.loads(raw_quiz)
                    for mcq in parsed.get("mcqs", []):
                        top = mcq.get("topic")
                        if top and top not in topics:
                            topics.append(top)
                except Exception:
                    pass

            items.append(
                {
                    "id": nid,
                    "title": r["title"],
                    "created_at": to_iso_z(r["created_at"]),
                    "language": r["language"],
                    "quiz_ready": quiz_ready,
                    "last_score": last_score,
                    "last_total": last_total,
                    "topics": topics,
                }
            )

        return items, total


def get_dashboard_stats_sync(telegram_id: int) -> Dict[str, Any]:
    """Calculate dashboard metrics for a user."""
    with _get_connection() as conn:
        # Notes count
        notes_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM notes WHERE telegram_id = ?;",
            (telegram_id,),
        ).fetchone()
        notes_count = int(notes_row["cnt"]) if notes_row else 0

        # Quizzes taken
        quiz_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM quiz_attempts WHERE telegram_id = ?;",
            (telegram_id,),
        ).fetchone()
        quizzes_taken = int(quiz_row["cnt"]) if quiz_row else 0

        # Overall accuracy
        acc_row = conn.execute(
            """
            SELECT COUNT(*) as total, SUM(is_correct) as correct
            FROM question_attempts
            WHERE telegram_id = ?;
            """,
            (telegram_id,),
        ).fetchone()
        total_ans = int(acc_row["total"]) if acc_row else 0
        correct_ans = int(acc_row["correct"] or 0) if acc_row else 0
        accuracy_percent = (
            int(round((correct_ans / total_ans) * 100)) if total_ans > 0 else None
        )

        # Weak topics count
        weak_topics = get_weak_topics_sync(telegram_id)
        weak_topics_count = sum(1 for w in weak_topics if w.get("is_weak"))

        # Recent 5 notes
        recent_notes, _ = get_user_notes_sync(telegram_id, limit=5, offset=0)

        return {
            "notes_count": notes_count,
            "quizzes_taken": quizzes_taken,
            "accuracy_percent": accuracy_percent,
            "weak_topics_count": weak_topics_count,
            "recent_notes": recent_notes,
        }


def get_user_note_detail_sync(
    telegram_id: int, note_id: int
) -> Optional[Dict[str, Any]]:
    """Retrieve complete note details. Returns None if not found or not owned."""
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, telegram_id, title, language, summary_text, quiz_json, created_at
            FROM notes
            WHERE id = ? AND telegram_id = ?;
            """,
            (note_id, telegram_id),
        ).fetchone()
        if not row:
            return None

        # Parse MCQs from quiz_json
        mcqs = []
        if row["quiz_json"]:
            try:
                import json
                parsed = json.loads(row["quiz_json"])
                mcqs = parsed.get("mcqs", [])
            except Exception:
                pass

        # Fetch all quiz attempts for this note
        att_rows = conn.execute(
            """
            SELECT score, total, created_at
            FROM quiz_attempts
            WHERE note_id = ? AND telegram_id = ?
            ORDER BY id DESC;
            """,
            (note_id, telegram_id),
        ).fetchall()
        attempts = [
            {
                "score": a["score"],
                "total": a["total"],
                "created_at": to_iso_z(a["created_at"]),
            }
            for a in att_rows
        ]

        return {
            "id": row["id"],
            "title": row["title"],
            "created_at": to_iso_z(row["created_at"]),
            "language": row["language"],
            "summary_text": row["summary_text"],
            "mcqs": mcqs,
            "attempts": attempts,
        }


def get_history_stats_sync(telegram_id: int) -> Dict[str, Any]:
    """Retrieve quiz attempt history and 6-week accuracy trend."""
    with _get_connection() as conn:
        # 1. Past quiz attempts joined with note title
        rows = conn.execute(
            """
            SELECT qa.note_id, n.title, qa.score, qa.total, qa.created_at
            FROM quiz_attempts qa
            LEFT JOIN notes n ON qa.note_id = n.id
            WHERE qa.telegram_id = ?
            ORDER BY qa.id DESC
            LIMIT 50;
            """,
            (telegram_id,),
        ).fetchall()
        attempts = [
            {
                "note_id": r["note_id"],
                "title": r["title"] or f"Note #{r['note_id']}",
                "score": r["score"],
                "total": r["total"],
                "created_at": to_iso_z(r["created_at"]),
            }
            for r in rows
        ]

        # 2. Weekly accuracy grouping from question_attempts
        week_rows = conn.execute(
            """
            SELECT 
                strftime('%Y-%W', created_at) as week_key,
                MIN(created_at) as sample_date,
                COUNT(*) as attempts,
                SUM(is_correct) as correct
            FROM question_attempts
            WHERE telegram_id = ?
            GROUP BY strftime('%Y-%W', created_at)
            ORDER BY week_key DESC
            LIMIT 6;
            """,
            (telegram_id,),
        ).fetchall()

        weekly = []
        for w in reversed(week_rows):
            att_cnt = int(w["attempts"])
            corr_cnt = int(w["correct"] or 0)
            acc_pct = int(round((corr_cnt / att_cnt) * 100)) if att_cnt > 0 else 0

            # Format label from sample_date, e.g. "Oct 24"
            sample_dt = w["sample_date"]
            try:
                from datetime import datetime
                parsed_dt = datetime.fromisoformat(sample_dt)
                week_label = parsed_dt.strftime("%b %d")
            except Exception:
                week_label = w["week_key"]

            weekly.append(
                {
                    "week": week_label,
                    "accuracy_percent": acc_pct,
                    "attempts": att_cnt,
                }
            )

        return {"attempts": attempts, "weekly": weekly}


def get_leaderboard_sync(
    current_user_id: int, limit: int = 20
) -> List[Dict[str, Any]]:
    """Retrieve top active students for the campus leaderboard."""
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                u.telegram_id,
                COALESCE(u.name, 'Student #' || substr(u.telegram_id, -4)) as display_name,
                COUNT(DISTINCT qz.id) as quizzes_taken,
                COUNT(qa.id) as total_questions,
                COALESCE(SUM(CASE WHEN qa.is_correct = 1 THEN 1 ELSE 0 END), 0) as correct_questions,
                CASE
                    WHEN COUNT(qa.id) > 0 THEN ROUND(100.0 * SUM(CASE WHEN qa.is_correct = 1 THEN 1 ELSE 0 END) / COUNT(qa.id))
                    ELSE 0
                END as accuracy_percent
            FROM users u
            LEFT JOIN quiz_attempts qz ON qz.telegram_id = u.telegram_id
            LEFT JOIN question_attempts qa ON qa.telegram_id = u.telegram_id
            GROUP BY u.telegram_id, u.name
            ORDER BY quizzes_taken DESC, accuracy_percent DESC, total_questions DESC
            LIMIT ?;
            """,
            (limit,),
        ).fetchall()

        result = []
        for rank, r in enumerate(rows, 1):
            result.append(
                {
                    "rank": rank,
                    "name": r["display_name"],
                    "quizzes_taken": int(r["quizzes_taken"]),
                    "total_questions": int(r["total_questions"]),
                    "accuracy_percent": int(r["accuracy_percent"]),
                    "is_me": int(r["telegram_id"]) == current_user_id,
                }
            )
        return result


