"""Pydantic schemas for validating Gemma output and data models."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DifficultTerm(BaseModel):
    """A difficult or technical term and its plain-language definition."""

    term: str = Field(description="The technical or difficult term")
    meaning: str = Field(description="Explanation or definition of the term")


class MCQ(BaseModel):
    """Multiple choice question with exactly 4 options, 1 correct answer, and topic."""

    question: str = Field(description="The question prompt")
    options: List[str] = Field(
        description="Exactly 4 answer choices", min_length=4, max_length=4
    )
    correct_index: int = Field(
        description="Zero-based index of the correct answer (0-3)", ge=0, le=3
    )
    explanation: str = Field(
        description="Brief explanation of why the correct option is right"
    )
    topic: Optional[str] = Field(
        default="General",
        description="Subtopic name (at most 3 words, e.g. 'Inertia', 'Momentum')",
    )

    @field_validator("options")
    @classmethod
    def validate_options_count(cls, v: List[str]) -> List[str]:
        if len(v) != 4:
            raise ValueError(f"MCQ must have exactly 4 options, got {len(v)}")
        return v

    @field_validator("topic", mode="before")
    @classmethod
    def truncate_topic(cls, v: Optional[str]) -> str:
        if not v:
            return "General"
        val = str(v).strip()
        return val[:30] if len(val) > 30 else val


class StudyResult(BaseModel):
    """Complete structured output from Gemma note analysis."""

    title: Optional[str] = Field(
        default=None,
        description="Short, descriptive title for the note (at most 6 words)",
    )
    summary: str = Field(
        description="Concise summary of note concepts, under 120 words"
    )
    key_points: List[str] = Field(
        default_factory=list, description="Core takeaways or formulas (3 to 6 items)"
    )
    difficult_terms: List[DifficultTerm] = Field(
        default_factory=list, description="Difficult terms and meanings"
    )
    mcqs: List[MCQ] = Field(
        description="Exactly 5 multiple choice questions testing the note"
    )
    short_questions: List[str] = Field(
        default_factory=list, description="2 to 3 conceptual or discussion questions"
    )

    @field_validator("title", mode="before")
    @classmethod
    def truncate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        val = str(v).strip()
        if not val:
            return None
        return val[:60] if len(val) > 60 else val

    @field_validator("mcqs")
    @classmethod
    def validate_mcqs_count(cls, v: List[MCQ]) -> List[MCQ]:
        if len(v) != 5:
            raise ValueError(f"StudyResult must have exactly 5 MCQs, got {len(v)}")
        return v


class UnreadableResult(BaseModel):
    """Schema for unreadable or non-study images."""

    error: str = Field(description="Error code, typically 'unreadable'")
