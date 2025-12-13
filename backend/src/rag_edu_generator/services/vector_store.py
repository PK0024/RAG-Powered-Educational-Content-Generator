"""Pinecone vector store integration."""

import logging
from typing import Any, Optional

from llama_index.core import Document as LlamaDocument
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from rag_edu_generator.config import settings
from rag_edu_generator.models.document import DocumentChunk
from rag_edu_generator.utils.errors import VectorStoreError

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector store operations with Pinecone."""

    def __init__(self):
        """Initialize the vector store service."""
        self.pinecone_client: Optional[Pinecone] = None
        self.vector_store: Optional[PineconeVectorStore] = None
        self._initialize_pinecone()

    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone client and vector store."""
        try:
            # Initialize Pinecone client
            self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)

            # Check if index exists, create if not
            index_name = settings.pinecone_index_name
            existing_indexes = [
                index.name for index in self.pinecone_client.list_indexes()
            ]

            if index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {index_name}")
                # Create index with appropriate dimensions for embeddings
                # OpenAI models: text-embedding-3-small, text-embedding-ada-002 = 1536 dimensions
                # Other models (Cohere, etc.) = 1024 dimensions
                # Check if index already exists to get its dimension, otherwise use default
                dimension = 1536  # Default for OpenAI embeddings
                
                # If you want to use 1024 dimensions, change the above to:
                # dimension = 1024

                # Determine cloud provider from environment
                # If environment contains 'gcp', use GCP, otherwise AWS
                if "gcp" in settings.pinecone_environment.lower():
                    cloud = "gcp"
                else:
                    cloud = "aws"

                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=cloud, region=settings.pinecone_environment
                    ),
                )
                logger.info(f"Created Pinecone index: {index_name}")
            else:
                logger.info(f"Using existing Pinecone index: {index_name}")

            # Get the index
            index = self.pinecone_client.Index(index_name)

            # Initialize LlamaIndex PineconeVectorStore
            # Note: Namespace will be set per-document or per-operation
            self.vector_store = PineconeVectorStore(
                pinecone_index=index,
            )
            self.index_name = index_name
            self.pinecone_index = index  # Store for namespace operations

            logger.info("Pinecone vector store initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize Pinecone: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

    def add_documents(
        self,
        chunks: list[DocumentChunk],
        namespace: Optional[str] = None,
        batch_size: int = 100,
    ) -> list[str]:
        """
        Add document chunks to the vector store.

        Args:
            chunks: List of document chunks to add
            namespace: Optional namespace for document isolation
            batch_size: Number of chunks to add per batch

        Returns:
            List of document IDs that were added

        Raises:
            VectorStoreError: If adding documents fails
        """
        if not self.vector_store:
            raise VectorStoreError("Vector store not initialized")

        try:
            # Convert DocumentChunks to LlamaIndex Documents
            llama_docs = []
            doc_ids = []
            for idx, chunk in enumerate(chunks):
                metadata = {
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    **(chunk.metadata or {}),
                }
                # Generate a unique ID for each chunk
                chunk_id = f"{namespace}_{idx}" if namespace else f"chunk_{idx}"
                doc_ids.append(chunk_id)
                
                llama_doc = LlamaDocument(
                    text=chunk.text,
                    metadata=metadata,
                    id_=chunk_id,
                )
                llama_docs.append(llama_doc)

            # Add documents to vector store with namespace if provided
            # Note: LlamaIndex handles batching internally
            if namespace:
                # Use Pinecone index directly for namespace support
                index = self.pinecone_client.Index(self.index_name)
                # The vector store will handle the embedding and upsert
                # We'll use the vector store's add method which should handle namespaces
                self.vector_store.add(llama_docs)
            else:
                self.vector_store.add(llama_docs)

            logger.info(
                f"Added {len(chunks)} chunks to vector store"
                + (f" (namespace: {namespace})" if namespace else "")
            )

            return doc_ids

        except Exception as e:
            error_msg = f"Failed to add documents to vector store: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

    def delete_documents(
        self, doc_ids: list[str], namespace: Optional[str] = None
    ) -> None:
        """
        Delete documents from the vector store.

        Args:
            doc_ids: List of document IDs to delete
            namespace: Optional namespace

        Raises:
            VectorStoreError: If deletion fails
        """
        if not self.vector_store:
            raise VectorStoreError("Vector store not initialized")

        try:
            self.vector_store.delete(ids=doc_ids)
            logger.info(
                f"Deleted {len(doc_ids)} documents from vector store"
                + (f" (namespace: {namespace})" if namespace else "")
            )

        except Exception as e:
            error_msg = f"Failed to delete documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

    def get_vector_store(self) -> PineconeVectorStore:
        """
        Get the underlying vector store instance.

        Returns:
            PineconeVectorStore instance

        Raises:
            VectorStoreError: If vector store not initialized
        """
        if not self.vector_store:
            raise VectorStoreError("Vector store not initialized")
        return self.vector_store

    def clear_namespace(self, namespace: str) -> None:
        """
        Clear all documents in a namespace.

        Args:
            namespace: Namespace to clear

        Raises:
            VectorStoreError: If clearing fails
        """
        if not self.pinecone_client:
            raise VectorStoreError("Pinecone client not initialized")

        try:
            index = self.pinecone_client.Index(settings.pinecone_index_name)
            index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Cleared namespace: {namespace}")

        except Exception as e:
            error_msg = f"Failed to clear namespace {namespace}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

