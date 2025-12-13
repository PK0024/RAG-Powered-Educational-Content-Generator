"""PDF upload route."""

import logging
import uuid
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from typing import List

from rag_edu_generator.models.schemas import ErrorResponse, UploadResponse
from rag_edu_generator.services.content_generator import ContentGenerator
from rag_edu_generator.services.pdf_extractor import PDFExtractor
from rag_edu_generator.services.rag_service import RAGService
from rag_edu_generator.services.vector_store import VectorStoreService
from rag_edu_generator.utils.chunking import HybridChunker
from rag_edu_generator.utils.errors import PDFExtractionError, RAGServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

# Global services (in production, use dependency injection)
pdf_extractor = PDFExtractor()
chunker = HybridChunker()
vector_store_service = VectorStoreService()
rag_service = RAGService(vector_store_service)
content_generator = ContentGenerator(rag_service)


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def upload_pdf(files: List[UploadFile] = File(..., description="PDF files to upload")) -> UploadResponse:
    """
    Upload and index one or more PDF files.

    Args:
        files: List of PDF files to upload (up to 300 pages total)

    Returns:
        UploadResponse with document ID and metadata

    Raises:
        HTTPException: If upload or processing fails
    """
    try:
        # Log received files for debugging
        logger.info(f"Received upload request")
        logger.info(f"Files parameter type: {type(files)}")
        logger.info(f"Files parameter value: {files}")
        logger.info(f"Number of files: {len(files) if files else 0}")
        
        if files:
            for i, file in enumerate(files):
                logger.info(f"  File {i+1}: filename={file.filename}, content_type={getattr(file, 'content_type', 'unknown')}")
        
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one file must be uploaded",
            )

        # Validate all files are PDFs
        invalid_files = []
        for file in files:
            if not file.filename or not file.filename.lower().endswith(".pdf"):
                invalid_files.append(file.filename or "Unknown file")
        
        if invalid_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only PDF files are allowed. Invalid files: {', '.join(invalid_files)}",
            )

        # Extract and validate page counts for all files
        extracted_docs = []
        total_pages = 0
        file_info = []

        for file in files:
            # Read file content
            file_content = await file.read()

            if len(file_content) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is empty",
                )

            # Extract text from PDF (this will check individual file page count)
            try:
                extracted_doc = pdf_extractor.extract_from_bytes(
                    file_content, filename=file.filename
                )
            except PDFExtractionError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PDF extraction failed for {file.filename}: {str(e)}",
                )

            # Check total page count
            total_pages += extracted_doc.page_count
            
            if total_pages > PDFExtractor.MAX_PAGES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Total pages ({total_pages}) exceeds the maximum limit of {PDFExtractor.MAX_PAGES} pages. "
                           f"Please upload files with fewer total pages.",
                )

            extracted_docs.append(extracted_doc)
            file_info.append({
                "filename": file.filename,
                "pages": extracted_doc.page_count
            })

        # Combine all documents into one
        combined_text_parts = []
        combined_metadata = {"files": file_info, "total_files": len(files)}
        
        for i, doc in enumerate(extracted_docs):
            # Add file separator and metadata
            file_header = f"\n\n=== FILE {i+1}: {file_info[i]['filename']} ===\n\n"
            combined_text_parts.append(file_header + doc.text)
            if doc.metadata:
                combined_metadata[f"file_{i+1}_metadata"] = doc.metadata

        # Create combined document
        from rag_edu_generator.models.document import ExtractedDocument
        combined_doc = ExtractedDocument(
            text="\n\n".join(combined_text_parts),
            page_count=total_pages,
            chunks=[],
            metadata=combined_metadata,
        )

        # Chunk the combined document
        chunks = chunker.chunk_document(combined_doc)

        if not chunks:
            # Provide more detailed error message
            text_length = len(combined_doc.text.strip()) if combined_doc.text else 0
            error_detail = (
                f"No content could be extracted from the PDFs. "
                f"Total text length: {text_length} characters. "
                f"This usually means the PDF is image-based (scanned) or has no selectable text. "
                f"Please ensure your PDFs contain extractable text, not just images."
            )
            logger.warning(f"Chunking failed: {error_detail}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail,
            )

        # Logging summary
        logger.info("\n" + "=" * 80)
        logger.info("UPLOAD SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Number of files: {len(files)}")
        for info in file_info:
            logger.info(f"  - {info['filename']}: {info['pages']} pages")
        logger.info(f"Total Pages: {total_pages}")
        logger.info(f"Total Chunks: {len(chunks)}")
        logger.info(f"Average chunks per page: {len(chunks) / total_pages if total_pages > 0 else 0:.2f}")
        logger.info("=" * 80)

        # Generate document ID (use namespace for document isolation)
        document_id = str(uuid.uuid4())

        # Log namespace for verification
        logger.info(f"Using namespace '{document_id}' for document isolation")

        # Index documents in vector store
        try:
            rag_service.index_documents(chunks, namespace=document_id)
        except RAGServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to index document: {str(e)}",
            )

        file_names = ", ".join([f.filename for f in files])
        logger.info(
            f"Successfully uploaded and indexed {len(files)} PDF file(s): {file_names} "
            f"(document_id: {document_id}, total_pages: {total_pages}, "
            f"chunks: {len(chunks)})"
        )

        return UploadResponse(
            document_id=document_id,
            page_count=total_pages,
            chunks_created=len(chunks),
            message=f"Successfully uploaded and indexed {len(files)} file(s) ({file_names})",
            filename=file_names,  # Store actual filename(s) for display in chat and responses
        )

    except HTTPException:
        raise
    except ValueError as e:
        # This might catch FastAPI validation errors
        logger.error(f"Validation error during PDF upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request format: {str(e)}. Please ensure files are sent correctly.",
        )
    except Exception as e:
        logger.error(f"Unexpected error during PDF upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

