"""Pydantic schemas for portal API request and response models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TokenExchangeRequest(BaseModel):
    """Payload sent by React /login to exchange magic-link token for session cookie."""

    token: str = Field(..., min_length=1)


class OkResponse(BaseModel):
    """Generic success response."""

    ok: bool = True


class MeResponse(BaseModel):
    """User profile response for /api/me."""

    name: Optional[str] = None
    language: str = "en"
    bot_username: str = ""


class NoteRow(BaseModel):
    """Compact summary of a study note for dashboard and notes list."""

    id: int
    title: Optional[str] = None
    created_at: str
    language: str
    quiz_ready: bool
    last_score: Optional[int] = None
    last_total: Optional[int] = None
    topics: List[str] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    """Study dashboard metrics for /api/dashboard."""

    notes_count: int
    quizzes_taken: int
    accuracy_percent: Optional[int] = None
    weak_topics_count: int
    recent_notes: List[NoteRow] = Field(default_factory=list)


class NotesListResponse(BaseModel):
    """Paginated list of notes for /api/notes."""

    items: List[NoteRow] = Field(default_factory=list)
    total: int


class NoteDetailResponse(BaseModel):
    """Detailed note view including MCQs and past quiz attempts for /api/notes/{id}."""

    id: int
    title: Optional[str] = None
    created_at: str
    language: str
    summary_text: str
    mcqs: List[Dict[str, Any]] = Field(default_factory=list)
    attempts: List[Dict[str, Any]] = Field(default_factory=list)


class WeakTopicItem(BaseModel):
    """Topic performance row for /api/weak-topics."""

    topic: str
    attempts: int
    correct: int
    accuracy_percent: int
    is_weak: bool


class MistakeItem(BaseModel):
    """Active mistake notebook row for /api/mistakes."""

    note_id: int
    note_title: Optional[str] = None
    q_index: int
    topic: str
    question: str
    options: List[str] = Field(default_factory=list)
    chosen_index: int
    correct_index: int
    explanation: str
    last_attempt_at: str


class HistoryAttemptItem(BaseModel):
    """Quiz attempt log item."""

    note_id: int
    title: str
    score: int
    total: int
    created_at: str


class WeeklyHistoryItem(BaseModel):
    """Weekly aggregate accuracy bar chart item."""

    week: str
    accuracy_percent: int
    attempts: int


class HistoryResponse(BaseModel):
    """Historical timeline and 6-week accuracy trend for /api/history."""

    attempts: List[HistoryAttemptItem] = Field(default_factory=list)
    weekly: List[WeeklyHistoryItem] = Field(default_factory=list)


class LeaderboardItem(BaseModel):
    """Campus leaderboard entry for /api/leaderboard."""

    rank: int
    name: str
    quizzes_taken: int
    total_questions: int
    accuracy_percent: int
    is_me: bool = False


class AskQuestionRequest(BaseModel):
    """Payload for asking the AI tutor a question about a study note."""

    question: str = Field(..., min_length=2, max_length=1000)


class AskQuestionResponse(BaseModel):
    """Gemma AI response to student's question."""

    answer: str

