"""Chat/Q&A route."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_edu_generator.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from rag_edu_generator.services.rag_service import RAGService
from rag_edu_generator.services.vector_store import VectorStoreService
from rag_edu_generator.utils.errors import RAGServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Global services (in production, use dependency injection)
vector_store_service = VectorStoreService()
rag_service = RAGService(vector_store_service)


@router.post(
    "/",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with the indexed material using RAG.

    Args:
        request: Chat request with question and optional document_id

    Returns:
        ChatResponse with answer and sources

    Raises:
        HTTPException: If query fails
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty",
            )

        if not request.document_id or not request.document_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document ID is required for session isolation. Please upload a PDF first.",
            )

        # Validate document_id exists (check if namespace has content)
        # This ensures we only query documents from the current session
        # Note: We make this lenient - if validation fails, we still proceed with the query
        # The query itself will handle missing documents gracefully
        try:
            from rag_edu_generator.config import settings
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=settings.pinecone_api_key)
            index = pc.Index(settings.pinecone_index_name)
            stats = index.describe_index_stats()
            namespace_stats = stats.get("namespaces", {})
            
            # Check if namespace exists and has vectors
            if request.document_id in namespace_stats:
                vector_count = namespace_stats[request.document_id].get("vector_count", 0)
                if vector_count > 0:
                    logger.info(f"Validated document_id '{request.document_id}' exists with {vector_count} vectors")
                else:
                    logger.warning(f"Document ID '{request.document_id}' exists but has 0 vectors")
            else:
                # Log available namespaces for debugging
                available_namespaces = list(namespace_stats.keys())[:10]  # Limit to first 10
                logger.warning(
                    f"Document ID '{request.document_id}' not found in namespace stats. "
                    f"Available namespaces (first 10): {available_namespaces}. "
                    f"Proceeding with query - it will handle missing documents."
                )
                # Don't raise an error - let the query proceed
                # The query will return appropriate results or handle missing documents
        except Exception as e:
            logger.warning(f"Could not validate document_id: {e}. Proceeding with query anyway.")
            # Continue anyway - the query will handle missing documents gracefully

        # Check if user is asking about uploaded materials
        question_lower = request.question.lower().strip()
        is_asking_about_materials = any(
            phrase in question_lower
            for phrase in [
                "what materials",
                "what documents",
                "what files",
                "what pdfs",
                "what have i uploaded",
                "what did i upload",
                "what files did i upload",
                "what documents did i upload",
                "what materials did i upload",
                "list my files",
                "list my documents",
                "list my materials",
                "show my files",
                "show my documents",
                "show my materials",
                "what are my files",
                "what are my documents",
                "what are my materials",
            ]
        )

        # If asking about uploaded materials, return filename directly
        if is_asking_about_materials:
            if request.filename:
                filename_display = request.filename
            else:
                filename_display = "No filename provided"
            
            answer = f"You have uploaded the following material(s) in this session:\n\n**{filename_display}**\n\nYou can ask questions about the content in this document, and I'll answer based on the information from it."
            return ChatResponse(
                answer=answer,
                sources=[],
                from_document=False,
                message="Information about uploaded materials",
                filename=request.filename or filename_display,
            )

        # Query RAG service (only from the specified document_id namespace)
        try:
            result = rag_service.query(
                question=request.question,
                similarity_top_k=5,
                namespace=request.document_id,  # Enforce session isolation
            )
        except RAGServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"RAG query failed: {str(e)}",
            )

        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            from_document=result.get("from_document", True),
            message=result.get("message"),
            filename=request.filename,  # Return filename for display
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

