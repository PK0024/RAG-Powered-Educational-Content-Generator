"""Competitive quiz route with adaptive learning."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_edu_generator.models.schemas import (
    CompetitiveQuizAnswerRequest,
    CompetitiveQuizAnswerResponse,
    CompetitiveQuizGenerateRequest,
    CompetitiveQuizGenerateResponse,
    CompetitiveQuizStartRequest,
    CompetitiveQuizStartResponse,
    ErrorResponse,
)
from rag_edu_generator.services.competitive_quiz_service import CompetitiveQuizService
from rag_edu_generator.services.content_generator import ContentGenerator
from rag_edu_generator.services.rag_service import RAGService
from rag_edu_generator.services.vector_store import VectorStoreService
from rag_edu_generator.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/competitive-quiz", tags=["competitive-quiz"])

# Global services
vector_store_service = VectorStoreService()
rag_service = RAGService(vector_store_service)
content_generator = ContentGenerator(rag_service)
competitive_quiz_service = CompetitiveQuizService(content_generator)


@router.post(
    "/generate-bank",
    response_model=CompetitiveQuizGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_question_bank(
    request: CompetitiveQuizGenerateRequest,
) -> CompetitiveQuizGenerateResponse:
    """
    Generate a question bank for competitive quiz.

    Args:
        request: Request with number of questions, optional topic, and document_id

    Returns:
        Question bank with quiz_id

    Raises:
        HTTPException: If generation fails
    """
    try:
        result = competitive_quiz_service.generate_question_bank(
            num_questions=request.num_questions,
            topic=request.topic,
            document_id=request.document_id,
        )

        return CompetitiveQuizGenerateResponse(
            question_bank=result["question_bank"],
            quiz_id=result["quiz_id"],
        )

    except ContentGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate question bank: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error generating question bank: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "/start",
    response_model=CompetitiveQuizStartResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def start_quiz(
    request: CompetitiveQuizStartRequest,
) -> CompetitiveQuizStartResponse:
    """
    Start a competitive quiz session.

    Args:
        request: Request with quiz_id and number of questions

    Returns:
        First question and session information

    Raises:
        HTTPException: If quiz start fails
    """
    try:
        result = competitive_quiz_service.start_quiz(
            quiz_id=request.quiz_id,
            num_questions=request.num_questions,
        )

        return CompetitiveQuizStartResponse(
            question=result["question"],
            session_id=result["session_id"],
            current_difficulty=result["current_difficulty"],
        )

    except ContentGenerationError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error starting quiz: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "/answer",
    response_model=CompetitiveQuizAnswerResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def submit_answer(
    request: CompetitiveQuizAnswerRequest,
) -> CompetitiveQuizAnswerResponse:
    """
    Submit an answer and get next question.

    Args:
        request: Request with session_id, question_id, and answer

    Returns:
        Answer result and next question (if available)

    Raises:
        HTTPException: If answer submission fails
    """
    try:
        result = competitive_quiz_service.submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer,
        )

        return CompetitiveQuizAnswerResponse(
            is_correct=result["is_correct"],
            correct_answer=result["correct_answer"],
            explanation=result.get("explanation"),
            reward=result["reward"],
            next_question=result.get("next_question"),
            next_difficulty=result.get("next_difficulty"),
            is_complete=result["is_complete"],
            stats=result["stats"],
        )

    except ContentGenerationError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error submitting answer: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

