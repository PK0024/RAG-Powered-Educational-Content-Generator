"""Document management route for listing existing documents."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_edu_generator.config import settings
from rag_edu_generator.models.schemas import ErrorResponse
from pinecone import Pinecone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    "/list",
    responses={
        500: {"model": ErrorResponse},
    },
)
async def list_documents():
    """
    List all existing documents (namespaces) in Pinecone.

    Returns:
        List of documents with their IDs, filenames, and metadata
    """
    try:
        # Connect to Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)
        index = pc.Index(settings.pinecone_index_name)

        # Get index stats to see all namespaces
        stats = index.describe_index_stats()
        namespaces = stats.get("namespaces", {})

        documents = []

        # For each namespace, try to get metadata from a sample vector
        for namespace, ns_stats in namespaces.items():
            vector_count = ns_stats.get("vector_count", 0)
            
            if vector_count > 0:
                # Try to fetch a sample vector to get metadata (filename)
                try:
                    # Query with empty vector to get one result (just for metadata)
                    # We'll use fetch to get metadata from the first vector ID
                    # First, let's try to get one vector's metadata
                    sample_query = index.query(
                        vector=[0.0] * 1536,  # Dummy vector (will be ignored, we just want metadata)
                        top_k=1,
                        namespace=namespace,
                        include_metadata=True,
                    )
                    
                    filename = None
                    upload_info = None
                    
                    if sample_query.get("matches"):
                        match = sample_query["matches"][0]
                        # Handle both dict and object formats
                        metadata = match.get("metadata", {}) if isinstance(match, dict) else (match.metadata or {})
                        
                        # Check various places where filename might be stored
                        # Priority: 1) filename field (direct), 2) files array, 3) file_1_metadata
                        if "filename" in metadata and metadata.get("filename"):
                            # Direct filename field (preferred - stored in first chunk)
                            filename = metadata.get("filename")
                        elif "files" in metadata:
                            files_info = metadata.get("files", [])
                            if files_info and isinstance(files_info, list):
                                filenames = [
                                    f.get("filename", "") 
                                    for f in files_info 
                                    if isinstance(f, dict) and f.get("filename")
                                ]
                                if filenames:
                                    filename = ", ".join(filenames)
                        elif "file_1_metadata" in metadata:
                            file_meta = metadata.get("file_1_metadata", {})
                            if isinstance(file_meta, dict) and file_meta.get("filename"):
                                filename = file_meta.get("filename")
                    
                    documents.append({
                        "document_id": namespace,
                        "filename": filename or f"Document {namespace[:8]}...",
                        "vector_count": vector_count,
                    })
                except Exception as e:
                    logger.warning(f"Could not get metadata for namespace {namespace}: {e}")
                    # Still include it but without filename
                    documents.append({
                        "document_id": namespace,
                        "filename": "Unknown",
                        "vector_count": vector_count,
                    })

        logger.info(f"Found {len(documents)} existing documents in Pinecone")
        
        return {
            "documents": documents,
            "total": len(documents),
        }

    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )

