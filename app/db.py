"""Database persistence layer using SQLite3."""

import asyncio
import hashlib
import logging
import sqlite3
from typing import Any, Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Active database path (defaults to settings.DATABASE_PATH, configurable for tests)
_DB_PATH: str = settings.DATABASE_PATH


def set_db_path(path: str) -> None:
    """Set the database path (used primarily for tests)."""
    global _DB_PATH
    _DB_PATH = path


def get_db_path() -> str:
    """Get the active database path."""
    return _DB_PATH


def compute_image_hash(image_bytes: bytes, language: str, style: str = "full") -> str:
    """Compute sha256 hash of resized image bytes + language + style as cache key."""
    h = hashlib.sha256()
    h.update(image_bytes)
    h.update(language.lower().encode("utf-8"))
    h.update(style.lower().encode("utf-8"))
    return h.hexdigest()


def _get_connection() -> sqlite3.Connection:
    """Create a short-lived SQLite connection with row factory and timeout."""
    conn = sqlite3.connect(_DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Safely convert a sqlite3.Row to a dictionary across all Python versions."""
    return {k: row[k] for k in row.keys()}


def ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    """Add column to table if it doesn't already exist."""
    pragma_rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    existing_cols = {
        row["name"] if isinstance(row, sqlite3.Row) else row[1]
        for row in pragma_rows
    }
    if column not in existing_cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl};")
        logger.info("Added column '%s' to table '%s'", column, table)


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize SQLite database with WAL mode and create tables if missing."""
    if db_path:
        set_db_path(db_path)

    with _get_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                name        TEXT,
                language    TEXT NOT NULL DEFAULT 'en',
                created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id    INTEGER NOT NULL,
                language       TEXT NOT NULL,
                style          TEXT NOT NULL DEFAULT 'full',
                image_hash     TEXT NOT NULL,
                file_id        TEXT,
                file_unique_id TEXT,
                summary_text   TEXT NOT NULL,
                quiz_json      TEXT,
                created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_notes_hash ON notes(image_hash);"
        )
        ensure_column(conn, "notes", "title", "TEXT")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id     INTEGER NOT NULL,
                telegram_id INTEGER NOT NULL,
                score       INTEGER NOT NULL,
                total       INTEGER NOT NULL,
                created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS question_attempts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id   INTEGER NOT NULL,
                note_id       INTEGER NOT NULL,
                q_index       INTEGER NOT NULL,
                topic         TEXT NOT NULL DEFAULT 'General',
                chosen_index  INTEGER NOT NULL,
                correct_index INTEGER NOT NULL,
                is_correct    INTEGER NOT NULL,
                source        TEXT NOT NULL DEFAULT 'quiz',
                created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_qa_user ON question_attempts(telegram_id, created_at);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_qa_question ON question_attempts(telegram_id, note_id, q_index);"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portal_tokens (
                token_hash  TEXT PRIMARY KEY,
                telegram_id INTEGER NOT NULL,
                expires_at  TEXT NOT NULL,
                used_at     TEXT
            );
            """
        )
    logger.info("SQLite database initialized at '%s' (WAL mode enabled)", _DB_PATH)


# --- Async wrapper functions executed via asyncio.to_thread ---


def _upsert_user(telegram_id: int, name: Optional[str], language: str) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (telegram_id, name, language)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                name = COALESCE(excluded.name, users.name),
                language = CASE WHEN excluded.language != '' THEN excluded.language ELSE users.language END;
            """,
            (telegram_id, name, language),
        )


async def upsert_user(
    telegram_id: int, name: Optional[str] = None, language: str = "en"
) -> None:
    """Create or update a user record."""
    await asyncio.to_thread(_upsert_user, telegram_id, name, language)


def _get_user_language(telegram_id: int) -> str:
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT language FROM users WHERE telegram_id = ?;", (telegram_id,)
        ).fetchone()
        return row["language"] if row else "en"


async def get_user_language(telegram_id: int) -> str:
    """Retrieve user language preference, default to 'en'."""
    return await asyncio.to_thread(_get_user_language, telegram_id)


def _set_user_language(telegram_id: int, language: str) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (telegram_id, language)
            VALUES (?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET language = excluded.language;
            """,
            (telegram_id, language),
        )


async def set_user_language(telegram_id: int, language: str) -> None:
    """Update user language preference."""
    await asyncio.to_thread(_set_user_language, telegram_id, language)


def _get_cached_note(image_hash: str) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, title, summary_text, quiz_json, file_id, file_unique_id
            FROM notes
            WHERE image_hash = ?
            ORDER BY id DESC
            LIMIT 1;
            """,
            (image_hash,),
        ).fetchone()
        if row:
            return _row_to_dict(row)
        return None


async def get_cached_note(image_hash: str) -> Optional[Dict[str, Any]]:
    """Look up latest cached note by image hash."""
    return await asyncio.to_thread(_get_cached_note, image_hash)


def _get_note_by_id(note_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, telegram_id, title, language, style, image_hash, file_id, file_unique_id, summary_text, quiz_json
            FROM notes
            WHERE id = ?;
            """,
            (note_id,),
        ).fetchone()
        if row:
            return _row_to_dict(row)
        return None


async def get_note_by_id(note_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve note record by note_id."""
    return await asyncio.to_thread(_get_note_by_id, note_id)


def _save_note(
    telegram_id: int,
    language: str,
    image_hash: str,
    summary_text: str,
    quiz_json: str,
    file_id: Optional[str] = None,
    file_unique_id: Optional[str] = None,
    style: str = "full",
    title: Optional[str] = None,
) -> int:
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO notes (telegram_id, language, style, image_hash, file_id, file_unique_id, summary_text, quiz_json, title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                telegram_id,
                language,
                style,
                image_hash,
                file_id,
                file_unique_id,
                summary_text,
                quiz_json,
                title,
            ),
        )
        return cursor.lastrowid


async def save_note(
    telegram_id: int,
    language: str,
    image_hash: str,
    summary_text: str,
    quiz_json: str,
    file_id: Optional[str] = None,
    file_unique_id: Optional[str] = None,
    style: str = "full",
    title: Optional[str] = None,
) -> int:
    """Insert a note record and return its primary key id."""
    return await asyncio.to_thread(
        _save_note,
        telegram_id,
        language,
        image_hash,
        summary_text,
        quiz_json,
        file_id,
        file_unique_id,
        style,
        title,
    )


def _save_quiz_attempt(
    note_id: int, telegram_id: int, score: int, total: int
) -> int:
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO quiz_attempts (note_id, telegram_id, score, total)
            VALUES (?, ?, ?, ?);
            """,
            (note_id, telegram_id, score, total),
        )
        return cursor.lastrowid


async def save_quiz_attempt(
    note_id: int, telegram_id: int, score: int, total: int
) -> int:
    """Record a completed quiz attempt and return its attempt id."""
    return await asyncio.to_thread(
        _save_quiz_attempt, note_id, telegram_id, score, total
    )
