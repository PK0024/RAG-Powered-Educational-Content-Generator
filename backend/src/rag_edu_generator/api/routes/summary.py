"""Summary generation route."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_edu_generator.models.schemas import (
    ErrorResponse,
    SummaryRequest,
    SummaryResponse,
)
from rag_edu_generator.services.content_generator import ContentGenerator
from rag_edu_generator.services.rag_service import RAGService
from rag_edu_generator.services.vector_store import VectorStoreService
from rag_edu_generator.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])

# Global services (in production, use dependency injection)
vector_store_service = VectorStoreService()
rag_service = RAGService(vector_store_service)
content_generator = ContentGenerator(rag_service)


@router.post(
    "/",
    response_model=SummaryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_summary(request: SummaryRequest) -> SummaryResponse:
    """
    Generate a summary of the indexed content.

    Args:
        request: Summary generation request

    Returns:
        SummaryResponse with generated summary

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Validate length
        if request.length not in ["short", "medium", "long"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Length must be 'short', 'medium', or 'long'",
            )

        # Generate summary
        try:
            summary_data = content_generator.generate_summary(
                length=request.length,
                namespace=request.document_id,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Summary generation failed: {str(e)}",
            )

        return SummaryResponse(summary=summary_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during summary generation: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

