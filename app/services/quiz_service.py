"""Quiz service managing quiz state, answer checking, and scoring logic."""

import html
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from app.i18n import t
from app.schemas import MCQ, StudyResult

OPTION_LETTERS = ["A", "B", "C", "D"]


@dataclass
class QuizState:
    """In-memory state for an active quiz session."""

    mcqs: List[MCQ]
    current_index: int = 0
    score: int = 0
    answered_current: bool = False
    user_answers: Dict[int, int] = field(default_factory=dict)

    @property
    def total_questions(self) -> int:
        return len(self.mcqs)

    @property
    def is_finished(self) -> bool:
        return self.current_index >= self.total_questions


class QuizService:
    """Pure business logic for quizzes."""

    def create_quiz(self, study_result: StudyResult) -> QuizState:
        """Initialize a new quiz state from a StudyResult."""
        if not study_result.mcqs:
            raise ValueError("StudyResult does not contain any MCQs")
        return QuizState(mcqs=list(study_result.mcqs))

    def get_current_question(self, state: QuizState) -> Optional[Tuple[int, MCQ, int]]:
        """Get the current question index (1-based), MCQ object, and total count."""
        if state.is_finished:
            return None
        current_mcq = state.mcqs[state.current_index]
        return state.current_index + 1, current_mcq, state.total_questions

    def check_answer(
        self, state: QuizState, option_index: int
    ) -> Tuple[bool, str, str]:
        """Validate chosen option, increment score if correct, and return feedback.

        Returns:
            Tuple of (is_correct, correct_letter, explanation).
        """
        if state.is_finished:
            raise ValueError("Cannot answer an already completed quiz")
        if state.answered_current:
            raise ValueError("Current question has already been answered")

        mcq = state.mcqs[state.current_index]
        is_correct = option_index == mcq.correct_index
        correct_letter = OPTION_LETTERS[mcq.correct_index]

        state.user_answers[state.current_index] = option_index
        state.answered_current = True
        if is_correct:
            state.score += 1

        return is_correct, correct_letter, mcq.explanation

    def next_question(self, state: QuizState) -> bool:
        """Advance to the next question. Returns True if more questions remain."""
        if not state.is_finished:
            state.current_index += 1
            state.answered_current = False
        return not state.is_finished

    def format_question_message(
        self, mcq: MCQ, current: int, total: int, lang: str = "en"
    ) -> str:
        """Format a single MCQ with HTML escaping and option letters."""
        header = t("question_header", lang, current=current, total=total)
        q_text = html.escape(mcq.question.strip())

        options_formatted = []
        for idx, opt in enumerate(mcq.options):
            letter = OPTION_LETTERS[idx]
            safe_opt = html.escape(opt.strip())
            options_formatted.append(f"<b>{letter}.</b> {safe_opt}")

        body = "\n".join(options_formatted)
        return f"{header}\n\n{q_text}\n\n{body}"

    def format_answer_feedback(
        self,
        mcq: MCQ,
        is_correct: bool,
        correct_letter: str,
        lang: str = "en",
    ) -> str:
        """Format the result of answering a question with explanation."""
        if is_correct:
            result_header = t("answer_correct", lang)
        else:
            result_header = t(
                "answer_incorrect", lang, correct_letter=correct_letter
            )

        exp_prefix = t("explanation_prefix", lang)
        safe_exp = html.escape(mcq.explanation.strip())

        return f"{result_header}\n\n{exp_prefix}\n{safe_exp}"

    def format_score_card(self, state: QuizState, lang: str = "en") -> str:
        """Format final quiz score and encouraging feedback."""
        total = state.total_questions
        score = state.score
        percentage = int(round((score / total) * 100)) if total > 0 else 0

        if percentage == 100:
            feedback = t("feedback_perfect", lang)
        elif percentage >= 60:
            feedback = t("feedback_good", lang)
        else:
            feedback = t("feedback_retry", lang)

        return t(
            "quiz_completed",
            lang,
            score=score,
            total=total,
            percentage=percentage,
            feedback=feedback,
        )
