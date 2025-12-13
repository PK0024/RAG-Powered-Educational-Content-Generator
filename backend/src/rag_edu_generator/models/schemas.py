"""Pydantic schemas for API requests and responses."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response for PDF upload."""

    document_id: str = Field(..., description="Unique identifier for the document")
    page_count: int = Field(..., description="Number of pages in the PDF")
    chunks_created: int = Field(..., description="Number of chunks created")
    message: str = Field(..., description="Success message")


class ChatRequest(BaseModel):
    """Request for chat endpoint."""

    question: str = Field(..., description="User question")
    document_id: str = Field(
        ..., description="Document ID to scope the query (required for session isolation)"
    )
    filename: Optional[str] = Field(
        default=None, description="Name of the uploaded file(s) for context"
    )


class ChatResponse(BaseModel):
    """Response for chat endpoint."""

    answer: str = Field(..., description="Answer to the question")
    sources: list[dict[str, Any]] = Field(
        default_factory=list, description="Source chunks used for the answer"
    )
    from_document: bool = Field(
        default=True, description="Whether the answer is based on the uploaded document"
    )
    message: Optional[str] = Field(
        default=None, description="Additional message about the answer source"
    )
    filename: Optional[str] = Field(
        default=None, description="Name of the uploaded file being queried"
    )


class QuizRequest(BaseModel):
    """Request for quiz generation."""

    num_questions: int = Field(
        default=10, ge=1, le=50, description="Number of questions to generate"
    )
    question_types: Optional[list[str]] = Field(
        default=None,
        description="Question types (e.g., ['multiple_choice', 'short_answer'])",
    )
    document_id: Optional[str] = Field(
        None, description="Optional document ID to scope the quiz"
    )


class QuizResponse(BaseModel):
    """Response for quiz generation."""

    quiz: dict[str, Any] = Field(..., description="Generated quiz data")


class SummaryRequest(BaseModel):
    """Request for summary generation."""

    length: str = Field(
        default="medium",
        description="Summary length: 'short', 'medium', or 'long'",
    )
    document_id: Optional[str] = Field(
        None, description="Optional document ID to scope the summary"
    )


class SummaryResponse(BaseModel):
    """Response for summary generation."""

    summary: dict[str, Any] = Field(..., description="Generated summary data")


class FlashcardsRequest(BaseModel):
    """Request for flashcard generation."""

    num_flashcards: int = Field(
        default=20, ge=1, le=100, description="Number of flashcards to generate"
    )
    document_id: Optional[str] = Field(
        None, description="Optional document ID to scope the flashcards"
    )


class FlashcardsResponse(BaseModel):
    """Response for flashcard generation."""

    flashcards: dict[str, Any] = Field(..., description="Generated flashcards data")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class CompetitiveQuizGenerateRequest(BaseModel):
    """Request for generating competitive quiz question bank."""

    num_questions: int = Field(
        default=50, ge=20, le=100, description="Number of questions in question bank"
    )
    topic: Optional[str] = Field(
        None, description="Optional specific topic to focus on"
    )
    document_id: Optional[str] = Field(
        None, description="Optional document ID to scope the quiz"
    )


class CompetitiveQuizGenerateResponse(BaseModel):
    """Response for competitive quiz question bank generation."""

    question_bank: list[dict[str, Any]] = Field(
        ..., description="Question bank with all difficulty levels"
    )
    quiz_id: str = Field(..., description="Unique quiz ID for this session")


class CompetitiveQuizStartRequest(BaseModel):
    """Request to start a competitive quiz."""

    quiz_id: str = Field(..., description="Quiz ID from question bank")
    num_questions: int = Field(
        default=10, ge=5, le=10, description="Number of questions in quiz (5-10)"
    )


class CompetitiveQuizStartResponse(BaseModel):
    """Response for starting competitive quiz."""

    question: dict[str, Any] = Field(..., description="First question")
    session_id: str = Field(..., description="Session ID for this quiz attempt")
    current_difficulty: str = Field(..., description="Current difficulty level")


class CompetitiveQuizAnswerRequest(BaseModel):
    """Request for submitting an answer in competitive quiz."""

    session_id: str = Field(..., description="Session ID")
    question_id: str = Field(..., description="Question ID")
    answer: str = Field(..., description="User's answer")


class CompetitiveQuizAnswerResponse(BaseModel):
    """Response for competitive quiz answer submission."""

    is_correct: bool = Field(..., description="Whether answer is correct")
    correct_answer: str = Field(..., description="Correct answer")
    explanation: Optional[str] = Field(None, description="Explanation")
    reward: float = Field(..., description="Reward received")
    next_question: Optional[dict[str, Any]] = Field(
        None, description="Next question (if available)"
    )
    next_difficulty: Optional[str] = Field(None, description="Next difficulty level")
    is_complete: bool = Field(..., description="Whether quiz is complete")
    stats: dict[str, Any] = Field(..., description="Quiz statistics")


class EvaluateAnswerRequest(BaseModel):
    """Request for evaluating a short answer."""

    user_answer: str = Field(..., description="User's answer to evaluate")
    correct_answer: str = Field(..., description="Correct answer")
    question: str = Field(..., description="The question that was asked")


class EvaluateAnswerResponse(BaseModel):
    """Response for answer evaluation."""

    is_correct: bool = Field(..., description="Whether the answer is correct")
    feedback: str = Field(..., description="Feedback on the answer")

