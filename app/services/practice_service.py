"""Service for building and managing practice sets from mistakes without AI calls."""

from dataclasses import dataclass
import html
import logging
from typing import Dict, List, Optional, Tuple

from app import db_stats
from app.i18n import t
from app.schemas import MCQ, StudyResult

logger = logging.getLogger(__name__)


@dataclass
class PracticeItem:
    """A practice question originating from a specific note mistake."""

    note_id: int
    q_index: int
    topic: str
    mcq: MCQ
    note_title: Optional[str] = None


@dataclass
class PracticeState:
    """State tracking for an active practice session."""

    questions: List[PracticeItem]
    current_index: int = 0
    score: int = 0
    answered_current: bool = False
    is_finished: bool = False

    @property
    def total_questions(self) -> int:
        return len(self.questions)


class PracticeService:
    """Builds practice quizzes from recorded student mistakes."""

    async def build_practice_set(
        self, telegram_id: int, topic_filter: Optional[str] = None
    ) -> List[PracticeItem]:
        """Construct a practice set of up to 5 questions.

        Rules (AGENT_PORTAL.md Section 8):
        - Pick up to 5 mistakes
        - At most 2 per note
        - Weakest topics first
        - Filter by topic if topic_filter is provided
        - Read questions from notes.quiz_json
        """
        # 1. Fetch user weak topics for weakness ranking
        weak_topics = await db_stats.get_weak_topics(telegram_id)
        topic_accuracy: Dict[str, int] = {}
        for item in weak_topics:
            t_key = item["topic"].strip().lower()
            topic_accuracy[t_key] = item["accuracy_percent"]

        # 2. Fetch distinct active mistakes
        mistakes = await db_stats.get_mistakes(telegram_id, topic=topic_filter)
        if not mistakes:
            return []

        # 3. Sort mistakes: weakest topics first (lowest accuracy first)
        def get_weakness_score(m: Dict) -> int:
            t_key = (m.get("topic") or "General").strip().lower()
            return topic_accuracy.get(t_key, 100)

        sorted_mistakes = sorted(mistakes, key=get_weakness_score)

        # 4. Enforce 2-per-note cap and max 5 questions
        selected_mistakes: List[Dict] = []
        note_counts: Dict[int, int] = {}

        for m in sorted_mistakes:
            nid = m["note_id"]
            if note_counts.get(nid, 0) < 2:
                selected_mistakes.append(m)
                note_counts[nid] = note_counts.get(nid, 0) + 1
                if len(selected_mistakes) == 5:
                    break

        # 5. Extract MCQ objects from notes.quiz_json
        items: List[PracticeItem] = []
        for m in selected_mistakes:
            raw_json = m.get("quiz_json")
            if not raw_json:
                continue
            try:
                study_result = StudyResult.model_validate_json(raw_json)
                q_idx = m["q_index"]
                if 0 <= q_idx < len(study_result.mcqs):
                    mcq = study_result.mcqs[q_idx]
                    items.append(
                        PracticeItem(
                            note_id=m["note_id"],
                            q_index=q_idx,
                            topic=m.get("topic") or mcq.topic or "General",
                            mcq=mcq,
                            note_title=m.get("note_title"),
                        )
                    )
            except Exception as err:
                logger.warning(
                    "Failed to parse quiz_json for note %s: %s", m["note_id"], err
                )

        return items

    def create_practice(self, questions: List[PracticeItem]) -> PracticeState:
        """Create a new PracticeState instance."""
        return PracticeState(questions=questions)

    def get_current_question(
        self, state: PracticeState
    ) -> Tuple[int, PracticeItem, int]:
        """Return (1-based current number, PracticeItem, total count)."""
        if state.current_index >= len(state.questions):
            raise IndexError("Practice question index out of bounds")
        return (
            state.current_index + 1,
            state.questions[state.current_index],
            len(state.questions),
        )

    def check_answer(
        self, state: PracticeState, chosen_index: int
    ) -> Tuple[bool, str, PracticeItem]:
        """Check user option choice and update practice score."""
        item = state.questions[state.current_index]
        is_correct = chosen_index == item.mcq.correct_index
        letters = ["A", "B", "C", "D"]
        correct_letter = letters[item.mcq.correct_index]
        if is_correct:
            state.score += 1
        state.answered_current = True
        return is_correct, correct_letter, item

    def next_question(self, state: PracticeState) -> bool:
        """Advance to next question. Returns True if next exists, False if finished."""
        if state.current_index < len(state.questions) - 1:
            state.current_index += 1
            state.answered_current = False
            return True
        state.is_finished = True
        return False

    def format_question_message(
        self, item: PracticeItem, current: int, total: int, lang: str = "en"
    ) -> str:
        """Format HTML question message for practice."""
        letters = ["A", "B", "C", "D"]
        header = t(
            "practice_header", lang, current=current, total=total, topic=item.topic
        )
        escaped_q = html.escape(item.mcq.question)
        options_text = "\n".join(
            f"<b>{letters[i]}.</b> {html.escape(opt)}"
            for i, opt in enumerate(item.mcq.options)
        )
        return f"{header}\n\n<b>{escaped_q}</b>\n\n{options_text}"

    def format_answer_feedback(
        self,
        item: PracticeItem,
        is_correct: bool,
        correct_letter: str,
        lang: str = "en",
    ) -> str:
        """Format HTML feedback after student answers."""
        feedback = t(
            "answer_correct" if is_correct else "answer_incorrect",
            lang,
            correct_letter=correct_letter,
        )
        explanation = ""
        if item.mcq.explanation:
            explanation = (
                f"\n\n{t('explanation_prefix', lang)} "
                f"{html.escape(item.mcq.explanation)}"
            )
        return f"{feedback}{explanation}"

    def format_score_card(
        self,
        state: PracticeState,
        weak_topics: List[Dict],
        lang: str = "en",
    ) -> str:
        """Format final scorecard HTML including remaining weak topics."""
        total = state.total_questions
        pct = int(round(state.score / total * 100)) if total > 0 else 0

        still_weak = [w for w in weak_topics if w.get("is_weak")]
        if still_weak:
            bullets = "".join(
                t(
                    "weak_topic_item",
                    lang,
                    topic=html.escape(w["topic"]),
                    accuracy=w["accuracy_percent"],
                    correct=w["correct"],
                    attempts=w["attempts"],
                )
                for w in still_weak[:5]
            )
            weak_summary = f"{t('still_weak_prefix', lang)}{bullets}"
        else:
            weak_summary = t("no_more_weak", lang)

        return t(
            "practice_completed",
            lang,
            score=state.score,
            total=total,
            percentage=pct,
            weak_summary=weak_summary,
        )
