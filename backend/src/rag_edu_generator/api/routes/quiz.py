"""Quiz generation route."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_edu_generator.models.schemas import (
    ErrorResponse,
    EvaluateAnswerRequest,
    EvaluateAnswerResponse,
    QuizRequest,
    QuizResponse,
)
from rag_edu_generator.services.content_generator import ContentGenerator
from rag_edu_generator.services.rag_service import RAGService
from rag_edu_generator.services.vector_store import VectorStoreService
from rag_edu_generator.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["quiz"])

# Global services (in production, use dependency injection)
vector_store_service = VectorStoreService()
rag_service = RAGService(vector_store_service)
content_generator = ContentGenerator(rag_service)


@router.post(
    "/",
    response_model=QuizResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_quiz(request: QuizRequest) -> QuizResponse:
    """
    Generate a quiz from the indexed content.

    Args:
        request: Quiz generation request

    Returns:
        QuizResponse with generated quiz

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Generate quiz
        try:
            quiz_data = content_generator.generate_quiz(
                num_questions=request.num_questions,
                question_types=request.question_types,
                namespace=request.document_id,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Quiz generation failed: {str(e)}",
            )

        return QuizResponse(quiz=quiz_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during quiz generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "/evaluate-answer",
    response_model=EvaluateAnswerResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def evaluate_answer(request: EvaluateAnswerRequest) -> EvaluateAnswerResponse:
    """
    Evaluate a short answer question using LLM.

    Args:
        request: Evaluation request with user answer, correct answer, and question

    Returns:
        EvaluateAnswerResponse with is_correct and feedback

    Raises:
        HTTPException: If evaluation fails
    """
    try:
        # Evaluate answer
        try:
            evaluation = content_generator.evaluate_answer(
                user_answer=request.user_answer,
                correct_answer=request.correct_answer,
                question=request.question,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Answer evaluation failed: {str(e)}",
            )

        return EvaluateAnswerResponse(
            is_correct=evaluation.get("is_correct", False),
            feedback=evaluation.get("feedback", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during answer evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

