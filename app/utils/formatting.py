"""Formatting helpers for building and splitting HTML messages."""

import html
from typing import List

from app.i18n import t
from app.schemas import StudyResult


def format_study_summary(result: StudyResult, lang: str = "en") -> str:
    """Format a StudyResult into an HTML message containing summary, key points, and difficult terms.

    All model text is escaped with html.escape to protect Telegram HTML parse mode.
    """
    parts: List[str] = []

    # 1. Summary
    if result.summary:
        summary_title = t("summary_heading", lang)
        safe_summary = html.escape(result.summary.strip())
        parts.append(f"{summary_title}\n{safe_summary}")

    # 2. Key Points
    if result.key_points:
        kp_title = t("key_points_heading", lang)
        points_lines = [
            f"• {html.escape(point.strip())}" for point in result.key_points if point.strip()
        ]
        if points_lines:
            parts.append(f"{kp_title}\n" + "\n".join(points_lines))

    # 3. Difficult Terms
    if result.difficult_terms:
        terms_title = t("difficult_terms_heading", lang)
        term_lines = [
            f"• <b>{html.escape(item.term.strip())}</b>: {html.escape(item.meaning.strip())}"
            for item in result.difficult_terms
            if item.term.strip()
        ]
        if term_lines:
            parts.append(f"{terms_title}\n" + "\n".join(term_lines))

    return "\n\n".join(parts)


def split_message(text: str, max_chars: int = 4000) -> List[str]:
    """Split long message text at paragraph or line boundaries to respect Telegram's 4096 limit."""
    if len(text) <= max_chars:
        return [text]

    chunks: List[str] = []
    current_chunk: List[str] = []
    current_length = 0

    # Split by double newlines first (paragraphs)
    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:
        p_len = len(paragraph) + (2 if current_chunk else 0)
        if current_length + p_len <= max_chars:
            current_chunk.append(paragraph)
            current_length += p_len
        else:
            # If current chunk has content, flush it
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_length = 0

            # If the paragraph alone is too large, split by single newline
            if len(paragraph) > max_chars:
                lines = paragraph.split("\n")
                for line in lines:
                    l_len = len(line) + (1 if current_chunk else 0)
                    if current_length + l_len <= max_chars:
                        current_chunk.append(line)
                        current_length += l_len
                    else:
                        if current_chunk:
                            chunks.append("\n".join(current_chunk))
                            current_chunk = []
                            current_length = 0
                        # Extreme edge case: single line longer than max_chars
                        if len(line) > max_chars:
                            for i in range(0, len(line), max_chars):
                                chunks.append(line[i : i + max_chars])
                        else:
                            current_chunk.append(line)
                            current_length = len(line)
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
            else:
                current_chunk.append(paragraph)
                current_length = len(paragraph)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks
