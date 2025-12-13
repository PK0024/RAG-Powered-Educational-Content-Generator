"""Flashcard generation route."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_edu_generator.models.schemas import (
    ErrorResponse,
    FlashcardsRequest,
    FlashcardsResponse,
)
from rag_edu_generator.services.content_generator import ContentGenerator
from rag_edu_generator.services.rag_service import RAGService
from rag_edu_generator.services.vector_store import VectorStoreService
from rag_edu_generator.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/flashcards", tags=["flashcards"])

# Global services (in production, use dependency injection)
vector_store_service = VectorStoreService()
rag_service = RAGService(vector_store_service)
content_generator = ContentGenerator(rag_service)


@router.post(
    "/",
    response_model=FlashcardsResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_flashcards(
    request: FlashcardsRequest,
) -> FlashcardsResponse:
    """
    Generate flashcards from the indexed content.

    Args:
        request: Flashcard generation request

    Returns:
        FlashcardsResponse with generated flashcards

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Generate flashcards
        try:
            flashcards_data = content_generator.generate_flashcards(
                num_flashcards=request.num_flashcards,
                namespace=request.document_id,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Flashcard generation failed: {str(e)}",
            )

        return FlashcardsResponse(flashcards=flashcards_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during flashcard generation: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

