"""Hybrid chunking strategy for documents."""

import logging
from typing import Optional

from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter

from rag_edu_generator.models.document import DocumentChunk, ExtractedDocument

logger = logging.getLogger(__name__)


class HybridChunker:
    """Hybrid chunking strategy: semantic chunks respecting page boundaries."""

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        separator: str = "\n\n",
    ):
        """
        Initialize the hybrid chunker.

        Args:
            chunk_size: Target size for chunks in characters
            chunk_overlap: Overlap between chunks in characters
            separator: Separator to use for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

        # Initialize LlamaIndex sentence splitter
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator,
        )

    def chunk_document(
        self, document: ExtractedDocument
    ) -> list[DocumentChunk]:
        """
        Chunk a document using hybrid strategy.

        The strategy:
        1. Split document by pages
        2. Apply semantic chunking within each page
        3. Maintain page number metadata

        Args:
            document: Extracted document to chunk

        Returns:
            List of DocumentChunk objects with page metadata
        """
        chunks: list[DocumentChunk] = []

        # Split text by pages (assuming double newline separates pages)
        # In practice, we'll use the page boundaries from PDF extraction
        full_text = document.text
        page_texts = full_text.split("\n\n")

        # If we have page count, try to align with it
        # Otherwise, use semantic splitting
        if document.page_count > 0 and len(page_texts) >= document.page_count:
            # Use page-based splitting
            current_chunk_index = 0
            for page_num in range(min(document.page_count, len(page_texts))):
                page_text = page_texts[page_num].strip()
                if not page_text:
                    continue

                # Create LlamaIndex document for this page
                # Include document metadata (especially files info) in first page
                page_metadata = {"page_number": page_num + 1}
                if page_num == 0 and document.metadata:
                    # Include document metadata in first page (for filename retrieval)
                    page_metadata.update(document.metadata)
                llama_doc = LlamaDocument(
                    text=page_text,
                    metadata=page_metadata,
                )

                # Split page into semantic chunks
                page_nodes = self.splitter.get_nodes_from_documents([llama_doc])

                for node in page_nodes:
                    chunk = DocumentChunk(
                        text=node.text,
                        page_number=page_num + 1,
                        chunk_index=current_chunk_index,
                        metadata={
                            **(node.metadata or {}),
                            "start_char_idx": node.start_char_idx,
                            "end_char_idx": node.end_char_idx,
                        },
                    )
                    chunks.append(chunk)
                    current_chunk_index += 1
        else:
            # Fallback: use semantic splitting on entire document
            # and try to infer page numbers from text structure
            llama_doc = LlamaDocument(
                text=full_text, metadata=document.metadata or {}
            )
            nodes = self.splitter.get_nodes_from_documents([llama_doc])

            for idx, node in enumerate(nodes):
                # Try to extract page number from metadata or estimate
                page_number = 1
                if node.metadata and "page_number" in node.metadata:
                    page_number = node.metadata["page_number"]
                elif document.page_count > 0:
                    # Estimate page number based on position
                    estimated_page = (
                        int((idx / len(nodes)) * document.page_count) + 1
                    )
                    page_number = min(estimated_page, document.page_count)

                chunk = DocumentChunk(
                    text=node.text,
                    page_number=page_number,
                    chunk_index=idx,
                    metadata={
                        **(node.metadata or {}),
                        "start_char_idx": node.start_char_idx,
                        "end_char_idx": node.end_char_idx,
                    },
                )
                chunks.append(chunk)

        # Log detailed chunking information
        logger.info("=" * 80)
        logger.info("CHUNKING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Document pages: {document.page_count}")
        logger.info(f"Total chunks created: {len(chunks)}")
        
        if chunks:
            # Show page distribution
            page_distribution = {}
            for chunk in chunks:
                page = chunk.page_number
                page_distribution[page] = page_distribution.get(page, 0) + 1
            
            logger.info(f"Chunks per page distribution:")
            for page in sorted(page_distribution.keys())[:10]:  # Show first 10 pages
                logger.info(f"  Page {page}: {page_distribution[page]} chunks")
            if len(page_distribution) > 10:
                logger.info(f"  ... and {len(page_distribution) - 10} more pages")
            
            # Show first few chunks with details
            logger.info("\n" + "-" * 80)
            logger.info("FIRST 5 CHUNKS DETAILS:")
            logger.info("-" * 80)
            for i, chunk in enumerate(chunks[:5], 1):
                logger.info(f"\nChunk #{i}:")
                logger.info(f"  Page: {chunk.page_number}")
                logger.info(f"  Chunk Index: {chunk.chunk_index}")
                logger.info(f"  Text Length: {len(chunk.text)} characters")
                logger.info(f"  Text Preview (first 200 chars):")
                preview = chunk.text[:200].replace('\n', ' ').replace('\r', ' ')
                logger.info(f"    {preview}...")
                if chunk.metadata:
                    logger.info(f"  Metadata: {chunk.metadata}")
        
        logger.info("=" * 80)

        return chunks

    def chunk_text(
        self, text: str, page_number: int = 1, metadata: Optional[dict] = None
    ) -> list[DocumentChunk]:
        """
        Chunk a text string.

        Args:
            text: Text to chunk
            page_number: Page number for metadata
            metadata: Additional metadata

        Returns:
            List of DocumentChunk objects
        """
        llama_doc = LlamaDocument(
            text=text,
            metadata={"page_number": page_number, **(metadata or {})},
        )
        nodes = self.splitter.get_nodes_from_documents([llama_doc])

        chunks = []
        for idx, node in enumerate(nodes):
            chunk = DocumentChunk(
                text=node.text,
                page_number=page_number,
                chunk_index=idx,
                metadata={
                    **(node.metadata or {}),
                    "start_char_idx": node.start_char_idx,
                    "end_char_idx": node.end_char_idx,
                },
            )
            chunks.append(chunk)

        return chunks

